import json
import os
import logging

logger = logging.getLogger(__name__)

DATA_FILE = "user_data.json"

def load_data():
    """Loads user data from JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return {}

def save_data(data):
    """Saves user data to JSON file."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save data: {e}")

def get_user_settings(chat_id):
    """Gets settings for a specific user."""
    data = load_data()
    return data.get(str(chat_id), {})

def update_user_setting(chat_id, key, value):
    """Updates a specific setting for a user."""
    data = load_data()
    chat_id_str = str(chat_id)
    if chat_id_str not in data:
        data[chat_id_str] = {}
    
    data[chat_id_str][key] = value
    save_data(data)

def log_mood(chat_id, mood):
    """Logs the user's mood with a timestamp."""
    from datetime import datetime
    
    data = load_data()
    chat_id_str = str(chat_id)
    
    if chat_id_str not in data:
        data[chat_id_str] = {}
        
    if "mood_history" not in data[chat_id_str]:
        data[chat_id_str]["mood_history"] = []
        
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mood": mood
    }
    data[chat_id_str]["mood_history"].append(entry)
    save_data(data)

def log_daily_review(chat_id, rating, text):
    """Logs the user's daily review."""
    from datetime import datetime
    
    data = load_data()
    chat_id_str = str(chat_id)
    
    if chat_id_str not in data:
        data[chat_id_str] = {}
        
    if "daily_reviews" not in data[chat_id_str]:
        data[chat_id_str]["daily_reviews"] = []
        
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "rating": rating,
        "text": text
    }
    data[chat_id_str]["daily_reviews"].append(entry)
    save_data(data)

def log_user_message(chat_id, message_text):
    """Logs a general message from the user."""
    from datetime import datetime
    
    data = load_data()
    chat_id_str = str(chat_id)
    
    if chat_id_str not in data:
        data[chat_id_str] = {}
        
    if "message_history" not in data[chat_id_str]:
        data[chat_id_str]["message_history"] = []
        
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message_text
    }
    data[chat_id_str]["message_history"].append(entry)
    save_data(data)
