FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app/
COPY frontend/ /app/frontend/
COPY tests/ /app/tests/

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]