from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import yt_dlp

app = FastAPI(title="YouTube 360p Downloader API")
templates = Jinja2Templates(directory="templates")

YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "noplaylist": True,
    "format": "18/bestaudio",  # 360p mp4 OR audio
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

        video = None
        audio = None

        for f in info.get("formats", []):
            # 🎥 360p video + audio (itag 18)
            if f.get("itag") == 18:
                video = {
                    "quality": "360p",
                    "ext": "mp4",
                    "filesize_mb": mb(f.get("filesize")),
                    "direct_link": f.get("url")
                }

            # 🎵 audio only (m4a)
            if f.get("vcodec") == "none" and f.get("acodec") != "none":
                audio = {
                    "ext": f.get("ext"),
                    "bitrate_kbps": f.get("abr"),
                    "filesize_mb": mb(f.get("filesize")),
                    "direct_link": f.get("url")
                }

        if not video and not audio:
            return JSONResponse(
                {"error": True, "message": "360p or audio not available without cookies"},
                status_code=403
            )

        return {
            "error": False,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "video_360p": video,
            "audio": audio
        }

    except Exception as e:
        return JSONResponse(
            {"error": True, "message": str(e)},
            status_code=500
        )
