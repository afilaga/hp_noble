# 🤖 Agent Role: VPS_OPS (Backend & Infrastructure)

**Focus**: Server `178.20.211.174`, CI/CD via GitHub, MariaDB, Nginx/HAProxy.
**Work Directory**: `/home/andrey/apps/noble-booking`

## 📋 System Context
- **OS**: Ubuntu 24.04 LTS
- **Stack**: FastAPI (Python 3.12), MariaDB, Telegram Bot (python-telegram-bot).
- **Domains**: 
  - API: `https://api.hpnoble.ru` (Internal port 8000)
  - Proxy Chain: HAProxy(443) -> Nginx(8448) -> Uvicorn(8000).
- **CI/CD**: Auto-deploy on `git push origin main` via GitHub Actions.

## 🛠 Operation Rules
1. **Deployment**: Prefer GitHub Push. If manual update is needed:
   `ssh andrey@178.20.211.174 "bash /home/andrey/apps/noble-booking/Booking/deploy/deploy_vps.sh"`
2. **Database**: MariaDB is local. Config is in `src/.env`.
3. **SSL**: Managed by Certbot on Nginx. HAProxy handles TCP passthrough via SNI.
4. **Logs**:
   - `sudo journalctl -u hp-api -f`
   - `sudo journalctl -u hp-bot -f`

## ⚠️ Critical Configs
- **CORS**: Must include `https://hpnoble.ru` in `src/.env`.
- **Nginx Config**: `/etc/nginx/sites-available/noble-api` (Listen 8448).
- **HAProxy Config**: `/etc/haproxy/haproxy.cfg` (SNI routing for api.hpnoble.ru).

## ✅ Verification
Always run: `curl https://api.hpnoble.ru/api/health` after changes.
