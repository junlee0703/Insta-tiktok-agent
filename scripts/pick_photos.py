#!/usr/bin/env python3
"""Pick photos for one TikTok slideshow from photos/rotation/.

Selection is "least-used-first": among every eligible candidate for a slot,
only the ones currently tied for the lowest usage count in
photos/rotation_usage.json are considered, and one is chosen uniformly at
random among that tied group. Every photo gets used before any photo gets
reused, so usage stays as close to equal as the constraints allow.

Usage counts are tracked **separately per slot type** (body / cta), not as one
pooled number. With a single pooled counter, a photo's chance of winning the
lower-volume slot ends up driven mostly by how often it happens to win the
higher-volume one, so a photo that rarely wins body picks keeps looking
"underused" and keeps winning CTA ties. Splitting the counters makes each
slot's fairness independent of the other.

Slide 1 is not part of this picker's output: it is a still frame from clips/
(chosen by pick_clip.py) stamped with the Instagram-matching overlay. See
playbook.md Workflow B.

Optional special roles live in photos/rotation_positions.json under "roles".
Both default to null, which disables them:

- "fixed_slide_2": one photo always used for slide 2, on every video, and
  never counted for fairness. Null means slide 2 is drawn from the general
  pool like any other slide.
- "cta_only": one photo reserved exclusively for the CTA slide, never drawn
  for a teaching point. Null means no photo is reserved.

No two adjacent slides may share a text position.

Usage:
    python3 scripts/pick_photos.py --total-slides 7

`--total-slides` counts only the photo-based slides (slide 2 + body + CTA); it
does NOT include slide 1, which is a separate clip-frame render.
Prints a JSON list, one entry per slide, each {"slot", "image", "position"}.
Updates photos/rotation_usage.json in place with the new counts.
"""
import argparse
import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSITIONS_PATH = PROJECT_ROOT / "photos" / "rotation_positions.json"
USAGE_PATH = PROJECT_ROOT / "photos" / "rotation_usage.json"


def load():
    data = json.loads(POSITIONS_PATH.read_text())
    positions = data["positions"]
    roles = data.get("roles") or {}
    usage = json.loads(USAGE_PATH.read_text())
    return positions, roles, usage


def save_usage(usage):
    USAGE_PATH.write_text(json.dumps(usage, indent=2) + "\n")


def least_used_choice(candidates, counts, used_this_video):
    fresh = [c for c in candidates if c not in used_this_video]
    pool = fresh if fresh else candidates
    min_count = min(counts.get(c, 0) for c in pool)
    tied = [c for c in pool if counts.get(c, 0) == min_count]
    return random.choice(tied)


def pick_sequence(total_slides):
    positions, roles, usage = load()
    if not positions:
        raise SystemExit(
            "photos/rotation_positions.json has no entries. Add one position "
            "entry per photo in photos/rotation/ before running the picker."
        )

    body_counts = usage["counts"]["body"]
    cta_counts = usage["counts"]["cta"]

    fixed_slide_2 = roles.get("fixed_slide_2")
    cta_only = roles.get("cta_only")
    for role_name, filename in (("fixed_slide_2", fixed_slide_2), ("cta_only", cta_only)):
        if filename and filename not in positions:
            raise SystemExit(
                f'roles.{role_name} is set to "{filename}", which has no entry '
                "in photos/rotation_positions.json. Point it at one of your own "
                "photos or set it to null."
            )

    all_photos = set(positions.keys())
    reserved = {p for p in (fixed_slide_2, cta_only) if p}
    general_pool = all_photos - reserved
    middle_pool = {p for p in all_photos if positions[p] == "middle"}

    used_this_video = set()
    sequence = []
    prev_position = None

    # Slide 2: fixed, when a photo is configured for the role.
    if fixed_slide_2:
        prev_position = positions[fixed_slide_2]
        sequence.append(
            {"slot": "fixed_slide_2", "image": fixed_slide_2, "position": prev_position}
        )

    # Body slides: everything between slide 2 and the CTA.
    num_body = total_slides - 1 - (1 if fixed_slide_2 else 0)
    for i in range(num_body):
        is_last_body = i == num_body - 1
        candidates = [
            p for p in general_pool
            if positions[p] != prev_position
            and not (is_last_body and positions[p] == "middle")
        ]
        if not candidates:
            raise SystemExit(
                f"No eligible photo for body slot {i + 1}. Add more photos, or "
                "spread their position tags in photos/rotation_positions.json "
                "so adjacent slides can differ."
            )
        photo = least_used_choice(candidates, body_counts, used_this_video)
        sequence.append({"slot": f"body_{i + 1}", "image": photo, "position": positions[photo]})
        used_this_video.add(photo)
        prev_position = positions[photo]

    # CTA: always from the middle-position pool.
    cta_candidates = list(middle_pool)
    if not cta_candidates:
        raise SystemExit(
            'The CTA slide draws from photos tagged "middle", but no photo in '
            "photos/rotation_positions.json carries that tag. Tag at least one."
        )
    cta = least_used_choice(cta_candidates, cta_counts, used_this_video)
    sequence.append({"slot": "cta", "image": cta, "position": "middle"})

    # Update usage counts, split by slot type (the fixed slide is never tracked).
    for entry in sequence:
        if entry["slot"] == "cta":
            cta_counts[entry["image"]] = cta_counts.get(entry["image"], 0) + 1
        elif entry["slot"] != "fixed_slide_2":
            body_counts[entry["image"]] = body_counts.get(entry["image"], 0) + 1
    save_usage(usage)

    return sequence


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--total-slides",
        type=int,
        required=True,
        help="Photo-based slide count: slide 2 + body + CTA (excludes slide 1, "
             "which is a separate clip-frame render)",
    )
    args = parser.parse_args()
    sequence = pick_sequence(args.total_slides)
    print(json.dumps(sequence, indent=2))


if __name__ == "__main__":
    main()
