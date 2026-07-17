#!/usr/bin/env python3
"""Create GitHub repo and push code."""
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

TOKEN = "***"
REPO_NAME = "chinese-idiom-dict"
DESCRIPTION = "A free English-language reference for classical Chinese idioms (成语). Programmatic SEO site targeting long-tail translation queries."
PROJECT_DIR = Path("/Users/zhangyunyi/projects/idiom-dict")

def api_call(url, method="GET", data=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode()
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

# Step 1: Verify token & get username
print("Step 1: Verifying token...")
status, user = api_call("https://api.github.com/user")
if status != 200:
    print(f"FAIL: Token invalid ({status}): {user}")
    raise SystemExit(1)
username = user["login"]
print(f"  ✓ Token valid. Logged in as: {username}")

# Step 2: Check if repo exists
print(f"\nStep 2: Checking if {username}/{REPO_NAME} exists...")
status, existing = api_call(f"https://api.github.com/repos/{username}/{REPO_NAME}")
if status == 200:
    print(f"  ! Repo already exists. Will use existing.")
    repo_url = existing["clone_url"]
    html_url = existing["html_url"]
elif status == 404:
    print(f"  → Creating new public repo...")
    status, created = api_call(
        "https://api.github.com/user/repos",
        method="POST",
        data={
            "name": REPO_NAME,
            "description": DESCRIPTION,
            "private": False,
            "has_issues": True,
            "has_pages": True,
            "has_wiki": False,
            "auto_init": False,
        }
    )
    if status not in (200, 201):
        print(f"FAIL: Could not create repo ({status}): {created}")
        raise SystemExit(1)
    repo_url = created["clone_url"]
    html_url = created["html_url"]
    print(f"  ✓ Created: {html_url}")
else:
    print(f"FAIL: Unexpected status {status}: {existing}")
    raise SystemExit(1)

print(f"\nRepo URL: {html_url}")
print(f"Clone URL: {repo_url}")

# Step 3: Configure git remote (using token in URL for auth)
print("\nStep 3: Configuring git remote...")
# Remove old remote if exists
subprocess.run(["git", "config", "user.name", "absg"], cwd=PROJECT_DIR, check=True)
subprocess.run(["git", "config", "user.email", "zyunyi0612@gmail.com"], cwd=PROJECT_DIR, check=True)
subprocess.run(["git", "remote", "remove", "origin"], cwd=PROJECT_DIR, capture_output=True)

# Use token-embedded URL (will be cleaned after push)
authed_url = f"https://{username}:{TOKEN}@github.com/{username}/{REPO_NAME}.git"
subprocess.run(["git", "remote", "add", "origin", authed_url], cwd=PROJECT_DIR, check=True)
print("  ✓ Remote 'origin' configured")

# Step 4: Push
print("\nStep 4: Pushing code to GitHub...")
result = subprocess.run(
    ["git", "push", "-u", "origin", "main"],
    cwd=PROJECT_DIR,
    capture_output=True,
    text=True,
)
print(f"  stdout: {result.stdout}")
if result.stderr:
    print(f"  stderr: {result.stderr}")
if result.returncode != 0:
    print(f"FAIL: push failed with code {result.returncode}")
    raise SystemExit(1)
print("  ✓ Push successful")

# Step 5: Clean up — remove token from remote URL
print("\nStep 5: Cleaning up token from git config...")
clean_url = f"https://github.com/{username}/{REPO_NAME}.git"
subprocess.run(["git", "remote", "set-url", "origin", clean_url], cwd=PROJECT_DIR, check=True)
print("  ✓ Token removed from git config (remote URL now plain HTTPS)")

# Final
print("\n" + "=" * 60)
print(f"🎉 SUCCESS! Code pushed to GitHub.")
print(f"   Repo: {html_url}")
print(f"   User: {username}")
print("=" * 60)
print("\nNext steps:")
print(f"  1. Visit {html_url} to verify the code is there")
print(f"  2. Go to https://pages.cloudflare.com to deploy")
print(f"     - Connect GitHub account")
print(f"     - Select {username}/{REPO_NAME}")
print(f"     - Build output directory: public")
print(f"     - Deploy — get a free *.pages.dev URL")
print("\nOr use GitHub Pages:")
print(f"  - Visit {html_url}/settings/pages")
print(f"  - Source: Deploy from branch")
print(f"  - Branch: main, folder: /public")
print(f"  - Site will be at https://{username}.github.io/{REPO_NAME}/")
