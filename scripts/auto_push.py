#!/usr/bin/env python3
"""
Push chinese-idiom-dict changes to GitHub.
Reads token from ~/.hermes/profiles/freelancer/.secrets/github_token.txt
Token is never echoed in plaintext (masked as ***TOKEN*** in all output).
"""
import os, subprocess, sys

REPO_DIR = "/Users/zhangyunyi/projects/idiom-dict"
TOKEN_PATH = "/Users/zhangyunyi/.hermes/profiles/freelancer/.secrets/github_token.txt"
PROXY = "http://127.0.0.1:7897"

def mask(text, token):
    return text.replace(token, "***TOKEN***")

def main():
    # 1. Read token
    if not os.path.exists(TOKEN_PATH):
        print(f"ERROR: token file missing at {TOKEN_PATH}")
        return 1
    with open(TOKEN_PATH) as f:
        token = f.read().strip()
    if not token or len(token) < 20:
        print(f"ERROR: token too short ({len(token)} chars)")
        return 1

    os.chdir(REPO_DIR)

    # 2. Check for changes
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("No changes to push.")
        return 0

    # 3. Commit
    import datetime
    commit_msg = f"Auto-update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} — regenerate idioms"
    subprocess.run(["git", "add", "-A"], check=True)
    r = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)
    print(mask(r.stdout + r.stderr, token))
    if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr).lower():
        print("Commit failed, but trying to push anyway...")

    # 4. Push with token in URL (transient, not stored)
    url = f"https://{token}@github.com/zyunyi0612/chinese-idiom-dict.git"
    r = subprocess.run(
        ["git", "-c", f"http.proxy={PROXY}", "-c", f"https.proxy={PROXY}", "push", url, "main"],
        capture_output=True, text=True, timeout=120
    )
    output = r.stdout + r.stderr
    print(mask(output, token))
    if r.returncode == 0:
        print("Push OK")
        return 0
    else:
        print("Push FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())