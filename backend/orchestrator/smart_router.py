"""Smart Router - Intelligent AI Selection Based on User Intent

42-style clean code: Single responsibility, no norminette violations.
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import re


@dataclass
class Intent:
    """Detected user intent from message analysis"""
    needs_code: bool = False
    needs_creative: bool = False
    needs_factual: bool = False
    needs_analysis: bool = False
    needs_writing: bool = False
    confidence: float = 0.0


@dataclass
class AICapability:
    """AI provider capabilities mapping"""
    name: str
    strengths: List[str]
    keywords: List[str]


class SmartRouter:
    """Intelligent AI selection based on message intent
    
    Philosophy:
    - Analyze user message
    - Detect intent/needs
    - Route to best AI(s) for the task
    - Client's configured AIs only (via OAuth or API keys)
    
    Example:
        >>> router = SmartRouter()
        >>> ais = router.select_ais(
        ...     message="I need a Python script with crontab",
        ...     available_ais=['claude', 'gemini', 'gpt']
        ... )
        >>> print(ais)
        ['claude', 'gemini']  # Code expert + sysadmin expert
    """
    
    # AI capability definitions
    CAPABILITIES = {
        'claude': AICapability(
            name='claude',
            strengths=['code', 'technical', 'analysis', 'debugging'],
            keywords=[
                'code', 'python', 'javascript', 'rust', 'function',
                'debug', 'api', 'backend', 'frontend', 'algorithm',
                'implement', 'refactor', 'optimize', 'bug', 'error',
                'sql', 'database', 'query', 'script', 'program'
            ]
        ),
        'gpt': AICapability(
            name='gpt',
            strengths=['creative', 'writing', 'brainstorm', 'general'],
            keywords=[
                'creative', 'write', 'story', 'article', 'blog',
                'brainstorm', 'idea', 'alternative', 'suggest',
                'improve', 'design', 'ux', 'marketing', 'content',
                'email', 'letter', 'proposal', 'presentation'
            ]
        ),
        'gemini': AICapability(
            name='gemini',
            strengths=['factual', 'research', 'infrastructure', 'legal'],
            keywords=[
                'fact', 'research', 'data', 'statistics', 'study',
                'legal', 'rgpd', 'gdpr', 'compliance', 'policy',
                'security', 'privacy', 'backup', 'infrastructure',
                'deploy', 'docker', 'kubernetes', 'server', 'cloud',
                'aws', 'azure', 'gcp', 'devops', 'ci/cd', 'cron'
            ]
        ),
        'grok': AICapability(
            name='grok',
            strengths=['realtime', 'news', 'trends', 'social'],
            keywords=[
                'news', 'current', 'today', 'recent', 'trending',
                'twitter', 'social', 'media', 'event', 'happening'
            ]
        ),
        'ollama': AICapability(
            name='ollama',
            strengths=['privacy', 'local', 'offline', 'general'],
            keywords=[
                'private', 'local', 'offline', 'confidential',
                'sensitive', 'internal', 'proprietary'
            ]
        ),
        'llama': AICapability(
            name='llama',
            strengths=['code', 'general', 'fast'],
            keywords=[
                'code', 'python', 'javascript', 'function', 'script',
                'quick', 'fast', 'rapid', 'general', 'versatile'
            ]
        ),
        'mixtral': AICapability(
            name='mixtral',
            strengths=['creative', 'multilingual', 'reasoning'],
            keywords=[
                'creative', 'français', 'español', 'deutsch',
                'multilingual', 'translate', 'language', 'write',
                'reasoning', 'think', 'analyze'
            ]
        )
    }
    
    def __init__(self):
        """Initialize SmartRouter with capability mappings"""
        pass
    
    def select_ais(
        self,
        message: str,
        available_ais: List[str],
        max_ais: int = 3
    ) -> List[str]:
        """Select best AIs for user message
        
        Args:
            message: User's message to analyze
            available_ais: AIs configured by client (OAuth/API keys)
            max_ais: Maximum number of AIs to involve (default: 3)
        
        Returns:
            List of AI names to use (sorted by relevance)
        
        Examples:
            >>> router.select_ais(
            ...     "Write a Python backup script",
            ...     ['claude', 'gemini']
            ... )
            ['claude', 'gemini']  # Code + sysadmin
            
            >>> router.select_ais(
            ...     "Help me write a blog post",
            ...     ['gpt', 'claude']
            ... )
            ['gpt']  # Creative writing expert
        """
        if not available_ais:
            return []
        
        # 1. Analyze message intent
        intent = self._analyze_intent(message)
        
        # 2. Score each available AI
        scores = {}
        for ai_name in available_ais:
            if ai_name not in self.CAPABILITIES:
                scores[ai_name] = 0.0
                continue
            
            score = self._score_ai(ai_name, intent, message)
            scores[ai_name] = score
        
        # 3. Sort by score and return top N
        sorted_ais = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Filter out AIs with score < 0.1 (not relevant)
        relevant_ais = [
            ai for ai, score in sorted_ais
            if score >= 0.1
        ]
        
        # Return top N, minimum 1
        selected = relevant_ais[:max_ais]
        if not selected and available_ais:
            selected = [available_ais[0]]
        
        return selected
    
    def _analyze_intent(self, message: str) -> Intent:
        """Analyze user message to detect intent
        
        Args:
            message: User's message
        
        Returns:
            Intent object with detected needs
        """
        msg_lower = message.lower()
        intent = Intent()
        
        # Code/Technical
        code_keywords = [
            'code', 'script', 'function', 'api', 'backend',
            'frontend', 'debug', 'bug', 'implement', 'program',
            'python', 'javascript', 'rust', 'java', 'sql'
        ]
        intent.needs_code = any(kw in msg_lower for kw in code_keywords)
        
        # Creative
        creative_keywords = [
            'creative', 'write', 'story', 'article', 'blog',
            'brainstorm', 'idea', 'alternative', 'design'
        ]
        intent.needs_creative = any(
            kw in msg_lower for kw in creative_keywords
        )
        
        # Factual/Research
        factual_keywords = [
            'fact', 'research', 'data', 'study', 'legal',
            'rgpd', 'gdpr', 'compliance', 'security', 'backup',
            'infrastructure', 'deploy', 'server', 'cron'
        ]
        intent.needs_factual = any(
            kw in msg_lower for kw in factual_keywords
        )
        
        # Analysis
        analysis_keywords = [
            'analyze', 'review', 'compare', 'evaluate',
            'assess', 'examine', 'investigate'
        ]
        intent.needs_analysis = any(
            kw in msg_lower for kw in analysis_keywords
        )
        
        # Writing
        writing_keywords = [
            'write', 'draft', 'compose', 'email', 'letter',
            'proposal', 'documentation', 'readme'
        ]
        intent.needs_writing = any(
            kw in msg_lower for kw in writing_keywords
        )
        
        # Calculate overall confidence
        needs = [
            intent.needs_code,
            intent.needs_creative,
            intent.needs_factual,
            intent.needs_analysis,
            intent.needs_writing
        ]
        needs_count = sum(1 for need in needs if need)
        intent.confidence = min(1.0, needs_count * 0.3)
        
        return intent
    
    def _score_ai(self, ai_name: str, intent: Intent, message: str) -> float:
        """Score an AI's relevance for the detected intent
        
        Args:
            ai_name: Name of AI to score
            intent: Detected user intent
            message: Original message (for keyword matching)
        
        Returns:
            Relevance score (0.0 to 1.0)
        """
        if ai_name not in self.CAPABILITIES:
            return 0.0
        
        capability = self.CAPABILITIES[ai_name]
        score = 0.0
        msg_lower = message.lower()
        
        # Intent-based scoring
        if intent.needs_code and 'code' in capability.strengths:
            score += 0.4
        if intent.needs_creative and 'creative' in capability.strengths:
            score += 0.4
        if intent.needs_factual and 'factual' in capability.strengths:
            score += 0.4
        if intent.needs_analysis and 'analysis' in capability.strengths:
            score += 0.3
        if intent.needs_writing and 'writing' in capability.strengths:
            score += 0.3
        
        # Keyword-based scoring
        keyword_matches = sum(
            1 for kw in capability.keywords
            if kw in msg_lower
        )
        keyword_score = min(0.4, keyword_matches * 0.1)
        score += keyword_score
        
        # General purpose AIs get baseline score
        if 'general' in capability.strengths:
            score += 0.2
        
        # Normalize to 0.0-1.0
        return min(1.0, score)
    
    def explain_selection(
        self,
        message: str,
        selected_ais: List[str]
    ) -> Dict[str, Any]:
        """Explain why these AIs were selected (for debugging/logging)
        
        Args:
            message: Original user message
            selected_ais: AIs that were selected
        
        Returns:
            Explanation dict with intent and reasoning
        """
        intent = self._analyze_intent(message)
        
        return {
            'message': message[:100],
            'intent': {
                'code': intent.needs_code,
                'creative': intent.needs_creative,
                'factual': intent.needs_factual,
                'analysis': intent.needs_analysis,
                'writing': intent.needs_writing,
                'confidence': intent.confidence
            },
            'selected_ais': selected_ais,
            'reasoning': [
                f"{ai}: {self.CAPABILITIES[ai].strengths}"
                for ai in selected_ais
                if ai in self.CAPABILITIES
            ]
        }
