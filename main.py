import logging
import config
from bot import create_application
from scheduler import ReminderScheduler
from telegram import Update

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Silence httpx logs (too noisy)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main():
    """Start the bot and scheduler."""
    try:
        application = create_application()
        
        # Initialize and start scheduler
        scheduler = ReminderScheduler(application)
        application.bot_data['scheduler'] = scheduler
        scheduler.start()

        # Run the bot until the user presses Ctrl-C
        logger.info("Starting bot...")
        if config.ADMIN_CHAT_ID:
            logger.info(f"Admin Monitoring Enabled. Admin ID: {config.ADMIN_CHAT_ID}")
        else:
            logger.warning("Admin Monitoring Disabled. No ADMIN_CHAT_ID found.")
            
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()
