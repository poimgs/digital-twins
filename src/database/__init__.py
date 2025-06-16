from .postgres_client import PostgreSQLClient
from .repositories import (
    DigitalTwinRepository, 
    StoryRepository, 
    UserMemoryRepository, 
    ConversationRepository
)

# Export all database components
__all__ = [
    'PostgreSQLClient',
    'DigitalTwinRepository',
    'StoryRepository', 
    'UserMemoryRepository',
    'ConversationRepository'
]

# Convenience function to get database client
def get_database_client() -> PostgreSQLClient:
    """Get the singleton database client"""
    return PostgreSQLClient()