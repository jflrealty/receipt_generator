# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY backend/ .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
