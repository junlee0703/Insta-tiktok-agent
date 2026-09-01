#!/usr/bin/env python3
"""Builds an Instagram Reel with the static overlay (3 layers: brand tag,
numbered statement, "caption below ↓") -- all stamped once at frame 1 and held for the
clip's full duration (no time-gating, no animation, no transitions, no
on-screen CTA -- see playbook.md Workflow C). Forked from a sibling
project's 4-layer version by dropping the old confrontational hook layer -- see
styles/ig_question_overlay.json's _note for how the remaining layers were
repositioned. Replaces the older time-gated multi-segment build for
Instagram.

Renders one transparent overlay PNG via generate_slides.render_slide()
against styles/ig_question_overlay.json, then ffmpeg-composites it onto
the clip for its whole length and mixes in a silent AAC track sized to that
same duration (Instagram's own real audio track is attached separately, at
post-creation time, via its native `audio.id` -- see playbook.md).

Usage:
    python3 scripts/build_ig_reel.py --clip <filename in clips/> \
        --brand-tag "<topic-specific credibility title>" \
        --question "<numbered statement>" \
        --out output/<name>/<name>.mp4
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_slides import render_slide, PROJECT_ROOT

try:
    import imageio_ffmpeg
except ImportError:
    imageio_ffmpeg = None

DEFAULT_CAPTION_BELOW = "caption below ↓"


def ffmpeg_executable() -> str:
    installed = shutil.which("ffmpeg")
    if installed:
        return installed
    if imageio_ffmpeg is not None:
        return imageio_ffmpeg.get_ffmpeg_exe()
    raise SystemExit(
        "ffmpeg is unavailable; install scripts/requirements.txt or add "
        "ffmpeg to PATH"
    )


def get_duration(clip_path: Path, ffmpeg: str) -> float:
    if imageio_ffmpeg is not None:
        _, duration = imageio_ffmpeg.count_frames_and_secs(str(clip_path))
        return duration

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise SystemExit("ffprobe is unavailable and imageio-ffmpeg is not installed")
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clip_path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--clip", required=True, help="Filename inside clips/")
    parser.add_argument("--question", required=True, help="On-screen numbered statement whose advice appears in the caption (legacy option name, layer 2)")
    parser.add_argument(
        "--brand-tag",
        required=True,
        help="Required topic-specific credibility title for layer 1 (see instagram/style_guide.md)",
    )
    parser.add_argument("--highlight-color", default=None,
                         help="Overrides brand_tag + technical_question background_color (the 9-color rotation) -- leaves text color/geometry untouched")
    parser.add_argument("--out", required=True, help="Output .mp4 path")
    args = parser.parse_args()

    clip_path = PROJECT_ROOT / "clips" / args.clip
    style_path = PROJECT_ROOT / "styles" / "ig_question_overlay.json"
    blank_path = PROJECT_ROOT / "scripts" / "_blank_transparent.png"
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = ffmpeg_executable()
    duration = get_duration(clip_path, ffmpeg)

    style_overrides = None
    if args.highlight_color:
        style_overrides = {
            "brand_tag": {"background_color": args.highlight_color},
            "technical_question": {"background_color": args.highlight_color},
            "caption_below": {"background_color": args.highlight_color},
        }

    overlay = render_slide(style_path, str(blank_path), {
        "brand_tag": args.brand_tag,
        "technical_question": args.question,
        "caption_below": DEFAULT_CAPTION_BELOW,
    }, style_overrides)
    overlay_path = out_path.parent / f"_overlay_{out_path.stem}.png"
    overlay.save(overlay_path)

    cmd = [
        ffmpeg, "-y",
        "-i", str(clip_path),
        "-i", str(overlay_path),
        "-f", "lavfi", "-t", str(duration), "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-filter_complex", "[0:v]scale=1080:1920[bg];[bg][1:v]overlay=0:0[v]",
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
        str(out_path), "-loglevel", "error",
    ]
    subprocess.run(cmd, check=True)
    overlay_path.unlink()

    print(f"wrote {out_path} (clip duration {duration:.2f}s, static overlay)")


if __name__ == "__main__":
    main()
