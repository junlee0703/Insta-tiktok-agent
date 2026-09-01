#!/usr/bin/env python3
"""Stamp variable text onto a real photo to produce a TikTok carousel slide,
in the "Ari" style: a real candid photo as the backdrop, with a consistent
bold-white text overlay on top (not a designed Canva graphic).

Two levels of config:

1. Style config (styles/<name>.json) — reusable across ANY photo, describes the
   canvas size and where each text box sits:

    {
      "canvas_size": [1080, 1920],
      "text_boxes": [
        {
          "name": "header",
          "x": 60, "y": 620, "width": 960, "height": 220,
          "font": "fonts/Montserrat-Bold.ttf",
          "font_size": 56,
          "min_font_size": 32,
          "auto_shrink": true,
          "color": "#FFFFFF",
          "align": "left",          // left | center | right
          "valign": "top",          // top | center | bottom
          "line_spacing": 1.2,
          "stroke_width": 2,
          "stroke_color": "#000000"
        }
      ]
    }

   A style config may also embed a fixed "template_image" (for the old
   Canva-graphic approach) — but for the photo-backdrop style, every slide in
   the content spec supplies its own "image" instead (see below).

2. Content spec (one per slideshow/post) — the photo + variable text for each
   slide:

    {
      "slides": [
        {"style": "styles/tiktok_teaching_boxed.json", "image": "photos/rotation/<a-photo>.jpg",
         "text": {"heading": "<slide heading>", "body": "<one supporting line>"}},
        {"style": "styles/tiktok_teaching_boxed.json", "image": "photos/rotation/<another>.jpg",
         "text": {"heading": "<next heading>", "body": "<next line>"}}
      ]
    }

Photos are resized+center-cropped to fill the style's canvas_size (like
TikTok's own display crop) so the same text-box coordinates work regardless of
each photo's original dimensions.

Usage:
    python3 scripts/generate_slides.py --content content_spec.json --out output/post-slug/
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CANVAS_SIZE = (1080, 1920)


def resolve(path_str: str) -> Path:
    p = Path(path_str)
    return p if p.is_absolute() else (PROJECT_ROOT / p)


def fit_to_canvas(img: Image.Image, canvas_size) -> Image.Image:
    """Scale to fill canvas_size then center-crop the overflow (a 'cover' fit)."""
    target_w, target_h = canvas_size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = round(src_w * scale), round(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if draw.textlength(trial, font=font) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def load_font(font_path, size, variation=None):
    font = ImageFont.truetype(font_path, size)
    if variation:
        try:
            font.set_variation_by_name(variation)
        except Exception:
            pass  # font has no named variation axis (e.g. a static font like Arial) -- ignore
    return font


def fit_text(draw, text, font_path, start_size, min_size, max_width, max_height, line_spacing, variation=None, max_lines=None):
    """Shrinks font size until the wrapped text fits. Normally "fits" means
    total height <= max_height. If `max_lines` is set, "fits" instead means
    the wrapped line count <= max_lines (max_height is ignored in that case)
    -- a direct line-count cap rather than a height proxy, for boxes like a
    hook where the real constraint is "don't run past N lines and cover the
    subject's face," not any particular pixel height."""
    size = start_size
    while size >= min_size:
        font = load_font(font_path, size, variation)
        lines = wrap_text(draw, text, font, max_width)
        line_height = font.getbbox("Ag")[3] * line_spacing
        total_height = line_height * len(lines)
        fits = len(lines) <= max_lines if max_lines is not None else total_height <= max_height
        if fits or size == min_size:
            return font, lines, line_height
        size -= 2
    font = load_font(font_path, min_size, variation)
    lines = wrap_text(draw, text, font, max_width)
    return font, lines, font.getbbox("Ag")[3] * line_spacing


def resolve_color(color_str):
    """Parses '#RRGGBB' or '#RRGGBBAA' into an (r,g,b,a) tuple (default a=255)."""
    return ImageColor.getcolor(color_str, "RGBA")


def text_width_with_spacing(draw, text, font, spacing):
    if not text:
        return 0
    widths = [draw.textlength(ch, font=font) for ch in text]
    return sum(widths) + spacing * (len(text) - 1)


def draw_text_letterspaced(draw, text, font, x, y, fill, spacing, stroke_width=0, stroke_color=None):
    cursor = x
    for ch in text:
        if stroke_width:
            draw.text((cursor, y), ch, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_color)
        else:
            draw.text((cursor, y), ch, font=font, fill=fill)
        cursor += draw.textlength(ch, font=font) + spacing


