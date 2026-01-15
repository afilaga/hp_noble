#!/bin/bash

# Configuration
APP_DIR="/opt/noble/booking" # Adjust to your actual server path if different

echo "🚀 Starting Docker Deployment..."

# 1. Update Code
# cd $APP_DIR
# git pull

# 2. Stop Legacy Services (if any) to free ports
echo "🛑 Stopping legacy systemd services..."
sudo systemctl stop noble-bot noble-api || true
sudo systemctl disable noble-bot noble-api || true

# 3. Build and Run Containers
echo "🐳 Building and Starting Containers..."
# Ensure data directory exists
mkdir -p data

# Run Compose
docker-compose up -d --build

# 4. Check Status
echo "📊 Checking Container Status..."
docker-compose ps

echo "✅ Deployment Complete! Site available at https://hpnoble.ru (after SSL init)"
