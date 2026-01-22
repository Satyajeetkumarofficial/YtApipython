from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI(title="YouTube Downloader API", version="1.0")

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "nocheckcertificate": True
}

def calc_filesize(f, duration):
    if f.get("filesize"):
        return f["filesize"]
    tbr = f.get("tbr")  # kbps
    if tbr and duration:
        return int((tbr * 1024 * duration) / 8)
    return None


@app.get("/fetch")
def fetch(url: str = Query(..., description="YouTube URL")):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)

    video_with_audio = []
    video_only = []
    audio = []

    duration = info.get("duration")

    for f in info.get("formats", []):
        # HLS skip
        if f.get("protocol", "").startswith("m3u8"):
            continue

        width = f.get("width")
        height = f.get("height")

        # 🎥 VIDEO + AUDIO (progressive)
        if f.get("vcodec") != "none" and f.get("acodec") != "none":
            label = f"{f.get('ext')} ({height}p)" if height else f.get("ext")
            video_with_audio.append({
                "label": label,
                "type": "video_with_audio",
                "width": width,
                "height": height,
                "extension": f.get("ext"),
                "fps": f.get("fps"),
                "url": f.get("url")
            })

        # 🎞️ VIDEO ONLY
        elif f.get("vcodec") != "none" and f.get("acodec") == "none":
            label = f"{f.get('ext')} ({height}p)" if height else f.get("ext")
            video_only.append({
                "label": label,
                "type": "video_only",
                "width": width,
                "height": height,
                "extension": f.get("ext"),
                "fps": f.get("fps"),
                "url": f.get("url")
            })

        # 🔊 AUDIO ONLY
        elif f.get("vcodec") == "none" and f.get("acodec") != "none":
            bitrate = int(f.get("abr", 0) * 1000) if f.get("abr") else None
            label = f"{f.get('ext')} ({int(f.get('abr', 0))}kb/s)"
            audio.append({
                "label": label,
                "type": "audio",
                "extension": f.get("ext"),
                "bitrate": bitrate,
                "url": f.get("url")
            })

    # sorting (better UX)
    video_with_audio.sort(key=lambda x: (x.get("height") or 0), reverse=True)
    video_only.sort(key=lambda x: (x.get("height") or 0), reverse=True)
    audio.sort(key=lambda x: (x.get("bitrate") or 0), reverse=True)

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
