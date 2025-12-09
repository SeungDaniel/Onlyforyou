import logging
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application
import config
import storage

logger = logging.getLogger(__name__)

# Specific Messages for each routine
WAKEUP_MESSAGES = [
    "Miin님! 일어나셨나요? 멍! 🐶 sh님이 기상 직후엔 **비피더스랑 물** 꼭 드시래요! 꿀꺽! 🥛",
    "굿모닝 Miin님! ☀️ sh님이 보내신 물과 비피더스 배달 왔습니다! 얼른 드세요! 🤖",
    "일어날 시간이에요 Miin님! 🌞 sh님이 비피더스랑 물 마시고 상쾌하게 시작하래요! 멍!",
]

MORNING_MESSAGES = [
    "Miin님, 오전 빈속에 챙길 시간이에요! 🤖 **홍삼(또는 로얄젤리)**이랑 **안타플러스**! sh님이 건강 챙기래요! 💊",
    "바쁘셔도 잠깐! sh님이 **홍삼이랑 안타플러스** 먹고 힘내라고 하셨어요! 아자아자! 💪",
    "Miin님! sh님이 걱정해요! 🥺 **홍삼(로얄젤리) & 안타플러스** 잊지 말고 챙겨주세요! 멍!",
]

LUNCH_MESSAGES = [
    "점심 맛있게 드셨나요? 🍱 sh님이 **아해티(녹차편), 하이파워**, 그리고 **큰 언니분이 주신 비타민C** 챙겨드리래요! 🍋",
    "식후 3총사 대기 중! **아해티, 하이파워, 비타민C**! sh님이 이거 먹어야 오후에 안 존대요! 😋",
    "배부르시죠? 🤖 소화도 시킬 겸 **아해티, 하이파워, 비타민C** 타임! sh님이 꼭 챙기라고 했어요!",
]

EXERCISE_TASKS = [
    "뒤꿈치 들기 5회",
    "앉았다 일어나기 5회",
    "스쿼트 5회",
    "팔 당기기 5회",
    "시원하게 기지개 한 번 펴기",
]

EXERCISE_TEMPLATES = [
    "Miin님! sh님이 지금 **{task}** 하래요! 딱 이것만 하고 쉬어요! 멍! 🐶",
    "운동 타임! ⏰ sh님의 미션: **{task}** 실시! 건강해지자구요! 💪",
    "Miin님, 많이 힘드시죠? 그래도 **{task}** 이거 하나만 해요! sh님이 부탁했어요! ❤️",
]

AFTERNOON_MESSAGES = [
    "Miin님! 오후 시간도 힘내세요! sh님이 응원하고 있어요! 어깨 한번 펴고 화이팅! 💪",
    "Miin님, 바쁘시죠? sh님이 잠깐 스트레칭하고 물 한 잔 마시래요! 힘내세요! ❤️",
    "나른해질 수 있는 오후, sh님의 응원 도착! 💌 Miin님 생각하면서 힘내라고 전해달래요! 아자아자! 🐶",
]

