"""
Test multiple bot configuration and setup
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.utils.config import Config
from src.database import PostgreSQLClient, DigitalTwinRepository
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_multi_bot_setup():
    """Test multi-bot configuration"""
    
    print("🤖 Digital Twin Multi-Bot Setup Test")
    print("=" * 50)
    
    # Test configuration
    print("\n📋 Testing Configuration...")
    if not Config.validate():
        print("❌ Configuration validation failed!")
        return False
    
    print("✅ Configuration is valid")
    
    # Test database
    print("\n🗄️  Testing Database...")
    try:
        db_client = PostgreSQLClient()
        await db_client.initialize()
        
        # Check twins in database
        twin_repo = DigitalTwinRepository()
        twins = await twin_repo.get_all_twins()
        
        print(f"✅ Found {len(twins)} digital twins in database:")
        for twin in twins:
            print(f"   🤖 {twin.name} ({twin.twin_id})")
        
        if not twins:
            print("⚠️  No digital twins found. Run database/seed.sql")
            return False
        
        await db_client.close()
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    # Test bot configurations
    print("\n🤖 Testing Bot Configurations...")
    bot_configs = Config.get_all_bot_configs()
    
    if not bot_configs:
        print("❌ No bot configurations found!")
        print("\nSetup instructions:")
        print("1. Create Telegram bots with @BotFather")
        print("2. Add BOT_TOKEN_* environment variables")
        print("3. Or use BOT_CONFIGS JSON")
        return False
    
    print(f"✅ Found {len(bot_configs)} bot configuration(s):")
    
    configured_twins = set(bot_configs.keys())
    available_twins = set(twin.twin_id for twin in twins)
    
    for twin_id, config in bot_configs.items():
        status = "✅" if twin_id in available_twins else "⚠️"
        print(f"   {status} {twin_id} -> @{config['username']}")
        if twin_id not in available_twins:
            print(f"      Warning: No digital twin '{twin_id}' found in database")
    
    # Check for twins without bots
    missing_bots = available_twins - configured_twins
    if missing_bots:
        print(f"\n⚠️  Digital twins without bot configurations:")
        for twin_id in missing_bots:
            print(f"   🤖 {twin_id} (needs BOT_TOKEN_{twin_id.upper()})")
    
    print(f"\n📊 Summary:")
    print(f"   Digital Twins in DB: {len(twins)}")
    print(f"   Bot Configurations: {len(bot_configs)}")
    print(f"   Ready to Start: {len(configured_twins & available_twins)}")
    
    if configured_twins & available_twins:
        print(f"\n🚀 Ready to start multi-bot system!")
        print(f"   Run: python bot.py")
        return True
    else:
        print(f"\n❌ No valid bot-twin pairs found!")
        return False

async def show_setup_help():
    """Show setup help for multi-bot system"""
    print(f"\n🔧 Multi-Bot Setup Help")
    print("=" * 30)
    print(f"\n1. Create Telegram Bots:")
    print(f"   - Message @BotFather on Telegram")
    print(f"   - Use /newbot for each digital twin")
    print(f"   - Save each bot token")
    
    print(f"\n2. Environment Variables:")
    print(f"   BOT_TOKEN_ALICE_CHEN=your_alice_bot_token")
    print(f"   BOT_TOKEN_BOB_MARTINEZ=your_bob_bot_token")
    print(f"   BOT_TOKEN_SARAH_KIM=your_sarah_bot_token")
    
    print(f"\n3. Start Development:")
    print(f"   make dev-up")
    
    print(f"\n4. Test Setup:")
    print(f"   python scripts/test-multi-bots.py")

if __name__ == "__main__":
    async def main():
        success = await test_multi_bot_setup()
        
        if not success:
            await show_setup_help()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Multi-bot system is ready!")
        else:
            print("❌ Setup incomplete. Follow the instructions above.")
    
    asyncio.run(main())