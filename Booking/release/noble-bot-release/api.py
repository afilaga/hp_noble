import logging
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn
from database import ReservationRepository, TableRepository, init_db, CustomerRepository

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = FastAPI(title="HookahPlace Noble API", version="1.0.0")

# CORS (разрешаем запросы с сайта)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В продакшене лучше указать конкретный домен
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

# --- Models ---

class ReservationCreate(BaseModel):
    name: str
    phone: str
    date: str # YYYY-MM-DD
    time: str # HH:MM
    guests: int
    table_id: Optional[str] = None
    comment: Optional[str] = None

class SlotRequest(BaseModel):
    date: str # YYYY-MM-DD
    guests: int

# --- Endpoints ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "HookahPlace Noble API"}

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
@app.post("/api/reservations") # Support both paths
def create_reservation(data: ReservationCreate):
    """
    Создание бронирования с сайта.
    """
    try:
        # Валидация входных данных
        if not data.date or not data.time or not data.phone:
             raise HTTPException(status_code=400, detail="Missing required fields")

        # Парсим дату/время
        start_dt_str = f"{data.date}T{data.time}:00"
        start_dt = datetime.fromisoformat(start_dt_str)
        
        # Определяем стол
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
        # Исправляем вызов, так как ReservationRepository.create принимает customer_id, а не имя/телефон напрямую
        res_id = ReservationRepository.create(
            customer_id=customer["id"],
            table_id=target_table_id,
            start_time=start_dt,
            party_size=data.guests,
            comment=data.comment,
            source="website" # Маркер, что бронь с сайта
        )
        
        logger.info(f"New website reservation: {res_id} for {data.name}")
        
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
