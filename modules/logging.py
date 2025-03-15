from telegram import Update
from telegram.ext import ContextTypes

# List of admin user IDs (imported from config.py)
from config import ADMIN_IDS

# Channel ID for logging (imported from config.py)
from config import LOG_CHANNEL_ID

async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Logs messages to a specific channel.

    Args:
        update (Update): The update object containing the message.
        context (ContextTypes.DEFAULT_TYPE): The context object for the bot.
    """
    if update.effective_user.id not in ADMIN_IDS:
        # Only admins can trigger logging manually
        await update.message.reply_text("You don't have permission to use this command.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to the message you want to log.")
        return

    message_to_log = update.message.reply_to_message
    log_text = (
        f"Log Entry:\n"
        f"From: {message_to_log.from_user.first_name} (ID: {message_to_log.from_user.id})\n"
        f"Chat: {message_to_log.chat.title} (ID: {message_to_log.chat.id})\n"
        f"Message: {message_to_log.text or 'Non-text message'}"
    )

    try:
        # Send the log to the specified channel
        await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=log_text)
        await update.message.reply_text("Message has been logged successfully.")
    except Exception as e:
        await update.message.reply_text(f"Failed to log message: {e}")

# Export the log_message function for integration in the main bot
__all__ = ["log_message"]
