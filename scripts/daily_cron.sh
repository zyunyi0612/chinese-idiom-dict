#!/bin/bash
# Daily cron job: generate N new idioms, regenerate site, push to GitHub.
# Logs to ~/projects/idiom-dict/logs/cron.log

set -e

PROJECT="/Users/zhangyunyi/projects/idiom-dict"
LOG_DIR="$PROJECT/logs"
LOG="$LOG_DIR/cron.log"
PYTHON=$(command -v python3 || echo "/usr/bin/python3")

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

log "=== Daily cron start ==="

# 1. Generate new idioms
log "Generating 10 new idioms..."
if $PYTHON "$PROJECT/scripts/gen_idioms.py" 10 >> "$LOG" 2>&1; then
    log "Generation OK"
else
    log "Generation FAILED — continuing with existing data"
fi

# 2. Regenerate the static site
log "Regenerating site..."
$PYTHON "$PROJECT/scripts/generate.py" >> "$LOG" 2>&1
log "Site regenerated"

# 3. Push to GitHub
log "Pushing to GitHub..."
if bash "$PROJECT/scripts/auto_push.sh" >> "$LOG" 2>&1; then
    log "Push OK"
else
    log "Push FAILED"
fi

# 4. Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "cron.log" -mtime +30 -delete 2>/dev/null || true

log "=== Daily cron done ==="