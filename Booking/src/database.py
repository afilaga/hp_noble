import mysql.connector
from mysql.connector import pooling
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from contextlib import contextmanager
import uuid
import threading
import os
import logging

# Configuration from ENV
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "reservations")

logger = logging.getLogger(__name__)

# Connection Pool
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="noble_pool",
        pool_size=5,
        pool_reset_session=True,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        autocommit=True
    )
except Exception as e:
    logger.error(f"Error creating connection pool: {e}")
    connection_pool = None

class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SEATED = "seated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class TableStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"

def init_db():
    """Initialize MySQL database schema"""
    # Note: We assume the DB_NAME already exists on the server.
    # If not, we'd need to connect without DB_NAME and create it.
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                email VARCHAR(255),
                telegram_id VARCHAR(100),
                visits_count INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tables (
                id VARCHAR(36) PRIMARY KEY,
                number INTEGER NOT NULL,
                capacity INTEGER NOT NULL,
                location VARCHAR(100) DEFAULT 'main',
                status VARCHAR(50) DEFAULT 'available',
                features TEXT,
                min_time INTEGER DEFAULT 30,
                max_time INTEGER DEFAULT 120,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_number (number)
            )
        """)
        
        # Reviews
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id VARCHAR(36) PRIMARY KEY,
                user_name VARCHAR(255),
                user_contact VARCHAR(255),
                text TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Admins
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                telegram_id VARCHAR(100) PRIMARY KEY,
                username VARCHAR(255),
                added_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Telegram Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telegram_users (
                telegram_id VARCHAR(100) PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Reservations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id VARCHAR(36) PRIMARY KEY,
                customer_id VARCHAR(36) NOT NULL,
                table_id VARCHAR(36),
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                party_size INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                special_requests TEXT,
                source VARCHAR(50) DEFAULT 'bot',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at DATETIME,
                seated_at DATETIME,
                completed_at DATETIME,
                cancelled_at DATETIME,
                cancellation_reason TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (table_id) REFERENCES tables(id)
            )
        """)
        
        # Indexes
        cursor.execute("CREATE INDEX idx_reservations_date ON reservations(start_time)")
        cursor.execute("CREATE INDEX idx_reservations_status ON reservations(status)")
        cursor.execute("CREATE INDEX idx_customers_phone ON customers(phone)")
        
        cursor.close()

@contextmanager
def get_connection():
    if not connection_pool:
        raise Exception("Database connection pool not initialized")
    
    conn = connection_pool.get_connection()
    try:
        yield conn
    except Exception:
        # conn.rollback() # MySQL connector autocommit=True in pool
        raise
    finally:
        conn.close()

class CustomerRepository:
    @staticmethod
    def create(name: str, phone: str, email: str = None, telegram_id: str = None) -> str:
        customer_id = str(uuid.uuid4())
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO customers (id, name, phone, email, telegram_id)
                   VALUES (%s, %s, %s, %s, %s)""",
                (customer_id, name, phone, email, telegram_id),
            )
            cursor.close()
        return customer_id

    @staticmethod
    def get(customer_id: str) -> Optional[Dict]:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
            row = cursor.fetchone()
            cursor.close()
            return row

    @staticmethod
    def get_by_phone(phone: str) -> Optional[Dict]:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM customers WHERE phone = %s", (phone,))
            row = cursor.fetchone()
            cursor.close()
            return row

    @staticmethod
    def get_or_create(name: str, phone: str, telegram_id: str = None) -> Dict:
        existing = CustomerRepository.get_by_phone(phone)
        if existing:
            if telegram_id and not existing.get("telegram_id"):
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE customers SET telegram_id = %s WHERE id = %s",
                        (telegram_id, existing["id"]),
                    )
                    cursor.close()
                    existing["telegram_id"] = telegram_id
            return existing
        customer_id = CustomerRepository.create(name, phone, telegram_id=telegram_id)
        return CustomerRepository.get(customer_id)

    @staticmethod
    def increment_visits(customer_id: str):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE customers SET visits_count = visits_count + 1 WHERE id = %s",
                (customer_id,),
            )
            cursor.close()

class TableRepository:
    @staticmethod
    def create(number: int, capacity: int, location: str = "main", features: List[str] = None) -> str:
        table_id = str(uuid.uuid4())
        features_json = json.dumps(features or [])
        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO tables (id, number, capacity, location, features)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (table_id, number, capacity, location, features_json),
                )
            except mysql.connector.IntegrityError:
                # Handle duplicate number silently or update? For now, ignore
                pass
            cursor.close()
        return table_id

    @staticmethod
    def get_available(party_size: int, start_time: datetime, end_time: datetime) -> List[Dict]:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT t.* FROM tables t
                WHERE t.status = 'available'
                AND t.capacity >= %s
                AND t.id NOT IN (
                    SELECT r.table_id FROM reservations r
                    WHERE r.status NOT IN ('cancelled', 'no_show', 'completed')
                    AND r.start_time < %s
                    AND r.end_time > %s
                    AND r.table_id IS NOT NULL
                )
                ORDER BY t.capacity
                """,
                (party_size, end_time, start_time),
            )
            rows = cursor.fetchall()
            cursor.close()
            return rows
            
    @staticmethod
    def get_all() -> List[Dict]:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tables ORDER BY number")
            rows = cursor.fetchall()
            cursor.close()
            return rows

    @staticmethod
    def setup_default_tables():
        existing = TableRepository.get_all()
        if not existing:
            defaults = [
                (1, 2, "у окна", ["романтичное место"]),
                (2, 4, "основной зал", []),
                (3, 4, "основной зал", []),
                (4, 6, "основной зал", []),
                (5, 8, "VIP", ["отдельная комната"]),
                (6, 2, "терраса", ["на улице"]),
                (7, 4, "терраса", ["на улице"]),
            ]
            for number, capacity, location, features in defaults:
                TableRepository.create(number, capacity, location, features)

