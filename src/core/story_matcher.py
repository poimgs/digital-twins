from typing import List, Optional, Dict, Any
from ..database.repositories import StoryRepository
from ..models import Story
from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class StoryMatcher:
    """Handles story selection and relevance matching"""
    
    def __init__(self):
        self.repository = StoryRepository()
        self.llm_client = LLMClient()
    
    async def select_best_story(
        self, 
        twin_id: str, 
        user_context: str, 
        conversation_context: str,
        chat_id: int
    ) -> Optional[Story]:
        """Select most relevant story for current context"""
        try:
            # Get available stories for twin
            stories = await self.repository.get_stories_by_twin(twin_id)
            if not stories:
                return None
            
            # Get user's story history to avoid repetition
            story_history = await self.repository.get_user_story_history(chat_id)
            
            # Filter out recently told stories
            available_stories = [s for s in stories if s.story_id not in story_history]
            if not available_stories:
                return None
            
            # Score each story
            story_scores = []
            for story in available_stories:
                score = await self.calculate_story_relevance(
                    story, user_context, conversation_context
                )
                story_scores.append((story, score))
            
            # Return highest scoring story
            if story_scores:
                return max(story_scores, key=lambda x: x[1])[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error selecting story: {e}")
            return None
    
    async def calculate_story_relevance(
        self, 
        story: Story, 
        user_context: str, 
        conversation_context: str
    ) -> float:
        """Calculate how relevant a story is to current context"""
        try:
            scoring_prompt = f"""
            Rate how relevant this story is to the current conversation context (0.0 to 1.0):
            
            Story: {story.title}
            Story themes: {story.themes}
            Story triggers: {story.conversation_triggers}
            Story summary: {story.full_content[:200]}...
            
            User context: {user_context}
            Recent conversation: {conversation_context}
            
            Consider:
            1. Semantic relevance to conversation topics (0.4 weight)
            2. Relevance to user's interests and background (0.3 weight)
            3. Emotional appropriateness for conversation tone (0.2 weight)
            4. Natural storytelling opportunity (0.1 weight)
            
            Return only a decimal number between 0.0 and 1.0, where:
            - 0.0 = completely irrelevant
            - 0.5 = somewhat relevant
            - 1.0 = highly relevant and perfect timing
            """
            
            score_str = await self.llm_client.simple_prompt(scoring_prompt, temperature=0.1, max_tokens=10)
            
            try:
                score = float(score_str.strip())
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            except ValueError:
                # Fallback to keyword matching
                return self._simple_keyword_relevance(story, user_context, conversation_context)
            
        except Exception as e:
            logger.error(f"Error calculating story relevance: {e}")
            return self._simple_keyword_relevance(story, user_context, conversation_context)
    
    def _simple_keyword_relevance(
        self, 
        story: Story, 
        user_context: str, 
        conversation_context: str
    ) -> float:
        """Fallback simple keyword matching"""
        score = 0.0
        search_text = (user_context + " " + conversation_context).lower()
        
        # Check story themes
        for theme in story.themes:
            if theme.lower() in search_text:
                score += 0.3
        
        # Check conversation triggers
        for trigger in story.conversation_triggers:
            if trigger.lower() in search_text:
                score += 0.4
        
        return min(score, 1.0)