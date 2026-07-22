#!/bin/bash
# Catch-up push: only push, don't generate. Runs at noon and 8pm.
# Useful when the 3am push failed (e.g. proxy was down).
# If there's nothing to push, exits silently.

set -e
PROJECT="/Users/zhangyunyi/projects/idiom-dict"
LOG_DIR="$PROJECT/logs"
LOG="$LOG_DIR/cron.log"

export PATH="/Users/zhangyunyi/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
mkdir -p "$LOG_DIR"

# Check if there are unpushed commits
cd "$PROJECT"
UNPUSHED=$(git log --oneline origin/main..HEAD 2>/dev/null | wc -l | tr -d ' ')
if [ "$UNPUSHED" -eq 0 ]; then
    # Nothing to push — exit silently
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Catch-up push start ($UNPUSHED unpushed commits) ===" >> "$LOG"
python3 "$PROJECT/scripts/auto_push.py" >> "$LOG" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Catch-up push done ===" >> "$LOG"
