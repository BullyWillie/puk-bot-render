FROM python:3.12-slim

WORKDIR /app

# Копируем всё
COPY src/Bot.py .
COPY src/audio ./audio
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "Bot.py"]