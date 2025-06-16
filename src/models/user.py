from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

@dataclass
class UserMemory:
    """User memory model"""
    chat_id: int
    profile: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    shared_topics: List[str] = field(default_factory=list)
    emotional_reactions: Dict[str, Any] = field(default_factory=dict)
    last_interaction: Optional[str] = None
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMemory':
        """Create UserMemory from dictionary"""
        return cls(
            chat_id=data['chat_id'],
            profile=data.get('profile', {}),
            conversation_history=data.get('conversation_history', []),
            shared_topics=data.get('shared_topics', []),
            emotional_reactions=data.get('emotional_reactions', {}),
            last_interaction=data.get('last_interaction'),
            created_at=data.get('created_at')
        )
    
    def get_user_context_string(self) -> str:
        """Build user context string for prompts"""
        context_parts = []
        
        # Basic profile info
        if self.profile.get('name'):
            context_parts.append(f"User's name: {self.profile['name']}")
        
        if self.profile.get('interests'):
            context_parts.append(f"Interests: {self.profile['interests']}")
        
        if self.profile.get('occupation'):
            context_parts.append(f"Occupation: {self.profile['occupation']}")
        
        if self.profile.get('location'):
            context_parts.append(f"Location: {self.profile['location']}")
        
        # Recent conversation context
        if self.conversation_history:
            recent = self.conversation_history[-3:]  # Last 3 interactions
            context_parts.append("Recent topics discussed:")
            for interaction in recent:
                user_msg = interaction.get('user_message', '')
                if user_msg:
                    context_parts.append(f"- {user_msg[:100]}...")
        
        # Life events they've shared
        if self.profile.get('life_events'):
            context_parts.append(f"Personal experiences shared: {self.profile['life_events'][-2:]}")
        
        return "\n".join(context_parts) if context_parts else "This is a new conversation."
    
    def get_recent_conversation_text(self, exchanges: int = 3) -> str:
        """Get recent conversation as formatted text"""
        if not self.conversation_history:
            return "No recent conversation history."
        
        recent = self.conversation_history[-(exchanges * 2):] if len(self.conversation_history) >= exchanges * 2 else self.conversation_history
        
        conversation_text = []
        for interaction in recent:
            user_msg = interaction.get('user_message')
            twin_response = interaction.get('twin_response')
            
            if user_msg:
                conversation_text.append(f"User: {user_msg}")
            if twin_response:
                conversation_text.append(f"Twin: {twin_response}")
        
        return "\n".join(conversation_text)

@dataclass
class ConversationSession:
    """Conversation session model"""
    id: Optional[str]
    chat_id: int
    twin_id: str
    current_story_id: Optional[str] = None
    session_state: str = 'active'
    context_data: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    last_activity: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        """Create ConversationSession from dictionary"""
        return cls(
            id=data.get('id'),
            chat_id=data['chat_id'],
            twin_id=data['twin_id'],
            current_story_id=data.get('current_story_id'),
            session_state=data.get('session_state', 'active'),
            context_data=data.get('context_data', {}),
            started_at=data.get('started_at'),
            last_activity=data.get('last_activity')
        )