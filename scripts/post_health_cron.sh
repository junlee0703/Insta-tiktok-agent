#!/bin/bash
# Cron wrapper for check_post_health.py.
#
# Postiz silently drops a post when a publish fails (see the 2026-08-08 audit
# entry in drafts/log.md), so this runs shortly after each posting slot and
# raises a macOS notification when something needs a manual repost.
#
# Installed via `crontab -e`. Log: drafts/post_health.log

cd "$(dirname "$0")/.." || exit 1

# cron gets a minimal PATH. Add wherever `postiz` lives on your machine
# (Homebrew's prefix on macOS, often ~/.local/bin or /usr/local/bin elsewhere).
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

LOG="drafts/post_health.log"
OUT=$(/usr/bin/python3 scripts/check_post_health.py --days 2 2>&1)
STATUS=$?

printf '\n===== %s =====\n%s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$OUT" >> "$LOG"

if [ $STATUS -ne 0 ]; then
    COUNT=$(printf '%s' "$OUT" | grep -c '^FAILED\|^LATE')
    MSG="$COUNT post(s) need a repost. See drafts/post_health.log"
    # Desktop notification where one is available; the log above is always written.
    if [ -x /usr/bin/osascript ]; then
        /usr/bin/osascript -e "display notification \"$MSG\" with title \"Postiz: post did not publish\" sound name \"Basso\""
    elif command -v notify-send >/dev/null 2>&1; then
        notify-send "Postiz: post did not publish" "$MSG"
    else
        printf 'ALERT: %s\n' "$MSG" >&2
    fi
fi

exit $STATUS
