import os
import asyncio
import random
from datetime import datetime, time

from telethon import TelegramClient, events
from telethon.tl.types import User
import openai

# =======================
# CONFIG FROM ENV
# =======================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# =======================
# SETTINGS
# =======================
WORK_HOURS = (time(9, 0), time(22, 0))
MIN_DELAY = 20
MAX_DELAY = 90
ENABLE_BOT = True

# =======================
# SYSTEM PROMPT
# =======================
SYSTEM_PROMPT = """
Ты — личный секретарь владельца Telegram аккаунта.
Ты отвечаешь от его имени.

Стиль:
— кратко
— без официоза
— по делу
— дружелюбно
— без эмодзи
— не начинай с приветствий

Правила:
— если не уверен, НЕ ОТВЕЧАЙ
— если вопрос личный — НЕ ОТВЕЧАЙ
— если похоже на спам — НЕ ОТВЕЧАЙ
— отвечай только если есть смысл
"""

# =======================
# TELEGRAM CLIENT
# =======================
client = TelegramClient("userbot_session", API_ID, API_HASH)

def is_work_time():
    now = datetime.now().time()
    return WORK_HOURS[0] <= now <= WORK_HOURS[1]

async def ai_answer(text: str):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.4,
        max_tokens=200
    )
    answer = response.choices[0].message.content.strip()
    return answer if len(answer) > 2 else None

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not ENABLE_BOT:
        return

    if not event.is_private:
        return

    sender = await event.get_sender()
    if not isinstance(sender, User):
        return

    if sender.contact:
        return

    if not is_work_time():
        return

    text = event.raw_text.strip()
    if len(text) < 2:
        return

    await asyncio.sleep(random.randint(MIN_DELAY, MAX_DELAY))

    try:
        answer = await ai_answer(text)
        if answer:
            await event.respond(answer)
    except Exception as e:
        print("AI error:", e)

print("🤖 Telegram secretary started")
client.start()
client.run_until_disconnected()
