import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration - PostgreSQL unified approach"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Database Configuration - Two ways to connect to PostgreSQL:
    # 1. Direct PostgreSQL URL (local development or custom)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # 2. Supabase PostgreSQL (production) - connects directly to PostgreSQL, not REST API
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_DB_PASSWORD: str = os.getenv("SUPABASE_DB_PASSWORD", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Story settings
    STORY_HISTORY_DAYS: int = int(os.getenv("STORY_HISTORY_DAYS", "7"))
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required = [cls.TELEGRAM_BOT_TOKEN, cls.OPENAI_API_KEY]
        
        # Check database configuration - at least one method must be available
        has_direct_db = bool(cls.DATABASE_URL)
        has_supabase = bool(cls.SUPABASE_URL and cls.SUPABASE_DB_PASSWORD)
        
        if not (has_direct_db or has_supabase):
            return False
        
        return all(required)
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return cls.ENVIRONMENT.lower() == "development"
    
    @classmethod
    def get_connection_info(cls) -> dict:
        """Get database connection info for logging"""
        if cls.DATABASE_URL:
            return {
                "type": "Direct PostgreSQL",
                "source": "DATABASE_URL",
                "environment": cls.ENVIRONMENT
            }
        elif cls.SUPABASE_URL and cls.SUPABASE_DB_PASSWORD:
            return {
                "type": "Supabase PostgreSQL", 
                "source": "SUPABASE_URL + SUPABASE_DB_PASSWORD",
                "environment": cls.ENVIRONMENT,
                "project": cls.SUPABASE_URL.split('//')[1].split('.')[0]
            }
        else:
            return {"type": "None", "error": "No valid database configuration"}