#!/usr/bin/env python3
import os
import json
import base64
import requests
from collections import defaultdict

# ================== PATHS ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "input.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "base64.txt")

# ================== HELPERS ==================
def b64e(s: str) -> str:
    return base64.b64encode(s.encode()).decode()

def fix_vmess(link):
    try:
        raw = link.replace("vmess://", "")
        j = json.loads(base64.b64decode(raw + "===").decode())
        clean = json.dumps(j, separators=(",", ":"))
        return "vmess://" + b64e(clean)
    except Exception:
        return None

def fix_ss(link):
    try:
        raw = link.replace("ss://", "").split("#")[0]
        base64.b64decode(raw + "===")
        return "ss://" + raw
    except Exception:
        try:
            return "ss://" + b64e(raw)
        except Exception:
            return None

def normalize(line):
    line = line.strip()
    if not line:
        return None, None

    if line.startswith("vmess://"):
        return "vmess", fix_vmess(line)
    if line.startswith("ss://"):
        return "ss", fix_ss(line)
    if line.startswith("vless://"):
        return "vless", line
    if line.startswith("trojan://"):
        return "trojan", line
    if line.startswith("hysteria://"):
        return "hysteria", line
    if line.startswith("hysteria2://"):
        return "hysteria2", line
    if line.startswith("tuic://"):
        return "tuic", line
    if line.startswith("socks://"):
        return "socks", line
    if line.startswith("http://") or line.startswith("https://"):
        return "http", line
    return None, None

# ================== CORE ==================
def read_input_links():
    if not os.path.exists(INPUT_FILE):
        print("[Error] input.txt not found")
        return []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_subscription(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text.splitlines()
    except Exception as e:
        print(f"[Skip] Failed to fetch {url} -> {e}")
        return []

# ================== RUN ==================
def main():
    # پاکسازی همه خروجی‌ها
    for f in os.listdir(BASE_DIR):
        if f.startswith("base64") and f.endswith(".txt"):
            open(os.path.join(BASE_DIR, f), "w", encoding="utf-8").close()
        elif f.endswith(".txt") and f not in ["input.txt", "base.txt"]:
            open(os.path.join(BASE_DIR, f), "w", encoding="utf-8").close()

    # دیکشنری برای دسته‌بندی پروتکل‌ها
    protocols_dict = defaultdict(list)

    links = read_input_links()
    if not links:
        print("[Error] No subscription links found")
        return

    for idx, link in enumerate(links, start=1):
        lines = fetch_subscription(link)
        processed_lines = []
        count_valid = 0

        for line in lines:
            proto, norm = normalize(line)
            if norm:
                processed_lines.append(norm)
                protocols_dict[proto].append(norm)
                count_valid += 1

        if not processed_lines:
            print(f"[Skip] Subscription {idx} invalid or empty")
            continue

        # Base64 ساب
        raw_text = "\n".join(processed_lines)
        b64_text = base64.b64encode(raw_text.encode()).decode()

        # نوشتن در فایل اصلی
        with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
            out.write(f"===== SUBSCRIPTION {idx} =====\n")
            out.write(b64_text + "\n\n")

        # فایل جدا برای ساب
        sub_file = os.path.join(BASE_DIR, f"base64_{idx}.txt")
        with open(sub_file, "w", encoding="utf-8") as f:
            f.write(b64_text)

        print(f"[✓] Subscription {idx} processed ({count_valid} configs)")

    # دسته‌بندی پروتکل‌ها و ذخیره جداگانه
    for proto, lines in protocols_dict.items():
        proto_file = os.path.join(BASE_DIR, f"{proto}.txt")
        if lines:
            joined = "\n".join(lines)
            b64_proto = base64.b64encode(joined.encode()).decode()
            with open(proto_file, "w", encoding="utf-8") as f:
                f.write(b64_proto)
            print(f"[✓] Protocol {proto} saved ({len(lines)} configs)")

    print("[✓] All done.")

if __name__ == "__main__":
    main()
