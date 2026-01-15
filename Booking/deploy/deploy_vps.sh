#!/bin/bash

# Configuration
APP_DIR="/home/andrey/apps/noble-booking"
VENV_DIR="$APP_DIR/venv"
SERVICE_BOT="hp-bot.service"
SERVICE_API="hp-api.service"

echo "🚀 Starting Deployment from GitHub..."

# 1. Update Code
cd $APP_DIR
echo "📂 Pulling latest code..."
git pull origin main

# 2. Setup/Update Virtual Environment
echo "🐍 Updating Python environment..."
# Backend is in Booking subfolder in this repo
cd $APP_DIR/Booking

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtualenv..."
    python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Setup Systemd Services (if changed)
echo "⚙️ Refreshing Systemd configs..."
sudo cp $APP_DIR/Booking/deploy/$SERVICE_BOT /etc/systemd/system/
sudo cp $APP_DIR/Booking/deploy/$SERVICE_API /etc/systemd/system/

sudo systemctl daemon-reload

# 4. Restart Services
echo "🔄 Restarting Services..."
sudo systemctl restart $SERVICE_BOT
sudo systemctl restart $SERVICE_API

echo "✅ Deployment Complete!"
