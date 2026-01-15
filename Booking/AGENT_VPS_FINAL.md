# 🚀 HookahPlace Noble: Backend & Infrastructure Report

**Date**: 2026-01-15
**Server**: `178.20.211.174` (Ubuntu 24.04 LTS)
**Architecture**: GitHub -> GitHub Actions -> VPS (HAProxy -> Nginx -> FastAPI)

---

## 🌍 Infrastructure Overview

| Component | Detail |
|-----------|--------|
| **API Domain** | `https://api.hpnoble.ru` |
| **API Port** | `8000` (internal) |
| **Proxy Port** | `8448` (Nginx to HAProxy) |
| **Database** | MariaDB (Local on VPS) |
| **Base Dir** | `/home/andrey/apps/noble-booking` |
| **Python** | 3.12 (Venv: `./venv`) |

---

## 🛠 Service Management

### API (FastAPI)
- **Service**: `hp-api.service`
- **Control**: `sudo systemctl [start|stop|restart|status] hp-api`
- **Logs**: `sudo journalctl -u hp-api -f`

### Telegram Bot
- **Service**: `hp-bot.service`
- **Control**: `sudo systemctl [start|stop|restart|status] hp-bot`
- **Logs**: `sudo journalctl -u hp-bot -f`

---

## 💾 Database Details (MariaDB)
- **DB Name**: `reservations`
- **User**: `noble`
- **Host**: `localhost`
- **Password**: *stored in `/home/andrey/apps/noble-booking/src/.env`*

---

## 🔄 CI/CD Workflow (Auto-deploy)
The system is configured for automatic deployment via GitHub Actions.
1. **Trigger**: Push to `main` branch (path `Booking/**`).
2. **Action**: SSH into VPS -> run `/home/andrey/apps/noble-booking/Booking/deploy/deploy_vps.sh`.
3. **Secret**: `SSH_PRIVATE_KEY` in GitHub repo (RSA 4096).

---

## 📝 Instructions for Future Agents

1. **Environment Variables**: Always edit `.env` in `/home/andrey/apps/noble-booking/src/.env`.
2. **SSL**: Managed by Certbot. To renew: `sudo certbot renew`.
3. **CORS**: If the frontend domain changes, update `CORS_ORIGINS` in `.env`.
4. **Proxy Chain**: 
   - External (443) -> **HAProxy** (mode tcp) 
   - HAProxy -> **Nginx** (port 8448, SSL termination)
   - Nginx -> **Uvicorn** (port 8000)

---

## ✅ Health Check
- API: `curl https://api.hpnoble.ru/api/health`
- Expected: `{"status":"ok","service":"HookahPlace Noble API"}`
