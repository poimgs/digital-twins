from typing import Dict, Any, Optional
from ..database.repositories import UserMemoryRepository
from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger
from ..models import UserMemory

logger = setup_logger(__name__)

class UserMemoryManager:
    """Manages user memory with twin-specific isolation"""
    
    def __init__(self):
        self.repository = UserMemoryRepository()
        self.llm_client = LLMClient()
    
    async def get_user_memory(self, chat_id: int, twin_id: str = None) -> UserMemory:
        """Get user memory (optionally twin-specific)"""
        return await self.repository.get_or_create_user_memory(chat_id)
    
    async def update_from_message(self, chat_id: int, user_message: str, twin_id: str) -> bool:
        """Update user memory from new message with twin context"""
        try:
            # Extract information from message
            extracted_info = await self.llm_client.extract_user_info(user_message)
            
            # Update global profile (shared across all twins)
            if extracted_info:
                await self.repository.update_user_profile(chat_id, extracted_info)
            
            # Add conversation entry with twin-specific context
            await self.repository.add_conversation_entry(chat_id, user_message, extracted_info, twin_id)
            
            return True
        except Exception as e:
            logger.error(f"Error updating user memory for twin {twin_id}: {e}")
            return False
    
    async def add_twin_response(self, chat_id: int, response: str, twin_id: str) -> bool:
        """Add twin response to conversation history"""
        return await self.repository.add_twin_response(chat_id, response, twin_id)
    
    async def get_user_context_string(self, chat_id: int, twin_id: str) -> str:
        """Get formatted user context for prompts (twin-specific)"""
        memory = await self.get_user_memory(chat_id)
        
        # Build context including twin-specific conversation history
        context_parts = []
        
        # Global user profile (shared across twins)
        profile = memory.profile
        if profile.get('name'):
            context_parts.append(f"User's name: {profile['name']}")
        if profile.get('interests'):
            context_parts.append(f"Interests: {profile['interests']}")
        if profile.get('occupation'):
            context_parts.append(f"Occupation: {profile['occupation']}")
        if profile.get('location'):
            context_parts.append(f"Location: {profile['location']}")
        
        # Twin-specific conversation history
        twin_history = await self.get_twin_specific_history(chat_id, twin_id)
        if twin_history:
            context_parts.append(f"Our conversation history:")
            for interaction in twin_history[-3:]:  # Last 3 interactions
                user_msg = interaction.get('user_message', '')
                if user_msg:
                    context_parts.append(f"- User said: {user_msg[:100]}...")
        
        # Life events they've shared (global)
        if profile.get('life_events'):
            context_parts.append(f"Personal experiences they've shared: {profile['life_events'][-2:]}")
        
        return "\n".join(context_parts) if context_parts else "This is our first conversation."
    
    async def get_recent_conversation(self, chat_id: int, twin_id: str, exchanges: int = 3) -> str:
        """Get recent conversation history for this specific twin"""
        try:
            twin_history = await self.get_twin_specific_history(chat_id, twin_id)
            
            if not twin_history:
                return "No recent conversation history."
            
            recent = twin_history[-(exchanges * 2):] if len(twin_history) >= exchanges * 2 else twin_history
            
            conversation_text = []
            for interaction in recent:
                user_msg = interaction.get('user_message')
                twin_response = interaction.get('twin_response')
                
                if user_msg:
                    conversation_text.append(f"User: {user_msg}")
                if twin_response:
                    conversation_text.append(f"{interaction.get('twin_name', 'Twin')}: {twin_response}")
            
            return "\n".join(conversation_text)
        except Exception as e:
            logger.error(f"Error getting recent conversation for twin {twin_id}: {e}")
            return ""
    
    async def get_twin_specific_history(self, chat_id: int, twin_id: str) -> list:
        """Get conversation history specific to this twin"""
        try:
            memory = await self.get_user_memory(chat_id)
            
            # Filter conversation history for this specific twin
            twin_history = []
            for interaction in memory.conversation_history:
                if interaction.get('twin_id') == twin_id:
                    twin_history.append(interaction)
            
            return twin_history
        except Exception as e:
            logger.error(f"Error getting twin-specific history: {e}")
            return []
    
    async def get_current_story(self, chat_id: int, twin_id: str) -> Optional[str]:
        """Get current active story for this twin"""
        try:
            return await self.repository.get_current_story(chat_id, twin_id)
        except Exception as e:
            logger.error(f"Error getting current story: {e}")
            return None
    
    async def clear_twin_specific_memory(self, chat_id: int, twin_id: str) -> bool:
        """Clear conversation history for this specific twin only"""
        try:
            return await self.repository.clear_twin_conversation_history(chat_id, twin_id)
        except Exception as e:
            logger.error(f"Error clearing twin-specific memory: {e}")
            return False