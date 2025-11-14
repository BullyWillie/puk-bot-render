# bot/Bot.py
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
    keyboard=[[KeyboardButton(text="Пукнуть 💨")]],
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
        "Ты — мастер смешных пуков. Придумай короткий, зашифрованный 'пук' на тему '{topic}'. "
        "Сделай его юмористичным: используй эмодзи, каламбуры, тишину, стул, запах, неожиданный поворот. "
        "Максимум 1-2 предложения. Только текст, без объяснений. Пример: 'В тишине комнаты скрипнул стул... а потом 💨 неловкая пауза 🫢'."
    )
)

async def generate_puk(topic: str = "случайный пук") -> str:
    try:
        chain = prompt_template | llm
        puk = await asyncio.to_thread(chain.invoke, {"topic": topic})
        puk = puk.strip()
        return f"*{puk}*" if puk else "*п-у-к*... ИИ задумался 😴"
    except Exception as e:
        print(f"[LLM ОШИБКА] {e}")
        return "*п-у-к*... Модель отдыхает 💨"

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

# ====================== ОТЛАДКА ======================
def log(message: types.Message, action: str, response: str = None):
    user = f"{message.from_user.full_name} (@{message.from_user.username})" if message.from_user else "Unknown"
    chat = message.chat.title if hasattr(message.chat, 'title') else "ЛС"
    text = message.text or "[не текст]"
    print(f"\n[DEBUG] {action}")
    print(f"   От: {user}")
    print(f"   Чат: {chat} ({message.chat.type}, ID: {message.chat.id})")
    print(f"   Текст: {text}")
    if response:
        print(f"   → Пук: {response}")
    print("-" * 60)

# ====================== КОМАНДЫ ======================
@dp.message(CommandStart())
async def start_private(message: types.Message):
    me = await bot.get_me()
    response = (
        f"Привет! Я — **Пук-бот с ИИ на Render**\n\n"
        f"• Кнопка → ИИ-пук\n"
        f"• В группе: `/puk` → ИИ-пук\n"
        f"• Автопук каждые 30 мин\n\n"
        f"*Llama 3.1 локально!*"
    )
    await message.answer(response, reply_markup=keyboard)
    log(message, "ЛС: /start", response)

@dp.message(F.text == "Пукнуть 💨", F.chat.type == "private")
async def puk_button(message: types.Message):
    puk = await generate_puk()
    await message.answer(puk)
    log(message, "ЛС: Кнопка", puk)

@dp.message(Command("puk"))
async def puk_command(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    await add_group(message.chat.id)
    puk = await generate_puk()
    await message.reply(puk)
    log(message, "ГРУППА: /puk", puk)

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
                    chat = await bot.get_chat(chat_id)
                    print(f"[АВТОПУК] → {chat.title}: {puk}")
                except Exception as e:
                    print(f"[ОШИБКА] {e}")
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