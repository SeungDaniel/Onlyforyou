import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
# If you want to restrict the bot to a specific user/chat, set this.
# Otherwise, it can be dynamic. For now, we'll keep it simple.
ALLOWED_CHAT_ID = os.getenv("ALLOWED_CHAT_ID")

# Default Schedule is now dynamic
