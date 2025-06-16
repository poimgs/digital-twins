import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.bot.bot_manager import BotManager
from src.database import PostgreSQLClient
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def main():
    """Main function to run multiple digital twin bots"""
    try:
        # Validate configuration
        if not Config.validate():
            logger.error("Invalid configuration. Please check your environment variables.")
            logger.error("Required: OPENAI_API_KEY")
            logger.error("Database: Either DATABASE_URL or (SUPABASE_URL + SUPABASE_DB_PASSWORD)")
            logger.error("Bots: BOT_CONFIGS JSON or individual BOT_TOKEN_* variables")
            sys.exit(1)
        
        # Test database connection
        db_client = PostgreSQLClient()
        if not db_client.test_connection():
            logger.error("Failed to connect to database")
            sys.exit(1)
        
        await db_client.initialize()
        
        env_name = "Development (Local PostgreSQL)" if Config.is_development() else "Production (Supabase)"
        logger.info(f"Database connection successful - {env_name}")
        
        # Show bot configuration
        bot_configs = Config.get_all_bot_configs()
        logger.info(f"Found {len(bot_configs)} bot configuration(s):")
        for twin_id, config in bot_configs.items():
            logger.info(f"  🤖 {twin_id} -> @{config['username']}")
        
        # Create and start bot manager
        bot_manager = BotManager()
        
        logger.info(f"🚀 Starting Digital Twin Bots in {Config.ENVIRONMENT} mode...")
        await bot_manager.start_all_bots()
        
    except KeyboardInterrupt:
        logger.info("Bots stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Clean up database connection
        if 'db_client' in locals():
            await db_client.close()

if __name__ == '__main__':
    asyncio.run(main())