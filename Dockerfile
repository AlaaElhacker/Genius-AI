# Dockerfile
FROM python:3.11-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY app/ ./app/
COPY frontend/ ./frontend/

RUN mkdir -p data/uploads data/chroma_db

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]