# HookahPlace Noble Bot — Documentation 🤖

**Purpose:** This document serves as the **Single Source of Truth** for the HookahPlace Noble Telegram Bot (`bot.py`). Use this context to understand, modify, or debug the system.

---

## 1. Project Overview
*   **Name:** HookahPlace Noble Booking Bot
*   **Stack:** Python 3.10+, `python-telegram-bot` (v20+ async), SQLite3, `python-dotenv`.
*   **Path:** `/Users/andreyfilatiev/Documents/Hookah Place Noble/Site/модуль/`
*   **Main File:** `bot.py`
*   **Database:** `reservations.db` (SQLite)
*   **Design Philosophy:** Minimalist guest interface (inline buttons), robust error handling, persistent admin access.

---

## 2. File Structure

### `bot.py` (The Brain)
*   **Entry Point:** `main()`
*   **Handlers:**
    *   `CommandHandler("start", start)`: Main Menu.
    *   `CommandHandler("adminnoble", admin_panel)`: Hidden admin panel.
    *   **ConversationHandlers:**
        1.  `booking_conv`: Booking flow (Name -> Phone -> Date -> Time -> Guests -> Confirm).
        2.  `review_conv`: Feedback flow (Text -> Contact).
        3.  `admin_manage_conv`: Add/Remove admins.
*   **Key Logic:**
    *   **Booking:** Uses `InlineKeyboardMarkup` for Date/Time/Guests to prevent typos.
    *   **Validation:** Removes `ReplyKeyboardMarkup` before showing Inline calendars to avoid conflicts.
    *   **Admin Check:** `is_admin(user_id)` checks both `ADMIN_IDS` (env) and `admins` (DB).

### `database.py` (The Memory)
*   **Pattern:** Repository Pattern (Static methods).
*   **Tables:**
    1.  `reservations`:
        *   `id` (UUID), `customer_name`, `customer_phone`, `start_time` (ISO), `party_size`, `status` (pending/confirmed), `telegram_id`.
    2.  `admins`:
        *   `telegram_id` (PK, TEXT), `username`, `added_by`.
    3.  `reviews`:
        *   `id`, `user_name`, `contact`, `text`, `created_at`.
    4.  `telegram_users`:
        *   `telegram_id` (PK), `username`, `first_name`, `last_seen`. (Used for Newsletter).
*   **Classes:**
    *   `ReservationRepository`: `create`, `get_by_customer`.
    *   `AdminRepository`: `add`, `remove`, `get_all`, `is_admin_db`.
    *   `ReviewRepository`: `create`, `export_csv`.

### `.env` (Configuration)
```ini
TELEGRAM_BOT_TOKEN=...
ADMIN_IDS=113357472,123456789
```

---

## 3. Key Workflows

### A. Booking Flow (`booking_conv`)
1.  **Start:** User clicks "📅 Забронировать".
2.  **Entry Points:** Matches both "📅 Забронировать" (exact) and "Забронировать" (regex).
3.  **Input:** Name (Text) -> Phone (Text).
4.  **Transition:** Bot sends `ReplyKeyboardRemove()` -> Sends Inline Calendar. **Critical:** Do not remove the keyboard removal step, or the interface hangs.
5.  **Selection:** Date (Callback, includes "Today" + 13 days, Russian weekdays) -> Time (Callback) -> Guests (Callback).
6.  **Comment & Consent:** User adds comment (or skips).
7.  **Consent:** Bot asks for "Processing Personal Data" consent. Must click "Agree" to proceed.
8.  **Confirmation:** Shows summary.
9.  **End:** Saves to DB, shows "✅ Created", returns to Main Menu.
10. **Fallbacks:** Includes Main Menu buttons ("🌐 Сайт", etc.) to prevent hanging if user switches context mid-booking.

### B. Admin Panel (`/adminnoble`)
*   **Status:** Hidden command.
*   **Access:**
    *   `/adminnoble` command.
    *   Works safely inside flows (Booking, Review) as a fallback.
*   **Features:**
    *   **Bookings:** "📅 Актуальные брони" (shows upcoming bookings list, including 'seated').
    *   **Reviews:** "💬 Просмотр отзывов" (shows last 5) + "📥 Скачать отзывы" (CSV export).
    *   **Exports:** "📥 Скачать брони" (CSV export of all reservations).
    *   **Access:** "👥 Управление админами" (Dynamic DB table).
    *   **Newsletter:** "📢 Рассылка" (Send text/photo to all bot users from `telegram_users`).
*   **Notifications:**
    *   Admins (from ENV and DB) receive instant PM from bot on **New Booking** and **New Review**.
    *   Notifications contain clickable phone links (`tel:...`) and direct Telegram links (`tg://user...`).

### C. Link Formats
*   **Site:** Plain text `https://...` (for readability).
*   **Reviews:** Hyperlinks `[Text](url)` (to keep it short).
*   **Phones:** Clickable `[Phone](tel:...)`.

---

## 4. Common Issues & Solutions
*   **"Bot Hangs after Phone"**: Ensure `ReplyKeyboardRemove()` is sent *before* `InlineKeyboardMarkup`.
*   **"Menu Buttons Don't Work in Booking"**: Ensure Main Menu regex patterns are added to `fallbacks` list in `ConversationHandler`.
*   **"Admin Command Ignored"**: Ensure `CommandHandler("adminnoble", ...)` is added to `fallbacks` of ALL `ConversationHandler`s.
*   **"Duplicate Main"**: Ensure only one `def main():` exists and is called under `if __name__ == "__main__":`.
*   **"Review Flow Hangs"**: Ensure notifications are wrapped in `try-except` blocks to prevent crashing the flow if an admin blocks the bot.

---

## 5. Deployment / Restart

We now use a unified script.

1.  **Script:** `bash deploy/deploy.sh`
2.  **What it does:**
    *   Installs dependencies from `requirements.txt`.
    *   Restarts systemd services (`noble-bot`, `noble-api`).
    *   Shows status.

**Manual Restart:**
```bash
systemctl restart noble-bot
# OR manually:
pkill -f "python3 bot.py"; python3 src/bot.py
```

---

## 6. Universal Backend (API)
*   **File:** `api.py`
*   **Purpose:** Bridge between Website and Database (FastAPI).
*   **Run:** `uvicorn api:app --reload` (Port 8000).
*   **Endpoints:**
    *   `GET /api/health`: Health check.
    *   `GET /api/slots?date=YYYY-MM-DD&guests=N`: Get available slots.
    *   `POST /api/reservations`: Create booking.
*   **Integration:**
    *   Bot and API share `reservations.db` (WAL mode safe).
    *   Bot uses `python-telegram-bot`, API uses `FastAPI` + `uvicorn`.

## 7. Future Roadmap
*   [x] Push notifications for Admins on new booking/review (IMPLEMETED).
*   [x] Newsletter mechanism (Broadcast to all users).
*   [x] Personal Data Consent step.
*   [ ] Dockerization (Phase 5).
*   [ ] "Blacklist" for no-show guests.
*   [ ] Web Admin Interface (via `api.py`).
