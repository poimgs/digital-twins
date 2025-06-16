import logging
import sys
from pathlib import Path
from .config import Config

def setup_logger(name: str = __name__) -> logging.Logger:
    """Set up logger with file and console handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "bot.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger