#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import base64
import shutil
import requests
from pathlib import Path
from ping3 import ping

# ===================== PATHS =====================
ROOT = Path(__file__).parent
INPUT_FILE = ROOT / "input.txt"

PING_DIR = ROOT / "ping"
BASE64_DIR = ROOT / "base64"

# ===================== RESET =====================
for d in [PING_DIR, BASE64_DIR]:
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True, exist_ok=True)

# ===================== PING SETTINGS (FIXED) =====================
GOOD_THRESHOLD = 150
WARN_THRESHOLD = 300
TIMEOUT = 1
PING_COUNT = 3

# ===================== HELPERS =====================
def extract_host(cfg: str):
    m = re.search(r"@([^:/?#\s]+)", cfg)
    if m:
        return m.group(1)
    m = re.search(r"://([^:/?#\s]+)", cfg)
    return m.group(1) if m else None

def avg_ping(host):
    res = []
    for _ in range(PING_COUNT):
        try:
            r = ping(host, timeout=TIMEOUT, unit="ms")
            if r:
                res.append(r)
        except Exception:
            pass
    return sum(res)/len(res) if res else None

def ping_status(ms):
    if ms is None:
        return "bad"
    if ms < GOOD_THRESHOLD:
        return "good"
    if ms < WARN_THRESHOLD:
        return "warn"
    return "bad"

def normalize_protocol(line):
    line = line.strip()
    if not line:
        return None
    prefixes = (
        "vless://", "vmess://", "trojan://",
        "ss://", "ssss://", "hysteria://",
        "hysteria2://", "tuic://",
        "socks://", "http://", "https://"
    )
    return line if line.startswith(prefixes) else None

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

def normalize_for_base(line):
    if line.startswith("vmess://"):
        return fix_vmess(line)
    if line.startswith("ss://"):
        return fix_ss(line)
    return line

# ===================== LOAD SUB LINKS =====================
if not INPUT_FILE.exists():
    raise SystemExit("input.txt not found")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    sub_links = [l.strip() for l in f if l.strip()]

# ===================== PROCESS EACH SUB =====================
for idx, sub in enumerate(sub_links, start=1):
    try:
        r = requests.get(sub, timeout=20)
        r.raise_for_status()
        raw_lines = r.text.splitlines()
    except Exception:
        continue

    seen = set()
    configs = []

    for l in raw_lines:
        n = normalize_protocol(l)
        if n and n not in seen:
            seen.add(n)
            configs.append(n)

    sub_dir = PING_DIR / f"sub_{idx}"
    sub_dir.mkdir(exist_ok=True)

    good, warn, all_cfg = [], [], []
    proto_map = {}

    for cfg in configs:
        host = extract_host(cfg)
        status = "bad"
        if host:
            ms = avg_ping(host)
            status = ping_status(ms)

        if status in ("good", "warn"):
            all_cfg.append(cfg)
        if status == "good":
            good.append(cfg)
        if status == "warn":
            warn.append(cfg)

        proto = cfg.split("://")[0]
        proto_map.setdefault(proto, []).append(cfg)

    # save ping outputs
    def save(name, lines):
        if not lines:
            return
        with open(sub_dir / f"{name}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    save("good", good)
    save("warn", warn)
    save("all", all_cfg)

    for p, lst in proto_map.items():
        save(p, lst)

    # ===================== BASE64 CONVERT =====================
    b64_sub = BASE64_DIR / f"sub_{idx}"
    b64_sub.mkdir(exist_ok=True)

    for file in sub_dir.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            lines = []
            for ln in f:
                x = normalize_for_base(ln.strip())
                if x:
                    lines.append(x)

        if not lines:
            continue

        raw = "\n".join(lines)
        encoded = base64.b64encode(raw.encode()).decode()

        with open(b64_sub / file.name, "w", encoding="utf-8") as out:
            out.write(encoded)

print("DONE")
