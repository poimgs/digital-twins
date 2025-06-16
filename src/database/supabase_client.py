from typing import Optional
from supabase import create_client, Client
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class SupabaseClient:
    """Singleton Supabase client"""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> 'SupabaseClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            try:
                self._client = create_client(
                    Config.SUPABASE_URL,
                    Config.SUPABASE_ANON_KEY
                )
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance"""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            result = self.client.table('digital_twins').select('count').execute()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False