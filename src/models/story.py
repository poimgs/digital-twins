from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class Story:
    """Story model"""
    story_id: str
    twin_id: str
    title: str
    full_content: str
    themes: List[str]
    emotional_tone: str
    adaptability_level: float = 0.5
    key_facts: List[str] = None
    conversation_triggers: List[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.key_facts is None:
            self.key_facts = []
        if self.conversation_triggers is None:
            self.conversation_triggers = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Story':
        """Create Story from dictionary"""
        return cls(
            story_id=data['story_id'],
            twin_id=data['twin_id'],
            title=data['title'],
            full_content=data['full_content'],
            themes=data.get('themes', []),
            emotional_tone=data.get('emotional_tone', 'neutral'),
            adaptability_level=data.get('adaptability_level', 0.5),
            key_facts=data.get('key_facts', []),
            conversation_triggers=data.get('conversation_triggers', []),
            created_at=data.get('created_at')
        )

@dataclass
class StorySegment:
    """Story segment model"""
    id: str
    story_id: str
    segment_order: int
    segment_type: str
    content: str
    transition_hook: Optional[str] = None
    interaction_points: List[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.interaction_points is None:
            self.interaction_points = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorySegment':
        """Create StorySegment from dictionary"""
        return cls(
            id=data['id'],
            story_id=data['story_id'],
            segment_order=data['segment_order'],
            segment_type=data['segment_type'],
            content=data['content'],
            transition_hook=data.get('transition_hook'),
            interaction_points=data.get('interaction_points', []),
            created_at=data.get('created_at')
        )