def make_vertical_gradient(size, top_color, bottom_color):
    """Returns an RGBA image of the given size, a smooth vertical gradient
    from top_color to bottom_color (both '#RRGGBB' strings)."""
    w, h = size
    top = ImageColor.getrgb(top_color)
    bottom = ImageColor.getrgb(bottom_color)
    grad = Image.new("RGB", (1, max(h, 1)))
    for row in range(max(h, 1)):
        t = row / max(h - 1, 1)
        rgb = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        grad.putpixel((0, row), rgb)
    grad = grad.resize((max(w, 1), max(h, 1)))
    return grad.convert("RGBA")


def draw_gradient_line(img, line, font, x, y, top_color, bottom_color, stroke_width, stroke_color,
                        shadow_offset=0, shadow_color="#000000"):
    """Draws one line of text filled with a vertical gradient instead of a
    flat color, by drawing a drop shadow, then a black outline pass, both
    directly on the image, then compositing a gradient rectangle through a
    white text-shaped mask on top."""
    draw = ImageDraw.Draw(img)
    if shadow_offset:
        draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=shadow_color)
    if stroke_width:
        # Outline-only pass: draw the glyph in the stroke color so the
        # outline is visible once the gradient fill covers the interior.
        draw.text((x, y), line, font=font, fill=stroke_color,
                   stroke_width=stroke_width, stroke_fill=stroke_color)

    bbox = draw.textbbox((x, y), line, font=font)
    if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
        return
    pad = stroke_width + 2
    mask_box = (int(bbox[0] - pad), int(bbox[1] - pad), int(bbox[2] + pad) + 1, int(bbox[3] + pad) + 1)
    mask = Image.new("L", (mask_box[2] - mask_box[0], mask_box[3] - mask_box[1]), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((x - mask_box[0], y - mask_box[1]), line, font=font, fill=255)

    gradient = make_vertical_gradient(mask.size, top_color, bottom_color)
    img.paste(gradient, (mask_box[0], mask_box[1]), mask)


def wrap_runs_inline(draw, runs, font, max_width, default_color):
    """Tokenizes a list of {"text", "color"} runs into words (dropping the
    runs' own spacing) and greedily wraps them into lines, same as normal
    paragraph wrapping, but keeping each word's color so a sentence can flow
    across a shared line with only some words tinted (e.g. numbers in
    yellow, the rest in white) instead of every run forcing its own line."""
    tokens = []
    for run in runs:
        color = run.get("color", default_color)
        for word in run["text"].split(" "):
            if word:
                tokens.append((word, color))
    space_width = draw.textlength(" ", font=font)
    lines, current, current_width = [], [], 0
    for word, color in tokens:
        word_width = draw.textlength(word, font=font)
        added = word_width if not current else word_width + space_width
        if current and current_width + added > max_width:
            lines.append(current)
            current, current_width = [(word, color)], word_width
        else:
            current.append((word, color))
            current_width += added
    if current:
        lines.append(current)
    return lines, space_width


def measure_text_box_height(draw, box, value):
    """Mirrors draw_text_box's own sizing/wrapping pass (both the inline_runs
    and default branches) to get a box's total rendered text height without
    drawing anything. Used by render_slide() to vertically center a group of
    boxes (e.g. heading + body) as a unit -- the group's real height depends
    on how much each box's text actually wraps to at its fitted font size,
    not just a static y in the style file."""
    font_path = resolve(box["font"])
    start_size = box.get("font_size", 48)
    min_size = box.get("min_font_size", 24) if box.get("auto_shrink", True) else start_size
    line_spacing = box.get("line_spacing", 1.2)
    variation = box.get("font_variation")
    default_color = box.get("color", "#FFFFFF")

    runs = value["runs"] if isinstance(value, dict) and "runs" in value else [{"text": value}]
    has_per_run_size = any("font_size" in run for run in runs)

    if not has_per_run_size and box.get("inline_runs") and len(runs) > 1:
        combined_text = " ".join(" ".join(r["text"].split()) for r in runs)
        font, _, line_height = fit_text(
            draw, combined_text, str(font_path), start_size, min_size,
            box["width"], box.get("height", 10**6), line_spacing, variation,
        )
        lines_tokens, _ = wrap_runs_inline(draw, runs, font, box["width"], default_color)
        return line_height * len(lines_tokens)

    if has_per_run_size:
        total = 0
        for run in runs:
            run_font = load_font(str(font_path), run.get("font_size", start_size), run.get("font_variation", variation))
            run_line_height = run_font.getbbox("Ag")[3] * line_spacing
            total += run_line_height * len(wrap_text(draw, run["text"], run_font, box["width"]))
        return total

    combined_text = "\n".join(run["text"] for run in runs)
    font, _, line_height = fit_text(
        draw, combined_text, str(font_path), start_size, min_size,
        box["width"], box.get("height", 10**6), line_spacing, variation,
        box.get("max_lines"),
    )
    n_lines = sum(len(wrap_text(draw, run["text"], font, box["width"])) for run in runs)
    return line_height * n_lines


def draw_text_box(img, draw, box, value, box_bottoms=None):
    """`value` is normally a plain string. It may also be a dict
    {"runs": [{"text": "...", "color": "#..."}, ...]} to render a couple of
    differently-styled segments stacked in the same box (e.g. a hook line
    plus a highlighted parenthetical). Each run may set:
      - "color" (flat fill) or "gradient": ["#top", "#bottom"] (a vertical
        gradient fill, e.g. for a glossy gold impact-word look)
      - "shadow_offset" (pixels) + "shadow_color" — only meaningful on a
        "gradient" run, draws an offset drop-shadow copy of the glyphs
        underneath the stroke/fill pass for a raised, embossed look
      - "font_size" to override the box's default size for just that run
        (e.g. making one emphasized word render bigger than the rest) —
        when any run sets its own size, auto-shrink-to-fit is skipped in
        favor of using each run's size exactly as authored.
    Colors accept 8-digit hex ("#RRGGBBAA") for opacity, on top of the usual
    6-digit form.
    A box may set "font_variation" (a named instance on a variable font, e.g.
    "Medium"/"Semibold"/"Black") — ignored harmlessly on fonts without that
    axis, which includes the bundled static Montserrat faces.
    A box may set "letter_spacing" (extra px between characters), rendered
    via manual per-character drawing instead of PIL's normal text draw.
    A box can also set "background_color" to draw a filled rounded rectangle
    behind the text, e.g. for a white-sticker caption look. By default
    ("background_mode" unset or "block") this is one rectangle spanning the
    whole wrapped block, sized to the widest line. With
    "background_mode": "per_line", each line instead gets its own tightly
    fit rectangle (background_padding_x/y around that line's actual glyph
    bbox, background_radius for corner rounding, default 0 = sharp corners)
    — the "each line highlighted separately" look.
    A box may set "y_below": {"of": "<other box name>", "gap": <px>} to
    position itself a fixed gap below wherever that other box actually ended
    up ending (its lowest highlight-box edge, or text bottom if it has none)
    — requires the referenced box to be rendered earlier in the same
    render_slide() call. `box_bottoms` is the shared dict tracking this
    across all boxes in one slide; pass the same dict for every box in a
    render_slide() call.
    """
    box_bottoms = box_bottoms if box_bottoms is not None else {}
    font_path = resolve(box["font"])
    start_size = box.get("font_size", 48)
    min_size = box.get("min_font_size", 24) if box.get("auto_shrink", True) else start_size
    align = box.get("align", "left")
    valign = box.get("valign", "top")
    line_spacing = box.get("line_spacing", 1.2)
    default_color = box.get("color", "#FFFFFF")
    stroke_width = box.get("stroke_width", 0)
    stroke_color = box.get("stroke_color", "#000000")
    variation = box.get("font_variation")
    letter_spacing = box.get("letter_spacing", 0)

    runs = value["runs"] if isinstance(value, dict) and "runs" in value else [{"text": value}]
    has_per_run_size = any("font_size" in run for run in runs)

    if not has_per_run_size and box.get("inline_runs") and len(runs) > 1:
        # Multi-color runs meant to flow as one wrapped paragraph (e.g. a
        # sentence with a few yellow-highlighted numbers/terms), not one
        # run per line like the default runs behavior below. Only supports
        # "per_line" background highlighting, not "block".
        combined_text = " ".join(" ".join(r["text"].split()) for r in runs)
        font, _, line_height = fit_text(
            draw, combined_text, str(font_path), start_size, min_size,
            box["width"], box.get("height", 10**6), line_spacing, variation,
        )
        lines_tokens, space_width = wrap_runs_inline(draw, runs, font, box["width"], default_color)
        total_height = line_height * len(lines_tokens)

        if "y_below" in box:
            ref = box["y_below"]
            y = box_bottoms.get(ref["of"], box.get("y", 0)) + ref.get("gap", 0)
        elif valign == "center":
            y = box["y"] + (box.get("height", total_height) - total_height) / 2
        elif valign == "bottom":
            y = box["y"] + box.get("height", total_height) - total_height
        else:
            y = box["y"]

        background_color = box.get("background_color")
        bg_rgba = resolve_color(background_color) if background_color else None
        stroke_fill = resolve_color(stroke_color) if stroke_width else None

        lowest_bg_bottom = None
        for tokens in lines_tokens:
            line_width = sum(draw.textlength(w, font=font) for w, _ in tokens) + space_width * (len(tokens) - 1)
            if align == "center":
                x = box["x"] + (box["width"] - line_width) / 2
            elif align == "right":
                x = box["x"] + box["width"] - line_width
            else:
                x = box["x"]

            if bg_rgba:
                pad_x = box.get("background_padding_x", 12)
                pad_y = box.get("background_padding_y", 8)
                line_text = " ".join(w for w, _ in tokens)
                bbox = draw.textbbox((x, y), line_text, font=font)
                rect = [bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y]
                draw.rounded_rectangle(rect, radius=box.get("background_radius", 0), fill=bg_rgba)
                lowest_bg_bottom = max(lowest_bg_bottom or 0, rect[3])

            cursor = x
            for word, color in tokens:
                draw.text((cursor, y), word, font=font, fill=resolve_color(color),
                          stroke_width=stroke_width, stroke_fill=stroke_fill)
                cursor += draw.textlength(word, font=font) + space_width
            y += line_height

        if "name" in box:
            box_bottoms[box["name"]] = lowest_bg_bottom if lowest_bg_bottom is not None else y
        return

    if has_per_run_size:
        # Manual sizing mode: each run uses its own explicit font size,
        # no shared auto-fit pass across the whole box.
        styled_lines = []
        for run in runs:
            run_font = load_font(str(font_path), run.get("font_size", start_size), run.get("font_variation", variation))
            run_line_height = run_font.getbbox("Ag")[3] * line_spacing
            for line in wrap_text(draw, run["text"], run_font, box["width"]):
                styled_lines.append((
                    line, run.get("color", default_color), run.get("gradient"), run_font, run_line_height,
                    run.get("shadow_offset", 0), run.get("shadow_color", "#000000"),
                ))
    else:
        combined_text = "\n".join(run["text"] for run in runs)
        font, _, line_height = fit_text(
            draw, combined_text, str(font_path), start_size, min_size,
            box["width"], box.get("height", 10**6), line_spacing, variation,
            box.get("max_lines"),
        )
        styled_lines = [
            (
                line, run.get("color", default_color), run.get("gradient"), font, line_height,
                run.get("shadow_offset", 0), run.get("shadow_color", "#000000"),
            )
            for run in runs
            for line in wrap_text(draw, run["text"], font, box["width"])
        ]

    total_height = sum(lh for _, _, _, _, lh, _, _ in styled_lines)
    if "y_below" in box:
        ref = box["y_below"]
        y = box_bottoms.get(ref["of"], box.get("y", 0)) + ref.get("gap", 0)
    elif valign == "center":
        y = box["y"] + (box.get("height", total_height) - total_height) / 2
    elif valign == "bottom":
        y = box["y"] + box.get("height", total_height) - total_height
    else:
        y = box["y"]

    background_color = box.get("background_color")
    background_mode = box.get("background_mode", "block")
    bg_rgba = resolve_color(background_color) if background_color else None

    if bg_rgba and background_mode == "block" and styled_lines:
        pad_x = box.get("background_padding_x", 28)
        pad_y = box.get("background_padding_y", 18)
        max_line_width = max(draw.textlength(line, font=f) for line, _, _, f, _, _, _ in styled_lines)
        rect_left = box["x"] + (box["width"] - max_line_width) / 2 - pad_x
        rect_right = box["x"] + (box["width"] + max_line_width) / 2 + pad_x
        rect_top = y - pad_y
        rect_bottom = y + total_height + pad_y
        draw.rounded_rectangle(
            [rect_left, rect_top, rect_right, rect_bottom],
            radius=box.get("background_radius", 20),
            fill=bg_rgba,
        )

    lowest_bg_bottom = None
    for line, color, gradient, line_font, line_height, shadow_offset, shadow_color in styled_lines:
        if letter_spacing:
            line_width = text_width_with_spacing(draw, line, line_font, letter_spacing)
        else:
            line_width = draw.textlength(line, font=line_font)
        if align == "center":
            x = box["x"] + (box["width"] - line_width) / 2
        elif align == "right":
            x = box["x"] + box["width"] - line_width
        else:
            x = box["x"]

        if bg_rgba and background_mode == "per_line" and line:
            pad_x = box.get("background_padding_x", 12)
            pad_y = box.get("background_padding_y", 8)
            bbox = draw.textbbox((x, y), line, font=line_font)
            if letter_spacing:
                # textbbox measures normal character spacing, which
                # undershoots the actual letter-spaced glyph run -- widen
                # the right edge to match line_width or the highlight
                # clips the last character(s).
                bbox = (bbox[0], bbox[1], x + line_width, bbox[3])
            rect = [bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y]
            draw.rounded_rectangle(rect, radius=box.get("background_radius", 0), fill=bg_rgba)
            lowest_bg_bottom = max(lowest_bg_bottom or 0, rect[3])

        fill_color = resolve_color(color)
        stroke_fill = resolve_color(stroke_color) if stroke_width else None
        if gradient:
            draw_gradient_line(img, line, line_font, x, y, gradient[0], gradient[1], stroke_width, stroke_color,
                                shadow_offset=shadow_offset, shadow_color=shadow_color)
        elif letter_spacing:
            draw_text_letterspaced(draw, line, line_font, x, y, fill_color, letter_spacing,
                                    stroke_width=stroke_width, stroke_color=stroke_fill)
        else:
            draw.text(
                (x, y), line, font=line_font, fill=fill_color,
                stroke_width=stroke_width, stroke_fill=stroke_fill,
            )
        y += line_height

    if "name" in box:
        box_bottoms[box["name"]] = lowest_bg_bottom if lowest_bg_bottom is not None else y


def render_slide(style_config_path: Path, image_override: str, text: dict, style_overrides: dict = None) -> Image.Image:
    """`style_overrides` is an optional {box_name: {prop: value, ...}} dict --
    properties there are merged on top of that named box's config from the
    style file for this render only (e.g. swapping just "background_color"
    per post for a color-rotation system, without duplicating the whole
    style file per color)."""
    config = json.loads(style_config_path.read_text())
    canvas_size = tuple(config.get("canvas_size", DEFAULT_CANVAS_SIZE))

    image_path = resolve(image_override) if image_override else resolve(config["template_image"])
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)  # phone photos often carry a rotation flag in EXIF, not the pixels
    img = img.convert("RGBA")
    img = fit_to_canvas(img, canvas_size)
    draw = ImageDraw.Draw(img)

    text_boxes = [dict(b) for b in config["text_boxes"]]  # shallow copies -- vertical_center_group below adjusts "y" without mutating the parsed style config

    # A style config may set "vertical_center_group": ["heading", "body"] (box
    # names in top-to-bottom order) to center that chain of boxes as a single
    # unit on the canvas, rather than each box sitting at a static y. Real
    # rendered height varies per slide (auto-shrink, line count), so this
    # measures the group first, then overrides the first box's "y" -- the
    # rest keep chaining off it via their existing "y_below".
    group_names = config.get("vertical_center_group")
    if group_names:
        box_by_name = {b["name"]: b for b in text_boxes}
        total_height = 0
        for i, name in enumerate(group_names):
            box = box_by_name[name]
            value = text.get(name)
            if not value:
                continue
            merged = {**box, **(style_overrides.get(name, {}) if style_overrides else {})}
            total_height += measure_text_box_height(draw, merged, value)
            if i > 0 and "y_below" in box:
                total_height += box["y_below"].get("gap", 0)
        first_box = box_by_name[group_names[0]]
        first_box["y"] = (canvas_size[1] - total_height) / 2
        first_box["valign"] = "top"

    box_bottoms = {}
    for box in text_boxes:
        value = text.get(box["name"])
        if not value:
            continue
        if style_overrides and box["name"] in style_overrides:
            box = {**box, **style_overrides[box["name"]]}
        draw_text_box(img, draw, box, value, box_bottoms)

    return img


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--content", required=True, help="Path to content spec JSON")
    parser.add_argument("--out", required=True, help="Output directory for numbered slide PNGs")
    args = parser.parse_args()

    content_path = resolve(args.content)
    content = json.loads(content_path.read_text())

    out_dir = resolve(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, slide in enumerate(content["slides"], start=1):
        style_config_path = resolve(slide.get("style") or slide["template"])
        img = render_slide(style_config_path, slide.get("image"), slide.get("text", {}), slide.get("style_overrides"))
        out_path = out_dir / f"slide_{i:02d}.png"
        img.convert("RGB").save(out_path)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
