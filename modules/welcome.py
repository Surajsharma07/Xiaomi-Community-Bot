from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes, MessageHandler, filters
from config import ADMIN_IDS, WELCOME_MESSAGE

async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not update.message or not update.message.new_chat_members:
        return

    for member in update.message.new_chat_members:
        # Restrict the user's permissions until verification is complete
        try:
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=member.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
        except Exception as e:
            print(f"Failed to restrict permissions for {member.id}: {e}")
            continue

        # Create a button that routes the user to the bot's PM for verification
        try:
            chat_id = update.effective_chat.id
            user_name = member.first_name

            # Send the welcome message with the verification button
            welcome_message = await update.message.reply_text(
                f"Hi {user_name}! Welcome to the group. Please verify yourself by clicking the button below."
            )

            # Update the button URL to include the bot's welcome message ID
            verification_button = InlineKeyboardButton(
                text="Verify Now",
                url=f"https://t.me/{context.bot.username}?start=verify_{member.id}_{chat_id}_{welcome_message.message_id}_clickedby_{update.effective_user.id}"
            )
            await welcome_message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([[verification_button]])
            )
        except Exception as e:
            print(f"Failed to send welcome message to {member.id}: {e}")
            continue

        # Notify admins about the new user
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"New user {member.first_name} (ID: {member.id}) has joined the group. Verification initiated."
                )
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")

# Handler for new chat members
welcome_handler = MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, send_welcome_message)

# Export handler for integration in the main bot
__all__ = ["welcome_handler"]