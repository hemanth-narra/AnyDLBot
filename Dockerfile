# ──────────────────────────────────────────────
# AnyDLBot – Production Docker Image
# Base: python:3.11-slim (lighter, no GUI deps)
# ──────────────────────────────────────────────
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies:
#   ffmpeg  – required for screenshot generation and audio extraction
#   wget    – used for downloading resources
#   ca-certs – HTTPS support
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        wget \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies first (layer-cache friendly)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Create the downloads directory the bot expects
RUN mkdir -p DOWNLOADS

# The bot reads config from environment variables at runtime.
# Pass TG_BOT_TOKEN, APP_ID, API_HASH etc via "docker run -e" or docker-compose.
CMD ["python", "bot.py"]
