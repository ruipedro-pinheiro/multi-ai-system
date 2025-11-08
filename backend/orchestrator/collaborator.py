"""AI Collaborator - Makes AIs discuss and reach consensus

This is the CORE of Chika - makes AIs act like team members.
"""
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime
from .smart_router import SmartRouter
from providers.ai_personas import AIPersonas


class AICollaborator:
    """Orchestrates multi-AI collaboration
    
    Workflow:
    1. User sends message
    2. Decide which AIs should respond
    3. Let first AI respond
    4. Ask second AI if they agree
    5. If disagreement → private discussion
    6. Return consensus to user
    """
    
    def __init__(self, llm_router, db_session):
        """
        Args:
            llm_router: LLM router instance (from providers/llm_router.py)
            db_session: Database session for storing discussions
        """
        self.router = llm_router
        self.db = db_session
    
    async def process_user_message(
        self,
        room,
        user_message: str,
        context: List[Dict]
    ) -> Dict:
        """Process user message and orchestrate AI responses
        
        Args:
            room: Room object (SQLAlchemy model)
            user_message: User's message
            context: Conversation history
        
        Returns:
            {
                'response': str,  # Final response to user
                'author': str,  # Which AI responded
                'discussion_id': int | None,  # If there was a private discussion
                'mentions': List[str]  # Who was mentioned
            }
        """
        
        # 1. Detect @mentions in user message
        mentions = self._extract_mentions(user_message)
        
        # 2. Decide which AIs to involve
        active_ais = room.ai_list
        if mentions:
            # User explicitly mentioned AIs
            target_ais = [ai for ai in mentions if ai in active_ais]
        else:
            # Auto-select based on message type
            target_ais = self._auto_select_ais(user_message, active_ais)
        
        if not target_ais:
            target_ais = [active_ais[0]] if active_ais else ['claude']
        
        # 3. Get first AI's response
        primary_ai = target_ais[0]
        primary_response = await self._get_ai_response(
            ai_name=primary_ai,
            user_message=user_message,
            context=context
        )
        
        # 4. If multiple AIs involved, check for consensus
        if len(target_ais) > 1:
            return await self._multi_ai_consensus(
                room=room,
                primary_ai=primary_ai,
                primary_response=primary_response,
                other_ais=target_ais[1:],
                user_message=user_message,
                context=context
            )
        
        # Single AI response
        return {
            'response': primary_response,
            'author': primary_ai,
            'discussion_id': None,
            'mentions': ['@user']
        }
    
    async def _multi_ai_consensus(
        self,
        room,
        primary_ai: str,
        primary_response: str,
        other_ais: List[str],
        user_message: str,
        context: List[Dict]
    ) -> Dict:
        """Get consensus from multiple AIs
        
        Process:
        1. Show primary AI's response to other AIs
        2. Ask if they agree
        3. If disagreement → private discussion
        4. Return consensus
        """
        
        # Ask second AI what they think
        secondary_ai = other_ais[0]
        review_prompt = f"""
@{primary_ai} proposed this response to the user:

"{primary_response}"

Do you agree with this approach? If not, what would you suggest instead?
Be constructive and specific.
"""
        
        secondary_response = await self._get_ai_response(
            ai_name=secondary_ai,
            user_message=review_prompt,
            context=context
        )
        
        # Detect if there's disagreement
        has_disagreement = self._detect_disagreement(secondary_response)
        
        if has_disagreement:
            # Start private discussion
            discussion = await self._private_discussion(
                room=room,
                participants=[primary_ai, secondary_ai],
                topic=f"How to respond to: {user_message[:100]}",
                initial_messages=[
                    {'ai': primary_ai, 'content': primary_response},
                    {'ai': secondary_ai, 'content': secondary_response}
                ],
                context=context
            )
            
            # Return consensus from discussion
            return {
                'response': discussion['consensus'],
                'author': f"{primary_ai} & {secondary_ai}",
                'discussion_id': discussion['id'],
                'mentions': ['@user']
            }
        
        # Agreement - return primary response
        return {
            'response': primary_response,
            'author': primary_ai,
            'discussion_id': None,
            'mentions': ['@user']
        }
    
    async def _private_discussion(
        self,
        room,
        participants: List[str],
        topic: str,
        initial_messages: List[Dict],
        context: List[Dict],
        max_rounds: int = 3
    ) -> Dict:
        """Run a private discussion between AIs
        
        Args:
            room: Room object
            participants: List of AI names
            topic: What they're discussing
            initial_messages: Starting messages
            context: Conversation context
            max_rounds: Max discussion rounds
        
        Returns:
            {
                'id': int,
                'consensus': str,
                'messages': List[Dict]
            }
        """
        from models.room import AIDiscussion
        
        # Create discussion record
        discussion = AIDiscussion(
            room_id=room.id,
            topic=topic,
            status='ongoing'
        )
        discussion.participant_list = participants
        discussion.message_list = initial_messages
        
        self.db.add(discussion)
        self.db.commit()
        
        # Run discussion rounds
        discussion_context = context.copy()
        
        for round_num in range(max_rounds):
            # Alternate between AIs
            current_ai = participants[round_num % len(participants)]
            other_ai = participants[(round_num + 1) % len(participants)]
            
            # Build discussion prompt
            discussion_history = "\n\n".join([
                f"@{msg['ai']}: {msg['content']}"
                for msg in discussion.message_list
            ])
            
            prompt = f"""
You are {current_ai}, discussing with @{other_ai} about: {topic}

Previous discussion:
{discussion_history}

What's your response? Try to reach consensus or propose a compromise.
If you agree with the other AI, say "I agree" and propose a final response to the user.
"""
            
            response = await self._get_ai_response(
                ai_name=current_ai,
                user_message=prompt,
                context=discussion_context
            )
            
            # Add to discussion
            discussion.add_message(current_ai, response)
            
            # Check if consensus reached
            if self._consensus_reached(response):
                discussion.status = 'resolved'
                discussion.consensus = self._extract_consensus(response)
                discussion.resolved_at = datetime.utcnow()
                self.db.commit()
                break
        
        # If no consensus after max_rounds, use last response
        if discussion.status != 'resolved':
            discussion.status = 'timeout'
            discussion.consensus = discussion.message_list[-1]['content']
            self.db.commit()
        
        return {
            'id': discussion.id,
            'consensus': discussion.consensus,
            'messages': discussion.message_list
        }
    
    async def _get_ai_response(
        self,
        ai_name: str,
        user_message: str,
        context: List[Dict]
    ) -> str:
        """Get response from specific AI with proper persona/identity
        
        IMPORTANT: Injecte system prompt pour que chaque IA sache qui elle est!
        """
        # Build messages WITHOUT system prompt (context already has conversation)
        user_messages = context.copy()
        user_messages.append({
            'role': 'user',
            'content': user_message
        })
        
        # Inject AI persona (system prompt) so it knows its identity
        messages_with_persona = AIPersonas.build_messages_with_persona(
            ai_name=ai_name,
            user_messages=user_messages
        )
        
        response = await self.router.chat(
            messages=messages_with_persona,
            preferred_provider=ai_name,
            stream=False
        )
        
        return response
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text
        
        Examples:
            "@claude what do you think?" -> ['claude']
            "@gpt and @gemini please help" -> ['gpt', 'gemini']
        """
        pattern = r'@(\w+)'
        mentions = re.findall(pattern, text.lower())
        return list(set(mentions))  # Remove duplicates
    
    def _auto_select_ais(self, message: str, available_ais: List[str]) -> List[str]:
        """Auto-select which AIs should respond based on message
        
        Uses SmartRouter for intelligent AI selection based on:
        - Message intent analysis
        - AI capability matching
        - Client's configured AIs only (OAuth/API keys)
        """
        smart_router = SmartRouter()
        selected = smart_router.select_ais(
            message=message,
            available_ais=available_ais,
            max_ais=2  # Default: max 2 AIs for initial response
        )
        
        return selected
    
    def _detect_disagreement(self, response: str) -> bool:
        """Detect if AI disagrees with previous response
        
        Keywords indicating disagreement:
        - "I disagree"
        - "Actually"
        - "However"
        - "I would suggest instead"
        - "Not sure about that"
        """
        disagreement_patterns = [
            r'\bi disagree\b',
            r'\bactually\b',
            r'\bhowever\b',
            r'\binstead\b',
            r'\bnot sure\b',
            r'\bI would.*differently\b',
            r'\bbetter approach\b'
        ]
        
        response_lower = response.lower()
        return any(re.search(pattern, response_lower) for pattern in disagreement_patterns)
    
    def _consensus_reached(self, response: str) -> bool:
        """Check if AI indicates consensus reached"""
        consensus_patterns = [
            r'\bi agree\b',
            r'\bsounds good\b',
            r'\bthat works\b',
            r'\blet\'s go with\b',
            r'\bconsensus\b'
        ]
        
        response_lower = response.lower()
        return any(re.search(pattern, response_lower) for pattern in consensus_patterns)
    
    def _extract_consensus(self, response: str) -> str:
        """Extract the consensus/final response from AI message
        
        Look for patterns like:
        - "I agree. Here's the final response: ..."
        - "Consensus: ..."
        """
        # Try to find explicit consensus statement
        match = re.search(r'(?:consensus|final response|here\'s what we should say):\s*(.+)', 
                         response, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # Otherwise return the whole response
        return response
