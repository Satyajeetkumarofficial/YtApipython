from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import yt_dlp

app = FastAPI(title="YouTube 360p Downloader")
templates = Jinja2Templates(directory="templates")

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "noplaylist": True,
    "format": "18/bestaudio",  # 360p OR audio
}

def mb(size):
    if not size:
        return None
    return round(size / 1024 / 1024, 2)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/fetch")
def fetch(url: str = Query(...)):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

    except Exception:
        # 🔥 MOST IMPORTANT PART
        return JSONResponse(
            {
                "error": True,
                "blocked": True,
                "message": "YouTube blocked automated access for this video",
                "hint": "This video plays in Incognito but download URLs require cookies in 2025",
                "solution": "Use cookies-based mode for guaranteed results"
            },
            status_code=200
        )

    video_360 = None
    audio_mp3 = None

    for f in info.get("formats", []):
        # 🎥 360p video+audio
        if f.get("itag") == 18:
            video_360 = {
                "quality": "360p",
                "ext": "mp4",
                "filesize_mb": mb(f.get("filesize")),
                "direct_link": f.get("url"),
            }

        # 🎵 audio
        if f.get("vcodec") == "none" and f.get("acodec") != "none":
            audio_mp3 = {
                "ext": f.get("ext"),
                "bitrate_kbps": f.get("abr"),
                "filesize_mb": mb(f.get("filesize")),
                "direct_link": f.get("url"),
            }

    return {
        "error": False,
        "title": info.get("title"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "video_360p": video_360,
        "audio": audio_mp3,
    }
