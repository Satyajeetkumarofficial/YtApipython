from fastapi import FastAPI, Query
import yt_dlp
import os
import config

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION
)

# ---------- HELPERS ----------

def build_label(ext, height=None, abr=None):
    if height:
        return f"{ext} ({height}p)"
    if abr:
        return f"{ext} ({int(abr)}kb/s)"
    return ext


def get_opts(use_proxy=False, use_cookies=False):
    opts = config.YDL_BASE_OPTS.copy()

    # Proxy
    if use_proxy and config.PROXY:
        opts["proxy"] = config.PROXY

    # Cookies
    if (
        use_cookies
        and config.USE_COOKIES_IF_EXISTS
        and os.path.exists(config.COOKIE_FILE)
    ):
        opts["cookiefile"] = config.COOKIE_FILE

    return opts


def extract_info_with_fallback(url: str):
    last_error = None

    for step in config.FALLBACK_ORDER:
        try:
            opts = get_opts(
                use_proxy=step["use_proxy"],
                use_cookies=step["use_cookies"]
            )
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            mode = f'proxy={step["use_proxy"]}, cookies={step["use_cookies"]}'
            return info, mode

        except Exception as e:
            last_error = str(e)

    raise Exception(last_error)


# ---------- API ----------

@app.get("/fetch")
def fetch(url: str = Query(...)):
    try:
        info, mode_used = extract_info_with_fallback(url)

        video_with_audio = []
        video_only = []
        audio = []

        for f in info.get("formats", []):

            # 🎥 VIDEO + AUDIO (ALL PROGRESSIVE)
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
            "mode_used": mode_used,
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
        return {
            "error": True,
            "message": str(e)
                }
