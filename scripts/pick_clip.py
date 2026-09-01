#!/usr/bin/env python3
"""Pick one background clip for an Instagram Reels post from clips/,
least-used-first (same fairness pattern as scripts/pick_photos.py, but
simpler -- there's only one slot/pool here, no hook/body/cta distinction and
no position rules, since a single video is the entire background).

Usage:
    python3 scripts/pick_clip.py
Prints the chosen filename and updates clips/clips_usage.json in place.
"""
import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
USAGE_PATH = PROJECT_ROOT / "clips" / "clips_usage.json"


def pick_clip():
    usage = json.loads(USAGE_PATH.read_text())
    counts = usage["counts"]
    min_count = min(counts.values())
    tied = [c for c, n in counts.items() if n == min_count]
    chosen = random.choice(tied)
    counts[chosen] += 1
    USAGE_PATH.write_text(json.dumps(usage, indent=2) + "\n")
    return chosen


if __name__ == "__main__":
    print(pick_clip())
