#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from ping3 import ping

# ==================== PATHS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "input.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "ping.txt")

# پروتکل‌ها
PROTOCOL_FILES = {
    "vless": os.path.join(BASE_DIR, "vless.txt"),
    "trojan": os.path.join(BASE_DIR, "trojan.txt"),
    "ss": os.path.join(BASE_DIR, "ss.txt"),
    "hysteria": os.path.join(BASE_DIR, "hysteria.txt"),
    "tuic": os.path.join(BASE_DIR, "tuic.txt"),
}

# ==================== FIXED SETTINGS ====================
VALID_PING_MIN = 1
VALID_PING_MAX = 1500
GOOD_THRESHOLD = 150
WARN_THRESHOLD = 300
TIMEOUT = 1
PING_COUNT = 3

# ==================== HELPERS ====================
def extract_host(cfg: str):
    m = re.search(r"@([^:/?#\s]+)", cfg)
    if m:
        return m.group(1)
    m = re.search(r"://([^:/?#\s]+)", cfg)
    return m.group(1) if m else None

def ping_host(host):
    results = []
    for _ in range(PING_COUNT):
        try:
            r = ping(host, timeout=TIMEOUT, unit="ms")
            if r is not None:
                results.append(r)
        except Exception:
            pass
    return sum(results)/len(results) if results else None

def classify(avg):
    if avg is None:
        return "bad"
    if VALID_PING_MIN <= avg <= GOOD_THRESHOLD:
        return "good"
    if avg <= WARN_THRESHOLD:
        return "warn"
    return "bad"

def save(path, data):
    if data:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(data))

# ==================== RESET OUTPUT ====================
open(OUTPUT_FILE, "w", encoding="utf-8").close()
for f in PROTOCOL_FILES.values():
    open(f, "w", encoding="utf-8").close()

# ==================== READ INPUT ====================
if not os.path.exists(INPUT_FILE):
    print("[ERROR] input.txt not found")
    exit(1)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# حذف تکراری‌ها
configs = list(dict.fromkeys(lines))

# ==================== PROCESS ====================
ping_results = []
protocol_lists = {k: [] for k in PROTOCOL_FILES.keys()}

for idx, cfg in enumerate(configs, start=1):
    host = extract_host(cfg)
    if not host:
        continue
    avg = ping_host(host)
    status = classify(avg)
    if status == "bad":
        continue  # رد کانفیگ خراب
    # برچسب سبز/زرد
    label = "[GOOD]" if status=="good" else "[WARN]"
    ping_results.append(f"{label} {cfg}")

    # دسته‌بندی پروتکل
    if cfg.startswith("vless://"):
        protocol_lists["vless"].append(cfg)
    elif cfg.startswith("trojan://"):
        protocol_lists["trojan"].append(cfg)
    elif cfg.startswith("ss://") or cfg.startswith("ssss://"):
        protocol_lists["ss"].append(cfg)
    elif cfg.startswith("hysteria://") or cfg.startswith("hysteria2://"):
        protocol_lists["hysteria"].append(cfg)
    elif cfg.startswith("tuic://"):
        protocol_lists["tuic"].append(cfg)

    # هر ساب جداگانه
    sub_file = os.path.join(BASE_DIR, f"sub{idx}.txt")
    save(sub_file, [f"{label} {cfg}"])

# ==================== SAVE FINAL OUTPUTS ====================
save(OUTPUT_FILE, ping_results)
for proto, path in PROTOCOL_FILES.items():
    save(path, protocol_lists[proto])

print("[✓] Pinning completed successfully")
print(f"[✓] Main output: {OUTPUT_FILE}")
for proto, path in PROTOCOL_FILES.items():
    print(f"[✓] {proto} output: {path}")
