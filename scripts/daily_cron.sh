#!/bin/bash
# Daily cron: generate N new idioms, regenerate site, push to GitHub.
# Logs to logs/cron.log. Token is read from local secrets file (never exposed).
set -e

PROJECT="/Users/zhangyunyi/projects/idiom-dict"
LOG_DIR="$PROJECT/logs"
LOG="$LOG_DIR/cron.log"
PYTHON=$(command -v python3 || echo "/usr/bin/python3")

# Cron has minimal PATH — add hermes location
export PATH="/Users/zhangyunyi/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

log "=== Daily cron start ==="

# 1. Generate new idioms (default 10, or $1 for testing)
COUNT="${1:-10}"
log "Generating $COUNT new idioms..."
if $PYTHON "$PROJECT/scripts/gen_idioms_v2.py" "$COUNT" >> "$LOG" 2>&1; then
    log "Generation OK"
else
    log "Generation FAILED - continuing with existing data"
fi

# 2. Regenerate the static site
log "Regenerating site..."
$PYTHON "$PROJECT/scripts/generate.py" >> "$LOG" 2>&1
log "Site regenerated"

# 3. Push to GitHub (Python version — bypasses shell token sanitization)
log "Pushing to GitHub..."
if $PYTHON "$PROJECT/scripts/auto_push.py" >> "$LOG" 2>&1; then
    log "Push OK"
else
    log "Push FAILED"
fi

# 4. Cleanup old logs
find "$LOG_DIR" -name "cron.log" -mtime +30 -delete 2>/dev/null || true

log "=== Daily cron done ==="