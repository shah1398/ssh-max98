#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import base64
import shutil
import logging
import requests
from pathlib import Path
from ping3 import ping

# ================= CONFIG =================
INPUT_FILE = "input.txt"
PING_DIR = Path("ping")
BASE64_DIR = Path("base64")
LOG_DIR = Path("logs")

PING_COUNT = 3
TIMEOUT = 1
GOOD_MS = 150
WARN_MS = 300
MAX_PER_SUB = 1000

PROTOCOLS = {
    "vless://": "vless",
    "trojan://": "trojan",
    "ss://": "ss",
    "hysteria": "hysteria",
    "tuic://": "tuic",
}

# ================= INIT =================
def reset_all():
    """پاک کردن پوشه‌ها و آماده‌سازی"""
    for d in [PING_DIR, BASE64_DIR, LOG_DIR]:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

reset_all()

logging.basicConfig(
    filename=LOG_DIR / "run.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logging.info("=== START RUN ===")

# ================= HELPERS =================
def extract_host(cfg: str):
    m = re.search(r"@([^:/?#]+)", cfg)
    if m:
        return m.group(1)
    m = re.search(r"://([^:/?#]+)", cfg)
    return m.group(1) if m else None

def avg_ping(host):
    results = []
    for _ in range(PING_COUNT):
        try:
            r = ping(host, timeout=TIMEOUT, unit="ms")
            if r:
                results.append(r)
        except:
            continue
    return sum(results)/len(results) if results else None

def classify(ms):
    if ms is None:
        return "bad"
    if ms <= GOOD_MS:
        return "good"
    if ms <= WARN_MS:
        return "warn"
    return "bad"

def to_base64(text: str):
    return base64.b64encode(text.encode()).decode()

def save(path, data):
    if data:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(data))

# ================= MAIN =================
try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        subs = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    logging.error(f"{INPUT_FILE} not found!")
    exit("Input file not found!")

for idx, sub_url in enumerate(subs, 1):
    sub_name = f"sub{idx}"
    ping_sub = PING_DIR / sub_name
    base64_sub = BASE64_DIR / sub_name
    ping_sub.mkdir()
    base64_sub.mkdir()

    try:
        raw = requests.get(sub_url, timeout=20).text.splitlines()
    except Exception as e:
        logging.error(f"Sub {idx} download failed: {e}")
        continue

    raw = list(dict.fromkeys(raw))  # حذف تکراری‌ها

    good, warn = [], []
    proto_map = {v: [] for v in PROTOCOLS.values()}

    for cfg in raw:
        host = extract_host(cfg)
        if not host:
            continue

        ms = avg_ping(host)
        status = classify(ms)

        if status == "good":
            good.append(cfg)
        elif status == "warn":
            warn.append(cfg)

        if status in ("good", "warn"):
            for p, name in PROTOCOLS.items():
                if cfg.startswith(p):
                    proto_map[name].append(cfg)

    final_cfgs = (good + warn)[:MAX_PER_SUB]

    # ذخیره خروجی پین
    save(ping_sub / "all.txt", final_cfgs)
    save(ping_sub / "good.txt", good)
    save(ping_sub / "warn.txt", warn)
    for proto, data in proto_map.items():
        save(ping_sub / f"{proto}.txt", data)

    # تبدیل Base64
    for txt in ping_sub.glob("*.txt"):
        content = txt.read_text(encoding="utf-8")
        if content.strip():
            out = base64_sub / f"{txt.stem}_base64.txt"
            out.write_text(to_base64(content), encoding="utf-8")

    logging.info(f"Sub {idx}: total={len(raw)} good={len(good)} warn={len(warn)} final={len(final_cfgs)}")

logging.info("=== END RUN ===")
print("Run completed successfully!")
