from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI(title="YouTube Clean Downloader API")

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "format": "best"
}

def mb(size):
    if not size:
        return None
    return round(size / 1024 / 1024, 2)

@app.get("/fetch")
def fetch(url: str = Query(...)):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)

    mp4_list = []
    mp3_list = []

    for f in info.get("formats", []):
        # ✅ ONLY progressive MP4 (video + audio)
        if (
            f.get("ext") == "mp4"
            and f.get("vcodec") != "none"
            and f.get("acodec") != "none"
            and not f.get("protocol", "").startswith("m3u8")
        ):
            mp4_list.append({
                "quality": f.get("format_note") or f.get("height"),
                "resolution": f.get("resolution"),
                "filesize_mb": mb(f.get("filesize")),
                "direct_link": f.get("url")
            })

        # ✅ AUDIO only (MP3 / M4A)
        if (
            f.get("vcodec") == "none"
            and f.get("acodec") != "none"
            and not f.get("protocol", "").startswith("m3u8")
        ):
            mp3_list.append({
                "bitrate_kbps": round(f.get("abr", 0), 1),
                "ext": f.get("ext"),
                "filesize_mb": mb(f.get("filesize")),
                "direct_link": f.get("url")
            })

    return {
        "title": info.get("title"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "mp4_video_audio": mp4_list,
        "audio_only": mp3_list
    }
