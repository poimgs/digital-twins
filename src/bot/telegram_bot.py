from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

from .conversation_manager import ConversationManager
from ..database.repositories import DigitalTwinRepository, ConversationRepository
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class TelegramBot:
    """Main Telegram bot class"""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.twin_repo = DigitalTwinRepository()
        self.conversation_repo = ConversationRepository()
    
    def create_application(self) -> Application:
        """Create and configure Telegram application"""
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("twins", self.twins_command))
        application.add_handler(CommandHandler("story", self.story_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(
            CallbackQueryHandler(self.twin_selection_callback, pattern="^select_twin:")
        )
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        return application
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        
        # Get available twins
        twins = await self.twin_repo.get_all_twins()
        
        if not twins:
            await update.message.reply_text("Sorry, no digital twins are available right now.")
            return
        
        # Create inline keyboard with available twins
        keyboard = []
        for twin in twins:
            keyboard.append([InlineKeyboardButton(
                twin.name, 
                callback_data=f"select_twin:{twin.twin_id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            "🤖 Welcome to the Digital Twins Story Bot!\n\n"
            "I connect you with digital twins who love sharing their personal stories. "
            "Each twin has their own personality, experiences, and way of talking.\n\n"
            "Choose a twin to start chatting:"
        )
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def twin_selection_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle twin selection from inline keyboard"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.effective_chat.id
        twin_id = query.data.split(':')[1]
        
        # Set active twin for user
        await self.conversation_repo.set_active_twin(chat_id, twin_id)
        
        # Get twin info
        twin = await self.twin_repo.get_twin_by_id(twin_id)
        
        if twin:
            greeting_message = await self.conversation_manager.generate_twin_greeting(twin, chat_id)
            
            await query.edit_message_text(
                f"🎭 Now chatting with {twin.name}\n\n{greeting_message}\n\n"
                f"You can:\n"
                f"• Just chat naturally\n"
                f"• Ask questions about my experiences\n"
                f"• Use /twins to switch twins\n"
                f"• Use /help for more commands"
            )
        else:
            await query.edit_message_text("Sorry, I couldn't find that digital twin.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        chat_id = update.effective_chat.id
        user_message = update.message.text
        
        response = await self.conversation_manager.handle_user_message(chat_id, user_message)
        await update.message.reply_text(response)
    
    async def twins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /twins command to switch twins"""
        await self.start_command(update, context)
    
    async def story_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /story command - deprecated but kept for backward compatibility"""
        await update.message.reply_text(
            "Just chat naturally with me! I'll share stories when they feel relevant to our conversation. 😊"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🤖 Digital Twins Bot Commands:\n\n"
            "/start - Choose a digital twin to chat with\n"
            "/twins - Switch to a different twin\n"
            "/help - Show this help message\n\n"
            "💬 Just chat naturally! The digital twins will:\n"
            "• Remember what you share about yourself\n"
            "• Share relevant personal stories during conversation\n"
            "• Adapt their personality to match the flow\n"
            "• Build a relationship with you over time\n\n"
            "No need for special commands - just be yourself! 😊"
        )
        await update.message.reply_text(help_text)