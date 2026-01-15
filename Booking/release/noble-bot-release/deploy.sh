#!/bin/bash

# Configuration
APP_DIR="/opt/noble/booking"
REPO_URL="YOUR_REPO_URL_HERE" # Update this manually or via git config

echo "🚀 Starting Deployment..."

# 1. Update Code
# Assuming we are already in the git repo or need to pull
# git pull origin main

# 2. Update Dependencies
echo "📦 Installing Dependencies..."
pip3 install -r requirements.txt

# 3. Reload Systemd
echo "🔄 Reloading Services..."
# Copy service files if they changed (uncomment if you want to auto-update services)
# cp hp-bot.service /etc/systemd/system/
# cp hp-api.service /etc/systemd/system/
# systemctl daemon-reload

# 4. Restart Services
systemctl restart hp-bot
systemctl restart hp-api

# 5. Check Status
systemctl status hp-bot --no-pager
systemctl status hp-api --no-pager

echo "✅ Deployment Complete!"
