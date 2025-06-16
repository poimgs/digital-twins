#!/usr/bin/env python3
"""
Helper script to set up multiple Telegram bots for digital twins
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database import DigitalTwinRepository
import asyncio

async def get_digital_twins():
    """Get all digital twins from database"""
    try:
        repo = DigitalTwinRepository()
        twins = await repo.get_all_twins()
        return twins
    except Exception as e:
        print(f"Error fetching twins: {e}")
        return []

def generate_env_config(twins):
    """Generate environment variable configuration for bots"""
    
    print("🤖 Multi-Bot Setup Guide")
    print("=" * 50)
    print()
    print("Step 1: Create Telegram Bots")
    print("----------------------------")
    print("For each digital twin, create a separate Telegram bot:")
    print()
    
    for i, twin in enumerate(twins, 1):
        bot_username = f"{twin.twin_id}_bot"
        print(f"{i}. Message @BotFather on Telegram")
        print(f"   Send: /newbot")
        print(f"   Bot name: {twin.name}")
        print(f"   Bot username: {bot_username}")
        print(f"   Save the token for: BOT_TOKEN_{twin.twin_id.upper()}")
        print()
    
    print("Step 2: Environment Configuration")
    print("--------------------------------")
    print("Add these environment variables to your .env file:")
    print()
    
    for twin in twins:
        env_var_name = f"BOT_TOKEN_{twin.twin_id.upper()}"
        username_var = f"BOT_USERNAME_{twin.twin_id.upper()}"
        bot_username = f"{twin.twin_id}_bot"
        
        print(f"# {twin.name}")
        print(f"{env_var_name}=your_{twin.twin_id}_bot_token_here")
        print(f"{username_var}={bot_username}")
        print()
    
    print("Step 3: JSON Configuration (Alternative)")
    print("--------------------------------------")
    print("Or use single JSON configuration:")
    print()
    
    json_config = "{"
    for i, twin in enumerate(twins):
        if i > 0:
            json_config += ","
        json_config += f'"{twin.twin_id}":{{"token":"your_{twin.twin_id}_token","username":"{twin.twin_id}_bot","twin_id":"{twin.twin_id}"}}'
    json_config += "}"
    
    print(f"BOT_CONFIGS={json_config}")
    print()
    
    print("Step 4: Start the Bots")
    print("----------------------")
    print("python bot.py")
    print()
    
    print("🎉 Each digital twin will have their own dedicated bot!")
    print("Users can chat with each twin independently.")

if __name__ == "__main__":
    async def main():
        twins = await get_digital_twins()
        
        if twins:
            generate_env_config(twins)
        else:
            print("❌ No digital twins found in database.")
            print("Please run the database setup first:")
            print("1. make dev-up")
            print("2. python scripts/test-database.py")
    
    asyncio.run(main())