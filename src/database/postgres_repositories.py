import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ..models import DigitalTwin, Story, StorySegment, UserMemory, ConversationSession
from .postgres_client import PostgreSQLClient
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class PostgreSQLBaseRepository:
    """Base repository for PostgreSQL operations"""
    
    def __init__(self):
        self.db = PostgreSQLClient()

class PostgreSQLDigitalTwinRepository(PostgreSQLBaseRepository):
    """PostgreSQL repository for digital twin operations"""
    
    async def get_all_twins(self) -> List[DigitalTwin]:
        """Get all available digital twins"""
        try:
            query = "SELECT * FROM digital_twins ORDER BY name"
            results = await self.db.execute_query(query)
            return [DigitalTwin.from_dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching twins: {e}")
            return []
    
    async def get_twin_by_id(self, twin_id: str) -> Optional[DigitalTwin]:
        """Get twin by ID"""
        try:
            query = "SELECT * FROM digital_twins WHERE twin_id = $1"
            result = await self.db.fetch_one(query, twin_id)
            if result:
                return DigitalTwin.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Error fetching twin {twin_id}: {e}")
            return None

class PostgreSQLStoryRepository(PostgreSQLBaseRepository):
    """PostgreSQL repository for story operations"""
    
    async def get_stories_by_twin(self, twin_id: str) -> List[Story]:
        """Get all stories for a twin"""
        try:
            query = "SELECT * FROM stories WHERE twin_id = $1 ORDER BY created_at"
            results = await self.db.execute_query(query, twin_id)
            return [Story.from_dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching stories for twin {twin_id}: {e}")
            return []
    
    async def get_story_by_id(self, story_id: str) -> Optional[Story]:
        """Get story by ID"""
        try:
            query = "SELECT * FROM stories WHERE story_id = $1"
            result = await self.db.fetch_one(query, story_id)
            if result:
                return Story.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Error fetching story {story_id}: {e}")
            return None
    
    async def get_story_segments(self, story_id: str) -> List[StorySegment]:
        """Get segments for a story"""
        try:
            query = "SELECT * FROM story_segments WHERE story_id = $1 ORDER BY segment_order"
            results = await self.db.execute_query(query, story_id)
            return [StorySegment.from_dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching segments for story {story_id}: {e}")
            return []
    
    async def get_story_segment(self, story_id: str, segment_order: int) -> Optional[StorySegment]:
        """Get specific story segment"""
        try:
            query = "SELECT * FROM story_segments WHERE story_id = $1 AND segment_order = $2"
            result = await self.db.fetch_one(query, story_id, segment_order)
            if result:
                return StorySegment.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Error fetching segment {segment_order} for story {story_id}: {e}")
            return None
    
    async def get_user_story_history(self, chat_id: int, days: int = None) -> List[str]:
        """Get list of stories recently told to user"""
        try:
            days = days or Config.STORY_HISTORY_DAYS
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT story_id FROM user_story_progress 
                WHERE chat_id = $1 AND created_at >= $2
            """
            results = await self.db.execute_query(query, chat_id, cutoff_date)
            
            return [row['story_id'] for row in results]
        except Exception as e:
            logger.error(f"Error getting story history for chat {chat_id}: {e}")
            return []
    
    async def create_story_progress(self, chat_id: int, story_id: str) -> bool:
        """Create story progress record"""
        try:
            query = """
                INSERT INTO user_story_progress (chat_id, story_id, current_segment, segments_completed, completion_status)
                VALUES ($1, $2, 1, ARRAY[1], 'in_progress')
                ON CONFLICT (chat_id, story_id) DO UPDATE SET
                    current_segment = 1,
                    segments_completed = ARRAY[1],
                    completion_status = 'in_progress',
                    last_interaction = NOW()
            """
            await self.db.execute_command(query, chat_id, story_id)
            return True
        except Exception as e:
            logger.error(f"Error creating story progress: {e}")
            return False
    
    async def update_story_progress(self, chat_id: int, story_id: str, segment: int) -> bool:
        """Update story progress"""
        try:
            # Get current progress
            select_query = """
                SELECT segments_completed FROM user_story_progress 
                WHERE chat_id = $1 AND story_id = $2
            """
            result = await self.db.fetch_one(select_query, chat_id, story_id)
            
            if result:
                completed = result.get('segments_completed', [])
                if segment not in completed:
                    completed.append(segment)
                
                update_query = """
                    UPDATE user_story_progress 
                    SET current_segment = $1, segments_completed = $2, last_interaction = NOW()
                    WHERE chat_id = $3 AND story_id = $4
                """
                await self.db.execute_command(update_query, segment, completed, chat_id, story_id)
            
            return True
        except Exception as e:
            logger.error(f"Error updating story progress: {e}")
            return False
    
    async def complete_story(self, chat_id: int, story_id: str) -> bool:
        """Mark story as completed"""
        try:
            query = """
                UPDATE user_story_progress 
                SET completion_status = 'completed' 
                WHERE chat_id = $1 AND story_id = $2
            """
            await self.db.execute_command(query, chat_id, story_id)
            return True
        except Exception as e:
            logger.error(f"Error completing story: {e}")
            return False

class PostgreSQLUserMemoryRepository(PostgreSQLBaseRepository):
    """PostgreSQL repository for user memory operations"""
    
    async def get_or_create_user_memory(self, chat_id: int) -> UserMemory:
        """Get or create user memory"""
        try:
            query = "SELECT * FROM user_memory WHERE chat_id = $1"
            result = await self.db.fetch_one(query, chat_id)
            
            if result:
                return UserMemory.from_dict(result)
            else:
                # Create new user memory
                insert_query = """
                    INSERT INTO user_memory (chat_id, profile, conversation_history, shared_topics, emotional_reactions)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                """
                new_memory = await self.db.fetch_one(
                    insert_query, 
                    chat_id, 
                    json.dumps({}), 
                    json.dumps([]), 
                    [], 
                    json.dumps({})
                )
                return UserMemory.from_dict(new_memory)
                
        except Exception as e:
            logger.error(f"Error with user memory for chat {chat_id}: {e}")
            return UserMemory(chat_id=chat_id)
    
    async def update_user_profile(self, chat_id: int, extracted_info: Dict[str, Any]) -> bool:
        """Update user profile with extracted information"""
        try:
            current_memory = await self.get_or_create_user_memory(chat_id)
            profile = current_memory.profile.copy()
            
            # Merge extracted info intelligently
            for key, value in extracted_info.items():
                if key in ['interests', 'life_events'] and isinstance(value, list):
                    # For lists, merge and deduplicate
                    existing = set(profile.get(key, []))
                    new_items = set(value)
                    profile[key] = list(existing.union(new_items))
                elif key == 'name' and not profile.get('name'):
                    # Only update name if not already set
                    profile[key] = value
                elif key not in ['name']:
                    # Update other fields normally
                    profile[key] = value
            
            query = """
                UPDATE user_memory 
                SET profile = $1, last_interaction = NOW()
                WHERE chat_id = $2
            """
            await self.db.execute_command(query, json.dumps(profile), chat_id)
            
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    async def add_conversation_entry(self, chat_id: int, user_message: str, extracted_info: Dict[str, Any] = None) -> bool:
        """Add conversation entry"""
        try:
            current_memory = await self.get_or_create_user_memory(chat_id)
            conversation_history = current_memory.conversation_history.copy()
            
            # Add new entry
            conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'extracted_info': extracted_info or {}
            })
            
            # Keep only recent history
            max_history = Config.MAX_CONVERSATION_HISTORY
            if len(conversation_history) > max_history:
                conversation_history = conversation_history[-max_history:]
            
            query = """
                UPDATE user_memory 
                SET conversation_history = $1
                WHERE chat_id = $2
            """
            await self.db.execute_command(query, json.dumps(conversation_history), chat_id)
            
            return True
        except Exception as e:
            logger.error(f"Error adding conversation entry: {e}")
            return False
    
    async def add_twin_response(self, chat_id: int, twin_response: str) -> bool:
        """Add twin response to last conversation entry"""
        try:
            current_memory = await self.get_or_create_user_memory(chat_id)
            conversation_history = current_memory.conversation_history.copy()
            
            if conversation_history:
                conversation_history[-1]['twin_response'] = twin_response
                conversation_history[-1]['response_timestamp'] = datetime.now().isoformat()
                
                query = """
                    UPDATE user_memory 
                    SET conversation_history = $1
                    WHERE chat_id = $2
                """
                await self.db.execute_command(query, json.dumps(conversation_history), chat_id)
            
            return True
        except Exception as e:
            logger.error(f"Error adding twin response: {e}")
            return False

class PostgreSQLConversationRepository(PostgreSQLBaseRepository):
    """PostgreSQL repository for conversation session operations"""
    
    async def get_or_create_session(self, chat_id: int, twin_id: str = None) -> ConversationSession:
        """Get or create conversation session"""
        try:
            query = """
                SELECT * FROM conversation_sessions 
                WHERE chat_id = $1 AND session_state = 'active'
                ORDER BY started_at DESC LIMIT 1
            """
            result = await self.db.fetch_one(query, chat_id)
            
            if result:
                return ConversationSession.from_dict(result)
            elif twin_id:
                # Create new session
                insert_query = """
                    INSERT INTO conversation_sessions (chat_id, twin_id, session_state, started_at, last_activity)
                    VALUES ($1, $2, 'active', NOW(), NOW())
                    RETURNING *
                """
                new_session = await self.db.fetch_one(insert_query, chat_id, twin_id)
                return ConversationSession.from_dict(new_session)
            else:
                # Return empty session
                return ConversationSession(id=None, chat_id=chat_id, twin_id='')
                
        except Exception as e:
            logger.error(f"Error with conversation session: {e}")
            return ConversationSession(id=None, chat_id=chat_id, twin_id='')
    
    async def set_active_twin(self, chat_id: int, twin_id: str) -> bool:
        """Set active twin for user"""
        try:
            # Close existing sessions
            update_query = """
                UPDATE conversation_sessions 
                SET session_state = 'inactive' 
                WHERE chat_id = $1 AND session_state = 'active'
            """
            await self.db.execute_command(update_query, chat_id)
            
            # Create new session
            insert_query = """
                INSERT INTO conversation_sessions (chat_id, twin_id, session_state, started_at, last_activity)
                VALUES ($1, $2, 'active', NOW(), NOW())
            """
            await self.db.execute_command(insert_query, chat_id, twin_id)
            return True
            
        except Exception as e:
            logger.error(f"Error setting active twin: {e}")
            return False
    
    async def update_session_story(self, chat_id: int, story_id: str) -> bool:
        """Update current story in session"""
        try:
            query = """
                UPDATE conversation_sessions 
                SET current_story_id = $1, last_activity = NOW()
                WHERE chat_id = $2 AND session_state = 'active'
            """
            await self.db.execute_command(query, story_id, chat_id)
            return True
        except Exception as e:
            logger.error(f"Error updating session story: {e}")
            return False
    
    async def clear_session_story(self, chat_id: int) -> bool:
        """Clear current story from session"""
        try:
            query = """
                UPDATE conversation_sessions 
                SET current_story_id = NULL, last_activity = NOW()
                WHERE chat_id = $2 AND session_state = 'active'
            """
            await self.db.execute_command(query, chat_id)
            return True
        except Exception as e:
            logger.error(f"Error clearing session story: {e}")
            return False