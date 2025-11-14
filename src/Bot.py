# src/Bot.py — ПОЛНЫЙ ПУК-БОТ С ГОЛОСОВЫМИ .MP3 ИЗ ПАПКИ
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram import F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
import asyncio
import aiosqlite
import random
import os

# ====================== НАСТРОЙКИ ======================
API_TOKEN = os.getenv('TELEGRAM_TOKEN')
PUK_INTERVAL = 60 * 60  # 1 час
ADMIN_ID = 1015269859   # ← ЗАМЕНИ НА СВОЙ ID (@userinfobot)

# ====================== ПАПКА С ГОЛОСОВЫМИ ПУКАМИ ======================
AUDIO_DIR = "/app/audio"  # Путь в Docker
VOICE_FILES = []

# ====================== КЛАВИАТУРА ДЛЯ АДМИНА ======================
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Группы"), KeyboardButton(text="Пукнуть")]],
    resize_keyboard=True
)

# ====================== БОТ ======================
default = DefaultBotProperties(parse_mode="Markdown")
bot = Bot(token=API_TOKEN, default=default)
dp = Dispatcher()

DB_NAME = "groups.db"

# ====================== ИНИЦИАЛИЗАЦИЯ ГОЛОСОВ ======================
def load_voice_files():
    global VOICE_FILES
    if not os.path.exists(AUDIO_DIR):
        print(f"[ОШИБКА] Папка {AUDIO_DIR} не найдена!")
        return
    VOICE_FILES = [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(".mp3")]
    print(f"[ГОЛОСА] Загружено {len(VOICE_FILES)} .mp3: {VOICE_FILES}")

# ====================== ОТПРАВКА СЛУЧАЙНОГО ГОЛОСА ======================
async def send_voice_puk(chat_id: int):
    if not VOICE_FILES:
        await bot.send_message(chat_id, "*п-у-к*... (голоса не найдены)")
        return
    
    file_name = random.choice(VOICE_FILES)
    file_path = os.path.join(AUDIO_DIR, file_name)
    try:
        with open(file_path, "rb") as audio:
            await bot.send_voice(chat_id, audio, caption=f"*{file_name}*")
        print(f"[ПУК] Отправлен: {file_name} → {chat_id}")
    except Exception as e:
        print(f"[ОШИБКА ГОЛОСА] {e}")
        await bot.send_message(chat_id, "*п-у-к*... (не смог пукнуть)")

# ====================== БАЗА ДАННЫХ ======================
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY, title TEXT)')
        await db.commit()
    print("База инициализирована")

async def add_group(chat_id: int, title: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO groups (chat_id, title) VALUES (?, ?)', (chat_id, title))
        await db.commit()

async def remove_group(chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM groups WHERE chat_id = ?', (chat_id,))
        await db.commit()

async def get_groups():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT chat_id, title FROM groups') as cursor:
            return await cursor.fetchall()

# ====================== ЛС: АДМИН ПАНЕЛЬ ======================
@dp.message(CommandStart(), F.from_user.id == ADMIN_ID)
async def start_admin(message: types.Message):
    await message.answer(
        "**Пук-бот — панель**\n\n"
        "• `Группы` — список чатов\n"
        "• `Пукнуть` — голосовой пук\n"
        "• `/puk` в группе\n"
        "• Автопук: 1/час",
        reply_markup=admin_keyboard
    )

@dp.message(F.text == "Группы", F.from_user.id == ADMIN_ID)
async def list_groups(message: types.Message):
    groups = await get_groups()
    if not groups:
        await message.answer("Нет активных групп.")
        return
    text = "**Активные группы:**\n\n"
    for i, (chat_id, title) in enumerate(groups, 1):
        text += f"{i}. `{title}` (`{chat_id}`)\n"
    text += "\nНапиши: `/leave ЧАТ_ID` — выйти"
    await message.answer(text)

@dp.message(Command("leave"), F.from_user.id == ADMIN_ID)
async def leave_group(message: types.Message):
    try:
        chat_id = int(message.text.split()[1])
        await bot.leave_chat(chat_id)
        await remove_group(chat_id)
        await message.answer(f"Вышел из группы `{chat_id}`")
    except:
        await message.answer("Использование: `/leave -1001234567890`")

@dp.message(F.text == "Пукнуть", F.from_user.id == ADMIN_ID)
async def puk_admin(message: types.Message):
    await send_voice_puk(message.chat.id)

# ====================== ГРУППА: /puk ======================
@dp.message(Command("puk"))
async def puk_command(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    await add_group(message.chat.id, message.chat.title or "Без названия")
    await send_voice_puk(message.chat.id)

# ====================== АВТОПУК ======================
async def auto_puk_task():
    await asyncio.sleep(10)
    print("Автопук (голос) запущен")
    while True:
        groups = await get_groups()
        if groups:
            for chat_id, title in groups:
                try:
                    await send_voice_puk(chat_id)
                    print(f"[АВТОПУК] → {title}")
                except Exception as e:
                    print(f"[ОШИБКА АВТОПУК] {chat_id}: {e}")
        await asyncio.sleep(PUK_INTERVAL)

# ====================== ЗАПУСК ======================
async def main():
    await init_db()
    load_voice_files()  # Загружаем .mp3
    asyncio.create_task(auto_puk_task())
    print("Пук-бот запущен! Голоса из /app/audio")
    await dp.start_polling(bot, polling_timeout=30)

if __name__ == '__main__':
    asyncio.run(main())
