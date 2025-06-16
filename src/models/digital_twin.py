from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class DigitalTwin:
    """Digital twin model"""
    twin_id: str
    name: str
    personality_traits: List[str]
    conversational_style: Dict[str, Any]
    background: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DigitalTwin':
        """Create DigitalTwin from dictionary"""
        return cls(
            twin_id=data['twin_id'],
            name=data['name'],
            personality_traits=data.get('personality_traits', []),
            conversational_style=data.get('conversational_style', {}),
            background=data.get('background', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def get_style_instructions(self) -> str:
        """Generate style instructions for LLM prompts"""
        style = self.conversational_style
        instructions = []
        
        # Formality level
        formality = style.get('formality_level', 0.5)
        if formality < 0.3:
            instructions.append("Speak very casually, use contractions and informal language")
        elif formality > 0.7:
            instructions.append("Maintain a more formal, professional tone")
        
        # Humor frequency
        humor = style.get('humor_frequency', 0.5)
        if humor > 0.6:
            instructions.append("Include light humor and witty observations when appropriate")
        
        # Technical depth
        tech_depth = style.get('technical_depth', 0.5)
        if tech_depth > 0.7:
            instructions.append("Don't shy away from technical details and precise terminology")
        
        # Common phrases
        phrases = style.get('common_phrases', [])
        if phrases:
            instructions.append(f"Naturally incorporate these phrases: {phrases}")
        
        # Response length preference
        length_pref = style.get('response_length_preference', 'medium')
        if length_pref == 'short':
            instructions.append("Keep responses concise and to the point")
        elif length_pref == 'long':
            instructions.append("Feel free to elaborate and provide detailed responses")
        
        return "\n".join(instructions)