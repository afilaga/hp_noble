# 🚀 Deployment Guide

This folder contains everything needed to deploy the **HookahPlace Noble** Booking System (Bot + API) to a Linux VPS (Ubuntu/Debian recommended).

## 1. Preparation

1.  **Server:** Ensure you have a VPS with Python 3.10+ installed.
2.  **Directory:** Create a folder: `/opt/noble/booking`
3.  **Upload:** Upload all files from this folder to the server.

## 2. Setup

### A. Install Dependencies
```bash
cd /opt/noble/booking
pip3 install -r requirements.txt
```

### B. Configure Environment
Create a `.env` file (or rename `.env.example` if you had one, or use existing):
```bash
nano .env
```
Content:
```ini
TELEGRAM_BOT_TOKEN=your_token_here
ADMIN_IDS=123456,789012
```

### C. Install Services (Systemd)
We use `systemd` to keep the bot and API running in the background and restart them automatically on crash/reboot.

1.  **Copy Service Files:**
    ```bash
    cp hp-bot.service /etc/systemd/system/
    cp hp-api.service /etc/systemd/system/
    ```

2.  **Reload Daemon:**
    ```bash
    systemctl daemon-reload
    ```

3.  **Enable & Start:**
    ```bash
    systemctl enable hp-bot
    systemctl start hp-bot
    
    systemctl enable hp-api
    systemctl start hp-api
    ```

## 3. Maintenance

### Check Logs
*   **Bot:** `journalctl -u hp-bot -f`
*   **API:** `journalctl -u hp-api -f`

### Update
Run the included script:
```bash
bash deploy.sh
```

### Ports
*   **API** runs on port `8000`. Ensure your firewall allows it if accessing externally.
*   **Bot** connects to Telegram servers (outbound), no incoming ports needed for polling.

## 4. Troubleshooting
*   **"Address already in use"**: The API port 8000 might be taken. Change `--port 8000` in `hp-api.service`.
*   **Permission Denied**: Ensure the `deploy.sh` is executable: `chmod +x deploy.sh`.
