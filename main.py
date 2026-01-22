from fastapi import FastAPI, Query, HTTPException
import yt_dlp

app = FastAPI(
    title="YouTube Max-Chance Downloader API",
    description="144p–1080p | Max Audio+Video | Audio Always | Thumbnail | No Server Load",
    version="FINAL-1.0"
)

# yt-dlp options (India + nearby friendly)
YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,

    # Geo handling
    "geo_bypass": True,
    "geo_bypass_country": "IN",

    # Stability
    "nocheckcertificate": True,
    "extractor_retries": 3,
    "fragment_retries": 3
}

@app.get("/")
def home():
    return {
        "status": True,
        "message": "YouTube Max-Chance API Running",
        "rule": "Audio+Video if possible, else Video + Audio always",
        "usage": "/youtube?url=YOUTUBE_URL"
    }

@app.get("/youtube")
def youtube(url: str = Query(..., description="YouTube video URL")):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        videos = {}
        best_audio = None

        for f in info.get("formats", []):
            if not f.get("url"):
                continue

            height = f.get("height")
            protocol = f.get("protocol")

            # 🎥 Collect video formats (144p–1080p)
            if height and 144 <= height <= 1080 and f.get("vcodec") != "none":
                quality = f"{height}p"

                # Decide type
                vtype = "audio_video"
                if f.get("acodec") == "none":
                    vtype = "video_only"

                # Keep first/best per quality
                if quality not in videos:
                    videos[quality] = {
                        "quality": quality,
                        "type": vtype,
                        "protocol": protocol,
                        "ext": f.get("ext"),
                        "fps": f.get("fps"),
                        "filesize": f.get("filesize"),
                        "url": f.get("url")
                    }

            # 🎧 Separate audio streams (DASH / MP4 / WebM)
            if f.get("vcodec") == "none" and f.get("abr"):
                if not best_audio or f.get("abr", 0) > best_audio.get("bitrate", 0):
                    best_audio = {
                        "type": "separate",
                        "bitrate": f.get("abr"),
                        "protocol": protocol,
                        "ext": f.get("ext"),
                        "filesize": f.get("filesize"),
                        "url": f.get("url")
                    }

        # 🔁 Fallback: HLS embedded audio (VERY IMPORTANT)
        if not best_audio:
            best_audio = {
                "type": "embedded",
                "note": "Audio is embedded inside HLS playlist",
                "protocol": "m3u8_native",
                "usage": "Use the same video URL to play audio+video (upto 720p)"
            }

        # Sort videos by quality
        video_list = sorted(
            videos.values(),
            key=lambda x: int(x["quality"].replace("p", ""))
        )

        return {
            "status": True,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),

            "videos": video_list,
            "best_audio": best_audio,

            "note": (
                "If video type is 'video_only' and best_audio.type is 'separate', "
                "play or merge client-side. "
                "If best_audio.type is 'embedded', audio is already inside HLS."
            )
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
