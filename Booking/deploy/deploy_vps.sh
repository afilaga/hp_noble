#!/bin/bash

# Configuration
APP_DIR="/home/andrey/apps/noble-booking"
VENV_DIR="$APP_DIR/venv"
SERVICE_BOT="hp-bot.service"
SERVICE_API="hp-api.service"

echo "🚀 Starting Deployment on VPS..."

# 1. Setup Virtual Environment
echo "🐍 Checking Python environment..."
cd $APP_DIR

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtualenv..."
    python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Setup Systemd Services
echo "⚙️ Configuring Systemd..."
sudo cp $APP_DIR/deploy/$SERVICE_BOT /etc/systemd/system/
sudo cp $APP_DIR/deploy/$SERVICE_API /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_BOT
sudo systemctl enable $SERVICE_API

# 3. Restart Services
echo "🔄 Restarting Services..."
sudo systemctl restart $SERVICE_BOT
sudo systemctl restart $SERVICE_API

echo "✅ Deployment Complete!"