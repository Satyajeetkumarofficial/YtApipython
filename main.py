from fastapi import FastAPI, Query, HTTPException
import yt_dlp

app = FastAPI(
    title="YouTube Downloader API",
    description="720p Audio+Video | 1080p Video-Only | Max Audio | No Server Load",
    version="FINAL"
)

YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "nocheckcertificate": True
}

@app.get("/")
def home():
    return {
        "status": True,
        "message": "YouTube Downloader API Running",
        "usage": "/youtube?url=YOUTUBE_URL"
    }

@app.get("/youtube")
def youtube(url: str = Query(..., description="YouTube video URL")):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        video_with_audio = []
        video_only_1080 = None
        best_audio = None

        for f in info.get("formats", []):
            if not f.get("url"):
                continue

            height = f.get("height")

            # 🎥 144p–720p : VIDEO + AUDIO (HLS / DASH allowed)
            if (
                height
                and 144 <= height <= 720
                and f.get("vcodec") != "none"
                and f.get("acodec") != "none"
            ):
                video_with_audio.append({
                    "quality": f"{height}p",
                    "type": "video+audio",
                    "ext": f.get("ext"),
                    "fps": f.get("fps"),
                    "filesize": f.get("filesize"),
                    "protocol": f.get("protocol"),
                    "url": f.get("url")
                })

            # 🎥 1080p : VIDEO ONLY (clearly labelled)
            if (
                height == 1080
                and f.get("vcodec") != "none"
                and f.get("acodec") == "none"
            ):
                video_only_1080 = {
                    "quality": "1080p",
                    "type": "video_only",
                    "note": "Audio not included (YouTube DASH/HLS)",
                    "ext": f.get("ext"),
                    "fps": f.get("fps"),
                    "filesize": f.get("filesize"),
                    "protocol": f.get("protocol"),
                    "url": f.get("url")
                }

            # 🎧 BEST AUDIO (maximum available bitrate, HLS allowed)
            if (
                f.get("vcodec") == "none"
                and f.get("acodec") != "none"
                and f.get("abr")
            ):
                if (not best_audio) or (f.get("abr", 0) > best_audio["bitrate"]):
                    best_audio = {
                        "bitrate": f.get("abr"),
                        "ext": f.get("ext"),
                        "filesize": f.get("filesize"),
                        "protocol": f.get("protocol"),
                        "url": f.get("url")
                    }

        # sort 144p → 720p
        video_with_audio = sorted(
            video_with_audio,
            key=lambda x: int(x["quality"].replace("p", ""))
        )

        return {
            "status": True,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "video_with_audio_upto_720p": video_with_audio,
            "video_only_1080p": video_only_1080,
            "best_audio": best_audio
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
