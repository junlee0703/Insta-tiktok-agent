# Photo Backdrop Library

This library backs TikTok's teaching/mistake/CTA slide backgrounds (slide 1
is a separate `clips/` still frame, not part of this pool — see
`playbook.md` Workflow B). Real candid photos, bold text stamped on top. No
graphic design needed — just real photos from your life/work.

## What kind of photos to send

*(Placeholder — this section was IB-recruiting-flavored in the original and
needs your own equivalent, e.g. "day in the life of someone planning for /
living in retirement": workspace/planning shots, lifestyle/personality
shots, loosely on-theme is enough since the photo doesn't need to literally
match the text on top of it.)*

Doesn't need to be curated or styled — candid/unpolished reads as more
authentic, which is the point.

## Technical notes

- Any aspect ratio is fine — `generate_slides.py` automatically resizes and
  center-crops every photo to fill the 1080×1920 canvas (the same way TikTok
  itself displays photos), so text-box coordinates stay consistent regardless of
  a photo's original shape.
- JPG or PNG both work. HEIC (the default iPhone format) does **not** —
  convert it first, e.g. `sips -s format jpeg in.HEIC --out out.jpg` on macOS.
- `generate_slides.py` auto-corrects EXIF rotation on load (phones often store
  a photo "sideways" in pixels plus a rotation flag) — so a photo that looks
  right in Photos/Preview will also render right in the final slide, no manual
  pre-rotation needed.
- No minimum resolution requirement, but higher-res source photos hold up
  better once cropped/enlarged to fill the frame.

## One folder, two optional roles

Every photo lives in `rotation/`. By default every slide draws from that one
pool in a randomized, least-used-first order, reshuffled fresh per video.

Two optional special roles are configured in `rotation_positions.json` under
`roles`, both `null` out of the box:

- `fixed_slide_2` — one photo that always lands on TikTok's slide 2, every
  video, never counted for fairness. Leave it `null` and slide 2 is drawn from
  the general pool like any other slide.
- `cta_only` — one photo reserved exclusively for the closing CTA slide, never
  drawn for a teaching point. Leave it `null` and no photo is reserved.

Set either to one of your own filenames to turn it on. Nothing is hardcoded in
the picker, so both are safe to ignore entirely.

## Each photo needs a fixed text position

Every photo needs an assigned text position — this isn't a free per-slide
choice. See `rotation_positions.json` for the authoritative
machine-readable manifest (filename → `top` / `middle` / `bottom` /
`upper_left` / `upper_right` / `lower_left` / `lower_right`, or whatever tag
vocabulary you want — `scripts/pick_photos.py` just uses these as opaque
labels to avoid two adjacent slides sharing a position). Currently **empty**
— add an entry for every photo you drop into `rotation/`.

At least one photo must carry the `middle` tag: the CTA slide draws only from
the middle pool, and the picker stops with an explanatory error if that pool is
empty.

## How photos get used (full selection algorithm)

1. **Fixed slide 2**: always the `FIXED_SLIDE_2` photo. No exceptions.
2. **CTA slide (always the last slide)**: randomly drawn from every photo
   sharing the `middle` position tag (including `CTA_ONLY`, which is
   eligible *only* here).
3. **Every other slide** (the teaching points): randomly draw a photo from
   the full pool, excluding the two reserved photos above. The slide's text
   position is whichever position that photo owns in
   `rotation_positions.json` — position follows the photo, it's not chosen
   independently.
4. **No two adjacent slides may share a text position** — when drawing a
   photo for a slide, re-roll if its position matches the slide immediately
   before or after it in the sequence.
5. Repeating a photo within one post is fine if there are more slides than
   eligible photos, but don't lock in the same across-post ordering —
   reshuffle fresh per video.
