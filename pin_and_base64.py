#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import base64
from ping3 import ping

# ==================== PATHS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "input.txt")
MAIN_OUTPUT = os.path.join(BASE_DIR, "ping.txt")
BASE64_OUTPUT_DIR = os.path.join(BASE_DIR, "base64_output")
os.makedirs(BASE64_OUTPUT_DIR, exist_ok=True)
FINAL_BASE64_FILE = os.path.join(BASE_DIR, "base64.txt")

# پروتکل‌ها و فایل‌های خروجی آن‌ها
PROTOCOL_FILES = {
    "vless": os.path.join(BASE_DIR, "vless.txt"),
    "trojan": os.path.join(BASE_DIR, "trojan.txt"),
    "ss": os.path.join(BASE_DIR, "ss.txt"),
    "hysteria": os.path.join(BASE_DIR, "hysteria.txt"),
    "tuic": os.path.join(BASE_DIR, "tuic.txt"),
}

# ==================== SETTINGS ====================
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
open(MAIN_OUTPUT, "w", encoding="utf-8").close()
for f in PROTOCOL_FILES.values():
    open(f, "w", encoding="utf-8").close()
# پاکسازی پوشه Base64 خروجی
for f in os.listdir(BASE64_OUTPUT_DIR):
    os.remove(os.path.join(BASE64_OUTPUT_DIR, f))

# ==================== READ INPUT ====================
if not os.path.exists(INPUT_FILE):
    print("[ERROR] input.txt not found")
    exit(1)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# حذف تکراری‌ها
configs = list(dict.fromkeys(lines))

# ==================== STEP 1: PIN CONFIG ====================
print("[*] Starting pinning process...")
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

# ذخیره خروجی اصلی و پروتکل‌ها
save(MAIN_OUTPUT, ping_results)
for proto, path in PROTOCOL_FILES.items():
    save(path, protocol_lists[proto])

print("[✓] Pinning completed. Outputs saved.")

# ==================== STEP 2: BASE64 CONVERT ====================
print("[*] Starting Base64 conversion...")
for file_name in [MAIN_OUTPUT] + list(PROTOCOL_FILES.values()):
    if not os.path.exists(file_name):
        continue
    with open(file_name, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        continue
    # تبدیل Base64
    subscription_b64 = base64.b64encode("\n".join(lines).encode()).decode()
    # ذخیره فایل جداگانه
    output_file = os.path.join(BASE64_OUTPUT_DIR, f"{os.path.basename(file_name).replace('.txt','_base64.txt')}")
    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(subscription_b64)
    print(f"[✓] Base64 created: {output_file}")

# ترکیب همه Base64 ها در یک فایل نهایی
all_lines = []
for file_name in [MAIN_OUTPUT] + list(PROTOCOL_FILES.values()):
    output_file = os.path.join(BASE64_OUTPUT_DIR, f"{os.path.basename(file_name).replace('.txt','_base64.txt')}")
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            all_lines.append(f.read())
with open(FINAL_BASE64_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(all_lines))

print(f"[✓] All Base64 combined in: {FINAL_BASE64_FILE}")
print("[✓] Process completed successfully!")
