#!/usr/bin/env python3
"""Enable GitHub Pages. Reads token from /tmp/gh_token.txt"""
import json, ssl, urllib.request

with open("/tmp/gh_token.txt") as f:
    gh_tok = f.read().strip()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

data = json.dumps({"source": {"branch": "main", "path": "/public"}}).encode()
req = urllib.request.Request(
    "https://api.github.com/repos/zyunyi0612/chinese-idiom-dict/pages",
    data=data,
    headers={
        "Authorization": "Bearer " + gh_tok,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json"
    },
    method="POST"
)
try:
    resp = urllib.request.urlopen(req, context=ctx)
    result = json.loads(resp.read())
    print(f"Pages URL: {result.get('html_url', 'pending...')}")
    print(f"Status: {result.get('status', 'unknown')}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP {e.code}: {body[:300]}")
except Exception as e:
    print(f"Error: {e}")