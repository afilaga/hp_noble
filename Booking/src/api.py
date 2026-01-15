import logging
import os
import re
import httpx
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn
from dotenv import load_dotenv
from database import (
    ReservationRepository, 
    TableRepository, 
    init_db, 
    CustomerRepository,
    AdminRepository,
    ReviewRepository
)

# Загрузка переменных из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


# Инициализация приложения
app = FastAPI(title="HookahPlace Noble API", version="1.0.0")

# CORS (разрешаем запросы с сайта)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных при старте
@app.on_event("startup")
def startup_event():
    init_db()
    TableRepository.setup_default_tables()
    logger.info("Database initialized")


# --- Telegram Notifications ---

def guest_word(n: int) -> str:
    """Склонение слова 'гость'"""
    if n == 1:
        return "гость"
    elif 2 <= n <= 4:
        return "гостя"
    return "гостей"


async def notify_admins(message: str):
    """
    Отправка уведомления всем админам через Telegram Bot API.
    Использует список из .env и из таблицы admins в БД.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping notifications")
        return
    
    notified = set()
    
    # 1. Admins from ENV
    for admin_id in ADMIN_IDS:
        admin_id = admin_id.strip()
        if admin_id and admin_id not in notified:
            await send_telegram_message(admin_id, message)
            notified.add(admin_id)
    
    # 2. Admins from DB
    try:
        db_admins = AdminRepository.get_all()
        for admin in db_admins:
            aid = admin["telegram_id"]
            if aid and aid not in notified:
                await send_telegram_message(aid, message)
                notified.add(aid)
    except Exception as e:
        logger.error(f"Error fetching admins from DB: {e}")


async def send_telegram_message(chat_id: str, text: str):
    """Отправка сообщения через Telegram Bot API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Telegram API error for {chat_id}: {response.text}")
    except Exception as e:
        logger.error(f"Failed to notify admin {chat_id}: {e}")


# --- Models ---

class ReservationCreate(BaseModel):
    name: str
    phone: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    guests: int
    table_id: Optional[str] = None
    comment: Optional[str] = None


class SlotRequest(BaseModel):
    date: str  # YYYY-MM-DD
    guests: int


# --- Endpoints ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "HookahPlace Noble API"}


@app.get("/api/reservations")
def get_reservations():
    """Получение списка активных бронирований"""
    try:
        return ReservationRepository.get_active()
    except Exception as e:
        logger.error(f"Error fetching reservations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reservations/all")
def get_all_reservations():
    """История всех бронирований"""
    try:
        # Поскольку в репозитории нет get_all, возвращаем активные
        return ReservationRepository.get_active()
    except Exception as e:
        logger.error(f"Error fetching all reservations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reservations/download")
def download_reservations():
    """Скачать бронирования в CSV"""
    try:
        from fastapi.responses import Response
        csv_data = ReservationRepository.export_csv()
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=reservations.csv"}
        )
    except Exception as e:
        logger.error(f"Error downloading reservations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reviews")
def get_reviews():
    """Получение списка отзывов"""
    try:
        return ReviewRepository.get_all()
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reviews/download")
def download_reviews():
    """Скачать отзывы в CSV"""
    try:
        from fastapi.responses import Response
        csv_data = ReviewRepository.export_csv()
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=reviews.csv"}
        )
    except Exception as e:
        logger.error(f"Error downloading reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tables/available")
def get_available_tables_endpoint(date: str, time: str, party_size: int):
    """
    Получение списка доступных столов на конкретное время
    """
    try:
        guests = party_size
        start_dt_str = f"{date}T{time}:00"
        start_dt = datetime.fromisoformat(start_dt_str)
        end_dt = start_dt + timedelta(minutes=90)
        
        available_tables = TableRepository.get_available(
            party_size=guests,
            start_time=start_dt,
            end_time=end_dt
        )
        
        return available_tables
        
    except Exception as e:
        logger.error(f"Error fetching tables: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reservation/create")
async def create_reservation(data: ReservationCreate):
    """
    Создание бронирования с сайта.
    Уведомляет админов через Telegram.
    """
    try:
        # Валидация входных данных
        if not data.date or not data.time or not data.phone:
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Парсим дату/время
        start_dt_str = f"{data.date}T{data.time}:00"
        start_dt = datetime.fromisoformat(start_dt_str)
        
        # Определяем стол — автовыбор
        target_table_id = data.table_id
        
        # Если стол "any" или не указан, выбираем автоматически
        if not target_table_id or target_table_id == 'any':
            end_dt = start_dt + timedelta(minutes=90)
            available = TableRepository.get_available(
                party_size=data.guests,
                start_time=start_dt,
                end_time=end_dt
            )
            if not available:
                raise HTTPException(status_code=409, detail="Нет свободных столов на это время")
            target_table_id = available[0]["id"]
        
        # Создаем (или находим) клиента
        customer = CustomerRepository.get_or_create(data.name, data.phone)
        
        # Создаем бронь
        res_id = ReservationRepository.create(
            customer_id=customer["id"],
            table_id=target_table_id,
            start_time=start_dt,
            party_size=data.guests,
            comment=data.comment,
            source="website"  # Маркер, что бронь с сайта
        )
        
        logger.info(f"New website reservation: {res_id} for {data.name}")
        
        # Уведомление админам
        try:
            formatted_date = start_dt.strftime("%d.%m.%Y")
            formatted_time = start_dt.strftime("%H:%M")
            clean_phone = re.sub(r'[^\d+]', '', data.phone)
            
            await notify_admins(
                f"🔔 <b>Новая бронь (Сайт)</b>\n\n"
                f"👤 {data.name}\n"
                f"📞 <a href='tel:{clean_phone}'>{data.phone}</a>\n\n"
                f"📅 {formatted_date} в {formatted_time}\n"
                f"👥 {data.guests} {guest_word(data.guests)}\n"
                f"{f'💬 {data.comment}' if data.comment else ''}"
            )
        except Exception as e:
            logger.error(f"Notification error: {e}")
        
        return {
            "success": True, 
            "reservation_id": res_id, 
            "message": "Бронирование успешно создано"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating reservation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
