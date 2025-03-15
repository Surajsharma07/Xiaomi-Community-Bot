from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from modules import welcome, logging, admin, antispam
from start import start
from config import ADMIN_IDS
import asyncio
import os

# Fetch the bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Bot token not found in environment variables.")

# Initialize the bot application
try:
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    print("DEBUG: Bot application initialized successfully.")
except Exception as e:
    print(f"DEBUG: Failed to initialize the bot application: {e}")
    raise RuntimeError(f"Failed to initialize the bot application: {e}")

try:
    # Register handlers from all imported modules
    application.add_handler(welcome.welcome_handler)
    application.add_handler(admin.ban_handler)
    application.add_handler(admin.unban_handler)
    application.add_handler(admin.kick_handler)
    application.add_handler(admin.mute_handler)
    application.add_handler(admin.unmute_handler)
    application.add_handler(admin.tmute_handler)
    application.add_handler(admin.dban_handler)
    application.add_handler(admin.gban_handler)
    application.add_handler(admin.pin_handler)
    application.add_handler(antispam.spam_handler)
    application.add_handler(CommandHandler("start", start))
    print("DEBUG: Handlers registered successfully.")
except Exception as e:
    print(f"DEBUG: Failed to register handlers: {e}")
    raise RuntimeError(f"Failed to register handlers: {e}")

# Log initialization
try:
    logging.log_message("Bot is starting...", context=None)
    print("DEBUG: Bot initialization log sent.")
except Exception as e:
    print(f"DEBUG: Failed to log bot initialization: {e}")

# Start the bot
if __name__ == "__main__":
    try:
        application.run_polling()
        logging.log_message("Bot is running.", context=None)
        print("DEBUG: Bot is running.")
    except Exception as e:
        print(f"DEBUG: Failed to start the bot: {e}")
