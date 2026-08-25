#!/usr/bin/env python3
"""
IndexNow ping — notify Bing/Yandex/Seznam/Naver of the N newest idiom pages.

Google does NOT use IndexNow; this gets instant crawling on Bing / Yahoo /
DuckDuckGo instead, which is real traffic while Google ramps a new domain.

Usage: python3 scripts/indexnow_ping.py [count] [--all]
  count  : ping the N newest idiom pages (default 10)
  --all  : ping every page in idioms.json (one-time backfill)
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DOMAIN = "https://chinese-idioms.top"
PING_URL = "https://api.indexnow.org/indexnow"
KEY_FILE = BASE_DIR / "data" / "indexnow_key.txt"


def main():
    args = sys.argv[1:]
    ping_all = "--all" in args
    count = 10
    for a in args:
        if a.isdigit():
            count = int(a)

    if not KEY_FILE.exists():
        print("ERROR: no indexnow key at", KEY_FILE)
        sys.exit(1)
    key = KEY_FILE.read_text().strip()

    with open(BASE_DIR / "idioms" / "idioms.json", encoding="utf-8") as f:
        idioms = json.load(f)

    # Newest first (id is roughly insertion-ordered; prefer stable order by last)
    pages = idioms if ping_all else idioms[-count:]
    urls = [f"{DOMAIN}/idiom/{i['id']}.html" for i in pages]

    # IndexNow accepts GET with urlList (up to 10k) — POST body is cleaner for many URLs
    payload = json.dumps({"host": "chinese-idioms.top", "key": key, "urlList": urls}).encode()
    req = urllib.request.Request(
        PING_URL,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"IndexNow OK: HTTP {resp.status}, {len(urls)} URLs")
            return 0
    except urllib.error.HTTPError as e:
        print(f"IndexNow ERROR: HTTP {e.code} — {e.read().decode()[:300]}")
        return 1
    except Exception as e:
        print(f"IndexNow ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
