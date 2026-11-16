"""Vercel entrypoint: adapt the FastAPI app from app.py with Mangum.

Vercel's Python runtime invokes this file as a serverless function; Mangum
translates the serverless event back into the original request path, so
all routes (/health, /api/info, /api/download) are handled by the FastAPI
app itself; vercel.json rewrites every path here.
"""

from mangum import Mangum

from app import app

handler = Mangum(app)
