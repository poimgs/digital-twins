import json
import asyncio
from typing import Dict, List, Optional, Any
import openai
from .config import Config
from .logger import setup_logger

logger = setup_logger(__name__)

class LLMClient:
    """Wrapper for OpenAI API calls"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_response: bool = False
    ) -> str:
        """Make chat completion request"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            response = await openai.ChatCompletion.acreate(**kwargs)
            content = response.choices[0].message.content
            
            if json_response:
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    return {}
            
            return content
            
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            if json_response:
                return {}
            return "I'm having trouble thinking right now. Could you try again?"
    
    async def simple_prompt(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_response: bool = False
    ) -> str:
        """Simple prompt completion"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(
            messages, temperature, max_tokens, json_response
        )
    
    async def extract_user_info(self, user_message: str) -> Dict[str, Any]:
        """Extract personal information from user message"""
        prompt = f"""
        Extract personal information from this user message: "{user_message}"
        
        Return a JSON object with any of these fields that are mentioned:
        {{
            "name": "user's name if mentioned",
            "age": "age if mentioned", 
            "location": "city/country if mentioned",
            "occupation": "job/profession if mentioned",
            "interests": ["list", "of", "interests", "mentioned"],
            "life_events": ["recent events or experiences shared"],
            "current_situation": "what they're currently doing/feeling"
        }}
        
        Only include fields that are explicitly mentioned. Return empty object if nothing personal is shared.
        """
        
        return await self.simple_prompt(prompt, temperature=0.1, json_response=True)