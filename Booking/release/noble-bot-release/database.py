import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from contextlib import contextmanager
import uuid
import threading
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "reservations.db")


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
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                telegram_id TEXT,
                visits_count INTEGER DEFAULT 0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tables (
                id TEXT PRIMARY KEY,
                number INTEGER NOT NULL UNIQUE,
                capacity INTEGER NOT NULL,
                location TEXT DEFAULT 'main',
                status TEXT DEFAULT 'available',
                features TEXT,
                min_time INTEGER DEFAULT 30,
                max_time INTEGER DEFAULT 120,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id TEXT PRIMARY KEY,
                user_name TEXT,
                user_contact TEXT,
                text TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS admins (
                telegram_id TEXT PRIMARY KEY,
                username TEXT,
                added_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                table_id TEXT, -- Убрали NOT NULL для брони без стола
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
                cancellation_reason TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (table_id) REFERENCES tables(id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_reservations_date ON reservations(start_time);
            CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
            CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
        """)


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class CustomerRepository:
    @staticmethod
    def create(
        name: str, phone: str, email: str = None, telegram_id: str = None
    ) -> str:
        customer_id = str(uuid.uuid4())[:8]
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO customers (id, name, phone, email, telegram_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (customer_id, name, phone, email, telegram_id),
            )
        return customer_id

    @staticmethod
    def get(customer_id: str) -> Optional[Dict]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE id = ?", (customer_id,)
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_phone(phone: str) -> Optional[Dict]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE phone = ?", (phone,)
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_or_create(name: str, phone: str, telegram_id: str = None) -> Dict:
        existing = CustomerRepository.get_by_phone(phone)
        if existing:
            if telegram_id and not existing.get("telegram_id"):
                with get_connection() as conn:
                    conn.execute(
                        "UPDATE customers SET telegram_id = ? WHERE id = ?",
                        (telegram_id, existing["id"]),
                    )
                    existing["telegram_id"] = telegram_id
            return existing
        customer_id = CustomerRepository.create(name, phone, telegram_id=telegram_id)
        return CustomerRepository.get(customer_id)

    @staticmethod
    def increment_visits(customer_id: str):
        with get_connection() as conn:
            conn.execute(
                "UPDATE customers SET visits_count = visits_count + 1 WHERE id = ?",
                (customer_id,),
            )

    @staticmethod
    def get_all(limit: int = 100) -> List[Dict]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM customers ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]


class TableRepository:
    @staticmethod
    def create(
        number: int, capacity: int, location: str = "main", features: List[str] = None
    ) -> str:
        table_id = str(uuid.uuid4())[:8]
        features_json = json.dumps(features or [])
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO tables (id, number, capacity, location, features)
                   VALUES (?, ?, ?, ?, ?)""",
                (table_id, number, capacity, location, features_json),
            )
        return table_id

    @staticmethod
    def get(table_id: str) -> Optional[Dict]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tables WHERE id = ?", (table_id,)
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_number(number: int) -> Optional[Dict]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tables WHERE number = ?", (number,)
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_all() -> List[Dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM tables ORDER BY number").fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_available(
        party_size: int, start_time: datetime, end_time: datetime
    ) -> List[Dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT t.* FROM tables t
                WHERE t.status = 'available'
                AND t.capacity >= ?
                AND t.id NOT IN (
                    SELECT r.table_id FROM reservations r
                    WHERE r.status NOT IN ('cancelled', 'no_show', 'completed')
                    AND r.start_time < ?
                    AND r.end_time > ?
                )
                ORDER BY t.capacity
            """,
                (party_size, end_time, start_time),
            ).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def update_status(table_id: str, status: str):
        with get_connection() as conn:
            conn.execute(
                "UPDATE tables SET status = ? WHERE id = ?", (status, table_id)
            )

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
        reservation_id = str(uuid.uuid4())[:8]
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Если передан комментарий, добавляем его в special_requests
        requests_list = special_requests or []
        if comment:
            requests_list.append(comment)
            
        # Для обратной совместимости сохраняем comment в отдельном поле, если бы оно было
        # но сейчас пишем в special_requests как JSON
        special_json = json.dumps(requests_list)

        with get_connection() as conn:
            conn.execute(
                """INSERT INTO reservations
                   (id, customer_id, table_id, start_time, end_time, party_size, special_requests, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
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
                conn.execute(
                    "UPDATE tables SET status = 'reserved' WHERE id = ?", (table_id,)
                )

        CustomerRepository.increment_visits(customer_id)
        return reservation_id

    @staticmethod
    def get(reservation_id: str) -> Optional[Dict]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_with_details(reservation_id: str) -> Optional[Dict]:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT r.*, t.number as table_number, t.location, t.capacity as table_capacity,
                       c.name as customer_name, c.phone as customer_phone, c.email as customer_email
                FROM reservations r
                JOIN tables t ON r.table_id = t.id
                JOIN customers c ON r.customer_id = c.id
                WHERE r.id = ?
            """,
                (reservation_id,),
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_customer(customer_id: str) -> List[Dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT r.*, t.number as table_number, t.location
                FROM reservations r
                LEFT JOIN tables t ON r.table_id = t.id
                WHERE r.customer_id = ?
                ORDER BY r.start_time DESC
            """,
                (customer_id,),
            ).fetchall()
            
            results = []
            for row in rows:
                res = dict(row)
                if res.get("special_requests"):
                    try:
                        requests = json.loads(res["special_requests"])
                        if requests:
                            res["comment"] = requests[0]
                    except:
                        pass
                results.append(res)
            return results

    @staticmethod
    def get_upcoming(limit: int = 50) -> List[Dict]:
        now = datetime.now()
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT r.*, t.number as table_number, t.location, c.name as customer_name, c.phone as customer_phone
                FROM reservations r
                LEFT JOIN tables t ON r.table_id = t.id
                JOIN customers c ON r.customer_id = c.id
                WHERE r.start_time > ?
                AND r.status IN ('pending', 'confirmed')
                ORDER BY r.start_time
                LIMIT ?
            """,
                (now, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_today() -> List[Dict]:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT r.*, t.number as table_number, t.location, c.name as customer_name, c.phone as customer_phone
                FROM reservations r
                LEFT JOIN tables t ON r.table_id = t.id
                JOIN customers c ON r.customer_id = c.id
                WHERE r.start_time >= ? AND r.start_time < ?
                ORDER BY r.start_time
            """,
                (today, tomorrow),
            ).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_active() -> List[Dict]:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT r.*, t.number as table_number, t.location, c.name as customer_name
                FROM reservations r
                LEFT JOIN tables t ON r.table_id = t.id
                JOIN customers c ON r.customer_id = c.id
                WHERE r.status IN ('pending', 'confirmed', 'seated')
                ORDER BY r.start_time
            """).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def update_status(reservation_id: str, status: str):
        now = datetime.now().isoformat()
        with get_connection() as conn:
            conn.execute(
                f"""
                UPDATE reservations SET status = ?, {status}_at = ?
                WHERE id = ?
            """,
                (status, now, reservation_id),
            )

            if status in ("completed", "cancelled", "no_show"):
                res = ReservationRepository.get(reservation_id)
                if res:
                    conn.execute(
                        "UPDATE tables SET status = 'available' WHERE id = ?",
                        (res["table_id"],),
                    )

    @staticmethod
    def get_stats() -> Dict:
        with get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM reservations").fetchone()[0]
            completed = conn.execute(
                "SELECT COUNT(*) FROM reservations WHERE status = 'completed'"
            ).fetchone()[0]
            cancelled = conn.execute(
                "SELECT COUNT(*) FROM reservations WHERE status = 'cancelled'"
            ).fetchone()[0]
            no_show = conn.execute(
                "SELECT COUNT(*) FROM reservations WHERE status = 'no_show'"
            ).fetchone()[0]
            pending = conn.execute(
                "SELECT COUNT(*) FROM reservations WHERE status = 'pending'"
            ).fetchone()[0]
            confirmed = conn.execute(
                "SELECT COUNT(*) FROM reservations WHERE status = 'confirmed'"
            ).fetchone()[0]

            return {
                "total": total,
                "completed": completed,
                "cancelled": cancelled,
                "no_show": no_show,
                "pending": pending,
                "confirmed": confirmed,
                "completion_rate": round(completed / total * 100, 2)
                if total > 0
                else 0,
            }

    @staticmethod
    def get_by_date_range(start: datetime, end: datetime) -> List[Dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT r.*, t.number as table_number, c.name as customer_name, c.phone as customer_phone
                FROM reservations r
                JOIN tables t ON r.table_id = t.id
                JOIN customers c ON r.customer_id = c.id
                WHERE r.start_time >= ? AND r.start_time < ?
                ORDER BY r.start_time
            """,
                (start, end),
            ).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_for_reminder(hours_before: int = 24) -> List[Dict]:
        now = datetime.now()
        target = now + timedelta(hours=hours_before)
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT r.*, t.number as table_number, c.name as customer_name, c.phone as customer_phone, c.telegram_id
                FROM reservations r
                JOIN tables t ON r.table_id = t.id
                JOIN customers c ON r.customer_id = c.id
                WHERE r.status = 'confirmed'
                AND r.start_time > ?
                AND r.start_time <= ?
            """,
                (now, target),
            ).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def export_csv() -> str:
        """Export reservations to CSV string"""
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(["ID", "Date", "Time", "Guests", "Name", "Phone", "Status", "Source", "Comment"])
        
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT 
                    r.id, r.start_time, r.party_size, r.status, r.source, r.special_requests,
                    c.name, c.phone
                FROM reservations r
                LEFT JOIN customers c ON r.customer_id = c.id
                ORDER BY r.start_time DESC
            """).fetchall()
            
            for row in rows:
                try:
                    start_dt = datetime.fromisoformat(row["start_time"])
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
        
        return output.getvalue()
