import base64
import requests
import os

# ==========================
# لینک‌ها به صورت مستقیم داخل کد
# ==========================
input_links = [
    "https://example.com/link1",
    "https://example.com/link2",
    # لینک‌های خودت رو اینجا اضافه کن
]

OUTPUT_FILE = "base64.txt"

def fetch_content(url, timeout=10):
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        content = resp.text.strip()
        try:
            return base64.b64decode(content).decode("utf-8")
        except Exception:
            return content
    except Exception as e:
        print(f"[Error] {url} -> {e}")
        return ""

def merge_and_deduplicate(contents):
    lines = []
    for c in contents:
        lines.extend(c.splitlines())
    unique_lines = list(dict.fromkeys([line.strip() for line in lines if line.strip()]))
    return "\n".join(unique_lines)

def encode_base64(data):
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")

def clear_output(file_path=OUTPUT_FILE):
    if os.path.exists(file_path):
        open(file_path, "w", encoding="utf-8").close()
        print(f"[Info] فایل خروجی پاک شد: {file_path}")

def run_task():
    print("[Info] شروع پردازش...")
    clear_output()
    
    if not input_links:
        print("[Warning] لینک برای پردازش موجود نیست!")
        return

    all_contents = [fetch_content(url) for url in input_links]
    merged = merge_and_deduplicate(all_contents)
    b64_result = encode_base64(merged)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(b64_result)
    
    print(f"[Done] خروجی ساخته شد: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_task()
