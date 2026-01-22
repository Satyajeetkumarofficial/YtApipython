from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp
import os
import config

app = FastAPI(title=config.APP_NAME, version=config.APP_VERSION)


def mb(size):
    if not size:
        return None
    return round(size / 1024 / 1024, 2)


def build_opts(use_proxy=False, use_cookies=False):
    opts = config.YDL_BASE_OPTS.copy()

    # ---- Client selection ----
    if use_cookies:
        # cookies => WEB client only
        opts["extractor_args"] = {
            "youtube": {
                "player_client": ["web"]
            }
        }
    else:
        # no cookies => android client
        opts["extractor_args"] = {
            "youtube": {
                "player_client": ["android"]
            }
        }

    # ---- Proxy ----
    if use_proxy and config.PROXY:
        opts["proxy"] = config.PROXY

    # ---- Cookies ----
    if use_cookies and os.path.exists(config.COOKIE_FILE):
        opts["cookiefile"] = config.COOKIE_FILE

    return opts


@app.get("/fetch")
def fetch(url: str = Query(...)):
    last_error = None

    for step in config.FALLBACK_ORDER:
        try:
            ydl_opts = build_opts(
                use_proxy=step["use_proxy"],
                use_cookies=step["use_cookies"]
            )

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            video_with_audio = []
            video_only = []
            audio = []

            for f in info.get("formats", []):
                if f.get("protocol", "").startswith("m3u8"):
                    continue

                # -------- video + audio (itag 18 mostly) --------
                if f.get("vcodec") != "none" and f.get("acodec") != "none":
                    video_with_audio.append({
                        "label": f"mp4 ({f.get('height')}p)",
                        "type": "video_with_audio",
                        "width": f.get("width"),
                        "height": f.get("height"),
                        "extension": f.get("ext"),
                        "fps": f.get("fps"),
                        "url": f.get("url"),
                    })

                # -------- video only --------
                if f.get("vcodec") != "none" and f.get("acodec") == "none":
                    video_only.append({
                        "label": f"mp4 ({f.get('height')}p)",
                        "type": "video_only",
                        "width": f.get("width"),
                        "height": f.get("height"),
                        "extension": f.get("ext"),
                        "fps": f.get("fps"),
                        "url": f.get("url"),
                    })

                # -------- audio only --------
                if f.get("vcodec") == "none" and f.get("acodec") != "none":
                    audio.append({
                        "label": f"{f.get('ext')} ({int(f.get('abr',0))}kb/s)",
                        "type": "audio",
                        "extension": f.get("ext"),
                        "bitrate": int(f.get("abr", 0) * 1000),
                        "url": f.get("url"),
                    })

            return {
                "error": False,
                "title": info.get("title"),
                "duration": str(info.get("duration")),
                "thumbnail": info.get("thumbnail"),
                "video_with_audio": video_with_audio,
                "video_only": video_only,
                "audio": audio,
                "join": config.JOIN_CHANNEL,
                "support": config.SUPPORT_USER,
            }

        except Exception as e:
            last_error = str(e)
            continue

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": last_error or "Unknown error"
        }
    )
