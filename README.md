# AnyDLBot 🤖

A Telegram bot that downloads videos and files from **1000+ websites** (YouTube, Instagram, Twitter, and more) using [yt-dlp](https://github.com/yt-dlp/yt-dlp) and uploads them directly to Telegram — including automatic splitting of files larger than 2 GB.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Multi-site downloads** | All sites supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| **Format selection** | Choose video quality, audio-only MP3 (64/128/320 kbps), or raw file |
| **Large file support** | Files > ~2 GB are automatically split and uploaded as numbered parts |
| **Custom thumbnails** | Send any photo to the bot to set it as the thumbnail for the next upload |
| **Ban list** | Block specific users by Telegram ID (`BANNED_USERS`) |
| **YouTube cookies** | Mount a `cookies.txt` to bypass YouTube bot-detection / age restrictions |
| **Docker ready** | Single-command deployment via Docker Compose |

---

## 🤖 Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/help` or `/about` | Usage instructions |
| `/me` | Show your account info |
| `/deletethumbnail` | Remove your saved custom thumbnail |
| `/generatecustomthumbnail` | Merge two photos (sent as an album) into a custom thumbnail |

**To download a file:** simply send any URL. The bot replies with format/quality buttons.

**Custom filename:** `https://example.com/video | myfilename.mp4`  
**Premium login:** `https://example.com/video | filename.mp4 | username | password`

---

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 20.x
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2.x
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/AnyDLBot.git
cd AnyDLBot
```

---

### Step 2 — Create your environment file

```bash
cp .env.example .env
```

Open `.env` and fill in your values (see the [Environment Variables](#-environment-variable-reference) section below).

---

### Step 3 — Build and start

```bash
docker compose up -d --build
```

Check the logs:

```bash
docker compose logs -f
```

Stop the bot:

```bash
docker compose down
```

---

### Step 4 — (Optional) Set up YouTube cookies

YouTube increasingly blocks downloads from server IPs with a **"Sign in to confirm you're not a bot"** error. The fix is to export your browser's YouTube cookies and give them to the bot.

#### Why cookies are needed

YouTube uses browser fingerprinting to detect automated bots. When you're logged into YouTube in your browser, your cookies prove you're a real user. Passing these cookies to yt-dlp lets it authenticate as you.

#### Step-by-step: Export cookies from your browser

> ⚠️ **Do this on your local machine** (laptop/desktop), not on the server. You need a browser logged into YouTube.

**Option A — Automatic export via yt-dlp (easiest)**

```bash
# Install yt-dlp locally if you haven't already
pip install yt-dlp

# Export cookies straight from Chrome (close Chrome first on some systems)
yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Or from Firefox
yt-dlp --cookies-from-browser firefox --cookies cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Or from Edge
yt-dlp --cookies-from-browser edge --cookies cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

This creates a `cookies.txt` file in Netscape format.

**Option B — Browser extension**

Install one of these extensions, then export cookies for `youtube.com`:
- Chrome/Edge: [cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
- Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

#### Step-by-step: Activate cookies in Docker

**1. Copy `cookies.txt` to your server** (next to `docker-compose.yml`):

```bash
scp cookies.txt ubuntu@your-server:~/AnyDLBot/cookies.txt
```

**2. Add `YTDL_COOKIES_FILE` to your `.env` file** on the server:

```bash
# .env
YTDL_COOKIES_FILE=/app/cookies.txt
```

**3. Restart the bot:**

```bash
docker compose up -d
```

The `cookies.txt` file is already volume-mounted read-only at `/app/cookies.txt` in the default `docker-compose.yml`. No rebuild is needed.

> 💡 **Tip:** Cookies expire after a few weeks. If YouTube downloads start failing again, re-export `cookies.txt` and copy it back to the server — no rebuild needed, just `docker compose restart anydlbot`.

---

### Step 5 — Updating

```bash
git pull
docker compose up -d --build
```

---

## ⚙️ docker-compose.yml reference

```yaml
version: "3.9"

services:
  anydlbot:
    build: .
    container_name: anydlbot
    restart: unless-stopped
    environment:
      - TG_BOT_TOKEN=${TG_BOT_TOKEN}
      - APP_ID=${APP_ID}
      - API_HASH=${API_HASH}
      - BANNED_USERS=${BANNED_USERS:-}
      - HTTP_PROXY=${HTTP_PROXY:-}
      - CHUNK_SIZE=${CHUNK_SIZE:-128}
      - DEF_THUMB_NAIL_VID_S=${DEF_THUMB_NAIL_VID_S:-}
      - YTDL_COOKIES_FILE=${YTDL_COOKIES_FILE:-}   # Optional: /app/cookies.txt
      - WEBHOOK=1
    volumes:
      - ./DOWNLOADS:/app/DOWNLOADS          # Persists files across restarts
      - ./cookies.txt:/app/cookies.txt:ro   # Optional: YouTube cookies
```

> `restart: unless-stopped` means the bot restarts automatically after a server reboot or crash.

---

## 🐳 Manual `docker run` (without Compose)

```bash
# Build the image
docker build -t anydlbot .

# Run the container
docker run -d \
  --name anydlbot \
  --restart unless-stopped \
  -e TG_BOT_TOKEN="your_bot_token" \
  -e APP_ID="your_app_id" \
  -e API_HASH="your_api_hash" \
  -e WEBHOOK=1 \
  -v $(pwd)/DOWNLOADS:/app/DOWNLOADS \
  anydlbot
```

**Windows (PowerShell)** — replace `$(pwd)` with `${PWD}`:

```powershell
docker run -d `
  --name anydlbot `
  --restart unless-stopped `
  -e TG_BOT_TOKEN="your_bot_token" `
  -e APP_ID="your_app_id" `
  -e API_HASH="your_api_hash" `
  -e WEBHOOK=1 `
  -v ${PWD}/DOWNLOADS:/app/DOWNLOADS `
  anydlbot
```

---

## 🛠️ Local / Manual Installation (without Docker)

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your config file and edit it
cp sample_config.py config.py
nano config.py

# Run the bot (without WEBHOOK env var, reads from config.py)
python bot.py
```

---

## 🔑 Environment Variable Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `TG_BOT_TOKEN` | ✅ Yes | — | Your bot token from [@BotFather](https://t.me/BotFather) |
| `APP_ID` | ✅ Yes | — | Telegram App ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ Yes | — | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BANNED_USERS` | No | _(none)_ | Space-separated Telegram user IDs to permanently block |
| `HTTP_PROXY` | No | _(none)_ | Proxy URL for geo-restricted downloads (e.g. `socks5://127.0.0.1:1080`) |
| `CHUNK_SIZE` | No | `128` | Download chunk size in bytes |
| `DEF_THUMB_NAIL_VID_S` | No | _(none)_ | Fallback thumbnail URL when a video has no thumbnail |
| `YTDL_COOKIES_FILE` | No | _(none)_ | Path to a Netscape `cookies.txt` inside the container (e.g. `/app/cookies.txt`) — bypasses YouTube bot-detection |
| `WEBHOOK` | No | `0` | **Must be `1` in Docker** — tells the bot to load config from env vars |

> ⚠️ `AUTH_USERS` is present in `sample_config.py` but is **not enforced anywhere in the bot logic** — setting it has no effect. Leave it out of your `.env`.

---

## 🔍 Troubleshooting

### YouTube says "Sign in to confirm you're not a bot"

This is YouTube's bot-detection blocking server IPs. Fix: export your browser cookies and mount them into the container.

See **[Step 4 — Set up YouTube cookies](#step-4--optional-set-up-youtube-cookies)** for the full guide.

> 💡 Quick fix: `yt-dlp --cookies-from-browser chrome --cookies cookies.txt "<any youtube url>"` then `scp cookies.txt server:~/AnyDLBot/` and add `YTDL_COOKIES_FILE=/app/cookies.txt` to your `.env`.

### Bot doesn't respond to messages
- Verify `TG_BOT_TOKEN` is correct and the bot is not stopped.
- Check logs: `docker compose logs -f`
- Send `/start` to the bot in Telegram to confirm it's reachable.

### `WEBHOOK=1` not set — bot ignores environment variables
The bot uses `WEBHOOK` to decide whether to read from `config.py` or from env vars. Always set `WEBHOOK=1` when running in Docker or with environment variables.

### Pyrogram session errors on restart
Pyrogram stores a session file inside the container. To reset it:
```bash
docker compose down
# Remove the session file
docker compose up -d --build
```

### Download fails for a specific site
- Some sites require cookies or a login. Use the extended URL format:
  ```
  https://example.com/video | filename.mp4 | username | password
  ```
- For geo-restricted content, set `HTTP_PROXY`.

### Large file doesn't get split
- FFmpeg is installed automatically by the Dockerfile.
- Verify it's present inside the running container:
  ```bash
  docker exec -it anydlbot ffmpeg -version
  ```

---

## 📂 Project Structure

```
AnyDLBot/
├── bot.py                        # Entry point
├── config.py                     # Local config (not committed to git)
├── sample_config.py              # Config template / Docker config loader
├── translation.py                # All bot message strings
├── Dockerfile                    # Docker image build instructions
├── docker-compose.yml            # Docker Compose service definition
├── .env.example                  # Environment variable template
├── cookies.txt                   # YouTube cookies (optional, gitignored)
├── requirements.txt              # Python dependencies
├── plugins/
│   ├── youtube_dl_echo.py        # URL detection, yt-dlp info fetch & format buttons
│   ├── dl_button.py              # Download, split (>2 GB) & upload handler
│   ├── cb_buttons.py             # Inline button callback handler (yt-dlp downloads)
│   ├── custom_thumbnail.py       # Photo save & /deletethumbnail, /generatecustomthumbnail
│   └── help_text.py              # /start, /help, /me, /upgrade commands
└── helper_funcs/
    ├── display_progress.py       # Progress bar, humanbytes, TimeFormatter
    ├── help_Nekmo_ffmpeg.py      # FFmpeg helpers (screenshots, video trim)
    ├── help_uploadbot.py         # HTTP direct-download helper
    └── split_video.py            # Large file splitter (>~2 GB via ffmpeg segment)
```

---

## 📜 License

GNU General Public License v3.0 — see [COPYING](COPYING) for details.

---

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — the download engine powering this bot
- [Pyrogram](https://github.com/pyrogram/pyrogram) by [Dan Tès](https://telegram.dog/haskell) — Telegram MTProto client
- [@SpEcHlDe](https://telegram.dog/ThankTelegram) — original [AnyDLBot](https://telegram.dog/AnyDLBot) concept
