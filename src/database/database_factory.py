from typing import Union
from ..utils.config import Config
from .supabase_client import SupabaseClient
from .postgres_client import PostgreSQLClient

class DatabaseFactory:
    """Factory to create appropriate database client based on environment"""
    
    @staticmethod
    def create_client() -> Union[SupabaseClient, PostgreSQLClient]:
        """Create database client based on configuration"""
        if Config.ENVIRONMENT == 'development' and Config.DATABASE_URL:
            return PostgreSQLClient()
        else:
            return SupabaseClient()