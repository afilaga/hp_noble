import os
import re
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Загрузка переменных из .env
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

from database import (
    ReservationRepository,
    TableRepository,
    CustomerRepository,
    ReservationStatus,
    ReviewRepository,
    AdminRepository,
    UserRepository,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")

# Состояния для ConversationHandler
NAME, PHONE, DATE, TIME, PARTY_SIZE, COMMENT, CONSENT, CONFIRMATION = range(8)
# Состояния для отзывов
REVIEW_TEXT, REVIEW_CONTACT = range(8, 10)
# Состояния для админов
ADMIN_CHOICE, ADMIN_INPUT_ADD, ADMIN_INPUT_DEL, ADMIN_NEWSLETTER_TEXT, ADMIN_NEWSLETTER_CONFIRM = range(10, 15)

# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

def is_admin(user_id: str) -> bool:
    if user_id in ADMIN_IDS: return True
    return AdminRepository.is_admin_db(user_id)

async def notify_admins(application: Application, message: str):
    """Уведомление всех админов (из .env и БД)"""
    notified = set()
    
    # 1. Admins from ENV
    for admin_id in ADMIN_IDS:
        if admin_id and admin_id not in notified:
            try:
                await application.bot.send_message(chat_id=admin_id, text=message, parse_mode="Markdown")
                notified.add(admin_id)
            except Exception as e:
                logger.error(f"Failed to notify env admin {admin_id}: {e}")

    # 2. Admins from DB
    try:
        db_admins = AdminRepository.get_all()
        for admin in db_admins:
            aid = admin["telegram_id"]
            if aid and aid not in notified:
                try:
                    await application.bot.send_message(chat_id=aid, text=message, parse_mode="Markdown")
                    notified.add(aid)
                except Exception as e:
                    logger.error(f"Failed to notify db admin {aid}: {e}")
    except Exception as e:
        logger.error(f"Error fetching admins from DB: {e}")

def guest_word(n: int) -> str:
    if n == 1:
        return "гость"
    elif 2 <= n <= 4:
        return "гостя"
    return "гостей"

# ============= ГЛАВНОЕ МЕНЮ =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User started bot: {user.id} ({user.first_name})")
    
    # Save/Update Telegram User
    try:
        UserRepository.upsert(str(user.id), user.username, user.first_name)
    except Exception as e:
        logger.error(f"Failed to upsert telegram user: {e}")

    welcome = f"""
🍃 *Добро пожаловать в HookahPlace Noble, {user.first_name}!*

Премиальный кальянный лаунж в Сочи
"""
    
    # Главное меню с кнопками
    keyboard = [
        [KeyboardButton("📅 Забронировать")],
        [KeyboardButton("🌐 Сайт"), KeyboardButton("📞 Контакты")],
        [KeyboardButton("⭐ Оставить отзыв")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome, parse_mode="Markdown", reply_markup=reply_markup
    )
    return ConversationHandler.END

# ... existing code ...



# ============= АДМИН-ПАНЕЛЬ =============





# ============= ОБРАБОТЧИКИ КНОПОК МЕНЮ =============

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌐 Сайт":
        await update.message.reply_text(
            "🌐 Наш сайт: https://hpnoble.ru",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("← Назад в меню")]], resize_keyboard=True
            ),
        )
    elif text == "📞 Контакты":
        keyboard = [
            [KeyboardButton("📷 Instagram")],
            [KeyboardButton("📞 Позвонить"), KeyboardButton("💬 WhatsApp")],
            [KeyboardButton("🗺 Открыть на карте")],
            [KeyboardButton("← Назад в меню")],
        ]
        await update.message.reply_text(
            "📞 *Контакты HookahPlace Noble*\n\nВыберите способ связи:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )
    elif text == "📷 Instagram":
        await update.message.reply_text(
            "📷 [Instagram](https://www.instagram.com/hookahplacenoble)",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("← Назад в меню")]], resize_keyboard=True
            ),
        )
    elif text == "📞 Позвонить":
        await update.message.reply_text(
            "📞 Позвонить: +7 (918) 279-96-96",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("← Назад в меню")]], resize_keyboard=True
            ),
        )
    elif text == "💬 WhatsApp":
        await update.message.reply_text(
            "💬 [WhatsApp](https://wa.me/79182799696)",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("← Назад в меню")]], resize_keyboard=True
            ),
        )
    elif text == "🗺 Открыть на карте":
        await update.message.reply_text(
            "🗺 [Мы на карте](https://yandex.ru/maps/-/CLd6e-jy)",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("← Назад в меню")]], resize_keyboard=True
            ),
        )
    elif text == "⭐ Оставить отзыв":
        keyboard = [
            [KeyboardButton("💬 Отзыв управляющему")],
            [KeyboardButton("⭐ Яндекс.Карты"), KeyboardButton("🗺 2ГИС")],
            [KeyboardButton("← Назад в меню")],
        ]
        await update.message.reply_text(
            "⭐ *Оставить отзыв*\n\nВыберите платформу:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )
    elif text == "⭐ Яндекс.Карты":
        await update.message.reply_text(
            "⭐ [Оставить отзыв на Яндекс](https://yandex.ru/maps/org/hookah_place_noble/142545357638/reviews/)",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("← Назад в меню")]], resize_keyboard=True
            ),
        )
    elif text == "🗺 2ГИС":
        await update.message.reply_text(
            "🗺 [Оставить отзыв в 2ГИС](https://go.2gis.com/hookahnoble)",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("← Назад в меню")]], resize_keyboard=True
            ),
        )
    # Отзыв управляющему обрабатывается отдельным Handler в main
    elif text == "← Назад в меню":
        return await start(update, context)

