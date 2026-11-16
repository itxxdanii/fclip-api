"""FClip downloader backend — drop-in replacement for the dead api.fclip.online.

Uses yt-dlp (free, open source) to extract the direct video file URLs for a
public Facebook video/Reel link. Keeps the SAME HTTP contract as the old
backend so the homepage widget needs no code change if api.fclip.online DNS
is pointed at this service:

  POST /api/info  {"url": "<facebook link>"}
    -> {"thumbnail", "title", "description", "duration", "normal", "hd"}

  GET /api/download?url=<facebook link>&quality=normal|hd
    -> 302 redirect to the direct fbcdn.net MP4 file

  GET /health -> {"ok": true}

Facebook serves two progressive MP4s that yt-dlp exposes as format ids
"sd" and "hd" — those map directly to the widget's normal/hd fields.
"""

import threading
import time
from urllib.parse import urlparse

import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="FClip API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fclip.online",
        "https://www.fclip.online",
        "http://localhost:8000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

FB_HOSTS = {
    "facebook.com",
    "www.facebook.com",
    "web.facebook.com",
    "m.facebook.com",
    "mbasic.facebook.com",
    "fb.watch",
}

# fbcdn links are signed and expire after a few hours; cache info for 1 hour.
CACHE_TTL = 3600
_cache: dict = {}
_lock = threading.Lock()


class InfoRequest(BaseModel):
    url: str


def _is_facebook_url(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower().split(":")[0]
    except Exception:
        return False
    return host in FB_HOSTS or host.endswith(".facebook.com")


def _extract(url: str) -> dict:
    now = time.time()
    with _lock:
        hit = _cache.get(url)
        if hit and now - hit["ts"] < CACHE_TTL:
            return hit["data"]

    opts = {
        "quiet": True,
        "noplaylist": True,
        "skip_download": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = {f.get("format_id"): f for f in info.get("formats", [])}
    normal = formats.get("sd", {}).get("url")
    hd = formats.get("hd", {}).get("url")

    if not normal and not hd:
        # Fallback: best progressive (audio+video in one file) format.
        progressive = [
            f
            for f in info.get("formats", [])
            if f.get("vcodec") not in (None, "none")
            and f.get("acodec") not in (None, "none")
            and f.get("url")
        ]
        if progressive:
            best = max(progressive, key=lambda f: f.get("height") or 0)
            normal = best["url"]
            hd = best["url"]

    if not normal and not hd:
        raise ValueError("no downloadable format found for this video")

    data = {
        "thumbnail": info.get("thumbnail"),
        "title": info.get("title"),
        "description": info.get("description"),
        "duration": info.get("duration"),
        "normal": normal or hd,
        "hd": hd or normal,
    }
    with _lock:
        _cache[url] = {"ts": now, "data": data}
    return data


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/info")
def info(req: InfoRequest):
    if not _is_facebook_url(req.url):
        raise HTTPException(status_code=400, detail="Not a Facebook video link")
    try:
        return _extract(req.url)
    except yt_dlp.utils.DownloadError as exc:
        raise HTTPException(
            status_code=422, detail=f"Could not fetch this video: {exc}"
        )
    except Exception as exc:  # noqa: BLE001 - surfaced as a clean API error
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/download")
def download(url: str, quality: str = "normal"):
    if not _is_facebook_url(url):
        raise HTTPException(status_code=400, detail="Not a Facebook video link")
    try:
        data = _extract(url)
    except Exception as exc:  # noqa: BLE001 - surfaced as a clean API error
        raise HTTPException(status_code=422, detail=str(exc))
    target = data["hd"] if quality == "hd" else data["normal"]
    return RedirectResponse(url=target, status_code=302)
