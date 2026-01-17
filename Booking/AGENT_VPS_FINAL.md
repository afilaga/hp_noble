# 🚀 HookahPlace Noble: Final System Report

**Date**: 2026-01-18
**Status**: n8n Migration Complete | Python Backend Deprecated
**Main Domains**: `hpnoble.ru` (Site) | `whooks.filatiev.pro` (n8n API)

---

## 🌍 Infrastructure Overview

| Component | Detail |
|-----------|--------|
| **Frontend (Reg.ru)** | `https://hpnoble.ru` |
| **Backend (n8n)** | `https://whooks.filatiev.pro/webhook/` |
| **Server** | `178.20.211.174` (Running n8n) |
| **Database** | SQLite (`/var/lib/n8n/reservations.db`) |
| **Old Python API** | **DEPRECATED & STOPPED** |

---

## 🛠 Service Management (n8n)

The entire backend logic (API + Bot) is now handled by **n8n workflows**.

### n8n Service
- **Control**: `sudo systemctl [start|stop|restart|status] n8n` (or `pm2 restart n8n`)
- **Logs**: `journalctl -u n8n -f` (or via n8n UI "Executions" tab)
- **Workflows**:
    1. **Telegram Bot**: Handles `/start`, `/book` dialogs.
    2. **REST API**: Handles website requests.

### 🛑 Deprecated Services
The following services should be **stopped/disabled**:
- `hp-api.service`
- `hp-bot.service`

---

## 💾 Database Details (SQLite)
- **Path**: `/var/lib/n8n/reservations.db`
- **Tables**: `reservations`, `tables`, `customers`, `reviews`, `conversation_states`
- **Management**: Use `sqlite3` CLI on VPS or n8n nodes.

---

## 🔌 API Endpoints (Webhooks)

All API calls from the frontend now go to `https://whooks.filatiev.pro/webhook/...`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tables` | Get all tables |
| `GET` | `/tables/available` | Get available tables (params: `party_size`, `date`, `time`) |
| `GET` | `/reservations` | Get active reservations |
| `POST` | `/reservation/create` | Create new reservation |
| `POST` | `/reservation/confirm` | Confirm reservation |
| `POST` | `/reservation/cancel` | Cancel reservation |

---

## 📝 Key Configurations

1. **n8n Env**: Credentials & DB path are configured in n8n (or `.env` if using Docker/custom setup).
2. **Frontend Config**: Update `VITE_API_BASE` in frontend to `https://whooks.filatiev.pro/webhook`.
3. **Telegram Webhook**: Pointed to `https://whooks.filatiev.pro/webhook/central-bistro-bot`.

---

## ✅ Health Check
- **API**: `curl https://whooks.filatiev.pro/webhook/tables` (Should return JSON list of tables)
- **Bot**: Send `/start` to `@hp_noble_bot`
