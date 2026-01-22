import os

# ---------- BASIC APP CONFIG ----------
APP_NAME = "YouTube Downloader API"
APP_VERSION = "1.0.0"
DEBUG = False


# ---------- PROXY CONFIG ----------
# Example:
# export HTTP_PROXY="http://user:pass@ip:port"
# export HTTPS_PROXY="http://user:pass@ip:port"

HTTP_PROXY = os.environ.get("HTTP_PROXY")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY")

# Prefer HTTPS proxy if available
PROXY = HTTPS_PROXY or HTTP_PROXY


# ---------- COOKIES CONFIG ----------
# cookies.txt same directory me hona chahiye
COOKIE_FILE = "cookies.txt"

USE_COOKIES_IF_EXISTS = True


# ---------- YT-DLP BASE OPTIONS ----------
YDL_BASE_OPTS = {
    "quiet": True,
    "skip_download": True,
    "nocheckcertificate": True,
    "extractor_args": {
        "youtube": {
            # Android client = less bot checks
            "player_client": ["android"]
        }
    }
}


# ---------- FALLBACK ORDER ----------
# Order SAME hai jaisa aapne bola
FALLBACK_ORDER = [
    {"use_proxy": False, "use_cookies": False},  # 1️⃣ No cookies + No proxy
    {"use_proxy": True,  "use_cookies": False},  # 2️⃣ Proxy only
    {"use_proxy": False, "use_cookies": True},   # 3️⃣ Cookies only
    {"use_proxy": True,  "use_cookies": True},   # 4️⃣ Cookies + Proxy
]


# ---------- METADATA ----------
JOIN_CHANNEL = "@ProXBotz on Telegram"
SUPPORT_USER = "@ProBotUpdate"
