# Docker Deployment Guide 🐳

This guide explains how to deploy the Booking System using Docker and Docker Compose.

## Prerequisites
- Docker installed on the server (`apt-get install docker.io docker-compose`).
- The project files uploaded to the server.

## Setup

1.  **Prepare Data Directory**:
    Docker will store the database in `./data/reservations.db`.
    If you have an existing database in `src/reservations.db`, **copy it to `data/`**:
    ```bash
    mkdir -p data
    cp src/reservations.db data/
    ```

2.  **Configuration**:
    Ensure `.env` exists with your tokens.

3.  **Run**:
    ```bash
    docker-compose up -d --build
    ```

## SSL Setup (First Run)

To get SSL certificates from Let's Encrypt for `hpnoble.ru`:

1.  **Download init script** (or run manually):
    Since we need to generate certs *before* Nginx can start with SSL config, follow this:

    ```bash
    # 1. Start Nginx only (comment out ssl_certificate lines in nginx/app.conf first OR use dummy certs)
    # EASIER WAY:
    curl -L https://raw.githubusercontent.com/wmnnd/nginx-certbot/master/init-letsencrypt.sh > init-letsencrypt.sh
    chmod +x init-letsencrypt.sh
    # Edit script to set domains=(hpnoble.ru www.hpnoble.ru) and email
    sudo ./init-letsencrypt.sh
    ```

    **Alternative (Manual Certbot)**:
    1.  Comment out the 443 server block in `nginx/app.conf`.
    2.  `docker-compose up -d nginx`
    3.  `docker-compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot -d hpnoble.ru -d www.hpnoble.ru`
    4.  Uncomment 443 block in `nginx/app.conf`.
    5.  `docker-compose restart nginx`

## Maintenance

-   **Logs**: `docker-compose logs -f`
-   **Restart**: `docker-compose restart`
-   **Update**:
    ```bash
    git pull
    docker-compose up -d --build
    ```
