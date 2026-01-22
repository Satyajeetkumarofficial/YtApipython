from fastapi import FastAPI, Query
import yt_dlp
import os
import config

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION
)

# -------------------------
# Utils
# -------------------------

def mb(size):
    if not size:
        return None
    return round(size / 1024 / 1024, 2)


def build_ydl_opts(use_cookie: bool, use_proxy: bool):
    opts = dict(config.YDL_BASE_OPTS)

    # cookies
    if use_cookie and os.path.exists(config.COOKIE_FILE):
        opts["cookiefile"] = config.COOKIE_FILE

    # proxy (example – change if needed)
    if use_proxy:
        # opts["proxy"] = "http://user:pass@ip:port"
        pass

    return opts


# -------------------------
# API
# -------------------------

@app.get("/fetch")
def fetch(url: str = Query(...)):

    last_error = None

    for step in config.FALLBACK_ORDER:
        use_cookie = step["cookie"]
        use_proxy = step["proxy"]

        try:
            ydl_opts = build_ydl_opts(use_cookie, use_proxy)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            # -------------------------
            # Base Info
            # -------------------------
            response = {
                "error": False,
                "title": info.get("title"),
                "duration": str(info.get("duration")),
                "thumbnail": info.get("thumbnail"),
                "video_with_audio": [],
                "video_only": [],
                "audio": [],
                "join": config.JOIN_CHANNEL,
                "support": config.SUPPORT_USER
            }

            # -------------------------
            # Formats
            # -------------------------
            for f in info.get("formats", []):

                # Progressive MP4 (video + audio)
                if (
                    f.get("ext") == "mp4"
                    and f.get("vcodec") != "none"
                    and f.get("acodec") != "none"
                    and not str(f.get("protocol", "")).startswith("m3u8")
                ):
                    response["video_with_audio"].append({
                        "label": f"mp4 ({f.get('height')}p)",
                        "type": "video_with_audio",
                        "width": f.get("width"),
                        "height": f.get("height"),
                        "extension": "mp4",
                        "fps": f.get("fps"),
                        "url": f.get("url"),
                    })

                # Video only
                if (
                    f.get("vcodec") != "none"
                    and f.get("acodec") == "none"
                    and not str(f.get("protocol", "")).startswith("m3u8")
                ):
                    response["video_only"].append({
                        "label": f"{f.get('ext')} ({f.get('height')}p)",
                        "type": "video_only",
                        "width": f.get("width"),
                        "height": f.get("height"),
                        "extension": f.get("ext"),
                        "fps": f.get("fps"),
                        "url": f.get("url"),
                    })

                # Audio only
                if (
                    f.get("vcodec") == "none"
                    and f.get("acodec") != "none"
                    and not str(f.get("protocol", "")).startswith("m3u8")
                ):
                    response["audio"].append({
                        "label": f"{f.get('ext')} ({int(f.get('abr', 0))}kb/s)",
                        "type": "audio",
                        "extension": f.get("ext"),
                        "bitrate": int(f.get("abr", 0)),
                        "url": f.get("url"),
                    })

            # अगर कुछ तो मिला → return
            if (
                response["video_with_audio"]
                or response["video_only"]
                or response["audio"]
            ):
                return response

        except Exception as e:
            last_error = str(e)
            continue

    # -------------------------
    # All fallbacks failed
    # -------------------------
    return {
        "error": True,
        "message": last_error or "Extraction failed"
            }
