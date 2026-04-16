# ──────────────────────────────────────────────
# AnyDLBot – Production Docker Image
# Base: python:3.11-slim (lighter, no GUI deps)
# ──────────────────────────────────────────────
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies:
#   ffmpeg        – required for video splitting, screenshots and audio extraction
#   gcc / python3-dev – required to compile tgcrypto (C extension)
#   wget / ca-certificates – HTTPS support
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        wget \
        ca-certificates \
        gcc \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies first (layer-cache friendly)
COPY requirements.txt .

# Install Python dependencies
# gcc is needed here to compile tgcrypto; we keep the compiler in the image
# because slim base images don't ship it by default.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Create the downloads directory the bot expects
RUN mkdir -p DOWNLOADS

# The bot reads config from environment variables at runtime.
# Pass TG_BOT_TOKEN, APP_ID, API_HASH etc via "docker run -e" or docker-compose.
CMD ["python", "bot.py"]
