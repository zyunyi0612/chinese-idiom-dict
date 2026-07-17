#!/usr/bin/env python3
"""Verify GitHub token works. Reads from local secrets file."""
import json, os, ssl, urllib.request

TOKEN_PATH = "/Users/zhangyunyi/.hermes/profiles/freelancer/.secrets/github_token.txt"

with open(TOKEN_PATH) as f:
    token = f.read().strip()

print(f"Token: {len(token)} chars, starts: {token[:8]}, ends: ...{token[-4:]}")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    "https://api.github.com/user",
    headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"}
)
try:
    resp = urllib.request.urlopen(req, context=ctx)
    d = json.loads(resp.read())
    print(f"OK: user={d['login']}, name={d.get('name','')}")
except urllib.error.HTTPError as e:
    print(f"FAIL: HTTP {e.code} - {e.read().decode()[:200]}")
except Exception as e:
    print(f"FAIL: {e}")