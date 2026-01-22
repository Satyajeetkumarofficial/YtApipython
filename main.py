from fastapi import FastAPI, Query, HTTPException
import yt_dlp

app = FastAPI(
    title="YouTube Downloader API",
    description="144p to 1080p Video + MP3 + Thumbnail",
    version="3.0"
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
        "endpoint": "/youtube?url=YOUTUBE_URL"
    }

@app.get("/youtube")
def youtube(url: str = Query(...)):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        video_map = {}
        audio_list = []

        for f in info.get("formats", []):
            if not f.get("url"):
                continue

            height = f.get("height")

            # 🎥 Video (144p – 1080p only)
            if (
                height
                and 144 <= height <= 1080
                and f.get("vcodec") != "none"
            ):
                q = f"{height}p"
                if q not in video_map:  # avoid duplicates
                    video_map[q] = {
                        "quality": q,
                        "ext": f.get("ext"),
                        "fps": f.get("fps"),
                        "filesize": f.get("filesize"),
                        "url": f.get("url")
                    }

            # 🎧 Audio only (MP3/M4A source)
            if f.get("vcodec") == "none" and f.get("abr"):
                audio_list.append({
                    "bitrate": f.get("abr"),
                    "ext": f.get("ext"),
                    "filesize": f.get("filesize"),
                    "url": f.get("url")
                })

        videos = sorted(
            video_map.values(),
            key=lambda x: int(x["quality"].replace("p", ""))
        )

        return {
            "status": True,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "available_video_qualities": [v["quality"] for v in videos],
            "video": videos,
            "audio": audio_list
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
