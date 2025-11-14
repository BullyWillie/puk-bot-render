FROM python:3.12-slim

WORKDIR /app

# Копируем из корня
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем бота из src/
COPY src/Bot.py .

CMD ["python", "Bot.py"]