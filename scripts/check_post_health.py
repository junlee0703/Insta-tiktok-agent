#!/usr/bin/env python3
"""Flag Postiz posts that failed to publish or silently stalled.

Postiz marks a failed publish as ERROR and then never retries and never
notifies, so a transient TikTok rejection permanently drops a post that only
gets noticed when someone spots it missing. See the 2026-08-08 audit entry in
drafts/log.md.

Run after any scheduled slot:

    python3 scripts/check_post_health.py            # last 2 days
    python3 scripts/check_post_health.py --days 7

Exits 1 if anything needs attention, so it can drive a cron/loop.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# Postiz can take ~30 min past the slot to flip a failed publish from QUEUE to
# ERROR (observed 2026-08-08 on cmsjppgd904rptc0y2hrdg09a). So a post that is
# merely late is not yet a distinct failure: wait past that lag before flagging,
# and call it LATE rather than asserting it is stuck.
LATE_AFTER = timedelta(minutes=40)


def fetch_posts(start, end):
    out = subprocess.run(
        ["postiz", "posts:list", "--startDate", iso(start), "--endDate", iso(end)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    # The CLI prints a human header line before the JSON body.
    brace = out.find("{")
    if brace == -1:
        raise SystemExit("could not find JSON in postiz output:\n" + out)
    return json.loads(out[brace:])["posts"]


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=2, help="how far back to look")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    posts = fetch_posts(now - timedelta(days=args.days), now + timedelta(days=1))

    failed, late = [], []
    for p in posts:
        due = datetime.fromisoformat(p["publishDate"].replace("Z", "+00:00"))
        if p["state"] == "ERROR":
            failed.append((due, p))
        elif p["state"] == "QUEUE" and now - due > LATE_AFTER:
            late.append((due, p))

    for label, group in (("FAILED", failed), ("LATE, still in QUEUE", late)):
        for due, p in sorted(group):
            print(
                f"{label}: {p['integration']['providerIdentifier']} "
                f"due {due:%Y-%m-%d %H:%M} UTC  {p['id']}\n"
                f"  {p['content'].splitlines()[0][:80]}"
            )

    checked = len(posts)
    if not failed and not late:
        print(f"All clear. {checked} posts checked over the last {args.days} day(s).")
        return 0

    print(
        f"\n{len(failed)} failed, {len(late)} late, out of {checked} checked.\n"
        "Postiz will not retry these on its own. To recover one: delete it, "
        "re-upload the rendered media from its output/ folder, and recreate it "
        "with the same caption and settings (playbook.md Workflow B step 8)."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
