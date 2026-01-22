from fastapi import FastAPI, Query, HTTPException
import yt_dlp

app = FastAPI(
    title="YouTube Max-Chance API",
    description="144p–1080p | Max Audio+Video | Always Audio | Thumbnail | No Server Load",
    version="MAX-FINAL"
)

YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,

    # 🌍 Geo friendly (India + nearby)
    "geo_bypass": True,
    "geo_bypass_country": "IN",

    # 🧠 Stability
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
def youtube(url: str = Query(...)):
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

            # 🎥 Collect ALL video qualities (144p–1080p)
            if height and 144 <= height <= 1080 and f.get("vcodec") != "none":
                q = f"{height}p"

                # Decide label
                av_type = "audio_video"
                if f.get("acodec") == "none":
                    av_type = "video_only"

                # Keep first best per quality
                if q not in videos:
                    videos[q] = {
                        "quality": q,
                        "type": av_type,
                        "protocol": protocol,
                        "ext": f.get("ext"),
                        "fps": f.get("fps"),
                        "url": f.get("url")
                    }

            # 🎧 Collect BEST audio (always)
            if f.get("vcodec") == "none" and f.get("abr"):
                if not best_audio or f.get("abr", 0) > best_audio["bitrate"]:
                    best_audio = {
                        "bitrate": f.get("abr"),
                        "protocol": protocol,
                        "ext": f.get("ext"),
                        "url": f.get("url")
                    }

        # Sort videos 144p → 1080p
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
                "If video type is 'video_only', "
                "use 'best_audio' with it. "
                "Server-side merge not used."
            )
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
