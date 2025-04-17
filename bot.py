import logging
import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Premium Database (in-memory, can be replaced with SQLite/JSON for persistence)
premium_db = {}

# Get API Tokens from config.py
from config import BITLY_TOKEN, TELEGRAM_BOT_TOKEN, ADMIN_USER_ID

# Shorten Link using Bitly API
def shorten_link(long_url):
    headers = {
        "Authorization": f"Bearer {BITLY_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"long_url": long_url}
    response = requests.post("https://api-ssl.bitly.com/v4/shorten", json=data, headers=headers)
    return response.json().get("link", long_url)

# Check if user is premium
def is_premium(user_id):
    if user_id not in premium_db:
        return False
    return datetime.strptime(premium_db[user_id], "%Y-%m-%d") >= datetime.now()

# /add_premium Command: Admin can grant premium access
def add_premium(update: Update, context: CallbackContext):
    # Ensure admin is using this command
    if update.message.from_user.id != ADMIN_USER_ID:  # Replace with your admin ID
        update.message.reply_text("You don't have permission to use this command.")
        return

    if len(context.args) != 2:
        update.message.reply_text("Usage: /add_premium <user_id> <days>")
        return
    
    user_id = int(context.args[0])
    days = int(context.args[1])
    until = datetime.now() + timedelta(days=days)
    
    premium_db[user_id] = until.strftime("%Y-%m-%d")
    update.message.reply_text(f"Premium access granted to {user_id} until {until.date()}.")

# Handle file requests and check premium status
def handle_file_request(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    file_url = "https://yourfileserver.com/file123"  # Replace with actual file URL

    if is_premium(user_id):
        update.message.reply_text(f"Here’s your direct file link:\n{file_url}")
    else:
        short_link = shorten_link(file_url)
        update.message.reply_text(f"You need to verify before accessing the file:\n{short_link}")

# /start Command: Send greeting message
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send any file or request a file to get started.")

# /help Command: Show instructions
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("Use /add_premium <user_id> <days> to give premium access.\nSend a file to get a shortened link.")

# Error Handler
def error(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Set up the Updater and Dispatcher
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("add_premium", add_premium))  # Premium command
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_file_request))  # Handle file requests

    # Log errors
    dp.add_error_handler(error)

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
