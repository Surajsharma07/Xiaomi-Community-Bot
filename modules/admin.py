from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import BadRequest
from datetime import timedelta, datetime, timezone
from pymongo import MongoClient
from config import ADMIN_IDS, DATABASE_URI

# Initialize MongoDB client
client = MongoClient(DATABASE_URI)
db = client.communitybot
banned_users_collection = db.banned_users

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Helper function to get the target user from a reply or username."""
    try:
        if update.message.reply_to_message:
            return update.message.reply_to_message.from_user
        elif context.args and context.args[0].startswith("@"):
            username = context.args[0][1:]
            chat_member = await context.bot.get_chat_member(update.effective_chat.id, username)
            return chat_member.user
        else:
            return None
    except BadRequest as e:
        await update.message.reply_text(f"Failed to fetch user: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"An unexpected error occurred while fetching the user: {e}")
    return None

async def delete_command_and_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete the command message and any service messages."""
    try:
        if update.message:
            await update.message.delete()
    except Exception:
        pass

async def handle_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, **kwargs):
    """Generic function to handle user actions like ban, unban, mute, etc."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("You don't have permission to use this command.")
        return

    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("Please reply to the user's message or provide their username.")
        return

    try:
        if action == "ban":
            await context.bot.ban_chat_member(update.effective_chat.id, user.id)
            banned_users_collection.insert_one({"user_id": user.id, "username": user.username})
            await update.message.reply_text(f"User {user.first_name} has been banned.")
        elif action == "unban":
            await context.bot.unban_chat_member(update.effective_chat.id, user.id)
            await update.message.reply_text(f"User {user.first_name} has been unbanned.")
        elif action == "kick":
            await context.bot.ban_chat_member(update.effective_chat.id, user.id)
            await context.bot.unban_chat_member(update.effective_chat.id, user.id)
            await update.message.reply_text(f"User {user.first_name} has been kicked.")
        elif action == "mute":
            permissions = kwargs.get("permissions", ChatPermissions(can_send_messages=False))
            await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=permissions)
            await update.message.reply_text(f"User {user.first_name} has been muted.")
        elif action == "unmute":
            permissions = kwargs.get("permissions", ChatPermissions(can_send_messages=True))
            await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=permissions)
            await update.message.reply_text(f"User {user.first_name} has been unmuted.")
        elif action == "tmute":
            duration = kwargs.get("duration")
            until_date = datetime.now(timezone.utc) + timedelta(seconds=duration)
            await context.bot.restrict_chat_member(
                update.effective_chat.id, user.id, permissions=ChatPermissions(can_send_messages=False), until_date=until_date
            )
            await update.message.reply_text(f"User {user.first_name} has been muted for {duration} seconds.")
        elif action == "dban":
            async for message in context.bot.get_chat_history(update.effective_chat.id):
                if message.from_user.id == user.id:
                    await message.delete()
            await context.bot.ban_chat_member(update.effective_chat.id, user.id)
            banned_users_collection.insert_one({"user_id": user.id, "username": user.username})
            await update.message.reply_text(f"User {user.first_name} has been dbanned.")
        elif action == "gban":
            banned_users_collection.insert_one({"user_id": user.id, "username": user.username})
            for group in await context.bot.get_my_groups():
                try:
                    await context.bot.ban_chat_member(group.id, user.id)
                except Exception:
                    pass
            await update.message.reply_text(f"User {user.first_name} has been globally banned.")
    except BadRequest as e:
        await update.message.reply_text(f"Failed to {action} user: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"An unexpected error occurred: {e}")
    finally:
        await delete_command_and_service_messages(update, context)

async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pin a message in the group."""
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to the message you want to pin.")
        return

    try:
        await context.bot.pin_chat_message(update.effective_chat.id, update.message.reply_to_message.message_id)
        await update.message.reply_text("Message has been pinned.")
    except BadRequest as e:
        await update.message.reply_text(f"Failed to pin message: {e.message}")
    except Exception as e:
        await update.message.reply_text(f"An unexpected error occurred: {e}")
    finally:
        await delete_command_and_service_messages(update, context)

# Handlers for the commands
ban_handler = CommandHandler("ban", lambda u, c: handle_user_action(u, c, action="ban"))
unban_handler = CommandHandler("unban", lambda u, c: handle_user_action(u, c, action="unban"))
kick_handler = CommandHandler("kick", lambda u, c: handle_user_action(u, c, action="kick"))
mute_handler = CommandHandler("mute", lambda u, c: handle_user_action(u, c, action="mute"))
unmute_handler = CommandHandler("unmute", lambda u, c: handle_user_action(u, c, action="unmute"))
tmute_handler = CommandHandler("tmute", lambda u, c: handle_user_action(u, c, action="tmute", duration=int(c.args[0]) if c.args else 0))
dban_handler = CommandHandler("dban", lambda u, c: handle_user_action(u, c, action="dban"))
gban_handler = CommandHandler("gban", lambda u, c: handle_user_action(u, c, action="gban"))
pin_handler = CommandHandler("pin", pin_message)

# Export handlers for integration in the main bot
__all__ = ["ban_handler", "unban_handler", "kick_handler", "mute_handler", "unmute_handler", "tmute_handler", "dban_handler", "gban_handler", "pin_handler"]
