FROM python:3.12-slim

WORKDIR /app

# Копируем файлы из src/ в /app
COPY src/Bot.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ← ВАЖНО: Запускаем из /app, где Bot.py уже есть
CMD ["python", "Bot.py"]