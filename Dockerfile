FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

# Render / Fly / any host that sets $PORT; default 8000.
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
