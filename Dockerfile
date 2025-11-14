FROM python:3.12-slim

WORKDIR /app

# Копируем из src/
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/Bot.py .

CMD ["python", "Bot.py"]