"""Room Manager - Manages chat rooms and message flow

Handles:
- Room creation
- Message routing
- AI orchestration coordination
- WebSocket broadcasts
"""
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from models.room import Room, Message, AIDiscussion, get_db
from orchestrator.collaborator import AICollaborator


class RoomManager:
    """Manages chat rooms and coordinates AI collaboration"""
    
    def __init__(self, llm_router, db_session):
        """
        Args:
            llm_router: LLM router instance
            db_session: Database session
        """
        self.router = llm_router
        self.db = db_session
        self.collaborator = AICollaborator(llm_router, db_session)
    
    def create_room(
        self,
        title: str,
        user_id: str,
        active_ais: List[str] = None
    ) -> Room:
        """Create a new chat room
        
        Args:
            title: Room title
            user_id: User identifier
            active_ais: List of AI names (default: ['claude', 'gpt'])
        
        Returns:
            Room object
        """
        if active_ais is None:
            active_ais = ['claude', 'gpt']
        
        room = Room(
            room_id=str(uuid.uuid4()),
            title=title,
            user_id=user_id
        )
        room.ai_list = active_ais
        
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        
        return room
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get room by ID"""
        return self.db.query(Room).filter(Room.room_id == room_id).first()
    
    def list_rooms(self, user_id: str) -> List[Room]:
        """List all rooms for a user"""
        return self.db.query(Room).filter(
            Room.user_id == user_id
        ).order_by(Room.updated_at.desc()).all()
    
    def add_user_message(
        self,
        room: Room,
        content: str
    ) -> Message:
        """Add user message to room
        
        Args:
            room: Room object
            content: Message content
        
        Returns:
            Message object
        """
        # Extract mentions
        from orchestrator.collaborator import AICollaborator
        mentions = AICollaborator(None, None)._extract_mentions(content)
        
        message = Message(
            room_id=room.id,
            role='user',
            author='user',
            content=content
        )
        message.mention_list = mentions
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def add_ai_message(
        self,
        room: Room,
        ai_name: str,
        content: str,
        mentions: List[str] = None,
        discussion_id: int = None
    ) -> Message:
        """Add AI message to room
        
        Args:
            room: Room object
            ai_name: AI name ('claude', 'gpt', etc.)
            content: Message content
            mentions: List of @mentions
            discussion_id: Associated discussion ID (if any)
        
        Returns:
            Message object
        """
        message = Message(
            room_id=room.id,
            role='assistant',
            author=ai_name,
            content=content,
            discussion_id=discussion_id
        )
        message.mention_list = mentions or []
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    async def process_user_message(
        self,
        room: Room,
        content: str
    ) -> Dict:
        """Process user message and get AI response(s)
        
        This is the main entry point for message handling.
        
        Args:
            room: Room object
            content: User message content
        
        Returns:
            {
                'user_message': Message,
                'ai_message': Message,
                'discussion': AIDiscussion | None
            }
        """
        # 1. Save user message
        user_msg = self.add_user_message(room, content)
        
        # 2. Get conversation context (comme ton MCP!)
        # FREEMIUM: 50 messages | PRO: 999999 (illimité)
        # TODO: Check if user is PRO tier
        context_limit = 999999  # Unlimited for now (PRO-like behavior)
        context = self.get_conversation_context(room, limit=context_limit)
        
        # 3. Orchestrate AI collaboration
        result = await self.collaborator.process_user_message(
            room=room,
            user_message=content,
            context=context
        )
        
        # 4. Save AI response
        ai_msg = self.add_ai_message(
            room=room,
            ai_name=result['author'],
            content=result['response'],
            mentions=result.get('mentions', []),
            discussion_id=result.get('discussion_id')
        )
        
        # 5. Get discussion if exists
        discussion = None
        if result.get('discussion_id'):
            discussion = self.db.query(AIDiscussion).get(result['discussion_id'])
        
        return {
            'user_message': user_msg,
            'ai_message': ai_msg,
            'discussion': discussion
        }
    
    def get_conversation_context(
        self,
        room: Room,
        limit: int = 50
    ) -> List[Dict]:
        """Get recent conversation history for context
        
        Args:
            room: Room object
            limit: Max number of messages (50=freemium, 999999=PRO unlimited)
        
        Returns:
            List of message dicts in OpenAI format
        
        Note:
            Équivalent à ton système MCP shared-context!
            - FREEMIUM: 50 messages (puis oublie les anciens)
            - PRO: 999999 = pratiquement illimité (comme ton MCP)
        """
        messages = self.db.query(Message).filter(
            Message.room_id == room.id
        ).order_by(Message.timestamp.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        messages = list(reversed(messages))
        
        # Convert to OpenAI format
        context = []
        for msg in messages:
            context.append({
                'role': msg.role,
                'content': msg.content
            })
        
        return context
    
    def get_messages(
        self,
        room: Room,
        limit: int = 100
    ) -> List[Message]:
        """Get all messages in a room
        
        Args:
            room: Room object
            limit: Max messages to return
        
        Returns:
            List of Message objects
        """
        return self.db.query(Message).filter(
            Message.room_id == room.id
        ).order_by(Message.timestamp).limit(limit).all()
    
    def get_discussions(
        self,
        room: Room
    ) -> List[AIDiscussion]:
        """Get all AI discussions in a room
        
        Args:
            room: Room object
        
        Returns:
            List of AIDiscussion objects
        """
        return self.db.query(AIDiscussion).filter(
            AIDiscussion.room_id == room.id
        ).order_by(AIDiscussion.created_at.desc()).all()
    
    def update_room_ais(
        self,
        room: Room,
        ai_list: List[str]
    ) -> Room:
        """Update which AIs are active in a room
        
        Args:
            room: Room object
            ai_list: New list of AI names
        
        Returns:
            Updated Room object
        """
        room.ai_list = ai_list
        room.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(room)
        return room
