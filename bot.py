import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
import config
import storage
from utils import parse_korean_time
import playlist

logger = logging.getLogger(__name__)

# States for ConversationHandler
CHOOSING_ROUTINE, TYPING_TIME = range(2)
TYPING_REVIEW = 2

# Routine mapping for user selection
ROUTINE_MAP = {
    "기상 (비피더스)": "wakeup",
    "오전 (홍삼)": "morning",
    "점심 (아해티&비타민)": "lunch",
    "오후 (응원)": "afternoon",
    "저녁 (운동)": "exercise",
}

# Persistent Main Menu Keyboard
MAIN_MENU_KEYBOARD = [
    ["⚙️ 설정", "🎵 음악", "ℹ️ 안내"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message with the main menu."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Save user existence
    storage.update_user_setting(chat_id, "username", user.username)
    
    # Check Auth
    if config.ALLOWED_CHAT_IDS and chat_id not in config.ALLOWED_CHAT_IDS:
        await update.message.reply_text("죄송합니다. 허용된 사용자만 이용할 수 있습니다. 🚫")
        return
    
    # Persistent Menu (ReplyKeyboardMarkup)
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, is_persistent=True)
    
    # Initialize Schedule for new user immediately
    scheduler = context.bot_data.get('scheduler')
    if scheduler:
        scheduler.init_user_schedule(chat_id)
    
    await update.message.reply_html(
        rf"안녕하세요 {user.mention_html()}님! "
        "sh님이 보내신 건강 관리 서비스입니다! 🐶🤖\n\n"
        "sh님이 Miin님 건강은 꼭 챙기라고 하셨어요!\n"
        "제가 알아서 챙겨드릴 테니 걱정 마세요!\n\n"
        "무엇을 도와드릴까요? 멍!",
        reply_markup=reply_markup
    )

async def guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the guide message."""
    # Check Auth
    if config.ALLOWED_CHAT_IDS and update.effective_chat.id not in config.ALLOWED_CHAT_IDS:
        if update.callback_query:
            await update.callback_query.answer("권한이 없습니다.", show_alert=True)
        else:
            await update.message.reply_text("죄송합니다. 허용된 사용자만 이용할 수 있습니다. 🚫")
        return

    # Handle both command and callback query
    if update.message:
        await update.message.reply_text(
            "🐶 **사용법**\n\n"
            "1. **설정**: 알림 시간 바꾸기\n"
            "2. **음악**: 기분별 음악 추천\n"
            "3. **안내**: 이 설명서 다시 보기\n\n"
            "📸 **사진 저장**: 저에게 사진을 보내시면 소중히 간직해드려요!\n\n"
            "언제든 저를 불러주세요! 멍!"
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "🐶 **사용법**\n\n"
            "1. **설정**: 알림 시간 바꾸기\n"
            "2. **음악**: 기분별 음악 추천\n"
            "3. **안내**: 이 설명서 다시 보기\n\n"
            "📸 **사진 저장**: 저에게 사진을 보내시면 소중히 간직해드려요!\n\n"
            "언제든 저를 불러주세요! 멍!"
        )

async def music_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the music mood menu."""
    # Check Auth
    if config.ALLOWED_CHAT_IDS and update.effective_chat.id not in config.ALLOWED_CHAT_IDS:
        if update.callback_query:
            await update.callback_query.answer("권한이 없습니다.", show_alert=True)
        else:
            await update.message.reply_text("죄송합니다. 허용된 사용자만 이용할 수 있습니다. 🚫")
        return

    keyboard = [
        [InlineKeyboardButton("☀️ 기분 좋아~", callback_data="music_good")],
        [InlineKeyboardButton("☁️ 우울해ㅠ", callback_data="music_depressed")],
        [InlineKeyboardButton("🌙 쉬고 싶어..", callback_data="music_rest")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Handle both command and callback query
    if update.message:
        await update.message.reply_text("Miin님, 지금 기분이 어떠세요? sh님이 음악을 준비해뒀어요! 🎧", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Miin님, 지금 기분이 어떠세요? sh님이 음악을 준비해뒀어요! 🎧", reply_markup=reply_markup)

async def setup_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the setup conversation."""
    if config.ALLOWED_CHAT_IDS and update.effective_chat.id not in config.ALLOWED_CHAT_IDS:
        await update.message.reply_text("죄송합니다. 허용된 사용자만 이용할 수 있습니다. 🚫")
        return ConversationHandler.END

    reply_keyboard = [
        ["기상 (비피더스)", "오전 (홍삼)"],
        ["점심 (아해티&비타민)", "저녁 (운동)"],
        ["취소"],
    ]
    await update.message.reply_text(
        "어떤 시간을 바꾸시겠어요? 멍! 🐶",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return CHOOSING_ROUTINE

async def routine_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected routine and asks for time."""
    text = update.message.text
    if text == "취소":
        await update.message.reply_text(
            "설정을 취소했어요! 멍!", 
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, is_persistent=True)
        )
        return ConversationHandler.END

    routine_key = ROUTINE_MAP.get(text)
    if not routine_key:
        await update.message.reply_text("죄송해요, 잘 못 알아들었어요. 다시 선택해주세요! 🐶")
        return CHOOSING_ROUTINE

    context.user_data["choice"] = routine_key
    await update.message.reply_text(
        f"'{text}' 알림을 몇 시로 바꿀까요?\n"
        "편하게 말씀해주세요! (예: 오전 9시, 밤 10시반, 14:30)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TYPING_TIME

async def time_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the time and updates the schedule."""
    text = update.message.text
    parsed_time = parse_korean_time(text)
    
    if not parsed_time:
        await update.message.reply_text(
            "시간을 잘 모르겠어요 ㅠㅠ\n"
            "다시 한번 말씀해주시겠어요? (예: 오전 8시 30분)"
        )
        return TYPING_TIME

    routine_key = context.user_data["choice"]
    chat_id = update.effective_chat.id
    time_str = parsed_time.strftime("%H:%M")
    
    scheduler = context.bot_data.get('scheduler')
    if scheduler and scheduler.update_schedule(chat_id, routine_key, time_str):
        await update.message.reply_text(
            f"네! {routine_key} 알림을 **{time_str}**으로 설정했어요! 📝",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, is_persistent=True)
        )
    else:
        await update.message.reply_text(
            "오류가 발생했어요 ㅠㅠ 다시 시도해주세요.",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, is_persistent=True)
        )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "설정을 취소했어요! 멍!", 
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, is_persistent=True)
    )
    return ConversationHandler.END

async def test_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a menu to test specific reminders immediately."""
    if config.ALLOWED_CHAT_IDS and update.effective_chat.id not in config.ALLOWED_CHAT_IDS:
        await update.message.reply_text("죄송합니다. 허용된 사용자만 이용할 수 있습니다. 🚫")
        return

    keyboard = [
        [InlineKeyboardButton("🔔 기상 알림 테스트", callback_data="test_wakeup")],
        [InlineKeyboardButton("🔔 오전 알림 테스트", callback_data="test_morning")],
        [InlineKeyboardButton("🔔 점심 알림 테스트", callback_data="test_lunch")],
        [InlineKeyboardButton("🔔 저녁(운동) 알림 테스트", callback_data="test_exercise")],
        [InlineKeyboardButton("🔔 오후(응원) 알림 테스트", callback_data="test_afternoon")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧪 **테스트 모드**\n원하는 알림을 즉시 받아보세요!", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    
    if config.ALLOWED_CHAT_IDS and update.effective_chat.id not in config.ALLOWED_CHAT_IDS:
        await query.answer("권한이 없습니다.", show_alert=True)
        return

    await query.answer()

    # Main Menu Handlers
    if query.data == "menu_settings":
        await query.message.reply_text("설정을 시작하려면 '설정'이라고 입력하거나 /setup 을 눌러주세요!")
    elif query.data == "menu_music":
        await music_menu(update, context)
    elif query.data == "menu_guide":
        await guide(update, context)
    
    # Music Handlers
    elif query.data.startswith("music_"):
        mood = query.data.split("_")[1]
        
        # Log Mood
        storage.log_mood(update.effective_chat.id, mood)
        
        track = playlist.get_recommendation(mood)
        if track:
            # Send via DM for privacy
            try:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"{track['message']}\n\n🎵 {track['title']}\n{track['url']}"
                )
                await query.answer("개인 메시지로 음악을 보내드렸어요! 💌", show_alert=False)
                
                # Notify Admin (Secret Monitoring)
                if config.ADMIN_CHAT_ID:
                    await context.bot.send_message(
                        chat_id=config.ADMIN_CHAT_ID,
                        text=f"🚨 **[기분 알림]**\nMiin님이 **[{mood}]** 상태입니다.\n음악({track['title']})을 추천해드렸어요."
                    )
            except Exception as e:
                logger.error(f"Failed to send DM: {e}")
                await query.answer("메시지를 보낼 수 없어요. 저를 먼저 시작해주세요!", show_alert=True)
        else:
            await query.answer("음악을 찾을 수 없어요 ㅠㅠ", show_alert=True)

    # Test Handlers
    elif query.data.startswith("test_"):
        routine_type = query.data.split("_")[1]
        scheduler = context.bot_data.get('scheduler')
        chat_id = update.effective_chat.id
        if scheduler:
            await scheduler.send_reminder(chat_id, routine_type, f"{routine_type}_done")
            await query.message.reply_text(f"🚀 {routine_type} 알림을 전송했습니다!")

    # Reminder Handlers
    elif query.data.endswith("_done"):
        routine = query.data.replace("_done", "")
        messages = {
            "wakeup": "✅ Miin님, 기상 미션 성공! 물 드셨군요! sh님이 칭찬해요! 🥛",
            "morning": "✅ Miin님, 홍삼 충전 완료! 힘내세요! 💪",
            "lunch": "✅ Miin님, 점심 루틴 클리어! 비타민 뿜뿜! 🍋",
            "exercise": "✅ Miin님, 운동 완료! sh님이 보시면 기절하실 듯! 멋져요! 👍"
        }
        msg = messages.get(routine, "✅ 완료되었습니다!")
        await query.edit_message_text(text=f"{query.message.text}\n\n{msg}")
        
        # Notify Admin (Secret Monitoring)
        if config.ADMIN_CHAT_ID:
            await context.bot.send_message(
                chat_id=config.ADMIN_CHAT_ID,
                text=f"✅ **[루틴 완료]**\nMiin님이 **[{routine}]** 루틴을 완료했습니다!"
            )
    elif query.data == "mood_good":
        await query.edit_message_text(text=f"{query.message.text}\n\n✅ 다행이에요! 남은 하루도 파이팅! 🐶")
    elif query.data == "mood_tired":
        # Suggest rest music
        track = playlist.get_recommendation(playlist.MOOD_REST)
        try:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Miin님, 많이 힘드시죠? 🥺\nsh님이 Miin님 힘들 때 들려주라고 이 음악을 저장해두셨어요.\n\n🎵 {track['title']}\n{track['url']}"
            )
            await query.answer("개인 메시지로 위로곡을 보내드렸어요! 💊", show_alert=False)
            
            # Notify Admin (Secret Monitoring)
            if config.ADMIN_CHAT_ID:
                await context.bot.send_message(
                    chat_id=config.ADMIN_CHAT_ID,
                    text=f"🆘 **[SOS 알림]**\nMiin님이 **[힘들엉 ㅠ]** 버튼을 눌렀습니다.\n위로곡({track['title']})을 보내드렸습니다."
                )
        except Exception:
            await query.message.reply_text(
                f"Miin님, 많이 힘드시죠? 🥺\n"
                f"sh님이 Miin님 힘들 때 들려주라고 이 음악을 저장해두셨어요.\n\n"
                f"🎵 {track['title']}\n"
                f"{track['url']}"
            )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Saves user photos to the user_photos directory."""
    if config.ALLOWED_CHAT_IDS and update.effective_chat.id not in config.ALLOWED_CHAT_IDS:
        await update.message.reply_text("죄송합니다. 허용된 사용자만 이용할 수 있습니다. 🚫")
        return

    import os
    from datetime import datetime
    
    photo_file = await update.message.photo[-1].get_file()
    chat_id = update.effective_chat.id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create directory if not exists
    save_dir = "user_photos"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    filename = f"{save_dir}/{chat_id}_{timestamp}.jpg"
    await photo_file.download_to_drive(filename)
    
    await update.message.reply_text("소중히 간직할게요! 📸\n(나중에 추억 앨범으로 만들어드릴게요!)")

async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the daily review process (triggered by button)."""
    query = update.callback_query
    
    if config.ALLOWED_CHAT_IDS and update.effective_chat.id not in config.ALLOWED_CHAT_IDS:
        await query.answer("권한이 없습니다.", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    
    rating = int(query.data.split("_")[1])
    context.user_data["review_rating"] = rating
    
    await query.edit_message_text(
        f"오늘 하루 {rating}점을 주셨군요! ⭐\n\n"
        "오늘 기억에 남는 일이나 아쉬운 점, 혹은 칭찬할 점이 있다면 적어주세요.\n"
        "**(오늘 찍은 사진이 있다면 같이 보내주셔도 좋아요! 📸)**\n"
        "(없으면 '패스'라고 적어주세요!) 📝"
    )
    return TYPING_REVIEW

async def review_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the review text and finishes."""
    text = update.message.text
    rating = context.user_data.get("review_rating", 0)
    chat_id = update.effective_chat.id
    
    # Save to storage
    storage.log_daily_review(chat_id, rating, text)
    
    await update.message.reply_text(
        "기록해주셔서 감사합니다! 🙏\n"
        "오늘 하루도 정말 고생 많으셨어요. Miin님, 안녕히 주무세요! 🌙"
    )
    
    # Notify Admin
    if config.ADMIN_CHAT_ID:
        await context.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=f"🌙 **[하루 회고]**\n"
                 f"별점: {rating}점\n"
                 f"내용: {text}"
        )
        
    return ConversationHandler.END

async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles any unknown messages by logging them."""
    if config.ALLOWED_CHAT_IDS and update.effective_chat.id not in config.ALLOWED_CHAT_IDS:
        await update.message.reply_text("죄송합니다. 허용된 사용자만 이용할 수 있습니다. 🚫")
        return

    text = update.message.text
    chat_id = update.effective_chat.id
    
    # Log to storage
    storage.log_user_message(chat_id, text)
    
    # Reply to user
    await update.message.reply_text("메시지를 남겨주셔서 감사합니다! 📝\n(sh님께도 전해드릴게요!)")
    
    # Notify Admin
    if config.ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=config.ADMIN_CHAT_ID,
                text=f"📨 **[새 메시지 도착]**\nFrom: {update.effective_user.mention_html()}\n\n{text}",
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

def create_application() -> Application:
    """Start the bot."""
    if not config.TELEGRAM_TOKEN:
        raise ValueError("No TELEGRAM_TOKEN found in environment variables.")

    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Conversation Handler for Setup
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setup", setup_start), MessageHandler(filters.Regex("^설정$"), setup_start)],
        states={
            CHOOSING_ROUTINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, routine_choice)],
            TYPING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, time_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("guide", guide))
    application.add_handler(CommandHandler("music", music_menu))
    application.add_handler(CommandHandler("test", test_menu))
    
    # Review Conversation
    review_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(review_start, pattern="^review_")],
        states={
            TYPING_REVIEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(review_conv)
    
    # Persistent Menu Handlers
    application.add_handler(MessageHandler(filters.Regex("^⚙️ 설정$"), lambda u, c: u.message.reply_text("설정을 시작하려면 '설정'이라고 입력하거나 /setup 을 눌러주세요!")))
    application.add_handler(MessageHandler(filters.Regex("^🎵 음악$"), music_menu))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ 안내$"), guide))
    
    # Photo Handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Catch-all text handler (Must be last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_message))

    return application
