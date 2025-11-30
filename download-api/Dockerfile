FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir yt-dlp flask mutagen psycopg2-binary

WORKDIR /app

COPY app.py .

CMD ["python", "app.py"]
