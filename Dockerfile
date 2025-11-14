FROM python:3.12-slim

WORKDIR /app

# КОПИРУЕМ ВСЮ ПАПКУ audio
COPY src/audio ./audio
COPY src/Bot.py .
COPY requirements.txt .

# ПРОВЕРЯЕМ, ЧТО ПАПКА СКОПИРОВАЛАСЬ
RUN ls -la /app/audio || echo "ПАПКА audio НЕ СКОПИРОВАЛАСЬ!"

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "Bot.py"]