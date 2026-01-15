import sqlite3
import os

DB_PATH = "reservations.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("База данных не найдена.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Начинаю миграцию...")
    
    try:
        # 1. Переименовываем старую таблицу
        cursor.execute("ALTER TABLE reservations RENAME TO reservations_old")
        print("Старая таблица переименована в reservations_old")
        
        # 2. Создаем новую таблицу
        # Берем SQL из обновленного database.py (копирую сюда для надежности)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                table_id TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                party_size INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                special_requests TEXT,
                source TEXT DEFAULT 'bot',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TEXT,
                seated_at TEXT,
                completed_at TEXT,
                cancelled_at TEXT,
                cancellation_reason TEXT
            )
        """)
        print("Новая таблица reservations создана")
        
        # 3. Копируем данные
        # У старой таблицы table_id был NOT NULL, так что все ок.
        # Список колонок должен совпадать.
        cursor.execute("""
            INSERT INTO reservations (
                id, customer_id, table_id, start_time, end_time, party_size, 
                status, special_requests, source, created_at, confirmed_at, 
                seated_at, completed_at, cancelled_at, cancellation_reason
            )
            SELECT 
                id, customer_id, table_id, start_time, end_time, party_size, 
                status, special_requests, source, created_at, confirmed_at, 
                seated_at, completed_at, cancelled_at, cancellation_reason
            FROM reservations_old
        """)
        print(f"Данные скопированы: {cursor.rowcount} строк")
        
        conn.commit()
        print("Миграция успешна!")
        
        # Опционально: удалить старую таблицу
        # cursor.execute("DROP TABLE reservations_old")
        
    except Exception as e:
        print(f"Ошибка миграции: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
