from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
import time

# List of admin user IDs (imported from config.py)
from config import ADMIN_IDS

# A dictionary to keep track of recent messages for spam detection
recent_messages = {}

# Anti-spam configuration
SPAM_THRESHOLD = 5  # Number of messages allowed within the time window
TIME_WINDOW = 10  # Time window in seconds

async def detect_spam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Detect and handle spam messages in the group."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    current_time = time.time()  # Use the time module to get the current timestamp

    # Initialize user message history if not present
    if chat_id not in recent_messages:
        recent_messages[chat_id] = {}
    if user_id not in recent_messages[chat_id]:
        recent_messages[chat_id][user_id] = []

    # Add the current message timestamp to the user's history
    recent_messages[chat_id][user_id].append(current_time)

    # Remove timestamps outside the time window
    recent_messages[chat_id][user_id] = [
        timestamp for timestamp in recent_messages[chat_id][user_id]
        if current_time - timestamp <= TIME_WINDOW
    ]

    # Check if the user exceeds the spam threshold
    if len(recent_messages[chat_id][user_id]) > SPAM_THRESHOLD:
        try:
            # Mute the user for spamming
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=None,  # No permissions
                until_date=int(current_time) + 60  # Mute for 60 seconds
            )
            await update.message.reply_text(
                f"User {update.effective_user.first_name} has been muted for spamming."
            )
        except Exception as e:
            await update.message.reply_text(f"Failed to mute user: {e}")

# Handler for detecting spam messages
spam_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, detect_spam)

# Export handler for integration in the main bot
__all__ = ["spam_handler"]
