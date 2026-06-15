FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
