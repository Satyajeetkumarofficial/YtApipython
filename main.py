from fastapi import FastAPI, Query, HTTPException
import yt_dlp

app = FastAPI(
    title="YouTube Downloader API",
    description="720p Video+Audio | 1080p Video-Only | Max Audio",
    version="4.0"
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

        video_av = []
        video_only_1080 = None
        best_audio = None

        for f in info.get("formats", []):
            if not f.get("url"):
                continue

            height = f.get("height")
            protocol = f.get("protocol")

            # 🎥 144p–720p : Video + Audio ONLY
            if (
                height
                and 144 <= height <= 720
                and f.get("vcodec") != "none"
                and f.get("acodec") != "none"
                and protocol != "m3u8_native"
            ):
                video_av.append({
                    "quality": f"{height}p",
                    "ext": f.get("ext"),
                    "fps": f.get("fps"),
                    "filesize": f.get("filesize"),
                    "url": f.get("url")
                })

            # 🎥 1080p : Video ONLY (labelled)
            if (
                height == 1080
                and f.get("vcodec") != "none"
                and f.get("acodec") == "none"
            ):
                video_only_1080 = {
                    "quality": "1080p",
                    "type": "video_only",
                    "note": "Audio not included (YouTube DASH)",
                    "ext": f.get("ext"),
                    "fps": f.get("fps"),
                    "filesize": f.get("filesize"),
                    "url": f.get("url")
                }

            # 🎧 Best Audio (Max bitrate)
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
                        "url": f.get("url")
                    }

        # sort video qualities
        video_av = sorted(video_av, key=lambda x: int(x["quality"].replace("p", "")))

        return {
            "status": True,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "video_with_audio_upto_720p": video_av,
            "video_only_1080p": video_only_1080,
            "best_audio": best_audio
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
