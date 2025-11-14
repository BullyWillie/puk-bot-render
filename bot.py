# Bot.py — В КОРНЕ РЕПОЗИТОРИЯ
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram import F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
import asyncio
import aiosqlite
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import os

# ====================== НАСТРОЙКИ ======================
API_TOKEN = os.getenv('TELEGRAM_TOKEN')
PUK_INTERVAL = 30 * 60
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = "llama3.1:8b"

# ====================== КЛАВИАТУРА ======================
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пукнуть")]],
    resize_keyboard=True
)

# ====================== БОТ ======================
default = DefaultBotProperties(parse_mode="Markdown")
bot = Bot(token=API_TOKEN, default=default)
dp = Dispatcher()

DB_NAME = "groups.db"

# ====================== LLM ======================
llm = OllamaLLM(base_url=OLLAMA_URL, model=OLLAMA_MODEL)

prompt_template = PromptTemplate(
    input_variables=["topic"],
    template=(
        "Придумай смешной пук на тему '{topic}'. "
        "Коротко, с эмодзи, каламбуром. Только текст."
    )
)

async def generate_puk(topic: str = "случайный пук") -> str:
    try:
        chain = prompt_template | llm
        puk = await asyncio.to_thread(chain.invoke, {"topic": topic})
        return f"*{puk.strip()}*"
    except Exception as e:
        print(f"[LLM ОШИБКА] {e}")
        return "*п-у-к*... ИИ спит"

# ====================== БАЗА ======================
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY)')
        await db.commit()
    print("База инициализирована")

async def add_group(chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO groups (chat_id) VALUES (?)', (chat_id,))
        await db.commit()
    print(f"Группа добавлена: {chat_id}")

async def get_groups():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT chat_id FROM groups') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

# ====================== КОМАНДЫ ======================
@dp.message(CommandStart())
async def start_private(message: types.Message):
    response = (
        f"**Пук-бот с ИИ на Render**\n\n"
        f"• Кнопка → ИИ-пук\n"
        f"• `/puk` в группе → пук\n"
        f"• Автопук каждые 30 мин"
    )
    await message.answer(response, reply_markup=keyboard)
    print(f"[ЛС] /start от {message.from_user.id}")

@dp.message(F.text == "Пукнуть", F.chat.type == "private")
async def puk_button(message: types.Message):
    puk = await generate_puk()
    await message.answer(puk)
    print(f"[ЛС] Кнопка → {puk}")

@dp.message(Command("puk"))
async def puk_command(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    await add_group(message.chat.id)
    puk = await generate_puk()
    await message.reply(puk)
    print(f"[ГРУППА] /puk → {puk}")

# ====================== АВТОПУК ======================
async def auto_puk_task():
    await asyncio.sleep(10)
    print("Автопук запущен")
    while True:
        groups = await get_groups()
        if groups:
            puk = await generate_puk()
            for chat_id in groups:
                try:
                    await bot.send_message(chat_id, puk)
                except: pass
        await asyncio.sleep(PUK_INTERVAL)

# ====================== ЗАПУСК ======================
async def main():
    await init_db()
    asyncio.create_task(auto_puk_task())
    print("Пук-бот запущен!")
    print(f"OLLAMA_URL: {OLLAMA_URL}")
    await dp.start_polling(bot, polling_timeout=30)

if __name__ == '__main__':
    asyncio.run(main())