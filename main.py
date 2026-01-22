from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI(
    title="YouTube Direct Downloader API",
    version="1.0"
)

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "nocheckcertificate": True
}

# 🔹 filesize calculator (exact + fallback)
def calc_filesize(f, duration):
    # exact filesize available
    if f.get("filesize"):
        return round(f["filesize"] / 1024 / 1024, 2)

    # fallback using bitrate
    tbr = f.get("tbr")  # kbps
    if tbr and duration:
        size_bytes = (tbr * 1024 * duration) / 8
        return round(size_bytes / 1024 / 1024, 2)

    return None


@app.get("/")
def home():
    return {
        "status": "API Running",
        "endpoint": "/fetch?url=YOUTUBE_URL"
    }


@app.get("/fetch")
def fetch(url: str = Query(..., description="YouTube video URL")):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)

    mp4_video_audio = []
    audio_only = []

    duration = info.get("duration")

    for f in info.get("formats", []):

        protocol = f.get("protocol", "")
        is_hls = protocol.startswith("m3u8")

        # 🎥 MP4 Video + Audio (progressive only)
        if (
            f.get("ext") == "mp4"
            and f.get("vcodec") != "none"
            and f.get("acodec") != "none"
            and not is_hls
        ):
            mp4_video_audio.append({
                "quality": f.get("format_note") or f.get("height"),
                "resolution": f.get("resolution"),
                "filesize_mb": calc_filesize(f, duration),
                "direct_link": f.get("url")
            })

        # 🔊 AUDIO only (m4a / webm)
        if (
            f.get("vcodec") == "none"
            and f.get("acodec") != "none"
            and not is_hls
        ):
            audio_only.append({
                "bitrate_kbps": round(f.get("abr", 0), 1),
                "ext": f.get("ext"),
                "filesize_mb": calc_filesize(f, duration),
                "direct_link": f.get("url")
            })

    return {
        "title": info.get("title"),
        "duration": duration,
        "thumbnail": info.get("thumbnail"),
        "mp4_video_audio": mp4_video_audio,
        "audio_only": audio_only
    }
