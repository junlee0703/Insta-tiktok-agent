#!/usr/bin/env python3
"""Overlay a pixel-coordinate grid on a template image to help pick text-box
positions for a templates/config/<name>.json file.

Usage:
    python3 scripts/calibrate_grid.py templates/hook_slide.png
    -> writes templates/hook_slide.grid.png
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

STEP = 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to the template image")
    parser.add_argument("--step", type=int, default=STEP, help="Grid spacing in pixels")
    args = parser.parse_args()

    src = Path(args.image)
    img = Image.open(src).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size

    font = ImageFont.load_default()
    for candidate in (
        Path(__file__).resolve().parent.parent / "fonts" / "Montserrat-Medium.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        try:
            font = ImageFont.truetype(str(candidate), 20)
            break
        except OSError:
            continue

    for x in range(0, w, args.step):
        draw.line([(x, 0), (x, h)], fill=(255, 0, 0, 120), width=1)
        draw.text((x + 2, 2), str(x), font=font, fill=(255, 0, 0, 220))
    for y in range(0, h, args.step):
        draw.line([(0, y), (w, y)], fill=(0, 120, 255, 120), width=1)
        draw.text((2, y + 2), str(y), font=font, fill=(0, 120, 255, 220))

    combined = Image.alpha_composite(img, overlay)
    out_path = src.with_suffix("")
    out_path = out_path.parent / f"{out_path.name}.grid.png"
    combined.convert("RGB").save(out_path)
    print(f"wrote {out_path} ({w}x{h}, grid every {args.step}px)")


if __name__ == "__main__":
    main()
