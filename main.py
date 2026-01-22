from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI(title="Incognito YouTube Downloader API")

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "nocheckcertificate": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]
        }
    }
}

def mb(size):
    if not size:
        return None
    return round(size / 1024 / 1024, 2)

@app.get("/fetch")
def fetch(url: str = Query(...)):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        video_360 = None
        audio_mp3 = None

        for f in info.get("formats", []):
            # ✅ 360p video + audio (itag 18)
            if (
                f.get("itag") == 18
                and f.get("ext") == "mp4"
                and f.get("vcodec") != "none"
                and f.get("acodec") != "none"
            ):
                video_360 = {
                    "label": "mp4 (360p)",
                    "quality": "360p",
                    "width": f.get("width"),
                    "height": f.get("height"),
                    "extension": "mp4",
                    "filesize_mb": mb(f.get("filesize")),
                    "direct_link": f.get("url")
                }

            # ✅ Best audio (for MP3 use)
            if (
                f.get("vcodec") == "none"
                and f.get("acodec") != "none"
                and f.get("abr")
            ):
                if not audio_mp3 or f.get("abr", 0) > audio_mp3["bitrate_kbps"]:
                    audio_mp3 = {
                        "label": "mp3",
                        "bitrate_kbps": round(f.get("abr")),
                        "extension": f.get("ext"),
                        "filesize_mb": mb(f.get("filesize")),
                        "direct_link": f.get("url")
                    }

        return {
            "error": False,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "video_with_audio": [video_360] if video_360 else [],
            "audio_mp3": [audio_mp3] if audio_mp3 else []
        }

    except Exception as e:
        return {
            "error": True,
            "message": str(e)
        }
