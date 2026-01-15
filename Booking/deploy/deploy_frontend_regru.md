# Deployment Guide (Reg.ru + VPS)

Architecture:
- **Frontend** (React): Hosted on **Reg.ru** (Static files).
- **Backend** (FastAPI + Bot): Hosted on **VPS** (Python).
- **Database** (MySQL): Hosted on **Reg.ru** (Remote connection from VPS).

---

## 1. Database (Reg.ru)
Ensure your MySQL database is accessible from the VPS IP (`178.20.211.174`).

1. Log in to Reg.ru Hosting Panel.
2. Go to **MySQL** -> **Remote Access**.
3. Add IP: `178.20.211.174` (or `%` for testing, but strictly limit to VPS IP for security).

---

## 2. Backend (VPS)
**Server**: `178.20.211.174`
**Path**: `/opt/noble-booking` (Example)

### Initial Setup
1. **SSH into VPS**:
   ```bash
   ssh andrey@178.20.211.174
   ```
2. **Install Python/Git**:
   ```bash
   sudo apt update
   sudo apt install python3-venv git
   ```
3. **Setup Project**:
   ```bash
   git clone https://github.com/USERNAME/noble-hookahplace-sochi.git /opt/noble-booking
   cd /opt/noble-booking/Booking
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Configure Environment**:
   Create `.env` based on `.env.example`:
   ```bash
   nano src/.env
   ```
   *Fill in DB_HOST (31.31.197.32), DB_USER, DB_PASSWORD from your notes.*

5. **Run as Systemd Service**:
   Create `/etc/systemd/system/noble-bot.service`:
   ```ini
   [Unit]
   Description=Noble Hookah Bot & API
   After=network.target

   [Service]
   User=andrey
   WorkingDirectory=/opt/noble-booking/Booking/src
   Environment="PATH=/opt/noble-booking/Booking/venv/bin"
   ExecStart=/opt/noble-booking/Booking/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
   # Note: For bot+api in one process, you might need a different entry point or run separately.
   # Recommended: Run 'python bot.py' if bot logic includes API startup or use separate services.
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   **Enable**: `sudo systemctl enable --now noble-bot`

---

## 3. Frontend (Reg.ru)
1. **Build Locally**:
   ```bash
   npm run build
   ```
2. **Upload**:
   - Copy contents of `dist/` to your hosting folder (e.g., `www/hpnoble.ru`) via FTP or SCP.
   - Ensure the `VITE_API_BASE` in your local `.env` was set slightly differently. Since frontend is static, it needs to know where the API is.
     - **Important**: The API is on the VPS (`http://178.20.211.174:8000` or via domain `https://api.hpnoble.ru` if configured).
     - Update `.env` for frontend build:
       ```
       VITE_API_BASE=http://178.20.211.174:8000/api
       ```
     - Rebuild: `npm run build`