class ReminderScheduler:
    DEFAULT_TIMES = {
        "wakeup": "07:00",
        "morning": "09:00",
        "lunch": "12:30",
        "afternoon": "14:00",
        "exercise": "19:00"
    }

    def __init__(self, application: Application):
        self.application = application
        self.scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

    async def send_reminder(self, chat_id: str, message_type: str, callback_data: str):
        """Sends a reminder message with a 'Done' button."""
        if not chat_id:
            logger.warning("No Chat ID provided for reminder.")
            return

        message = "알림 시간입니다!"
        keyboard = []

        if message_type == "wakeup":
            message = random.choice(WAKEUP_MESSAGES)
            keyboard.append([InlineKeyboardButton("✅ 먹었어!", callback_data="wakeup_done")])
        elif message_type == "morning":
            message = random.choice(MORNING_MESSAGES)
            keyboard.append([InlineKeyboardButton("✅ 챙겼어!", callback_data="morning_done")])
        elif message_type == "lunch":
            message = random.choice(LUNCH_MESSAGES)
            keyboard.append([InlineKeyboardButton("✅ 완료!", callback_data="lunch_done")])
        elif message_type == "exercise":
            task = random.choice(EXERCISE_TASKS)
            template = random.choice(EXERCISE_TEMPLATES)
            message = template.format(task=task)
            keyboard.append([InlineKeyboardButton("✅ 운동 완료!", callback_data="exercise_done")])
        elif message_type == "afternoon":
            message = random.choice(AFTERNOON_MESSAGES)
            keyboard.append([InlineKeyboardButton("힘들엉 ㅠ", callback_data="mood_tired")])
            keyboard.append([InlineKeyboardButton("괜찮아!", callback_data="mood_good")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup
            )
            logger.info(f"Sent reminder: {message} to {chat_id}")

            # Mirror to Admin (if admin exists and is not the recipient)
            if config.ADMIN_CHAT_ID and str(chat_id) != str(config.ADMIN_CHAT_ID):
                try:
                    await self.application.bot.send_message(
                        chat_id=config.ADMIN_CHAT_ID,
                        text=f"🔔 **[알림 발송 확인]**\nTo: {chat_id}\n\n{message}",
                        # No keyboard for admin mirror to avoid confusion, or keep it if they want to see buttons?
                        # User said "won't reply", so no buttons is safer/cleaner.
                    )
                except Exception as e:
                    logger.error(f"Failed to mirror reminder to admin: {e}")

        except Exception as e:
            logger.error(f"Failed to send reminder: {e}")

    def update_schedule(self, chat_id, job_type, time_str):
        """Updates the schedule for a specific job type."""
        try:
            hour, minute = map(int, time_str.split(':'))
            job_id = f"{job_type}_{chat_id}"
            
            # Remove existing job if it exists
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            self.scheduler.add_job(
                self.send_reminder,
                'cron',
                hour=hour,
                minute=minute,
                args=[chat_id, job_type, f"{job_type}_done"],
                id=job_id,
                replace_existing=True
            )
            
            # Save to storage (only if it's an update, not initial load)
            # note: The caller is responsible for saving to storage if this is a user-initiated change.
            # However, to be safe and consistent, we can check if this call is from load_jobs or user.
            # But the original code called storage.update_user_setting here. 
            # Let's keep it simple: We will assume this is always a valid update to persist 
            # unless we are just loading defaults in memory. 
            # Actually, `load_jobs` calls this. If we save here every time `load_jobs` runs, 
            # we might be writing to disk unnecessary defaults.
            # Let's decouple slightly: load_jobs will call a internal `_schedule_job` 
            # and this public method `update_schedule` will allow saving.
            
            storage.update_user_setting(chat_id, f"{job_type}_time", time_str)
            logger.info(f"Updated {job_type} schedule for {chat_id} to {time_str}")
            return True
        except ValueError:
            logger.error(f"Invalid time format: {time_str}")
            return False

    def _schedule_job(self, chat_id, job_type, time_str):
         """Internal method to add job without saving to storage."""
         try:
            hour, minute = map(int, time_str.split(':'))
            job_id = f"{job_type}_{chat_id}"
            
            self.scheduler.add_job(
                self.send_reminder,
                'cron',
                hour=hour,
                minute=minute,
                args=[chat_id, job_type, f"{job_type}_done"],
                id=job_id,
                replace_existing=True
            )
            logger.info(f"Scheduled {job_type} for {chat_id} at {time_str}")
         except ValueError as e:
             logger.error(f"Error scheduling job: {e}")

    def init_user_schedule(self, chat_id):
        """Initializes default schedules for a single user."""
        settings = storage.get_user_settings(chat_id)
        
        for job_type, default_time in self.DEFAULT_TIMES.items():
            # Use saved time if exists, else default
            time_str = settings.get(f"{job_type}_time", default_time)
            self._schedule_job(chat_id, job_type, time_str)

    def load_jobs(self):
        """Loads jobs from storage and defaults for all allowed users."""
        data = storage.load_data()
        
        # Get all relevant user IDs: those in storage + allowed IDs
        # allowed_chat_ids are ints in config, keys in data are strings
        all_users = set(data.keys())
        if config.ALLOWED_CHAT_IDS:
            all_users.update(str(uid) for uid in config.ALLOWED_CHAT_IDS)
            
        for chat_id in all_users:
            self.init_user_schedule(chat_id)
        
        # Daily Retrospective (23:00)
        self.scheduler.add_job(
            send_daily_review_prompt,
            'cron',
            hour=23,
            minute=0,
            args=[self.application],
            id="daily_review",
            replace_existing=True
        )

    def start(self):
        """Starts the scheduler."""
        self.load_jobs()
        self.scheduler.start()
        logger.info("Scheduler started and jobs loaded.")


async def send_daily_review_prompt(app):
    """Sends the daily review prompt to all users."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    import storage
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Load all users (Iterate over storage keys)
    data = storage.load_data()
    
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="review_1"),
            InlineKeyboardButton("2", callback_data="review_2"),
            InlineKeyboardButton("3", callback_data="review_3"),
            InlineKeyboardButton("4", callback_data="review_4"),
            InlineKeyboardButton("5", callback_data="review_5"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    for chat_id in data.keys():
        try:
            # Skip non-numeric keys (if any)
            if not chat_id.isdigit():
                continue
                
            await app.bot.send_message(
                chat_id=int(chat_id),
                text="Miin님, 오늘 하루는 어떠셨나요? 별점으로 알려주세요! (1~5점) ⭐",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to send review prompt to {chat_id}: {e}")
