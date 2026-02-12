#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import base64
import threading
import urllib.parse
import socket

# ===================== مسیر فایل‌ها =====================
INPUT_FILE = "input.txt"
OUTPUT_FILE = "base64.txt"

# ===================== توابع =====================

def fetch_url(url):
    """خواندن محتوا از لینک با timeout و کنترل خطا"""
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text.strip()
    except Exception as e:
        print(f"[⚠️] Cannot fetch {url}: {e}")
    return None

def safe_base64_encode(text):
    """تبدیل متن به Base64 استاندارد"""
    try:
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"[⚠️] Base64 encode error: {e}")
        return None

def is_valid_line(line):
    """بررسی خط خراب یا ناقص"""
    line = line.strip()
    if not line or len(line) < 5:
        return False
    lower = line.lower()
    if "pin=0" in lower or "pin=red" in lower or "pin=قرمز" in lower:
        return False
    return True

def parse_line(line):
    """تبدیل لینک یا خط به فرمت استاندارد قبل Base64"""
    try:
        decoded = urllib.parse.unquote(line.strip())
        return decoded
    except:
        return None

def process_link(link, results):
    content = fetch_url(link)
    if content:
        lines = content.splitlines()
        for line in lines:
            if not is_valid_line(line):
                continue
            parsed = parse_line(line)
            if parsed:
                encoded = safe_base64_encode(parsed)
                if encoded:
                    results.append(encoded)

def main():
    # ریست کردن فایل خروجی
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")

    # خواندن لینک‌ها از input.txt
    links = []
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            links.extend([line.strip() for line in f if line.strip()])

    print(f"[*] Total sources to fetch: {len(links)}")

    results = []
    threads = []

    for link in links:
        t = threading.Thread(target=process_link, args=(link, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # حذف خطوط تکراری
    final_results = list(dict.fromkeys(results))

    # ذخیره نهایی
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_results))

    print(f"[✅] Done. Total valid Base64 lines: {len(final_results)}")
    print(f"  -> Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