# ============= БРОНИРОВАНИЕ =============

async def book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало бронирования"""
    context.user_data.clear()
    user = update.effective_user
    context.user_data["telegram_id"] = str(user.id)
    context.user_data["username"] = user.username or ""
    
    await update.message.reply_text(
        "📝 *Новое бронирование*\n\nКак вас зовут?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["← Отмена"]], resize_keyboard=True),
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение имени"""
    name = update.message.text.strip()
    if name == "← Отмена":
        await start(update, context)
        return ConversationHandler.END
    
    if len(name) < 2:
        await update.message.reply_text("Имя слишком короткое. Попробуйте ещё раз:")
        return NAME

    context.user_data["name"] = name
    
    await update.message.reply_text(
        "📱 Введите номер телефона:",
        reply_markup=ReplyKeyboardMarkup([["← Отмена"]], resize_keyboard=True),
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение телефона"""
    phone = update.message.text.strip()
    if phone == "← Отмена":
        await start(update, context)
        return ConversationHandler.END

    context.user_data["phone"] = phone
    context.user_data["telegram_id"] = str(update.effective_user.id)
    
    # Убираем клавиатуру Reply
    await update.message.reply_text("Спасибо!", reply_markup=ReplyKeyboardRemove())
    
    # Генерируем кнопки с датами
    dates = []
    today = datetime.now()
    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    for i in range(0, 14): # Начинаем с 0 (сегодня), если нужно, или 1 (завтра) - юзер хотел "сегодня" тоже? В коде было range(1, 15). Оставлю range(0, 14) чтобы было доступно сегодня.
        date = today + timedelta(days=i)
        wd = weekdays_ru[date.weekday()]
        dates.append(
            [
                InlineKeyboardButton(
                    f"{date.strftime('%d.%m')} ({wd})",
                    callback_data=f"date_{date.strftime('%Y-%m-%d')}",
                )
            ]
        )
    
    await update.message.reply_text(
        "📅 Выберите дату:",
        reply_markup=InlineKeyboardMarkup(dates),
    )
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение даты"""
    query = update.callback_query
    await query.answer()
    
    date_str = query.data.split("_")[1]
    context.user_data["date"] = date_str
    
    # Генерируем временные слоты (12:00 - 23:30)
    times = []
    for hour in range(12, 24):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            times.append(
                [InlineKeyboardButton(time_str, callback_data=f"time_{time_str}")]
            )
    
    await query.edit_message_text(
        f"🕐 Выберите время на {date_str}:",
        reply_markup=InlineKeyboardMarkup(times),
    )
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение времени"""
    query = update.callback_query
    await query.answer()
    
    time_str = query.data.split("_")[1]
    context.user_data["time"] = time_str
    
    # Генерируем кнопки с количеством гостей (1-12)
    party = []
    for i in range(1, 13):
        party.append(
            [InlineKeyboardButton(f"{i} {guest_word(i)}", callback_data=f"party_{i}")]
        )
    
    await query.edit_message_text(
        "👥 Сколько гостей?",
        reply_markup=InlineKeyboardMarkup(party),
    )
    return PARTY_SIZE

async def get_party_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение количества гостей"""
    query = update.callback_query
    await query.answer()
    
    party_size = int(query.data.split("_")[1])
    context.user_data["party_size"] = party_size
    
    # Запрашиваем комментарий
    await query.edit_message_text(
        "💬 *Добавьте комментарий к бронированию* (необязательно):\n\nНапример: у окна, тихое место, день рождения и т.д.",
        parse_mode="Markdown",
    )
    
    await query.message.reply_text(
        "Введите комментарий или нажмите \"Пропустить\":",
        reply_markup=ReplyKeyboardMarkup([["⏭ Пропустить"], ["← Отмена"]], resize_keyboard=True),
    )
    return COMMENT

    return COMMENT

async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение комментария"""
    comment = update.message.text.strip()
    
    if comment == "← Отмена":
        await start(update, context)
        return ConversationHandler.END
    
    if comment != "⏭ Пропустить":
        context.user_data["comment"] = comment
    else:
        context.user_data["comment"] = ""
    
    # Ask for consent
    await update.message.reply_text(
        "🔒 *Обработка персональных данных*\n\n"
        "Подтверждая бронирование, вы даете согласие на обработку персональных данных.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Я согласен", callback_data="agree")],
            [InlineKeyboardButton("❌ Отмена", callback_data="cancel_consent")]
        ])
    )
    return CONSENT

async def get_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка согласия"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_consent":
        await query.edit_message_text("❌ Бронирование отменено.")
        await start(update, context)
        return ConversationHandler.END

    # Показываем подтверждение (перенесено из get_comment)
    name = context.user_data["name"]
    phone = context.user_data["phone"]
    date = context.user_data["date"]
    time = context.user_data["time"]
    party_size = context.user_data["party_size"]
    comment_text = context.user_data.get("comment", "")
    
    summary = f"📋 *Подтвердите бронирование:*\n\n👤 {name}\n📱 {phone}\n📅 {date}\n🕐 {time}\n👥 {party_size} {guest_word(party_size)}\n"
    if comment_text:
        summary += f"💬 {comment_text}\n"
    
    summary += "\n_Нажмите подтвердить для завершения_"
    
    await query.edit_message_text(
        summary,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel")],
        ]),
    )
    return CONFIRMATION

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение бронирования"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Бронирование отменено.")
        await start(update, context)
        return ConversationHandler.END
    
    # Сохраняем бронирование в базу
    name = context.user_data["name"]
    phone = context.user_data["phone"]
    telegram_id = context.user_data["telegram_id"]
    try:
        # User details from previous steps
        name = context.user_data.get("name", "Unknown")
        phone = context.user_data.get("phone", "Unknown")
        date = context.user_data.get("date")
        time = context.user_data.get("time")
        guests = context.user_data.get("party_size") # Changed from 'guests' to 'party_size' to match context.user_data
        # Extract comment
        comment = context.user_data.get("comment", "")
        # If it's a skip or cancel, get_comment handles it, but if we are here, we have a comment or empty string
        
        # Combine date/time
        # Note: date is 'YYYY-MM-DD', time is 'HH:MM'
        start_time_str = f"{date}T{time}:00"
        start_time_dt = datetime.fromisoformat(start_time_str)

        # Create/Get Customer first
        customer = CustomerRepository.get_or_create(name, phone, telegram_id=telegram_id)

        # Create reservation
        reservation_id = ReservationRepository.create(
            customer_id=customer["id"],
            table_id=None,
            start_time=start_time_dt,
            party_size=guests,
            comment=comment,
            source="bot"
        )

        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")
        
        # Success message
        await query.message.reply_text(
            f"✅ *Бронирование #{reservation_id[:8]} создано!*\n\n"
            f"📅 Дата: {formatted_date}\n"
            f"⏰ Время: {time}\n"
            f"👤 Гостей: {guests}",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["← Назад в меню"]], resize_keyboard=True)
        )
        
        # Remove inline keyboard first
        await query.edit_message_reply_markup(reply_markup=None)

        # Notify Admins
        try:
            # Prepare links
            clean_phone = re.sub(r'[^\d+]', '', phone)
            user = update.effective_user
            tg_link = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
            
            await notify_admins(context.application, 
                f"🔔 *Новая бронь (Бот)*\n\n"
                f"👤 {name}\n"
                f"📞 [{phone}](tel:{clean_phone})\n"
                f"✉️ [Написать в TG]({tg_link})\n\n"
                f"📅 {formatted_date} в {time}\n"
                f"👥 {guests} {guest_word(guests)}\n"
                f"{f'💬 {comment}' if comment else ''}"
            )
        except Exception as e:
            logger.error(f"Notification error: {e}")

    except Exception as e:
        logger.error(f"Error creating reservation: {e}", exc_info=True)
        await query.message.reply_text(
             f"❌ Ошибка при создании бронирования: {e}",
             reply_markup=ReplyKeyboardMarkup([["← Назад в меню"]], resize_keyboard=True)
        )
    
    return ConversationHandler.END

# ============= АДМИН-ПАНЕЛЬ =============

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-панель (доступ по команде /adminnoble)"""
    user_id = str(update.effective_user.id)
    if not is_admin(user_id):
        # Игнорируем или даём нейтральный ответ
        return
    
    keyboard = [
        [KeyboardButton("📅 Актуальные брони")],
        [KeyboardButton("💬 Просмотр отзывов"), KeyboardButton("📥 Скачать отзывы")],
        [KeyboardButton("📥 Скачать брони"), KeyboardButton("👥 Управление админами")],
        [KeyboardButton("📢 Рассылка")],
        [KeyboardButton("← Выход")],
    ]
    
    await update.message.reply_text(
        "👨‍💼 *Админ-панель*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return ConversationHandler.END



async def cancel_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена текущего действия"""
    await update.message.reply_text("❌ Действие отменено.", reply_markup=None)
    await start(update, context)
    return ConversationHandler.END

async def admin_download_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скачивание таблицы бронирований"""
    if not is_admin(str(update.effective_user.id)): return
    
    csv_data = ReservationRepository.export_csv()
    
    if not csv_data:
        await update.message.reply_text("📭 База данных пуста.")
        return

    await update.message.reply_document(
        document=csv_data.encode("utf-8"),
        filename=f"reservations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        caption="📊 Таблица бронирований"
    )

async def admin_download_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скачивание таблицы отзывов"""
    if not is_admin(str(update.effective_user.id)): return
    
    csv_data = ReviewRepository.export_csv()
    
    if not csv_data:
        await update.message.reply_text("📭 Отзывов нет.")
        return

    await update.message.reply_document(
        document=csv_data.encode("utf-8"),
        filename=f"reviews_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        caption="💬 Таблица отзывов"
    )

async def admin_show_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать актуальные брони"""
    if not is_admin(str(update.effective_user.id)): return
    
    # Use get_active (pending, confirmed, seated)
    bookings = ReservationRepository.get_active()
    # Limit manually if needed, or update repository to accept limit
    # We'll take first 20 just in case
    bookings = bookings[:20] 
     
    if not bookings:
        await update.message.reply_text("📭 *Нет актуальных броней.*", parse_mode="Markdown")
        return
        
    msg = "📅 *Актуальные брони:*\n\n"
    for b in bookings:
        dt = datetime.fromisoformat(b['start_time'])
        date_fmt = dt.strftime("%d.%m")
        time_fmt = dt.strftime("%H:%M")
        name = b.get('customer_name', 'Unknown')
        phone = b.get('customer_phone', '-')
        
        clean_phone = re.sub(r'[^\d+]', '', phone)
        phone_display = f"[{phone}](tel:{clean_phone})" if len(clean_phone) > 5 else phone
        
        guests = b['party_size']
        
        msg += f"🔹 *{date_fmt} {time_fmt}* — {name}\n📞 {phone_display} | 👥 {guests} чел.\n\n"
        
    await update.message.reply_text(msg, parse_mode="Markdown")

async def admin_stats_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика за сегодня"""
    if not is_admin(str(update.effective_user.id)): return
    await update.message.reply_text("📅 Статистика за сегодня: (В разработке)")

async def admin_stats_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика за неделю"""
    if not is_admin(str(update.effective_user.id)): return
    await update.message.reply_text("📆 Статистика за неделю: (В разработке)")
    
async def admin_reviews_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр отзывов (последние 5)"""
    if not is_admin(str(update.effective_user.id)): return
    
    reviews = ReviewRepository.get_all(limit=5)
    if not reviews:
        await update.message.reply_text("💬 *Отзывов пока нет.*", parse_mode="Markdown")
        return

    msg = "💬 *Последние отзывы:*\n\n"
    for r in reviews:
        date = r.get('created_at', '')[:16] # Cut seconds
        contact = r.get('user_contact', '-')
        
        clean_contact = re.sub(r'[^\d+]', '', contact)
        contact_display = contact
        if len(clean_contact) > 6 and not contact.startswith("@"):
             contact_display = f"[{contact}](tel:{clean_contact})"
             
        msg += f"👤 {r['user_name']} ({contact_display})\n🕒 {date}\n📝 {r['text']}\n\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ============= ОТЗЫВЫ =============

async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало подачи отзыва"""
    await update.message.reply_text(
        "📝 *Отзыв управляющему*\n\nНапишите ваш отзыв, предложение или жалобу:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["← Отмена"]], resize_keyboard=True),
    )
    return REVIEW_TEXT

async def get_review_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение текста отзыва"""
    text = update.message.text
    if text == "← Отмена":
        await start(update, context)
        return ConversationHandler.END

    context.user_data["review_text"] = text
    
    await update.message.reply_text(
        "📞 Оставьте контакт для обратной связи (телефон или ник в Telegram),\nили нажмите \"Пропустить\":",
        reply_markup=ReplyKeyboardMarkup([["⏭ Пропустить"], ["← Отмена"]], resize_keyboard=True),
    )
    return REVIEW_CONTACT

async def get_review_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение контакта и сохранение отзыва"""
    logger.info("Entering get_review_contact")
    try:
        contact = update.message.text
        logger.info(f"Review contact input: {contact}")
        
        if contact == "← Отмена":
            await start(update, context)
            return ConversationHandler.END
        
        user_name = update.effective_user.full_name
        
        if contact == "⏭ Пропустить":
            user = update.effective_user
            contact = f"@{user.username}" if user.username else str(user.id)
            logger.info("Review contact skipped, using: " + contact)
        
        text = context.user_data.get("review_text", "")
        
        if not text:
             logger.warning("Empty review text found in user_data")
             await update.message.reply_text("⚠ Текст отзыва не найден. Попробуйте снова.")
             return ConversationHandler.END
        
        # Сохраняем
        ReviewRepository.create(user_name, contact, text)
        logger.info("Review saved to DB")
        
        await update.message.reply_text(
            "✅ *Спасибо, что поделились отзывом!* \nМы обязательно рассмотрим его.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["← Назад в меню"]], resize_keyboard=True)
        )

        # Notify Admins
        # Prepare links
        clean_phone = re.sub(r'[^\d+]', '', contact) if contact and not contact.startswith("@") else ""
        user = update.effective_user
        tg_link = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
        
        # Если контакт - это телефон (не начинается с @ и содержит цифры), делаем ссылку
        contact_display = contact
        if clean_phone and len(clean_phone) > 5:
             contact_display = f"[{contact}](tel:{clean_phone})"
        
        await notify_admins(context.application, 
             f"💬 *Новый отзыв!*\n\n"
             f"👤 {user_name}\n"
             f"📞 {contact_display}\n"
             f"✉️ [Написать в TG]({tg_link})\n\n"
             f"📝 {text}"
        )

    except Exception as e:
        logger.error(f"Error saving review: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Произошла ошибка при сохранении отзыва: {e}")
        
    # Возвращаем главное меню
    await start(update, context)
    return ConversationHandler.END

# ============= УПРАВЛЕНИЕ АДМИНАМИ =============

async def admin_manage_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню управления админами"""
    user_id = str(update.effective_user.id)
    if not is_admin(user_id):
        return ConversationHandler.END

    admins = AdminRepository.get_all()
    admins_text = "\n".join([f"- {a['telegram_id']} ({a['username'] or 'No name'})" for a in admins])
    
    await update.message.reply_text(
        f"👥 *Список администраторов:*\n\n{admins_text}\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([
            ["➕ Добавить админа", "➖ Удалить админа"],
            ["← Назад"]
        ], resize_keyboard=True)
    )
    return ADMIN_CHOICE

async def admin_choice_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➕ Введите Telegram ID нового администратора (цифры):",
        reply_markup=ReplyKeyboardMarkup([["← Отмена"]], resize_keyboard=True)
    )
    return ADMIN_INPUT_ADD

async def admin_choice_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➖ Введите Telegram ID администратора для удаления:",
        reply_markup=ReplyKeyboardMarkup([["← Отмена"]], resize_keyboard=True)
    )
    return ADMIN_INPUT_DEL

async def admin_perform_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "← Отмена":
        await admin_manage_start(update, context)
        return ADMIN_CHOICE
        
    try:
        new_id = str(int(text.strip()))
        AdminRepository.add(new_id, "Added by bot", str(update.effective_user.id))
        await update.message.reply_text(f"✅ Админ {new_id} добавлен.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
        
    await admin_manage_start(update, context) # Возврат в меню админов
    return ADMIN_CHOICE

async def admin_perform_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "← Отмена":
        await admin_manage_start(update, context)
        return ADMIN_CHOICE

    try:
        del_id = text.strip()
        if del_id == str(update.effective_user.id):
             await update.message.reply_text("❌ Нельзя удалить самого себя.")
        else:
            AdminRepository.remove(del_id)
            await update.message.reply_text(f"✅ Админ {del_id} удален.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
        
    await admin_manage_start(update, context)
    return ADMIN_CHOICE

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_panel(update, context)
    return ConversationHandler.END

# ============= РАССЫЛКА =============

async def admin_newsletter_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало рассылки"""
    if not is_admin(str(update.effective_user.id)): return ConversationHandler.END
    
    await update.message.reply_text(
        "📢 *Рассылка*\n\nОтправьте текст сообщения или фото с подписью.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["← Отмена"]], resize_keyboard=True)
    )
    return ADMIN_NEWSLETTER_TEXT

async def admin_newsletter_get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение контента (текст или фото)"""
    text = update.message.text
    photo = update.message.photo
    caption = update.message.caption
    
    # Check for cancel via text
    if text == "← Отмена":
        await admin_panel(update, context)
        return ConversationHandler.END
        
    context.user_data["newsletter_type"] = "text"
    context.user_data["newsletter_content"] = ""
    
    if photo:
        context.user_data["newsletter_type"] = "photo"
        context.user_data["newsletter_photo_id"] = photo[-1].file_id
        context.user_data["newsletter_content"] = caption or "" # Caption is the text
        
        await update.message.reply_photo(
            photo=photo[-1].file_id,
            caption=f"📢 *Предпросмотр:*\n\n{caption or ''}\n\nОтправить всем?",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["✅ Отправить", "✏️ Изменить"], ["← Отмена"]], resize_keyboard=True)
        )
    else:
        # Text only
        if not text:
             await update.message.reply_text("⚠ Пожалуйста, отправьте текст или фото.", reply_markup=ReplyKeyboardMarkup([["← Отмена"]], resize_keyboard=True))
             return ADMIN_NEWSLETTER_TEXT

        context.user_data["newsletter_type"] = "text"
        context.user_data["newsletter_content"] = text
        
        await update.message.reply_text(
            f"📢 *Предпросмотр:*\n\n{text}\n\nОтправить всем?",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([["✅ Отправить", "✏️ Изменить"], ["← Отмена"]], resize_keyboard=True)
        )
        
    return ADMIN_NEWSLETTER_CONFIRM

async def admin_newsletter_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "← Отмена":
        await admin_panel(update, context)
        return ConversationHandler.END
        
    if text == "✏️ Изменить":
        await update.message.reply_text("Отправьте новый текст или фото:", reply_markup=ReplyKeyboardMarkup([["← Отмена"]], resize_keyboard=True))
        return ADMIN_NEWSLETTER_TEXT
        
    if text == "✅ Отправить":
        msg_type = context.user_data.get("newsletter_type", "text")
        content = context.user_data.get("newsletter_content", "")
        photo_id = context.user_data.get("newsletter_photo_id")
        
        users = UserRepository.get_all_ids()
        count = 0
        errors = 0
        
        status_msg = await update.message.reply_text(f"⏳ Рассылка для {len(users)} пользователей...")
        
        for uid in users:
            try:
                if msg_type == "photo" and photo_id:
                    await context.bot.send_photo(chat_id=uid, photo=photo_id, caption=content, parse_mode="Markdown")
                else:
                    await context.bot.send_message(chat_id=uid, text=content, parse_mode="Markdown")
                count += 1
            except Exception as e:
                errors += 1
                logger.error(f"Failed to send to {uid}: {e}")
        
        await status_msg.edit_text(
            f"✅ *Рассылка завершена!*\n\n"
            f"📬 Отправлено: {count}\n"
            f"❌ Ошибок: {errors}",
            parse_mode="Markdown"
        )
        
        # Add a small delay or just show admin panel again
        await admin_panel(update, context)
        return ConversationHandler.END
        
    # If text matches nothing (unexpected input)
    await update.message.reply_text("⚠ Неизвестная команда. Нажмите '✅ Отправить' или '← Отмена'.")
    return ADMIN_NEWSLETTER_CONFIRM

# ============= MAIN =============

def main():
    # Настройка логирования
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # ConversationHandler для бронирования
    booking_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📅 Забронировать$"), book_start),
            MessageHandler(filters.Regex("Забронировать"), book_start)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            DATE: [CallbackQueryHandler(get_date, pattern="^date_")],
            TIME: [CallbackQueryHandler(get_time, pattern="^time_")],
            PARTY_SIZE: [CallbackQueryHandler(get_party_size, pattern="^party_")],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)],
            CONSENT: [CallbackQueryHandler(get_consent, pattern="^(agree|cancel_consent)$")],
            CONFIRMATION: [CallbackQueryHandler(confirm_booking, pattern="^(confirm|cancel)$")],
        },
        fallbacks=[
            MessageHandler(filters.Regex("Отмена"), start),
            MessageHandler(filters.Regex("Назад"), start),
            CommandHandler("adminnoble", admin_panel),
            # Fallback для кнопок главного меню
            MessageHandler(filters.Regex("^(📅 Забронировать|🌐 Сайт|📞 Контакты|⭐ Оставить отзыв)$"), start)
        ],
    )

    # ConversationHandler для отзывов
    review_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("Отзыв управляющему"), review_start),
            MessageHandler(filters.Regex("^💬 Отзыв управляющему$"), review_start)
        ],
        states={
            REVIEW_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_review_text)],
            REVIEW_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_review_contact)],
        },
        fallbacks=[
            MessageHandler(filters.Regex("Отмена"), start),
            MessageHandler(filters.Regex("Пропустить"), get_review_contact),
            CommandHandler("adminnoble", admin_panel),
            # Fallback для кнопок главного меню
            MessageHandler(filters.Regex("^(📅 Забронировать|🌐 Сайт|📞 Контакты|⭐ Оставить отзыв)$"), start)
        ],
    )

    # ConversationHandler для управления админами
    admin_manage_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("Управление админами"), admin_manage_start)
        ],
        states={
            ADMIN_CHOICE: [
                MessageHandler(filters.Regex("Добавить админа"), admin_choice_add),
                MessageHandler(filters.Regex("Удалить админа"), admin_choice_del),
                MessageHandler(filters.Regex("Назад"), admin_back)
            ],
            ADMIN_INPUT_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_perform_add)],
            ADMIN_INPUT_DEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_perform_del)],
        },
        fallbacks=[
            MessageHandler(filters.Regex("Назад"), admin_back),
            MessageHandler(filters.Regex("Отмена"), admin_manage_start),
            CommandHandler("adminnoble", admin_panel)
        ],
    )
    
    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("adminnoble", admin_panel))
    
    # ConversationHandler для рассылки
    admin_newsletter_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📢 Рассылка$"), admin_newsletter_start)],
        states={
            ADMIN_NEWSLETTER_TEXT: [MessageHandler(filters.TEXT | filters.PHOTO, admin_newsletter_get_content)],
            ADMIN_NEWSLETTER_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_newsletter_confirm)],
        },
        fallbacks=[
             MessageHandler(filters.Regex("Отмена"), admin_back),
             CommandHandler("adminnoble", admin_panel)
        ]
    )

    # Сначала ConversationHandlers
    application.add_handler(booking_conv)
    application.add_handler(review_conv)
    application.add_handler(admin_manage_conv)
    application.add_handler(admin_newsletter_conv)
    

    
    # Админские действия (перед общим меню)
    application.add_handler(MessageHandler(filters.Regex("^📥 Скачать брони$"), admin_download_csv))
    application.add_handler(MessageHandler(filters.Regex("^📥 Скачать отзывы$"), admin_download_reviews))
    application.add_handler(MessageHandler(filters.Regex("^📅 Актуальные брони$"), admin_show_bookings))
    application.add_handler(MessageHandler(filters.Regex("^💬 Просмотр отзывов$"), admin_reviews_list))
    
    # application.add_handler(MessageHandler(filters.Regex("Отзывы управляющему"), admin_reviews_list)) # Старое удаляем, теперь через меню
    
    application.add_handler(MessageHandler(filters.Regex("Выход"), start))
    application.add_handler(MessageHandler(filters.Regex("Управление админами"), admin_manage_start))

    # Кнопка "Назад в меню" (перед общим меню, чтобы точно сработала)
    application.add_handler(MessageHandler(filters.Regex("Назад в меню"), start))
    
    # Общее меню (в конце)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
