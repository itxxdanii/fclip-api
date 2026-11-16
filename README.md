# FClip downloader backend (replacement for dead api.fclip.online)

Small FastAPI service using yt-dlp to extract direct MP4 links for public
Facebook videos/Reels. Same HTTP contract as the old backend, so the
homepage widget works unchanged once traffic reaches this service.

## Endpoints

- `POST /api/info` `{"url": "<facebook link>"}` → thumbnail, title,
  description, duration, normal (SD MP4), hd (HD MP4)
- `GET /api/download?url=<link>&quality=normal|hd` → 302 to the MP4 file
- `GET /health` → `{"ok": true}`

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
curl -s -X POST localhost:8000/api/info -H 'Content-Type: application/json' \
  -d '{"url": "https://www.facebook.com/NASA/videos/roman-launches-and-a-new-era-begins-official-nasa-recap/916920438162629"}'
```

## Deploy (pick one — needs the user's decision)

### Option A — Oracle Cloud Always Free VPS (best: always on, unlimited)
1. Sign up at cloud.oracle.com with the user's OWN card (verification only,
   no charge). Create an Always Free Ampere A1 VM (2 OCPU / 12 GB).
2. On the VM: install Docker, copy this folder, `docker build -t fclip-api .`
   then `docker run -d --restart always -p 8000:8000 fclip-api`.
3. Point the `api.fclip.online` DNS A record at the VM's public IP.
   The widget then works with ZERO code changes.

### Option B — Render free web service (no card, but sleeps)
1. Create a free Render account, new Web Service from this repo/folder.
   Render builds the Dockerfile automatically and gives a public URL.
2. Free services spin down after 15 min idle; the first call after sleep
   takes ~30–60s to wake up. The widget may need a longer wait message.
3. Either point `api.fclip.online` DNS at Render (custom domain) or edit
   the homepage widget's fetch URL to the Render URL.

## Limits / notes

- Only public videos/Reels work. Private, login-only, deleted or
  age-restricted videos fail with a clean 422 error.
- Info responses are cached 1 hour in memory; fbcdn links are signed and
  expire after a few hours, so downloads should start promptly.
- yt-dlp must be kept updated (`pip install -U yt-dlp`); Facebook changes
  its pages often and old versions stop extracting.
