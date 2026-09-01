#!/usr/bin/env python3
"""Validate this repo's configuration and report exactly what is still missing.

Run this first, and any time something fails:

    python3 scripts/check_setup.py

Exits 0 when everything needed to render and post is in place, 1 otherwise.
Checks are independent: one failure never hides the others, so a single run
gives you the full list of what to fix.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = re.compile(r"<[^<>]{1,300}>", re.S)

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))


def read_json(path):
    try:
        return json.loads((ROOT / path).read_text())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return exc


# --- brand.md -------------------------------------------------------------
brand_path = ROOT / "brand.md"
brand = brand_path.read_text() if brand_path.exists() else ""
if not brand:
    check("brand.md", False, "missing. This is the file you fill in first.")
else:
    left = PLACEHOLDER.findall(brand)
    check("brand.md filled in", not left,
          f"{len(left)} placeholder(s) still unedited, first: {left[0]}" if left else "")

    m = re.search(r"^autopilot:\s*(\w+)", brand, re.M)
    if not m:
        check("autopilot switch", False,
              'no "autopilot: off" line found in brand.md')
    elif m.group(1) not in ("on", "off"):
        check("autopilot switch", False,
              f'autopilot is "{m.group(1)}", expected "on" or "off"')
    else:
        state = m.group(1)
        check(f"autopilot: {state}", True,
              "publishes real public posts without showing you the copy first"
              if state == "on" else
              "shows you the copy in chat, then publishes publicly once approved")

# --- knowledge ------------------------------------------------------------
kdir = ROOT / "knowledge"
sources = [p for p in kdir.glob("*") if p.is_file()
           and p.name not in ("README.md", ".gitkeep")] if kdir.exists() else []
check("knowledge/ has source material", bool(sources),
      "empty. Content cannot be generated without it (Hard Rule 5)."
      if not sources else f"{len(sources)} file(s)")

# --- clips ----------------------------------------------------------------
cdir = ROOT / "clips"
clips = sorted(p.name for p in cdir.glob("*")
               if p.suffix.lower() in (".mp4", ".mov", ".m4v")) if cdir.exists() else []
check("clips/ has footage", bool(clips),
      "empty. Reels need at least one background video." if not clips
      else f"{len(clips)} clip(s)")

usage = read_json("clips/clips_usage.json")
if isinstance(usage, json.JSONDecodeError):
    check("clips_usage.json", False, f"invalid JSON: {usage}")
elif usage is None:
    check("clips_usage.json", False, "missing")
elif clips:
    counts = usage.get("counts", {})
    missing = [c for c in clips if c not in counts]
    stale = [c for c in counts if c not in clips]
    problems = []
    if missing:
        problems.append(f"not seeded: {', '.join(missing)}")
    if stale:
        problems.append(f"listed but not on disk: {', '.join(stale)}")
    check("clips_usage.json seeded", not problems,
          "; ".join(problems) + ". pick_clip.py needs one entry per clip."
          if problems else "")

# --- photos (TikTok only) -------------------------------------------------
pdir = ROOT / "photos" / "rotation"
photos = sorted(p.name for p in pdir.glob("*")
                if p.suffix.lower() in (".jpg", ".jpeg", ".png")) if pdir.exists() else []
pos_data = read_json("photos/rotation_positions.json")
if isinstance(pos_data, json.JSONDecodeError):
    check("rotation_positions.json", False, f"invalid JSON: {pos_data}")
elif pos_data is None:
    check("rotation_positions.json", False, "missing")
else:
    positions = pos_data.get("positions", {})
    roles = pos_data.get("roles") or {}
    if not photos:
        check("photos/rotation/ (TikTok only)", True,
              "empty — fine if you are only posting Instagram Reels")
    else:
        unmapped = [p for p in photos if p not in positions]
        check("every photo has a position", not unmapped,
              f"missing an entry for: {', '.join(unmapped)}" if unmapped else
              f"{len(photos)} photo(s)")
        has_middle = any(v == "middle" for v in positions.values())
        check('at least one photo tagged "middle"', has_middle,
              "the CTA slide draws only from the middle pool" if not has_middle else "")
    bad_roles = [f"roles.{k} -> {v}" for k, v in roles.items()
                 if v and v not in positions]
    check("photo roles point at real photos", not bad_roles,
          "; ".join(bad_roles) if bad_roles else "")

# --- style guide ----------------------------------------------------------
sg = ROOT / "instagram" / "style_guide.md"
if not sg.exists():
    check("instagram/style_guide.md", False, "missing")
else:
    body = sg.read_text()
    section = body.split("## Reel format")[0]
    left = PLACEHOLDER.findall(section)
    check("audience and positioning filled in", not left,
          f"{len(left)} placeholder(s) left in the Audience section. "
          "The agent will stop and ask rather than invent a persona."
          if left else "")
    bank = body.split("## Approved pairing bank")[-1]
    check("pairing bank has entries", "Empty out of the box" not in bank,
          "still the shipped placeholder" if "Empty out of the box" in bank else "")

# --- fonts ----------------------------------------------------------------
fonts = ["Montserrat-Black.ttf", "Montserrat-Bold.ttf", "Montserrat-Medium.ttf"]
missing_fonts = [f for f in fonts if not (ROOT / "fonts" / f).exists()]
check("bundled fonts present", not missing_fonts,
      f"missing: {', '.join(missing_fonts)}" if missing_fonts else "")

# --- dependencies ---------------------------------------------------------
try:
    import PIL  # noqa: F401
    check("Pillow installed", True)
except ImportError:
    check("Pillow installed", False, "pip install -r scripts/requirements.txt")

try:
    import imageio_ffmpeg  # noqa: F401
    bundled_ffmpeg = True
except ImportError:
    bundled_ffmpeg = False

check("ffmpeg available", shutil.which("ffmpeg") is not None or bundled_ffmpeg,
      "install it, or `pip install -r scripts/requirements.txt` for a bundled copy"
      if not (shutil.which("ffmpeg") or bundled_ffmpeg) else
      ("on PATH" if shutil.which("ffmpeg") else
       "bundled via imageio-ffmpeg (the TikTok frame-extraction step in "
       "playbook.md still wants ffmpeg on PATH)"))

for binary, why in [("ffprobe", "verifies rendered output decodes"),
                    ("postiz", "uploads and creates posts"),
                    ("jq", "parses postiz output in the workflow")]:
    check(f"{binary} on PATH", shutil.which(binary) is not None, why)

# --- report ---------------------------------------------------------------
width = max(len(n) for n, _, _ in results)
failed = 0
print()
for name, ok, detail in results:
    mark = "PASS" if ok else "FAIL"
    if not ok:
        failed += 1
    line = f"  [{mark}] {name.ljust(width)}"
    print(f"{line}  {detail}" if detail else line)
print()
if failed:
    print(f"{failed} item(s) need attention before this agent can post.")
    print('If you are using Claude Code or Codex here, just say "set me up"')
    print("and it will walk you through these one at a time.")
    sys.exit(1)
print("Setup looks complete.")
