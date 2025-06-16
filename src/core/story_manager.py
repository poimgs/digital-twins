from typing import Optional, Dict, Any
from ..database.repositories import StoryRepository, ConversationRepository
from ..models import Story, StorySegment
from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class StoryManager:
    """Manages story progression with twin-specific isolation"""
    
    def __init__(self):
        self.story_repo = StoryRepository()
        self.conversation_repo = ConversationRepository()
        self.llm_client = LLMClient()
    
    async def start_story_naturally(
        self, 
        chat_id: int, 
        story: Story, 
        twin_name: str,
        twin_personality: Dict[str, Any],
        user_context: str,
        transition: str = "",
        twin_id: str = None
    ) -> str:
        """Start sharing a story naturally in conversation"""
        try:
            # Get first segment or use full story
            segments = await self.story_repo.get_story_segments(story.story_id)
            
            if segments:
                first_segment = segments[0]
                story_content = first_segment.content
                story_hook = first_segment.transition_hook or ""
            else:
                story_content = story.full_content
                story_hook = ""
            
            # Create natural story introduction
            intro_prompt = f"""
            You are {twin_name} naturally weaving a personal story into conversation.
            
            Your personality: {twin_personality.get('personality_traits', [])}
            Your style: {twin_personality.get('conversational_style', {})}
            User context: {user_context}
            
            Transition phrase to use: "{transition}"
            Story to share: {story_content}
            
            Create a natural, conversational way to share this story that feels spontaneous and relevant.
            Include the story content but make it feel like natural storytelling.
            {f"End with: {story_hook}" if story_hook else ""}
            
            Keep it conversational and personal, as if talking to a friend.
            """
            
            response = await self.llm_client.simple_prompt(intro_prompt, temperature=0.7)
            
            # Track story start for this specific twin
            await self.story_repo.create_story_progress(chat_id, story.story_id, twin_id)
            await self.conversation_repo.update_session_story(chat_id, story.story_id, twin_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error starting story naturally: {e}")
            return "That reminds me of something that happened to me once... but I'm having trouble recalling the details right now!"
    
    async def continue_story_naturally(
        self, 
        chat_id: int, 
        story_id: str, 
        user_message: str,
        twin_id: str
    ) -> Optional[str]:
        """Continue story based on user engagement for specific twin"""
        try:
            if not self._indicates_story_continuation(user_message):
                # User changed topic - clear story for this twin only
                await self.conversation_repo.clear_session_story(chat_id, twin_id)
                return None
            
            return await self._get_next_story_segment(chat_id, story_id, twin_id)
                
        except Exception as e:
            logger.error(f"Error continuing story for twin {twin_id}: {e}")
            return "Sorry, I lost track of where I was in that story!"
    
    def _indicates_story_continuation(self, message: str) -> bool:
        """Check if user wants to hear more of the story"""
        continuation_phrases = [
            "what happened", "then what", "continue", "go on", "and then",
            "tell me more", "what next", "keep going", "more", "wow", "really",
            "that's interesting", "amazing", "incredible", "no way", "seriously"
        ]
        
        message_lower = message.lower()
        
        # Check for explicit continuation phrases
        if any(phrase in message_lower for phrase in continuation_phrases):
            return True
        
        # Check for short enthusiastic responses
        if len(message.split()) <= 3 and any(word in message_lower for word in ["wow", "cool", "nice", "great", "awesome"]):
            return True
        
        return False
    
    async def _get_next_story_segment(self, chat_id: int, story_id: str, twin_id: str) -> str:
        """Get next story segment for this twin"""
        try:
            # Get current progress for this twin
            progress = await self.story_repo.get_story_progress(chat_id, story_id, twin_id)
            if not progress:
                return "I think we lost track of that story!"
            
            current_segment = progress.get('current_segment', 1)
            next_segment_order = current_segment + 1
            
            # Get next segment
            next_segment = await self.story_repo.get_story_segment(story_id, next_segment_order)
            
            if next_segment:
                # Update progress for this twin
                await self.story_repo.update_story_progress(chat_id, story_id, next_segment_order, twin_id)
                
                response = next_segment.content
                if next_segment.transition_hook:
                    response += f" {next_segment.transition_hook}"
                
                return response
            else:
                # Story complete
                await self.story_repo.complete_story(chat_id, story_id, twin_id)
                await self.conversation_repo.clear_session_story(chat_id, twin_id)
                return "And that's how it all ended! What a journey that was."
                
        except Exception as e:
            logger.error(f"Error getting next story segment: {e}")
            return "Sorry, I'm having trouble remembering what happened next!"