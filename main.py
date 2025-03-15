from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from modules import welcome, logging, admin, antispam
from start import start
import asyncio
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

try:
    ADMIN_IDS = os.getenv("ADMIN_IDS")
    if not ADMIN_IDS:
        ADMIN_IDS = []
    else:
        ADMIN_IDS = list(map(int, ADMIN_IDS.split(',')))
except Exception as e:
    print(f"ERROR: Failed to load or parse ADMIN_IDS: {e}", file=sys.stderr)
    sys.exit(1)

# Fetch the bot token from environment variables
try:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("Bot token not found in environment variables.")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

# Initialize the bot application
try:
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    print("DEBUG: Bot application initialized successfully.")
except Exception as e:
    print(f"ERROR: Failed to initialize the bot application: {e}", file=sys.stderr)
    sys.exit(1)

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
    print(f"ERROR: Failed to register handlers: {e}", file=sys.stderr)
    sys.exit(1)

# Log initialization
try:
    logging.log_message("Bot is starting...", context=None)
    print("DEBUG: Bot initialization log sent.")
except Exception as e:
    print(f"ERROR: Failed to log bot initialization: {e}", file=sys.stderr)

# Start the bot
if __name__ == "__main__":
    try:
        application.run_polling()
        logging.log_message("Bot is running.", context=None)
        print("DEBUG: Bot is running.")
    except Exception as e:
        print(f"ERROR: Failed to start the bot: {e}", file=sys.stderr)
        sys.exit(1)
