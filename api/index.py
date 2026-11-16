"""Vercel entrypoint: re-export the FastAPI app from app.py.

Vercel's Python runtime serves this file as a serverless function and
detects the ASGI `app` object. All routes (/health, /api/info,
/api/download) are handled by the FastAPI app itself; vercel.json rewrites
every path here.
"""

from app import app  # noqa: F401  (Vercel picks up `app` from this module)
