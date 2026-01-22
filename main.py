from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI(title="YouTube Downloader API")

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "nocheckcertificate": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    }
}

def build_label(ext, height=None, abr=None):
    if height:
        return f"{ext} ({height}p)"
    if abr:
        return f"{ext} ({int(abr)}kb/s)"
    return ext

@app.get("/fetch")
def fetch(url: str = Query(...)):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        video_with_audio = []
        video_only = []
        audio = []

        for f in info.get("formats", []):

            # 🎥 VIDEO + AUDIO (SEARCH ALL POSSIBLE PROGRESSIVE)
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

            # 🎞 VIDEO ONLY (ALL QUALITIES)
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

        # 🔽 SORTING
        video_with_audio = sorted(
            video_with_audio,
            key=lambda x: x["height"] or 0,
            reverse=True
        )

        video_only = sorted(
            video_only,
            key=lambda x: x["height"] or 0,
            reverse=True
        )

        audio = sorted(
            audio,
            key=lambda x: x["bitrate"] or 0
        )

        return {
            "error": False,
            "title": info.get("title"),
            "duration": str(info.get("duration")),
            "thumbnail": info.get("thumbnail"),
            "video_with_audio": video_with_audio,
            "video_only": video_only,
            "audio": audio,
            "join": "@HazexAPI on Telegram",
            "support": "@MrHazex"
        }

    except Exception as e:
        return {
            "error": True,
            "message": str(e)
    }
