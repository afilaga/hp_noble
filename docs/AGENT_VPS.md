# Agent 1: VPS_OPS (Backend & Infrastructure)

**Focus**: Server `178.20.211.174`, Python, Docker, Logs.
**Work Directory**: `Site/Booking/`

## 📋 Context / Memory
- **Role**: Linux Sysadmin & Python Dev.
- **Key Files**:
    - `Booking/src/api.py` (Logic)
    - `Booking/deploy/deploy_vps.sh` (Action)
    - `Booking/.env` (Config)

## 🛠 Primary Commands
### 1. Deploy Updates
   ```bash
   ssh andrey@178.20.211.174 "bash /opt/noble-booking/Booking/deploy/deploy_vps.sh"
   ```

### 2. Check Logs
   ```bash
   ssh andrey@178.20.211.174 "journalctl -u noble-bot -f"
   ```

### 3. DB Migration
   *Execute SQL/Migrations via SSH or remote connection.*

## ⚠️ Operation Rules
- **Verify**: Always run `curl -I localhost:8000/api/health` after deployment.
- **Notify**: Inform HOSTING_OPS if API contracts change.
