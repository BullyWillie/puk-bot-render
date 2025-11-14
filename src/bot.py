# Bot.py — ПУК-БОТ БЕЗ ИИ (Render, 1 час, 50+ пуков)
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
ADMIN_ID = 1015269859   # ← ЗАМЕНИ НА СВОЙ ID (узнай через @userinfobot)

# ====================== 50+ ПУКОВ ======================
PUKS = [
    "*п-у-к*... я здесь! 😈", "Тегнули — пукнул! *пук!*", "О, меня звали? *пууук*",
    "Пук по вызову! 🚑", "Тег = пук. Закон.", "Кнопка нажата — *пук!*",
    "Автопук активирован! 💨", "💨 *ветерок*... это был я", "Стул скрипнул... а потом *пук!* 🪑",
    "В комнате повисла тишина... *п-у-к* 🫢", "Пукнул и сказал: 'Это был ветер!' 🌬️",
    "💨 *облачко*... кто-то пукнул", "Пук в тишине — самый громкий 🔇",
    "Слышали? Это был *пук-сигнал* 📡", "Пукнул — и все поняли, кто босс 💪",
    "💨 *аромат*... свежий пук", "Пук по расписанию! ⏰", "Кто-то пукнул... это я! 😏",
    "Пукнул в лифте — все вышли на 3-м 🛗", "💨 *пссст*... не говори никому",
    "Пукнул — и сказал: 'Это кофе!' ☕", "Ветер? Нет, это *пук!* 🌪️",
    "Пукнул так тихо, что никто не заметил... почти 🤫", "💨 *дымок*... пук-мастер на связи",
    "Пукнул — и все засмеялись 😂", "Пук по команде! 🫡", "💨 *взрыв*... маленький, но гордый",
    "Пукнул в библиотеке — выгнали 📚", "Кто пукнул? *Я!* 👈", "💨 *пузырь*... лопнул",
    "Пукнул — и сказал: 'Это был ИИ!' 🤖", "Пук по-английски: *toot!* 🇬🇧",
    "💨 *ароматерапия*... пук-терапия", "Пукнул в метро — все в масках 😷",
    "Пукнул — и все поняли: обед был тяжёлый 🍔", "💨 *облако*... пук-облако",
    "Пукнул в Zoom — все выключили камеры 📹", "Пук по-русски: *пууук!* 🇷🇺",
    "💨 *ветер перемен*... пук-перемен", "Пукнул — и сказал: 'Это был чай!' 🍵",
    "Пук в тишине — как гром ⚡", "💨 *пффф*... пук-шепот",
    "Пукнул — и все сделали вид, что ничего не было 🙈", "Пук по расписанию: 1 в час! ⏰",
    "💨 *дыхание дракона*... пук-дракон", "Пукнул в машине — окна вниз! 🚗",
    "Пукнул — и сказал: 'Это был кот!' 🐱", "💨 *пшшш*... пук-шипение",
    "Пукнул в кино — все вышли на попкорн 🍿", "Пук по-немецки: *furz!* 🇩🇪",
    "💨 *пук-сигнал*... SOS", "Пукнул — и все поздоровались 👋"
]

# ====================== КЛАВИАТУРА ======================
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Группы 📋"), KeyboardButton(text="Пукнуть 💨")]],
    resize_keyboard=True
)

# ====================== БОТ ======================
default = DefaultBotProperties(parse_mode="Markdown")
bot = Bot(token=API_TOKEN, default=default)
dp = Dispatcher()

DB_NAME = "groups.db"

# ====================== БАЗА ======================
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
        "**Пук-бот — панель управления**\n\n"
        "• `Группы` — список чатов\n"
        "• `Пукнуть` — пук в ЛС\n"
        "• Автопук: 1 раз в час\n"
        "• В группах: `/puk`",
        reply_markup=admin_keyboard
    )

@dp.message(F.text == "Группы 📋", F.from_user.id == ADMIN_ID)
async def list_groups(message: types.Message):
    groups = await get_groups()
    if not groups:
        await message.answer("Нет активных групп.")
        return
    text = "**Активные группы:**\n\n"
    for i, (chat_id, title) in enumerate(groups, 1):
        text += f"{i}. `{title}` (`{chat_id}`)\n"
    text += "\nНапиши: `/leave 123456789` — выйти из группы"
    await message.answer(text)

@dp.message(Command("leave"), F.from_user.id == ADMIN_ID)
async def leave_group(message: types.Message):
    try:
        chat_id = int(message.text.split()[1])
        await bot.leave_chat(chat_id)
        await remove_group(chat_id)
        await message.answer(f"Вышел из группы `{chat_id}`")
    except:
        await message.answer("Использование: `/leave ЧАТ_ID`")

@dp.message(F.text == "Пукнуть 💨", F.from_user.id == ADMIN_ID)
async def puk_admin(message: types.Message):
    puk = random.choice(PUKS)
    await message.answer(puk)

# ====================== ГРУППА: /puk ======================
@dp.message(Command("puk"))
async def puk_command(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    await add_group(message.chat.id, message.chat.title or "Без названия")
    puk = random.choice(PUKS)
    await message.reply(puk)

# ====================== АВТОПУК ======================
async def auto_puk_task():
    await asyncio.sleep(10)
    print("Автопук запущен (1 раз в час)")
    while True:
        groups = await get_groups()
        if groups:
            puk = random.choice(PUKS)
            for chat_id, title in groups:
                try:
                    await bot.send_message(chat_id, puk)
                    print(f"[АВТОПУК] → {title}")
                except Exception as e:
                    print(f"[ОШИБКА] {chat_id}: {e}")
        await asyncio.sleep(PUK_INTERVAL)

# ====================== ЗАПУСК ======================
async def main():
    await init_db()
    asyncio.create_task(auto_puk_task())
    print("Пук-бот запущен!")
    await dp.start_polling(bot, polling_timeout=30)

if __name__ == '__main__':
    asyncio.run(main())