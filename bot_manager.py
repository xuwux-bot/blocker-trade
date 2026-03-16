#!/usr/bin/env python3
import json
import time
import threading
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = "8497903162:AAHltWz1rASaLE5DhDgNCC4y9aLT7edGJeY"
OWNER_ID = 5150403377
DEVICES_FILE = "devices.json"

devices = {}

def load_devices():
    global devices
    try:
        with open(DEVICES_FILE, 'r', encoding='utf-8') as f:
            devices = json.load(f)
    except:
        devices = {}

def save_devices():
    with open(DEVICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(devices, f, indent=2, ensure_ascii=False)

def update_device(dev_id, data):
    if dev_id not in devices:
        devices[dev_id] = {}
    devices[dev_id].update(data)
    devices[dev_id]['last_seen'] = datetime.now().isoformat()
    save_devices()

def cleanup_devices():
    while True:
        time.sleep(10)
        now = datetime.now()
        to_delete = []
        for did, info in devices.items():
            last = datetime.fromisoformat(info.get('last_seen', '2000-01-01'))
            if (now - last).total_seconds() > 30:
                to_delete.append(did)
        for did in to_delete:
            del devices[did]
        save_devices()

threading.Thread(target=cleanup_devices, daemon=True).start()

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != OWNER_ID:
        return
    text = update.message.text.strip()
    parts = text.split()
    if not parts:
        return

    cmd = parts[0].lower()

    if cmd == '/help':
        help_text = (
            "📋 **Доступные команды:**\n\n"
            "**Управление блокировкой трейдов:**\n"
            "`/blocker trade [on|off]` – включить/выключить блокировку на **всех** устройствах.\n"
            "`/blocker trade <имя_устройства> [on|off]` – управление блокировкой на конкретном устройстве.\n\n"
            "**Просмотр устройств:**\n"
            "`/devices` – список всех активных устройств.\n"
            "`/device <имя_устройства>` – подробная информация о конкретном устройстве.\n\n"
            "**Управление файлами на устройствах:**\n"
            "`/file list <устройство>` – показать список файлов в папке блокировщика.\n"
            "`/file get <устройство> <имя_файла>` – скачать файл с устройства.\n"
            "`/file download <устройство> <имя_файла>` – подготовить устройство к приёму файла.\n"
            "`/file start <устройство> <имя_файла>` – запустить скрипт на устройстве.\n"
            "`/file stop <устройство> <имя_файла>` – остановить запущенный файл.\n\n"
            "**Управление консолью:**\n"
            "`/console monitor <устройство> <файл>` – переключить отправку вывода консоли.\n"
            "`/console send <устройство> <файл> <сообщение>` – отправить сообщение в stdin скрипта.\n\n"
            "**Общее:**\n"
            "`/help` – это сообщение."
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')

    elif cmd == '/devices':
        if not devices:
            await update.message.reply_text("Нет активных устройств.")
            return
        text = "📱 **Активные устройства:**\n"
        for did, info in devices.items():
            status = "✅" if info.get('enabled', True) else "❌"
            last = datetime.fromisoformat(info['last_seen']).strftime('%H:%M:%S')
            text += f"\n{status} **{info.get('name', did)}** (IP: {info.get('ip', '?')})\n"
            text += f"   ID: `{did}`\n"
            text += f"   Последний раз: {last}\n"
            text += f"   Заблокировано трейдов: {info.get('total_blocked', 0)}\n"
        await update.message.reply_text(text, parse_mode='Markdown')

    elif cmd == '/device' and len(parts) >= 2:
        target = parts[1]
        target_id = None
        for did, info in devices.items():
            if info.get('name') == target or did == target:
                target_id = did
                break
        if not target_id:
            await update.message.reply_text("❌ Устройство не найдено.")
            return
        await context.bot.send_message(chat_id=OWNER_ID, text=f"/device {target_id}")
        await update.message.reply_text(f"⏳ Запрос информации по устройству `{target}` отправлен.", parse_mode='Markdown')

    elif cmd == '/blocker' and len(parts) >= 2 and parts[1] == 'trade':
        if len(parts) >= 3:
            target_or_cmd = parts[2]
            if target_or_cmd in ('on', 'off'):
                for did in devices:
                    devices[did]['enabled'] = (target_or_cmd == 'on')
                save_devices()
                state = "включена" if target_or_cmd == 'on' else "приостановлена"
                await update.message.reply_text(f"✅ Блокировка {state} на **всех** устройствах.", parse_mode='Markdown')
                for did in devices:
                    await context.bot.send_message(chat_id=OWNER_ID, text=f"/blocker trade {did} {target_or_cmd}")
            else:
                target = target_or_cmd
                target_id = None
                for did, info in devices.items():
                    if info.get('name') == target or did == target:
                        target_id = did
                        break
                if target_id:
                    if len(parts) >= 4:
                        subcmd = parts[3]
                        if subcmd in ('on', 'off'):
                            devices[target_id]['enabled'] = (subcmd == 'on')
                            state = "включена" if subcmd == 'on' else "приостановлена"
                        else:
                            await update.message.reply_text("Используйте on или off, либо опустите для переключения.")
                            return
                    else:
                        current = devices[target_id].get('enabled', True)
                        devices[target_id]['enabled'] = not current
                        state = "включена" if not current else "приостановлена"
                    save_devices()
                    await update.message.reply_text(f"✅ Блокировка на устройстве `{target}` {state}.", parse_mode='Markdown')
                    cmd_state = "on" if devices[target_id]['enabled'] else "off"
                    await context.bot.send_message(chat_id=OWNER_ID, text=f"/blocker trade {target_id} {cmd_state}")
                else:
                    await update.message.reply_text("❌ Устройство не найдено.")
        else:
            for did in devices:
                devices[did]['enabled'] = not devices[did].get('enabled', True)
            save_devices()
            await update.message.reply_text("✅ Состояние блокировки переключено на всех устройствах.")
            for did in devices:
                cmd_state = "on" if devices[did]['enabled'] else "off"
                await context.bot.send_message(chat_id=OWNER_ID, text=f"/blocker trade {did} {cmd_state}")

    elif cmd == '/console' and len(parts) >= 3:
        subcmd = parts[1].lower()
        if len(parts) < 4:
            await update.message.reply_text("Использование: /console monitor <устройство> <файл> или /console send <устройство> <файл> <сообщение>")
            return
        target = parts[2]
        target_id = None
        for did, info in devices.items():
            if info.get('name') == target or did == target:
                target_id = did
                break
        if not target_id:
            await update.message.reply_text("❌ Устройство не найдено.")
            return

        if subcmd == 'monitor' and len(parts) >= 4:
            filename = parts[3]
            keyboard = [
                [InlineKeyboardButton("✅ Включить мониторинг", callback_data=f"console_on|{target_id}|{filename}")],
                [InlineKeyboardButton("❌ Выключить мониторинг", callback_data=f"console_off|{target_id}|{filename}")],
                [InlineKeyboardButton("🔄 Статус", callback_data=f"console_status|{target_id}|{filename}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"Управление мониторингом консоли для файла `{filename}` на устройстве `{target}`:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        elif subcmd == 'send' and len(parts) >= 5:
            filename = parts[3]
            message = ' '.join(parts[4:])
            await context.bot.send_message(chat_id=OWNER_ID, text=f"/console send {target_id} {filename} {message}")
            await update.message.reply_text(f"⏳ Сообщение отправлено в консоль `{filename}` на устройстве `{target}`.", parse_mode='Markdown')

    elif cmd == '/file' and len(parts) >= 3:
        subcmd = parts[1].lower()
        if len(parts) < 3:
            await update.message.reply_text("Использование: /file list <устройство> или /file get <устройство> <имя_файла> или /file download/start/stop <устройство> <имя_файла>")
            return
        target = parts[2]
        target_id = None
        for did, info in devices.items():
            if info.get('name') == target or did == target:
                target_id = did
                break
        if not target_id:
            await update.message.reply_text("❌ Устройство не найдено.")
            return

        if subcmd == 'list':
            await context.bot.send_message(chat_id=OWNER_ID, text=f"/file list {target_id}")
            await update.message.reply_text(f"⏳ Запрос списка файлов отправлен устройству `{target}`.", parse_mode='Markdown')
        elif subcmd == 'get' and len(parts) >= 4:
            filename = parts[3]
            await context.bot.send_message(chat_id=OWNER_ID, text=f"/file get {target_id} {filename}")
            await update.message.reply_text(f"⏳ Запрос файла `{filename}` отправлен устройству `{target}`.", parse_mode='Markdown')
        elif subcmd == 'download' and len(parts) >= 4:
            filename = parts[3]
            await context.bot.send_message(chat_id=OWNER_ID, text=f"/file download {target_id} {filename}")
            await update.message.reply_text(
                f"📤 Отправьте файл с именем **{filename}**.\n"
                f"В подписи к файлу обязательно укажите `{target_id}` (ID устройства).",
                parse_mode='Markdown'
            )
        elif subcmd == 'start' and len(parts) >= 4:
            filename = parts[3]
            await context.bot.send_message(chat_id=OWNER_ID, text=f"/file start {target_id} {filename}")
            await update.message.reply_text(f"⏳ Команда запуска файла `{filename}` отправлена устройству `{target}`.", parse_mode='Markdown')
        elif subcmd == 'stop' and len(parts) >= 4:
            filename = parts[3]
            await context.bot.send_message(chat_id=OWNER_ID, text=f"/file stop {target_id} {filename}")
            await update.message.reply_text(f"⏳ Команда остановки файла `{filename}` отправлена устройству `{target}`.", parse_mode='Markdown')
        else:
            await update.message.reply_text("Неизвестная подкоманда. Используйте list, get, download, start, stop.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split('|')
    if len(data) < 3:
        await query.edit_message_text("Ошибка: неверные данные")
        return
    
    action = data[0]
    target_id = data[1]
    filename = data[2]
    
    if action == 'console_on':
        await context.bot.send_message(chat_id=OWNER_ID, text=f"/console monitor {target_id} {filename} on")
        await query.edit_message_text(f"✅ Мониторинг консоли для `{filename}` включен на устройстве `{target_id}`.", parse_mode='Markdown')
    elif action == 'console_off':
        await context.bot.send_message(chat_id=OWNER_ID, text=f"/console monitor {target_id} {filename} off")
        await query.edit_message_text(f"❌ Мониторинг консоли для `{filename}` выключен на устройстве `{target_id}`.", parse_mode='Markdown')
    elif action == 'console_status':
        await context.bot.send_message(chat_id=OWNER_ID, text=f"/console status {target_id} {filename}")
        await query.edit_message_text(f"⏳ Запрос статуса мониторинга для `{filename}` отправлен устройству `{target_id}`.", parse_mode='Markdown')

def main():
    load_devices()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("help", handle))
    app.add_handler(CommandHandler("devices", handle))
    app.add_handler(CommandHandler("device", handle))
    app.add_handler(CommandHandler("blocker", handle))
    app.add_handler(CommandHandler("file", handle))
    app.add_handler(CommandHandler("console", handle))
    app.add_handler(CallbackQueryHandler(button_callback, pattern='^(console_on|console_off|console_status)\\|'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Бот-менеджер запущен. Ожидание команд...")
    app.run_polling()

if __name__ == "__main__":
    main()
