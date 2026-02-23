FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (better layer caching)
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app /app

# Create database directory with permissions
RUN mkdir -p /data && chmod 777 /data

ENV DB_PATH=/data/sqlite.db

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

