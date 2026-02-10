#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, base64
from ping3 import ping

# ================= PATHS =================
BASE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(BASE, "input.txt")
PING_OUT = os.path.join(BASE, "ping.txt")
BASE64_FINAL = os.path.join(BASE, "base64.txt")
BASE64_DIR = os.path.join(BASE, "base64_output")
os.makedirs(BASE64_DIR, exist_ok=True)

PROTO_FILES = {
    "vless": "vless.txt",
    "trojan": "trojan.txt",
    "ss": "ss.txt",
    "hysteria": "hysteria.txt",
    "tuic": "tuic.txt",
}

# ================= PIN SETTINGS (FIXED) =================
GOOD = 150
WARN = 300
TIMEOUT = 1
COUNT = 3

# ================= RESET =================
open(PING_OUT, "w").close()
open(BASE64_FINAL, "w").close()

for f in PROTO_FILES.values():
    open(os.path.join(BASE, f), "w").close()

for f in os.listdir(BASE64_DIR):
    os.remove(os.path.join(BASE64_DIR, f))

# ================= HELPERS =================
def host(cfg):
    m = re.search(r"@([^:/?#]+)", cfg)
    return m.group(1) if m else None

def ping_host(h):
    r = []
    for _ in range(COUNT):
        try:
            p = ping(h, timeout=TIMEOUT, unit="ms")
            if p: r.append(p)
        except: pass
    return sum(r)/len(r) if r else None

def status(ms):
    if ms is None: return None
    if ms <= GOOD: return "GOOD"
    if ms <= WARN: return "WARN"
    return None

# ================= READ INPUT =================
with open(INPUT, encoding="utf-8") as f:
    subs = list(dict.fromkeys(l.strip() for l in f if l.strip()))

good_cfgs = []
proto_data = {k: [] for k in PROTO_FILES}

# ================= PIN PROCESS =================
for cfg in subs:
    h = host(cfg)
    if not h: continue
    ms = ping_host(h)
    s = status(ms)
    if not s: continue

    good_cfgs.append(f"[{s}] {cfg}")

    if cfg.startswith("vless://"): proto_data["vless"].append(cfg)
    elif cfg.startswith("trojan://"): proto_data["trojan"].append(cfg)
    elif cfg.startswith("ss://"): proto_data["ss"].append(cfg)
    elif cfg.startswith("hysteria"): proto_data["hysteria"].append(cfg)
    elif cfg.startswith("tuic://"): proto_data["tuic"].append(cfg)

# ================= SAVE PIN OUTPUT =================
with open(PING_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(good_cfgs))

for k, v in proto_data.items():
    with open(os.path.join(BASE, PROTO_FILES[k]), "w", encoding="utf-8") as f:
        f.write("\n".join(v))

# ================= BASE64 CONVERT =================
all_b64 = []

def b64(file):
    with open(file, encoding="utf-8") as f:
        d = f.read().strip()
    if not d: return
    b = base64.b64encode(d.encode()).decode()
    out = os.path.join(BASE64_DIR, os.path.basename(file).replace(".txt","_base64.txt"))
    with open(out, "w") as o: o.write(b)
    all_b64.append(b)

b64(PING_OUT)
for f in PROTO_FILES.values():
    b64(os.path.join(BASE, f))

with open(BASE64_FINAL, "w") as f:
    f.write("\n".join(all_b64))
