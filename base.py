#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import base64
import urllib.parse

INPUT_FILE = "input.txt"
OUTPUT_DIR = "base64"

def fetch_url(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text.strip()
    except Exception as e:
        print(f"[⚠️] Cannot fetch {url}: {e}")
    return None

def safe_base64_encode(text):
    try:
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    except:
        return None

def is_valid_line(line):
    line = line.strip()
    if not line or len(line) < 5:
        return False
    lower = line.lower()
    if "pin=0" in lower or "pin=red" in lower or "pin=قرمز" in lower:
        return False
    return True

def parse_line(line):
    try:
        return urllib.parse.unquote(line.strip())
    except:
        return None

def main():
    if not os.path.exists(INPUT_FILE):
        print("input.txt not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    print(f"[*] Total sources to fetch: {len(links)}")

    sab_counter = 1

    for link in links:
        content = fetch_url(link)
        if not content:
            continue

        results = []
        lines = content.splitlines()

        for line in lines:
            if not is_valid_line(line):
                continue
            parsed = parse_line(line)
            if parsed:
                encoded = safe_base64_encode(parsed)
                if encoded:
                    results.append(encoded)

        if results:
            output_path = os.path.join(OUTPUT_DIR, f"sab{sab_counter}.txt")
            with open(output_path, "w", encoding="utf-8") as out:
                out.write("\n".join(results))
            print(f"[✔] sab{sab_counter}.txt saved ({len(results)} lines)")
            sab_counter += 1

    print("[✅] Done.")

if __name__ == "__main__":
    main()
