FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt \
    && playwright install --with-deps chromium

COPY backend backend
COPY distribution distribution

ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

ENV PORT=8080
EXPOSE 8080

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
