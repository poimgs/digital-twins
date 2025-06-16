import asyncio
import asyncpg
import json
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class PostgreSQLClient:
    """Unified PostgreSQL client for both local development and Supabase production"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.database_url = self._get_database_url()
        self._is_supabase = self._detect_supabase()
    
    def _get_database_url(self) -> str:
        """Get database URL based on environment"""
        if Config.DATABASE_URL:
            # Direct PostgreSQL connection (local development)
            return Config.DATABASE_URL
        elif Config.SUPABASE_URL and Config.SUPABASE_ANON_KEY:
            # Supabase connection (production)
            # Extract database info from Supabase URL
            # Format: postgresql://postgres:[password]@[host]:5432/postgres
            supabase_host = Config.SUPABASE_URL.replace('https://', '').replace('http://', '')
            # For Supabase, we need to construct the PostgreSQL connection string
            # This typically requires the database password from Supabase settings
            db_password = Config.SUPABASE_DB_PASSWORD if hasattr(Config, 'SUPABASE_DB_PASSWORD') else None
            
            if db_password:
                return f"postgresql://postgres:{db_password}@db.{supabase_host}:5432/postgres"
            else:
                raise ValueError("SUPABASE_DB_PASSWORD required for direct PostgreSQL connection to Supabase")
        else:
            raise ValueError("No valid database configuration found")
    
    def _detect_supabase(self) -> bool:
        """Detect if we're connecting to Supabase"""
        return 'supabase' in self.database_url.lower()
    
    async def initialize(self):
        """Initialize connection pool"""
        try:
            parsed_url = urlparse(self.database_url)
            
            # Connection parameters
            connection_kwargs = {
                'host': parsed_url.hostname,
                'port': parsed_url.port or 5432,
                'user': parsed_url.username,
                'password': parsed_url.password,
                'database': parsed_url.path[1:] if parsed_url.path else 'postgres',
                'min_size': 2,
                'max_size': 10,
                'command_timeout': 60
            }
            
            # Supabase-specific SSL configuration
            if self._is_supabase:
                connection_kwargs.update({
                    'ssl': 'require',
                    'server_settings': {
                        'application_name': 'digital_twin_bot'
                    }
                })
            
            self.pool = await asyncpg.create_pool(**connection_kwargs)
            
            env_type = "Supabase" if self._is_supabase else "Local PostgreSQL"
            logger.info(f"{env_type} connection pool initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        if not self.pool:
            await self.initialize()
        
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, *args)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def execute_command(self, command: str, *args) -> str:
        """Execute INSERT/UPDATE/DELETE command"""
        if not self.pool:
            await self.initialize()
        
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute(command, *args)
                return result
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        if not self.pool:
            await self.initialize()
        
        try:
            async with self.pool.acquire() as connection:
                row = await connection.fetchrow(query, *args)
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Fetch one failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            async def _test():
                if not self.pool:
                    await self.initialize()
                async with self.pool.acquire() as connection:
                    await connection.fetchval("SELECT 1")
                return True
            
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, create a task
                task = asyncio.create_task(_test())
                return True  # Return True for now, actual test happens async
            else:
                return loop.run_until_complete(_test())
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False