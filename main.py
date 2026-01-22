from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI(title="YouTube All-in-One API")

YDL_OPTS = {
    "quiet": True,
    "skip_download": True
}

def mb(size):
    if not size:
        return None
    return round(size / 1024 / 1024, 2)

@app.get("/fetch")
def fetch(url: str = Query(...)):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)

    mp4_videos = []
    mp3_audios = []

    for f in info.get("formats", []):
        # 🎥 MP4 Video + Audio (progressive)
        if (
            f.get("ext") == "mp4"
            and f.get("vcodec") != "none"
            and f.get("acodec") != "none"
        ):
            mp4_videos.append({
                "quality": f.get("format_note"),
                "resolution": f.get("resolution"),
                "filesize_mb": mb(f.get("filesize")),
                "cdn": f.get("url")
            })

        # 🔊 MP3 / m4a audio
        if f.get("vcodec") == "none" and f.get("acodec") != "none":
            mp3_audios.append({
                "bitrate_kbps": f.get("abr"),
                "ext": f.get("ext"),
                "filesize_mb": mb(f.get("filesize")),
                "cdn": f.get("url")
            })

    return {
        "title": info.get("title"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "mp4_video_audio": mp4_videos,
        "mp3_audio": mp3_audios
    }
