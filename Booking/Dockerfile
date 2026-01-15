FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if any needed for sqlite or others)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create data directory for volume mount
RUN mkdir -p /app/data

# Expose API port
EXPOSE 8000

# Command to run both Bot and API
# We use a shell script trick to run both in parallel. 
# Ideally, they should be separate containers, but for simplicity in this phase, we run them together.
CMD ["sh", "-c", "python3 src/bot.py & uvicorn src.api:app --host 0.0.0.0 --port 8000"]