class ReservationRepository:
    @staticmethod
    def create(
        customer_id: str,
        table_id: Optional[str],
        start_time: datetime,
        party_size: int,
        duration_minutes: int = 90,
        special_requests: List[str] = None,
        comment: str = None,
        source: str = "bot",
    ) -> str:
        reservation_id = str(uuid.uuid4())
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        requests_list = special_requests or []
        if comment:
            requests_list.append(comment)
        special_json = json.dumps(requests_list)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO reservations
                   (id, customer_id, table_id, start_time, end_time, party_size, special_requests, source)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    reservation_id,
                    customer_id,
                    table_id,
                    start_time,
                    end_time,
                    party_size,
                    special_json,
                    source,
                ),
            )
            if table_id:
                cursor.execute(
                    "UPDATE tables SET status = 'reserved' WHERE id = %s", (table_id,)
                )
            cursor.close()

        CustomerRepository.increment_visits(customer_id)
        return reservation_id
        
    @staticmethod
    def get_active() -> List[Dict]:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, t.number as table_number, t.location, c.name as customer_name, c.phone as customer_phone
                FROM reservations r
                LEFT JOIN tables t ON r.table_id = t.id
                JOIN customers c ON r.customer_id = c.id
                WHERE r.status IN ('pending', 'confirmed', 'seated')
                ORDER BY r.start_time
            """)
            rows = cursor.fetchall()
            cursor.close()
            return rows

    @staticmethod
    def get_upcoming(limit: int = 50) -> List[Dict]:
        now = datetime.now()
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT r.*, t.number as table_number, t.location, c.name as customer_name, c.phone as customer_phone
                FROM reservations r
                LEFT JOIN tables t ON r.table_id = t.id
                JOIN customers c ON r.customer_id = c.id
                WHERE r.start_time > %s
                AND r.status IN ('pending', 'confirmed')
                ORDER BY r.start_time
                LIMIT %s
                """,
                (now, limit),
            )
            rows = cursor.fetchall()
            cursor.close()
            return rows
            
    @staticmethod
    def export_csv() -> str:
        """Export reservations to CSV string"""
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Date", "Time", "Guests", "Name", "Phone", "Status", "Source", "Comment"])
        
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    r.id, r.start_time, r.party_size, r.status, r.source, r.special_requests,
                    c.name, c.phone
                FROM reservations r
                LEFT JOIN customers c ON r.customer_id = c.id
                ORDER BY r.start_time DESC
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    # In MySQL, start_time is datetime object if using connector properly
                    # Check if it's str or datetime
                    if isinstance(row["start_time"], str):
                        start_dt = datetime.fromisoformat(row["start_time"])
                    else:
                        start_dt = row["start_time"]
                        
                    date_str = start_dt.strftime("%Y-%m-%d")
                    time_str = start_dt.strftime("%H:%M")
                    
                    comment = ""
                    if row["special_requests"]:
                        try:
                            reqs = json.loads(row["special_requests"])
                            if reqs: comment = reqs[0]
                        except: pass

                    writer.writerow([
                        row["id"][:8], date_str, time_str, row["party_size"],
                        row["name"], row["phone"], row["status"], row["source"], comment
                    ])
                except Exception:
                    continue
            cursor.close()
        
        return output.getvalue()


class ReviewRepository:
    @staticmethod
    def create(user_name: str, user_contact: str, text: str) -> str:
        review_id = str(uuid.uuid4())
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reviews (id, user_name, user_contact, text) VALUES (%s, %s, %s, %s)",
                (review_id, user_name, user_contact, text),
            )
            cursor.close()
        return review_id

    @staticmethod
    def get_all(limit: int = 50) -> List[Dict]:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM reviews ORDER BY created_at DESC LIMIT %s", (limit,)
            )
            rows = cursor.fetchall()
            cursor.close()
            return rows
            
    @staticmethod
    def export_csv() -> str:
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Date", "Name", "Contact", "Text"])
        
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")
            rows = cursor.fetchall()
            for row in rows:
                writer.writerow([
                    row["id"][:8], row["created_at"], row["user_name"], row["user_contact"], row["text"]
                ])
            cursor.close()
        return output.getvalue()

class AdminRepository:
    @staticmethod
    def add(telegram_id: str, username: str = None, added_by: str = None):
        with get_connection() as conn:
            cursor = conn.cursor()
            # MySQL INSERT IGNORE
            cursor.execute(
                "INSERT IGNORE INTO admins (telegram_id, username, added_by) VALUES (%s, %s, %s)",
                (str(telegram_id), username, added_by),
            )
            cursor.close()

    @staticmethod
    def remove(telegram_id: str):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admins WHERE telegram_id = %s", (str(telegram_id),))
            cursor.close()
            
    @staticmethod
    def get_all() -> List[Dict]:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins ORDER BY created_at DESC")
            rows = cursor.fetchall()
            cursor.close()
            return rows

    @staticmethod
    def is_admin_db(telegram_id: str) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM admins WHERE telegram_id = %s", (str(telegram_id),))
            row = cursor.fetchone()
            cursor.close()
            return row is not None

class UserRepository:
    @staticmethod
    def upsert(telegram_id: str, username: str = None, first_name: str = None):
        now = datetime.now() # MySQL DATETIME
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO telegram_users (telegram_id, username, first_name, last_active_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    username = VALUES(username),
                    first_name = VALUES(first_name),
                    last_active_at = VALUES(last_active_at)
                """,
                (str(telegram_id), username, first_name, now)
            )
            cursor.close()
