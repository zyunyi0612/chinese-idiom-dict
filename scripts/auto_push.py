#!/usr/bin/env python3
"""
Push chinese-idiom-dict changes to GitHub.
Reads token from ~/.hermes/profiles/freelancer/.secrets/github_token.txt
Robust against transient proxy/network failures:
  - Probe proxy first, skip gracefully if down
  - Retry up to 3 times with backoff
  - Accumulate commits if push fails (next run will retry)
Token is never echoed in plaintext (masked as ***TOKEN*** in all output).
"""
import os, subprocess, sys, time, datetime, socket

REPO_DIR = "/Users/zhangyunyi/projects/idiom-dict"
TOKEN_PATH = "/Users/zhangyunyi/.hermes/profiles/freelancer/.secrets/github_token.txt"
PROXY = "http://127.0.0.1:7897"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 7897


def mask(text, token):
    return text.replace(token, "***TOKEN***")


def proxy_alive(timeout=2):
    """Check if the local HTTP proxy (Clash/V2Ray) is running."""
    try:
        with socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=timeout):
            return True
    except (socket.timeout, OSError):
        return False


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

    # 2. Probe proxy first — if it's down, skip push entirely (no point retrying)
    if not proxy_alive():
        print(f"WARN: proxy at {PROXY_HOST}:{PROXY_PORT} not running — skipping push.")
        print("Commits will accumulate locally and push on next successful run.")
        return 0  # not a failure, just deferred

    # 3. Check for changes
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        # Nothing new to commit, but there might be unpushed commits — try push anyway
        print("No uncommitted changes, but checking for unpushed commits...")
    else:
        # 4. Commit
        commit_msg = f"Auto-update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} - regenerate idioms"
        subprocess.run(["git", "add", "-A"], check=True)
        r = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)
        print(mask(r.stdout + r.stderr, token))

    # 5. Push with retry (up to 3 attempts, 20s backoff)
    url = f"https://{token}@github.com/zyunyi0612/chinese-idiom-dict.git"
    last_err = ""
    for attempt in range(1, 4):
        # Re-check proxy each attempt (might come back online)
        if not proxy_alive():
            print(f"Attempt {attempt}: proxy down, skipping.")
            time.sleep(5)
            continue

        r = subprocess.run(
            ["git", "-c", f"http.proxy={PROXY}", "-c", f"https.proxy={PROXY}",
             "push", url, "main"],
            capture_output=True, text=True, timeout=120
        )
        output = r.stdout + r.stderr
        print(mask(output, token))

        if r.returncode == 0:
            print(f"Push OK (attempt {attempt})")
            return 0

        last_err = output
        print(f"Attempt {attempt} failed, waiting 20s before retry...")
        time.sleep(20)

    print(f"Push FAILED after 3 attempts. Last error:")
    print(mask(last_err, token))
    print("Commits are retained locally; next cron run will retry automatically.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
