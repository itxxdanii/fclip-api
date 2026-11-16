"""Vercel entrypoint (root): re-export the FastAPI app from app.py.

Vercel's FastAPI backend-framework preset serves the app from this root
entrypoint, with the original request path preserved. No vercel.json
rewrites are used: internal rewrites in backend framework projects route
requests using the rewritten destination path, which broke routing.
"""

from app import app  # noqa: F401
