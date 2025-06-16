from typing import Optional
from ..core import UserMemoryManager, StoryMatcher, StoryManager, LLMJudge
from ..database.repositories import DigitalTwinRepository, ConversationRepository
from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ConversationManager:
    """Manages conversation flow and responses"""
    
    def __init__(self):
        self.user_memory = UserMemoryManager()
        self.story_matcher = StoryMatcher()
        self.story_manager = StoryManager()
        self.llm_judge = LLMJudge()
        self.twin_repo = DigitalTwinRepository()
        self.conversation_repo = ConversationRepository()
        self.llm_client = LLMClient()
    
    async def handle_user_message(self, chat_id: int, user_message: str) -> str:
        """Main conversation handler"""
        try:
            # Update user memory
            await self.user_memory.update_from_message(chat_id, user_message)
            
            # Get current session
            session = await self.conversation_repo.get_or_create_session(chat_id)
            
            if not session.twin_id:
                return "Please select a digital twin first using /start"
            
            # Get twin and context
            twin = await self.twin_repo.get_twin_by_id(session.twin_id)
            if not twin:
                return "Sorry, I can't find the selected digital twin."
            
            user_context = await self.user_memory.get_user_context_string(chat_id)
            conversation_context = await self.user_memory.get_recent_conversation(chat_id)
            
            # Generate response
            response = await self._generate_contextual_response(
                chat_id, user_message, twin, user_context, conversation_context, session
            )
            
            # Store response
            await self.user_memory.add_twin_response(chat_id, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling user message: {e}")
            return "Sorry, I'm having trouble responding right now. Try again in a moment!"
    
    async def _generate_contextual_response(
        self, 
        chat_id: int, 
        user_message: str, 
        twin, 
        user_context: str, 
        conversation_context: str,
        session
    ) -> str:
        """Generate response based on conversation context"""
        
        # If there's an active story, check if user wants to continue
        if session.current_story_id:
            story_response = await self.story_manager.continue_story_naturally(
                chat_id, session.current_story_id, user_message
            )
            
            if story_response:
                return story_response
            # If story_response is None, user changed topic - continue with regular flow
        
        # Use LLM Judge to determine conversation action
        action = await self.llm_judge.determine_conversation_action(
            twin.name, twin.__dict__, user_message, user_context, conversation_context
        )
        
        if action['type'] == 'share_story' and action['confidence'] > 0.6:
            # Select and start sharing a relevant story
            story = await self.story_matcher.select_best_story(
                twin.twin_id, user_context, conversation_context, chat_id
            )
            
            if story:
                return await self.story_manager.start_story_naturally(
                    chat_id, story, twin.name, twin.__dict__, 
                    user_context, action.get('transition', '')
                )
        
        # Default: Generate regular conversational response
        return await self._generate_conversational_response(
            twin, user_message, user_context, conversation_context
        )
    
    async def _generate_conversational_response(
        self, 
        twin, 
        user_message: str, 
        user_context: str, 
        conversation_context: str
    ) -> str:
        """Generate regular conversational response"""
        try:
            style_instructions = twin.get_style_instructions()
            
            prompt = f"""
            You are {twin.name}, a digital twin with a rich personal history.
            
            Personality: {twin.personality_traits}
            Background: {twin.background}
            
            Style guidelines:
            {style_instructions}
            
            User context: {user_context}
            Recent conversation: {conversation_context}
            
            User just said: "{user_message}"
            
            Respond naturally as {twin.name}. You can:
            - Continue the conversation naturally
            - Ask engaging follow-up questions
            - Share brief relevant thoughts or reactions
            - Reference what you know about the user appropriately
            
            Be conversational, engaging, and authentic to your personality.
            Keep responses natural and flowing - typically 1-3 sentences unless elaborating on something specific.
            """
            
            return await self.llm_client.simple_prompt(prompt, temperature=0.7)
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            return "I hear you! Tell me more about that."
    
    async def generate_twin_greeting(self, twin, chat_id: int) -> str:
        """Generate personalized greeting from twin"""
        try:
            user_context = await self.user_memory.get_user_context_string(chat_id)
            style_instructions = twin.get_style_instructions()
            
            prompt = f"""
            You are {twin.name}, a digital twin with this personality: {twin.personality_traits}
            
            Background: {twin.background}
            
            Style guidelines:
            {style_instructions}
            
            User context: {user_context}
            
            Generate a warm, personal greeting. If this is a returning user, acknowledge what you remember about them.
            Keep it conversational and match your personality. Limit to 2-3 sentences.
            """
            
            return await self.llm_client.simple_prompt(prompt, temperature=0.7)
            
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return "Hey there! Great to meet you. I'm excited to share some stories with you!"