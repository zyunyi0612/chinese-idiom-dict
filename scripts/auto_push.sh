#!/bin/bash
# Push chinese-idiom-dict changes to GitHub using token from local secrets file.
# Reads token from ~/.hermes/profiles/freelancer/.secrets/github_token.txt
# Never echoes the token to logs or process listings.

set -e

REPO_DIR="/Users/zhangyunyi/projects/idiom-dict"
TOKEN_FILE="$HOME/.hermes/profiles/freelancer/.secrets/github_token.txt"

# Resolve HOME for cron context (cron uses minimal env)
if [ ! -f "$TOKEN_FILE" ]; then
    TOKEN_FILE="/Users/zhangyunyi/.hermes/profiles/freelancer/.secrets/github_token.txt"
fi

if [ ! -f "$TOKEN_FILE" ]; then
    echo "ERROR: Token file not found at $TOKEN_FILE"
    exit 1
fi

# Read token into variable (not exposed)
TOKEN=$(cat "$TOKEN_FILE" | tr -d '\n\r ')

cd "$REPO_DIR"

# Check if there are changes to commit
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to push."
    exit 0
fi

# Configure git for this session
git config http.proxy http://127.0.0.1:7897
git config https.proxy http://127.0.0.1:7897

# Use token in remote URL (transient — reset after push)
ORIGINAL_REMOTE=$(git remote get-url origin)
git remote set-url origin "https://${TOKEN}@github.com/zyunyi0612/chinese-idiom-dict.git"

# Mask token in any output (escape special chars for sed)
function safe_git() {
    local escaped_token=$(printf '%s\n' "$TOKEN" | sed 's/[[\.*^$(){}?+|/]/\\&/g')
    git "$@" 2>&1 | sed "s|${escaped_token}|***TOKEN***|g"
}

# Commit and push
git add -A
safe_git commit -m "Auto-update: $(date +'%Y-%m-%d %H:%M') — regenerate idioms" || echo "Nothing to commit"

if safe_git push origin main; then
    echo "Push OK"
else
    echo "Push FAILED"
    git remote set-url origin "$ORIGINAL_REMOTE"
    exit 1
fi

# Reset remote to clean URL (no token)
git remote set-url origin "$ORIGINAL_REMOTE"
git config --unset http.proxy 2>/dev/null || true
git config --unset https.proxy 2>/dev/null || true

echo "Done. Remote reset to clean URL."