init_db()
TableRepository.setup_default_tables()

class ReviewRepository:
    @staticmethod
    def create(user_name: str, user_contact: str, text: str) -> str:
        review_id = str(uuid.uuid4())[:8]
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO reviews (id, user_name, user_contact, text) VALUES (?, ?, ?, ?)",
                (review_id, user_name, user_contact, text),
            )
        return review_id

    @staticmethod
    def get_all(limit: int = 50) -> List[Dict]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM reviews ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def export_csv() -> str:
        """Export reviews to CSV string"""
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(["ID", "Date", "Name", "Contact", "Text"])
        
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM reviews ORDER BY created_at DESC").fetchall()
            for row in rows:
                writer.writerow([
                    row["id"][:8],
                    row["created_at"],
                    row["user_name"],
                    row["user_contact"],
                    row["text"]
                ])
        
        return output.getvalue()

class AdminRepository:
    @staticmethod
    def add(telegram_id: str, username: str = None, added_by: str = None):
        with get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO admins (telegram_id, username, added_by) VALUES (?, ?, ?)",
                (str(telegram_id), username, added_by),
            )
            
    @staticmethod
    def remove(telegram_id: str):
        with get_connection() as conn:
            conn.execute("DELETE FROM admins WHERE telegram_id = ?", (str(telegram_id),))
            
    @staticmethod
    def get_all() -> List[Dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM admins ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]
            
    @staticmethod
    def is_admin_db(telegram_id: str) -> bool:
        with get_connection() as conn:
            row = conn.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (str(telegram_id),)).fetchone()
            return row is not None
