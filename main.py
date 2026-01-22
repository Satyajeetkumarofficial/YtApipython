from fastapi import FastAPI, Query
import yt_dlp
import os

app = FastAPI(title="YouTube Downloader API (Advanced Fallback)")

# ---------- BASE CONFIG ----------

BASE_OPTS = {
    "quiet": True,
    "skip_download": True,
    "nocheckcertificate": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    }
}

PROXY = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
COOKIE_FILE = "cookies.txt"


def get_opts(use_proxy=False, use_cookies=False):
    opts = BASE_OPTS.copy()

    if use_proxy and PROXY:
        opts["proxy"] = PROXY

    if use_cookies and os.path.exists(COOKIE_FILE):
        opts["cookiefile"] = COOKIE_FILE

    return opts


# ---------- HELPERS ----------

def build_label(ext, height=None, abr=None):
    if height:
        return f"{ext} ({height}p)"
    if abr:
        return f"{ext} ({int(abr)}kb/s)"
    return ext


def extract_info_with_fallback(url: str):
    attempts = [
        ("no_cookie_no_proxy", get_opts()),
        ("proxy_only", get_opts(use_proxy=True)),
        ("cookies_only", get_opts(use_cookies=True)),
        ("cookies_and_proxy", get_opts(use_proxy=True, use_cookies=True)),
    ]

    last_error = None

    for mode, opts in attempts:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info, mode
        except Exception as e:
            last_error = f"{mode}: {e}"

    raise Exception(last_error)


# ---------- API ----------

@app.get("/fetch")
def fetch(url: str = Query(...)):
    try:
        info, mode = extract_info_with_fallback(url)

        video_with_audio = []
        video_only = []
        audio = []

        for f in info.get("formats", []):

            # 🎥 VIDEO + AUDIO (SEARCH ALL PROGRESSIVE)
            if (
                f.get("ext") == "mp4"
                and f.get("vcodec") != "none"
                and f.get("acodec") != "none"
                and not f.get("protocol", "").startswith("m3u8")
            ):
                video_with_audio.append({
                    "label": build_label("mp4", f.get("height")),
                    "type": "video_with_audio",
                    "width": f.get("width"),
                    "height": f.get("height"),
                    "extension": "mp4",
                    "fps": f.get("fps"),
                    "url": f.get("url"),
                })

            # 🎞 VIDEO ONLY
            if (
                f.get("ext") == "mp4"
                and f.get("vcodec") != "none"
                and f.get("acodec") == "none"
            ):
                video_only.append({
                    "label": build_label("mp4", f.get("height")),
                    "type": "video_only",
                    "width": f.get("width"),
                    "height": f.get("height"),
                    "extension": "mp4",
                    "fps": f.get("fps"),
                    "url": f.get("url"),
                })

            # 🔊 AUDIO ONLY
            if f.get("vcodec") == "none" and f.get("acodec") != "none":
                audio.append({
                    "label": build_label(f.get("ext"), abr=f.get("abr")),
                    "type": "audio",
                    "extension": f.get("ext"),
                    "bitrate": f.get("abr"),
                    "url": f.get("url"),
                })

        # ---------- SORTING ----------
        video_with_audio.sort(key=lambda x: x["height"] or 0, reverse=True)
        video_only.sort(key=lambda x: x["height"] or 0, reverse=True)
        audio.sort(key=lambda x: x["bitrate"] or 0)

        return {
            "error": False,
            "mode_used": mode,  # debug / info
            "title": info.get("title"),
            "duration": str(info.get("duration")),
            "thumbnail": info.get("thumbnail"),
            "video_with_audio": video_with_audio,
            "video_only": video_only,
            "audio": audio,
            "join": "@ProXBotz on Telegram",
            "support": "@ProBotUpdate"
        }

    except Exception as e:
        return {
            "error": True,
            "message": str(e)
        }
