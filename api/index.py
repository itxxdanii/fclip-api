"""Vercel entrypoint: adapt the FastAPI app from app.py with Mangum.

Only `handler` is exported here, so Vercel's Python runtime uses the Mangum
adapter (not the plain ASGI app): Mangum translates the serverless event
back into the original request path, so all routes (/health, /api/info,
/api/download) are handled by the FastAPI app itself; vercel.json rewrites
every path here.
"""

from mangum import Mangum

from app import app as fastapi_app

handler = Mangum(fastapi_app)
