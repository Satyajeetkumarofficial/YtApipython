# ==============================
# App Info
# ==============================

APP_NAME = "YouTube Downloader API"
APP_VERSION = "2.0"

# ==============================
# Cookies / Proxy
# ==============================

COOKIE_FILE = "cookies.txt"   # cookies.txt must exist in root
USE_PROXY = False             # default False

# ==============================
# Branding
# ==============================

JOIN_CHANNEL = "@ProXBotz on Telegram"
SUPPORT_USER = "@ProBotUpdate"
# ==============================
# yt-dlp Base Options
# ==============================

YDL_BASE_OPTS = {
    "quiet": True,
    "skip_download": True,
    "nocheckcertificate": True,
    "extractor_retries": 3,
    "socket_timeout": 15,
}
