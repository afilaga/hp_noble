# 🤖 Agent Role: VPS_OPS (Backend & Infrastructure)

**Focus**: Server `178.20.211.174`, Automation via n8n.
**Work Directory**: `/home/andrey/apps/noble-booking` (Legacy/Backup)

## 📋 System Context
- **OS**: Ubuntu 24.04 LTS
- **Stack**: **n8n** (Node.js workflow automation), SQLite.
- **Domains**: 
  - API/Webhooks: `https://whooks.filatiev.pro`
- **Architecture**:
  - **n8n** handles all logic (Telegram Bot + REST API).
  - **SQLite** (`/var/lib/n8n/reservations.db`) stores data.
- **Legacy Python**: **DEPRECATED & STOPPED**.

## 🛠 Operation Rules
1. **n8n Management**:
   - Access: `https://whooks.filatiev.pro` (Web UI)
   - Restart: `sudo systemctl restart n8n` (or `pm2 restart n8n`)
   - Logs: `journalctl -u n8n -f` (or check "Executions" in UI)
2. **Workflows**:
   - **Telegram Bot**: Handles all chat interactions via Webhook.
   - **REST API**: Handles website booking requests via Webhooks.
3. **Database**: 
   - Path: `/var/lib/n8n/reservations.db`
   - Backup: Ensure this file is included in regular backups.

## ⚠️ Critical Configs
- **Env Vars**: Managed within n8n Credentials or system environment variables for n8n service.
- **Webhooks**: Ensure Frontend points to `https://whooks.filatiev.pro/webhook/...`.
- **Bot Token**: Configured in n8n Credentials (`Telegram Bot - Central Bistro`).

## 🔄 Emergency Procedures
### Bot Not Responding
1. Check n8n Executions log for errors.
2. Verify Webhook: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
3. Restart n8n: `sudo systemctl restart n8n`

## ✅ Verification
- **API Check**: `curl https://whooks.filatiev.pro/webhook/tables`
- **Bot Check**: Send `/start` to `@hp_noble_bot`
