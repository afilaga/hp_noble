import sqlite3
from src.database import DB_PATH, UserRepository

def backfill():
    print(f"Connecting to DB at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get all customers with telegram_id
    rows = conn.execute("SELECT telegram_id, name, phone FROM customers WHERE telegram_id IS NOT NULL").fetchall()
    
    print(f"Found {len(rows)} customers with telegram_id")
    
    count = 0
    for row in rows:
        tid = row["telegram_id"]
        name = row["name"]
        # We don't have username easily, so we skip it or put name as first_name
        try:
            UserRepository.upsert(telegram_id=tid, first_name=name)
            count += 1
        except Exception as e:
            print(f"Error upserting {tid}: {e}")
            
    print(f"Successfully backfilled {count} users to telegram_users table.")
    conn.close()

if __name__ == "__main__":
    backfill()
