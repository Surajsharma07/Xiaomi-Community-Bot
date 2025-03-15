from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

async def remove_service_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Removes service notification messages such as user joined, user left, pinned messages, etc.
    """
    try:
        if update.message and update.message.service_message:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
    except Exception as e:
        print(f"Failed to delete service notification message: {e}")

# Handler for service notifications
service_notification_handler = MessageHandler(filters.StatusUpdate.ALL, remove_service_notifications)
