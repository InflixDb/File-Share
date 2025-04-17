# bot.py
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telethon.sync import TelegramClient
from config import TELEGRAM_BOT_TOKEN, API_ID, API_HASH, FORCE_CHANNEL
from database import add_user, get_user, update_subscription, get_admins, add_admin, remove_admin, add_filter, get_filter

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Telethon client for channel management
client = TelegramClient('anon', API_ID, API_HASH)

# Command: Start
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = get_user(user_id)

    if not user:
        add_user(user_id)

    if check_subscription(update):
        update.message.reply_text("Welcome to the bot!")

# Command: Request subscription
def request_sub(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    update.message.reply_text(f"Please join our channel @YOUR_CHANNEL_NAME to proceed.")
    
# Command: Generate link
def genlink(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_subscription(update):
        return
    
    # Logic to generate a short URL for a file (Placeholder)
    short_url = "https://short.link/example"
    update.message.reply_text(f"Here is your short link: {short_url}")

# Command: Broadcast message (Admin only)
def batch(update: Update, context: CallbackContext):
    if update.message.from_user.id not in get_admins():
        update.message.reply_text("You don't have permission to use this command.")
        return
    
    message = ' '.join(context.args)
    if not message:
        update.message.reply_text("Please provide a message to broadcast.")
        return
    
    # Broadcast the message to all users in the database
    update.message.reply_text(f"Broadcasting: {message}")

# Command: Add Admin (Admin only)
def add_admin_cmd(update: Update, context: CallbackContext):
    if update.message.from_user.id not in get_admins():
        update.message.reply_text("You don't have permission to use this command.")
        return
    
    try:
        new_admin_id = int(context.args[0])
        add_admin(new_admin_id)
        update.message.reply_text(f"User {new_admin_id} has been added as admin.")
    except IndexError:
        update.message.reply_text("Usage: /add_admin <user_id>")

# Command: Set filter (Admin only)
def set_filter(update: Update, context: CallbackContext):
    if update.message.from_user.id not in get_admins():
        update.message.reply_text("You don't have permission to use this command.")
        return
    
    try:
        anime_name = context.args[0]
        link = context.args[1]
        add_filter(anime_name, link)
        update.message.reply_text(f"Filter set for {anime_name}. Link: {link}")
    except IndexError:
        update.message.reply_text("Usage: /set_filter <anime_name> <link>")

# Function to check if user is subscribed to the channel
async def check_subscription(update: Update):
    user_id = update.message.from_user.id
    try:
        user = await client.get_participant(FORCE_CHANNEL, user_id)
        return True
    except:
        return False

# Main function to start the bot
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("requestsub", request_sub))
    dp.add_handler(CommandHandler("genlink", genlink))
    dp.add_handler(CommandHandler("batch", batch))
    dp.add_handler(CommandHandler("add_admin", add_admin_cmd))
    dp.add_handler(CommandHandler("set_filter", set_filter))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
