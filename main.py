import os
import requests
import base64
import threading
import urllib.parse

# ===================== مسیر فایل‌ها =====================
INPUT_FILE = "input.txt"
OUTPUT_DIR = "base64"  # پوشه‌ای که فایل‌ها داخل آن ذخیره می‌شود
MIX_FILE = "base64/mix.txt"  # فایل نهایی mix که تمام داده‌ها در آن ذخیره می‌شود

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
    """خواندن لینک و تبدیل آن به Base64"""
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

def save_to_file(filename, content):
    """ذخیره محتوا در فایل با نام مشخص"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
        print(f"[✔] {filename} saved")

def get_filename_from_link(link):
    """گرفتن نام فایل از آخرین بخش لینک"""
    # استخراج آخرین بخش URL
    filename = link.split("/")[-1]
    
    # بررسی اینکه آیا پسوند txt دارد یا نه
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)  # جدا کردن نام و پسوند
        if ext != "txt":  # اگر پسوند غیر از txt بود، آن را به .txt تغییر می‌دهیم
            return f"{name}.txt"
        else:
            return filename  # اگر پسوند txt داشت، همان را استفاده می‌کنیم
    else:
        return f"{filename}.txt"  # اگر پسوند نداشت، .txt به نام اضافه می‌شود

def process_subs(links):
    """پردازش تمام لینک‌ها و ساخت فایل‌ها"""
    results = []
    threads = []

    # پردازش لینک‌ها به صورت موازی
    for link in links:
        t = threading.Thread(target=process_link, args=(link, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # حذف خطوط تکراری
    final_results = list(dict.fromkeys(results))

    # بررسی و ساخت پوشه base64 در صورت عدم وجود
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # ذخیره فایل‌ها
    for result in final_results:
        filename = get_filename_from_link(result)
        file_path = os.path.join(OUTPUT_DIR, filename)
        # ذخیره هر ساب در فایل مربوطه
        save_to_file(file_path, result)

    # ساخت فایل mix.txt که شامل تمام داده‌ها باشد
    with open(MIX_FILE, "w", encoding="utf-8") as mix_file:
        mix_file.write("\n".join(final_results))
        print(f"[✔] {MIX_FILE} saved")

# ===================== اجرای اصلی کد =====================
if __name__ == "__main__":
    # خواندن لینک‌ها از فایل input.txt
    links = []
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            links.extend([line.strip() for line in f if line.strip()])

    print(f"[*] Total sources to fetch: {len(links)}")

    # پردازش ساب‌ها و ذخیره فایل‌ها
    process_subs(links)

    print("[✅] All subs processed successfully.")
