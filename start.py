from telegram.ext import CommandHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command and verification process.
    If the user is accessing the bot via the verification link, check permissions and act accordingly.
    """
    if context.args and context.args[0].startswith("verify_"):
        try:
            user_id = int(context.args[0].split("_")[1])
            group_id = int(context.args[0].split("_")[2])
            message_id = int(context.args[0].split("_")[3])
            print(f"DEBUG: Verification link accessed with user_id={user_id}, group_id={group_id}, message_id={message_id}, accessed_by={update.effective_user.id}.")
        except (IndexError, ValueError):
            print("DEBUG: Invalid verification data received.")
            await update.message.reply_text("Invalid verification data.")
            return

        # Check the user's chat member status
        try:
            chat_member = await context.bot.get_chat_member(chat_id=group_id, user_id=update.effective_user.id)
            
            # If the user is an admin or owner
            if chat_member.status in ["administrator", "creator"]:
                await update.message.reply_text("You are an admin/owner, why would you want to verify?")
                print(f"DEBUG: User {user_id} is an admin/owner in group {group_id}.")
                return
            
            # If the user is restricted
            elif not chat_member.can_send_messages:
                # Create a button to open the web app for verification, including group_id and message_id in the URL
                web_app_button = InlineKeyboardButton(
                    text="Verify Your Details",
                    web_app={"url": f"https://app.vynix.in/verify.php?user_id={update.effective_user.id}&group_id={group_id}&message_id={message_id}"}
                )
                keyboard = InlineKeyboardMarkup([[web_app_button]])

                try:
                    await update.message.reply_text(
                        "Please verify your details by clicking the button below:",
                        reply_markup=keyboard
                    )
                    print(f"DEBUG: Verification message sent to user_id={user_id}.")
                except Exception as e:
                    print(f"DEBUG: Failed to send verification message: {e}")
                return
            
            # If the user already has access
            else:
                await update.message.reply_text("You already have access to the chat.")
                print(f"DEBUG: User {user_id} already unrestricted in group {group_id}.")
                return

        except Exception as e:
            print(f"DEBUG: Failed to check user permissions: {e}")
            await update.message.reply_text("An error occurred while checking your permissions.")
            return
    else:
        try:
            await update.message.reply_text("Welcome! Use the bot commands to interact.")
            print("DEBUG: Welcome message sent.")
        except Exception as e:
            print(f"DEBUG: Failed to send welcome message: {e}")