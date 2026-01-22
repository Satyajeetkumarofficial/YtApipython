# ==============================
# App Info
# ==============================

APP_NAME = "YouTube Downloader API"
APP_VERSION = "2.0"

# ==============================
# Cookies / Proxy
# ==============================

COOKIE_FILE = "cookies.txt"     # cookies.txt must exist
USE_PROXY = False               # default False

# ==============================
# Fallback Order (VERY IMPORTANT)
# ==============================

# 1 = No cookies, no proxy
# 2 = Proxy only
# 3 = Cookies only
# 4 = Cookies + Proxy

FALLBACK_ORDER = [
    {"cookie": False, "proxy": False},
    {"cookie": False, "proxy": True},
    {"cookie": True,  "proxy": False},
    {"cookie": True,  "proxy": True},
]

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
