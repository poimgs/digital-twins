from typing import Dict, Any
from ..utils.llm_client import LLMClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class LLMJudge:
    """LLM-powered conversation decision making"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def determine_conversation_action(
        self, 
        twin_name: str,
        twin_personality: Dict[str, Any],
        user_message: str, 
        user_context: str, 
        conversation_context: str
    ) -> Dict[str, Any]:
        """Determine what action to take in conversation"""
        try:
            judge_prompt = f"""
            You are an AI judge helping {twin_name} decide how to respond naturally in conversation.
            
            Twin personality: {twin_personality.get('personality_traits', [])}
            User message: "{user_message}"
            User context: {user_context}
            Recent conversation: {conversation_context}
            
            Determine the best response approach. Choose ONE:
            
            1. "regular_chat" - Continue normal conversation
            2. "share_story" - Natural moment to share a personal story
            3. "continue_story" - User wants to hear more of current story
            
            Consider:
            - Is the user asking about experiences, events, or topics that could trigger a story?
            - Does the conversation flow naturally toward storytelling?
            - Would a personal anecdote enhance the conversation?
            - Is the user showing interest in hearing more?
            
            Respond with JSON:
            {{
                "type": "regular_chat|share_story|continue_story",
                "confidence": 0.0-1.0,
                "reasoning": "brief explanation",
                "transition": "natural transition phrase if sharing story"
            }}
            """
            
            result = await self.llm_client.simple_prompt(
                judge_prompt, 
                temperature=0.3, 
                json_response=True
            )
            
            # Validate and provide defaults
            if not isinstance(result, dict):
                return self._default_action()
            
            action_type = result.get('type', 'regular_chat')
            if action_type not in ['regular_chat', 'share_story', 'continue_story']:
                action_type = 'regular_chat'
            
            return {
                'type': action_type,
                'confidence': result.get('confidence', 0.5),
                'reasoning': result.get('reasoning', 'Default action'),
                'transition': result.get('transition', '')
            }
            
        except Exception as e:
            logger.error(f"Error in conversation judge: {e}")
            return self._default_action()
    
    def _default_action(self) -> Dict[str, Any]:
        """Default action when LLM judge fails"""
        return {
            'type': 'regular_chat',
            'confidence': 0.5,
            'reasoning': 'Fallback to regular conversation',
            'transition': ''
        }