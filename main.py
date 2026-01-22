from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI(title="YouTube Downloader API", version="1.0")

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "nocheckcertificate": True
}

@app.get("/fetch")
def fetch(url: str = Query(...)):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        video_with_audio = []
        video_only = []
        audio = []

        for f in info.get("formats", []):
            if f.get("protocol", "").startswith("m3u8"):
                continue

            # VIDEO + AUDIO
            if f.get("vcodec") != "none" and f.get("acodec") != "none":
                video_with_audio.append({
                    "label": f"{f.get('ext')} ({f.get('height')}p)",
                    "type": "video_with_audio",
                    "width": f.get("width"),
                    "height": f.get("height"),
                    "extension": f.get("ext"),
                    "fps": f.get("fps"),
                    "url": f.get("url")
                })

            # VIDEO ONLY
            elif f.get("vcodec") != "none":
                video_only.append({
                    "label": f"{f.get('ext')} ({f.get('height')}p)",
                    "type": "video_only",
                    "width": f.get("width"),
                    "height": f.get("height"),
                    "extension": f.get("ext"),
                    "fps": f.get("fps"),
                    "url": f.get("url")
                })

            # AUDIO ONLY
            elif f.get("acodec") != "none":
                audio.append({
                    "label": f"{f.get('ext')} ({int(f.get('abr', 0))}kb/s)",
                    "type": "audio",
                    "extension": f.get("ext"),
                    "bitrate": int(f.get("abr", 0) * 1000),
                    "url": f.get("url")
                })

        return {
            "error": False,
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
