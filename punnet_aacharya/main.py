#!/usr/bin/env python
import logging
import sys
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

from config import BOT_TOKEN
from bot_handlers import (
    AstrologyBot, 
    error_handler,
    ONBOARDING, CONSULTATION
)

# Get logger for main module
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    logger.info("Starting Punnet Aacharya Vedic Astrology Bot")
    logger.info("=" * 50)
    
    if not BOT_TOKEN:
        logger.error("No bot token found! Please set TELEGRAM_BOT_TOKEN environment variable.")
        sys.exit(1)
    
    logger.info("Bot token found, proceeding with initialization")
    
    try:
        # Create the Application
        logger.info("Creating Telegram Application")
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("Telegram Application created successfully")
        
        # Initialize bot
        logger.info("Initializing AstrologyBot")
        bot = AstrologyBot()
        logger.info("AstrologyBot initialized successfully")
        
        # Add conversation handler for onboarding and consultation
        logger.info("Setting up conversation handler for onboarding and consultation")
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', bot.start)],
            states={
                ONBOARDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_onboarding)],
                CONSULTATION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_consultation),
                    CommandHandler('history', bot.show_history),
                    CommandHandler('reset', bot.reset_memory)
                ],
            },
            fallbacks=[CommandHandler('cancel', bot.cancel)],
        )
        
        application.add_handler(conv_handler)
        logger.info("Conversation handler added successfully")
        
        # Add error handler
        logger.info("Setting up error handler")
        application.add_error_handler(error_handler)
        logger.info("Error handler added successfully")
        
        # Start the bot
        logger.info("Starting Punnet Aacharya bot with Puneet Guruji...")
        logger.info("Bot is now running and listening for messages...")
        logger.info("=" * 50)
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 