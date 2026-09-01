# Instagram + TikTok Content Agent — Playbook

## Goal

Create Instagram Reels for **<Your Brand>** (`@<your-handle>`), render and QA
them, then create them as Postiz posts.

**Posts are real and public. The gate is the copy.** The agent writes the
on-screen text and caption, shows them in the chat, and waits for your
go-ahead. Once you approve the wording it renders, uploads, and publishes
without asking again. Never create Instagram drafts. Turning on autopilot in
[brand.md](brand.md) skips the copy approval as well.

A typical schedule is three Reels per day at 7:00 AM, 12:00 PM, and 7:00 PM in
your own timezone. LinkedIn and TikTok are not active channels by default.

### "Make 3 vids" shorthand

`make 3 vids` authorizes the full three-Reel public Instagram workflow with no
questions or copy preview. Create distinct, knowledge-grounded Reels for 7:00
AM, 12:00 PM, and 7:00 PM America/Los_Angeles; rotate clips and highlights;
render and visually inspect every Reel; upload them; create scheduled posts;
verify the stored state/timestamps; and update `drafts/log.md`.

Date rule: a request received from 12:00 AM through 5:59 AM Pacific targets the
current date. A request received at or after 6:00 AM Pacific targets the next
date. This shorthand explicitly authorizes public publishing. Every Reel must
have music: call Postiz `audioSearch` (an empty query is fine for random or
trending results), choose a returned track at random, and pass its `audio.id`
when creating the post. Never use Meta Graph API directly, never guess an audio
ID, and never fall back to publishing without music. If music selection is
unavailable, stop before creating the post and report the blocker.

Publishing is done through the [Postiz](https://postiz.com) CLI (`postiz`), which is
already authenticated on this machine (OAuth2, org `3d4c47be-cad6-4c65-8a85-69614782819a`).

## Non-negotiable rules

1. **Never go public without explicit approval — but "public" means different
   things per platform.**
   - **LinkedIn**: always create as `postiz posts:create -t draft ...`. LinkedIn
     has no private option — the moment a post is promoted to `schedule` it's
     live to everyone. Never use `-t schedule` for LinkedIn unless the user
     explicitly says to publish a specific post.
   - **TikTok**: `-t schedule` with `content_posting_method: "DIRECT_POST"`
     and `privacy_level: "PUBLIC_TO_EVERYONE"` — real and public the moment it
     publishes. Same gate as Instagram: approve the copy in chat first, then
     publish. Every TikTok creation is a real API call, so say what is about
     to happen before making it, and never create more than one at a time.
2. **Upload before attaching media** (Postiz Rule 2). Raw file paths and external
   URLs are rejected by TikTok/LinkedIn. Always:
   ```bash
   PATH1=$(postiz upload output/<post>/slide_01.png | jq -r '.path')
   ```
   then pass `$PATH1` (comma-joined for multiple) to `-m`.
3. **Don't freelance on voice.** Don't write LinkedIn copy or TikTok scripts from
   imagination — pull structure/hooks/CTAs from `linkedin/style_guide.md` and
   `tiktok/style_guide.md`. If those are still empty, stop and ask the user
   for example posts first.
4. **Dates are required by Postiz** even for drafts (`-s` flag). Use a near-future
   placeholder timestamp if the user hasn't specified a real slot — the user can
   change it later in the Postiz dashboard when they promote the draft.

## Connected accounts

Integration IDs live in [brand.md](brand.md). List yours with:

```
postiz integrations:list
```

LinkedIn settings: max 3000 chars, no required extra settings for a personal/page
text post; carousel needs 2+ images and no video mixed in.

TikTok settings: one video OR one picture OR multiple pictures — must have at
least one attachment. **Default settings object for a video post:**
```json
{
  "privacy_level": "PUBLIC_TO_EVERYONE",
  "duet": true,
  "stitch": true,
  "comment": true,
  "autoAddMusic": "no",
  "brand_content_toggle": false,
  "brand_organic_toggle": false,
  "video_made_with_ai": false,
  "content_posting_method": "DIRECT_POST"
}
```
- `privacy_level: "PUBLIC_TO_EVERYONE"` — real and immediately visible to
  everyone the moment it publishes. Use `SELF_ONLY` only when the user
  explicitly asks to keep a specific video private.
- `content_posting_method: "DIRECT_POST"` — actually publishes. `"UPLOAD"` sends
  to the TikTok app inbox as an unfinished draft instead (expires in 24h, and
  TikTok silently discards every setting here except a 90-character `title`) —
  only use it if the user explicitly asks to review/edit in-app first.
- `autoAddMusic` — confirmed via `postiz integrations:settings` (2026-07-31):
  **this only applies to photo posts.** For a video post it does nothing, so it's
  set to `"no"` here (still required by the schema, just inert). **There is no
  API-level way to add TikTok's own auto-picked or a specific sound to a video
  post** — that only happens if a human manually edits the post in the TikTok
  app. Per explicit user decision 2026-07-31, TikTok video posts are silent for
  now rather than solving this by baking in real audio (see Workflow C).

Instagram settings: `post_type: "post"` for a feed Reel; `audio` (`{"id":
"<track id>"}`, found via the `audioSearch` integration tool) attaches a real
licensed track — this is Instagram-only, TikTok has no equivalent. As of
2026-08-29, music is mandatory on every Reel. Use an empty
`audioSearch` query for random/trending choices and vary tracks within a batch
when possible. If Postiz authentication is expired, the tool is unavailable,
or no usable track is returned, stop before post creation rather than silently
publishing without music.

## Workflow A — LinkedIn text post

**As of 2026-07-31, LinkedIn runs its own complete playbook, fully rewritten
from scratch — see `linkedin/style_guide.md` for the 5 post types, weekly
schedule, and full rule set.** It no longer shares a topic-pillar system with
TikTok/Instagram, and the old mandatory "Class of 2028 + Class of 2029:"
hook / lead-magnet-checklist CTA structure is gone entirely, not just
superseded — don't reach for it.

1. Read `linkedin/style_guide.md` in full and write to whichever post type
   and structure you documented there.
2. Draft copy around the topic. **Any factual/technical claim must come from
   `knowledge/`** — check it before writing anything with a specific stat,
   formula, or "how it actually works" detail. If it's not covered there,
   say so instead of guessing.
3. **Aggressive line breaks, one CTA max (most posts get zero), hook names
   the concrete topic in the first line** — see `linkedin/style_guide.md`
   rules 1-4 for the full detail, these are the most-violated ones.
4. Post the full text in chat and get explicit approval before touching
   Postiz — same standing rule as every other platform.
5. Create as a draft:
   ```bash
   postiz posts:create -c "<copy>" -s "<ISO8601 date>" -t draft -i <YOUR_LINKEDIN_INTEGRATION_ID>
   ```
6. Log it in `drafts/log.md` with the returned post id and a one-line summary.
7. Tell the user it's ready to review in Postiz.

## Workflow B — TikTok photo slideshows

**Reverted, 2026-08-03, explicit user instruction ("revert the tiktok
change... go back to the slideshows instead of copying insta").** The
2026-07-31 "TikTok copies the Instagram Reel video" pivot is undone. TikTok
is back to its own photo-slideshow build using `scripts/pick_photos.py` +
`scripts/generate_slides.py`. **What's still shared with Instagram**: the same post type (of the day's 3-post rotation), the same
topic, and the same scheduled time — only the *delivery format* differs
(rendered photo carousel vs. Instagram's video). The caption format
(numbered keycap-emoji points + fixed CTA line) is shared verbatim between
platforms — the on-screen visual medium differs, the caption text does not.

**Visual system replaced 2026-08-03/04, explicit user spec ("THIS IS THE
TIKTOK PLAN NOW. DO ALL TIKTOKS LIKE THIS").** Real photo backdrops and the
fixed CTA wording both stay (confirmed with the user after their first spec
dropped both) — everything else about how text sits on the slide is new:
Montserrat (Black/Bold/Medium, copied into `fonts/` from local system
sources — no true "ExtraBold" weight was available, Black substitutes for
it), every text element sits on its own solid rounded-corner highlight box
(subtitle-style, not full-width), a small top brand tag and a bottom-right
watermark on every slide (both your own wording — see step 4 of the workflow),
and up to **8 slide roles** instead of 3: hook → up to 5
teaching slides (yellow heading + white body, one concept each, key
numbers/terms picked out in yellow) → one "here's what most people get
wrong" slide (red heading) → CTA (existing fixed text, yellow-box
treatment). Not every post needs all 5 teaching slots — use as many as the
topic actually supports. Teaching/mistake/CTA slides implemented as
`styles/tiktok_teaching_boxed.json`, `styles/tiktok_mistake_boxed.json`,
`styles/tiktok_cta_boxed.json`. Caption shrinks to match — see step 6.

**Teaching/mistake/CTA text sizing and CTA copy changed 2026-08-05, explicit
user instruction.** Heading/body font sizes on `tiktok_teaching_boxed.json`
and `tiktok_mistake_boxed.json` both raised **+10px** (heading 32/24 min →
42/34 min, body 24/20 min → 34/30 min) — box `x`/`width` (90/900) held
identical, only the text itself got bigger, see each file's `_note`.
`tiktok_cta_boxed.json`'s `cta` box: font raised the same way (28/22 min →
38/32 min), and its text color switched **white → black** (`#000000`) while
`background_color` (the yellow highlight) is unchanged. **The on-screen CTA
slide takes your own fixed wording** — write it once, then use it verbatim on
every post rather than rewording it per video. Full caps reads well in this
box if that suits your brand. This is the on-screen TikTok CTA slide only; the
caption's own final-line CTA (see "Content format" below) is separate and can
differ.

**Slide 1 changed again 2026-08-05, explicit user spec ("the 1st slide will
look identical to the reels").** The hook slide is no longer its own boxed
style on a `photos/rotation/` backdrop. Slide 1 now uses the **exact same
treatment as the Instagram Reel** — `styles/ig_question_overlay.json` (brand
tag + technical question, bundled Montserrat, per-line highlight boxes) —
stamped onto a **still frame pulled from one of the 3 `clips/` videos**
(least-used-first via `pick_clip.py`, same shared pool as Instagram) instead
of a `photos/rotation/` photo. `photos/rotation_usage.json`'s old "hook"
counter and `pick_photos.py`'s hook slot are gone (see that script's
docstring) — the photo picker now only ever fills fixed slide 2 / body / CTA.

**One deliberate difference from Instagram, same 2026-08-05 instruction**:
TikTok's slide 1 does **not** render the `caption_below` layer ("caption
below ↓") that Instagram's overlay has — that line only makes sense on
Instagram, where the caption sits directly below the reel in-app; TikTok's
teaching content already lives on the slides themselves. Build slide 1's
`text` dict with `brand_tag` + `hook` + `technical_question` only —
leave `caption_below` out of the dict entirely (an unset box is skipped by
`render_slide()`, not rendered blank).

**Corrected same day**: slide 1's hook (and its consequence word) must
be **the same as Instagram's**, not independently authored per platform —
i.e. it must follow the exact current Instagram hook-writing template
(`Goldman Stanley ..., and you're getting <CONSEQUENCE>.`, consequence word
ALL CAPS from the 9-word bank) and, when a companion Instagram Reel exists
for the same post, reuse that reel's hook text verbatim rather than writing
a new one. (This replaces an earlier, incorrect version of this section that
said TikTok could freely use its own hook text — it can still pick its own
*topic*, just not a differently-worded hook once the topic's set.) The
technical question is unaffected by this — still authored per Workflow C's
phrasing pattern, quoted.

**TikTok slide 1 forked off the shared Instagram style, 2026-08-05, explicit user spec ("FOR TIKTOK ONLY").** Slide 1 no longer renders `styles/ig_question_overlay.json` directly — it now uses `styles/tiktok_question_overlay.json`, a TikTok-only fork with exactly two differences from the Instagram file: (1) `brand_tag` moved down `y=200 → 350`; (2) a new `swipe_right` box (`"Swipe right →"`) rendered on every TikTok slide 1, always the same fixed text, not authored per-post. `hook` and `technical_question` are otherwise byte-identical between the two files (same position/size/font/color) — this is a narrow, deliberate divergence, not a full re-split; Instagram's `ig_question_overlay.json` is untouched. The new file has no `caption_below` box at all (TikTok never rendered that layer anyway, per the rule above — now enforced structurally by the file not defining it, rather than by the build script omitting it from the `text` dict).

**`swipe_right` recentered and repositioned 2026-08-06, explicit user instruction ("The 'Swipe right' is like far left. Center it... move it down 150 Y points... make it 10px bigger").** Was left-aligned at `x=30, y=1100, width=400`, Arial Bold 32px. Now `x=0, y=1250, width=1080`, `align: "center"` (matching `brand_tag`'s full-canvas-width-centered pattern rather than a narrow left-anchored box), Arial Bold 42px. Text/color/stroke unchanged (yellow `#FFEE8C`, black stroke, no highlight background). **The earlier "tight spacing" flag from 2026-08-05 is superseded by this move** — at y=1250 (150px lower than the old y=1100), `swipe_right` now sits well clear of `technical_question`'s lowest line even for a 2-line question; re-check on a 3-line question regardless, same as always.

**`brand_tag` font size synced to Instagram's, 2026-08-07, explicit user instruction ("The brand tag... didnt change. It should be the same font size as instagram").** The 2026-08-06 batch only updated Instagram's `brand_tag` `font_size` (36→46); TikTok's fork was never touched for size, only for `y` and the `swipe_right`/color/radius changes documented above — an oversight, since `brand_tag` size was never meant to diverge between the two files (only `y` position and the `swipe_right` box are the deliberate TikTok-only differences). Now `font_size: 46` on both. TikTok's `brand_tag` also moved up 50px same day (`y=350→300`) alongside the same move on Instagram's file — see the "hook capped at 3 lines" note below for both.

**9-color highlight rotation, 2026-08-05, explicit user spec, both platforms.** `brand_tag` and `technical_question` each have a `background_color` (the highlight box behind the text, not the text color itself, which stays unchanged). As of this date that color rotates per post instead of being fixed in the style file:
- **The 9 colors, in rotation order** (replaced 2026-08-06, see the dated note below for the original darker set): 1. `#2E2E5E` navy, 2. `#3A3A3A` charcoal, 3. `#5E3660` purple, 4. `#1A3650` midnight blue, 5. `#5E3636` burgundy, 6. `#365E36` forest green, 7. `#5E5836` bronze, 8. `#365E5E` teal, 9. `#503660` plum. All chosen by the user specifically to work with white text.
- **3 colors per day** (i.e. per 3-post batch), cycling through all 9 over 3 days/batches, then repeating from color 1. A "day" here means one topic/post's worth of content, not literal calendar days if batch size ever changes — the counter is posts, not dates.
- **Within one post, `brand_tag` and `technical_question` always share the exact same color** — that's one video's color. The *next* video (next post in the batch) gets the next color in the list. Instagram Reel and its TikTok companion for the *same topic* share the same color too (they're one "video" conceptually, just two delivery formats) — the rotation advances per **topic**, not per platform post.
- **Rotation state**: historical assignments are recorded in `drafts/log.md`.
  No batches have run yet, so **the next unused color is #1, navy `#2E2E5E`**;
  continue with charcoal `#3A3A3A` and purple `#5E3660`, then carry on down
  the list and restart at color #1 after plum. Update this line and the latest batch
  log after each new set so the rotation does not reset or skip.
- **Colors replaced 2026-08-06, explicit user instruction** ("these 9 colors are way too dark that I cant really tell the difference"). The original 9 (`#1A1A2E`, `#1C1C1C`, `#2D1B2E`, `#0D1B2A`, `#2E1A1A`, `#1A2E1A`, `#2E2B1A`, `#1A2E2E`, `#2A1A2E`) are retired — same 9 hues/order, each one lightened so they read as distinct colors in a grid view rather than all looking near-black, still dark enough for white text. The placeholder `background_color` baked into `styles/tiktok_question_overlay.json` (a fallback only, always overridden per-post) was updated to the new color 1, `#2E2E5E`; `styles/ig_question_overlay.json`'s own baked-in defaults (`#000000D9`/`#1A1A1ACC`) were never part of the rotation and were left as-is.
- **Highlight corners rounded 2026-08-06, explicit user instruction, both platforms.** Every box with a `background_color` (i.e. every "highlighted" text — `brand_tag` and `technical_question` on both platforms' hook-question style, plus TikTok's `heading`/`body` teaching and mistake boxes and the `cta` box) now uses `background_radius: 16` (was 0 on the hook-question boxes, 6/4 on the TikTok teaching/mistake/CTA boxes). `hook`, `caption_below`, and `swipe_right` have no `background_color` at all (stroked text only) so this doesn't apply to them.
- **Implementation**: no new style files per color. `scripts/generate_slides.py`'s `render_slide()` takes an optional `style_overrides` dict (`{box_name: {prop: value}}`) merged onto that box's config for one render only — a content spec's slide can set `"style_overrides": {"brand_tag": {"background_color": "<hex>"}, "technical_question": {"background_color": "<hex>"}}` (used for TikTok slide 1, built via `generate_slides.py`). `scripts/build_ig_reel.py` (Instagram's own build path, which doesn't go through a content-spec file) got a matching `--highlight-color <hex>` CLI flag that does the same merge internally. Only `background_color` changes via this override mechanism — padding, radius, mode, font, text color all stay exactly as authored in the base style file, per the user's explicit "just changing the COLOR of the HIGHLIGHT, nothing else" (radius is a separate, direct edit to the style files themselves, not part of this per-post override).

`scripts/generate_slides.py` gained an `inline_runs` box option to support
this: mixed-color runs (e.g. a sentence with a couple of yellow-highlighted
numbers) now wrap as one flowing paragraph instead of one run per line —
needed for the teaching/mistake body text. Only used when a box sets
`"inline_runs": true`; boxes that don't set it keep the original
one-run-per-line behavior.

**Teaching/mistake/CTA text enlarged and vertically centered, 2026-08-08,
explicit user instruction** ("for the slides after the 1st slide/hook, enlarge
the texts... right now the text is sitting in the upper third and it's too
small for how fast people scroll. center it vertically so it sits in the
middle of the screen, bump the font size up 30-40%"). Applies to
`styles/tiktok_teaching_boxed.json`, `styles/tiktok_mistake_boxed.json`, and
`styles/tiktok_cta_boxed.json` — every slide except slide 1 (the hook
slide keeps its own existing size/position rules, untouched). Two changes:
- **Font size, ~35% bump** (midpoint of the 30-40% range): teaching/mistake
  heading 42/34 → 57/46, body 34/30 → 46/41; CTA 38/32 → 51/43. `x`/`width`
  held identical, same pattern as every prior font-size change to these
  boxes. Heading/body `height` and the `y_below` gap between them were
  scaled by the same ~35% (heading height 140→190, body height 400→540, gap
  30→40) so the auto-shrink line-count tolerance stays proportionate to the
  bigger font instead of clamping down harder than before.
- **True vertical centering, not just a bigger fixed y.** The old fixed
  `y: 576` put heading+body in the upper third regardless of how much text a
  given slide had. Text height varies per slide (1 vs. 2 body lines,
  auto-shrink), so a single hand-picked y can't center every slide — a
  slide with more text would still start too high. `scripts/generate_slides.py`
  gained a real fix for this: a style config can set
  `"vertical_center_group": ["heading", "body"]` (box names, top-to-bottom
  order). `render_slide()` now measures each named box's actual rendered
  height first (new `measure_text_box_height()`, a non-drawing pass that
  mirrors `draw_text_box()`'s own sizing logic exactly — same `fit_text`/
  `wrap_text`/`wrap_runs_inline` calls, just no pixels drawn) before the real
  render pass, sums them plus the `y_below` gap, and overrides the *first*
  box's `y` so the whole group centers as a unit on the canvas
  (`(canvas_height - total_group_height) / 2`) — `body` still chains off
  `heading` via the pre-existing `y_below` mechanism, unchanged. Both
  `tiktok_teaching_boxed.json` and `tiktok_mistake_boxed.json` now set
  `vertical_center_group: ["heading", "body"]`. The CTA box didn't need this
  — it was already a single box at `y: 860, height: 200, valign: "center"`,
  which already put its center at `y: 960`, exactly the canvas midpoint
  (1920/2) — only its font size changed.
- Spot-checked against a re-render of the existing Treasury Stock Method
  TikTok spec (both a 1-line and a 2-line body slide, plus the CTA slide):
  text lands centered in both cases, noticeably larger, still wraps cleanly
  inside the 900px box width.

**Teaching/mistake slide text capped at 8-10 words per slide, 2026-08-06,
explicit user instruction** ("shorten the text and make it max 8-10 words
per slide. if it doesnt fit in one glance, split it into two slides").
Applies to slides 2+ (everything after the hook) — the heading+body
combined on any one `tiktok_teaching_boxed.json`/`tiktok_mistake_boxed.json`
slide should read in one glance, roughly 8-10 words total. If a teaching
point genuinely needs more than that, split it across two consecutive
slides rather than cramming it — this counts against the "up to 5 teaching
slides" budget same as any other slide. Does not apply to slide 1 (the
technical question keeps its own existing length/phrasing rules) or
to the CTA slide (fixed wording, unaffected).

**Build steps, one slideshow per post:**
1. Write the on-screen text pieces — the technical question
   for slide 1 (see "Content format" above for the current phrasing/length
   rules), one short line per teaching point (up to 5, 8-10 words
   per slide per the rule above), the mistake-slide line (same word cap),
   and the caption. **Any factual claim on a teaching or mistake slide must
   come from `knowledge/`**, same as always. Draft and get approval in chat
   first, same standing rule as always.
2. Pick a clip for slide 1, least-used-first, never by hand (same shared
   pool as Instagram):
   ```bash
   python3 scripts/pick_clip.py
   ```
   Extract a still frame to stamp the overlay onto:
   ```bash
   ffmpeg -i clips/<clip> -ss 2 -vframes 1 -y output/<name>/_slide1_frame.png
   ```
3. Pick photos for the rest of the slides, least-used-first, never by hand:
   ```bash
   python3 scripts/pick_photos.py --total-slides <N>
   ```
   `<N>` = the number of photo slides: body slides + CTA, plus one more if
   you configured a fixed slide 2 in `photos/rotation_positions.json` (e.g. 7
   for fixed slide 2 + 5 teaching/mistake + CTA). This does **not** include
   slide 1 (handled in step 2).
   Prints `{slot, image, position}` per slide — `position` still only
   drives the picker's own fairness/diversity logic now, it doesn't select
   a style file (the boxed styles use one fixed on-canvas layout per role,
   not a position variant per photo).
4. Build the content spec for `scripts/generate_slides.py`: slide 1 uses
   `styles/tiktok_question_overlay.json` (as of 2026-08-05, the TikTok-only
   fork of the Instagram treatment — see the "TikTok slide 1 forked" note
   above) with the step-2 extracted frame as its `image`, `text.brand_tag` /
   `text.technical_question` / `text.swipe_right` (always
   `"Swipe right →"`, fixed, not authored per-post), and
   `"style_overrides": {"brand_tag": {"background_color": "<hex>"}, "technical_question": {"background_color": "<hex>"}}`
   set to that post's color from the 9-color rotation (see the rotation note
   above for the current position); the fixed slide 2 and each
   body slide use `styles/tiktok_teaching_boxed.json` (or
   `styles/tiktok_mistake_boxed.json` for the one mistake slide) with
   `text.heading` + `text.body` (the body as `{"runs": [...]}` with
   `"color": "#FFCC00"` on the words worth calling out); the last slide uses
   `styles/tiktok_cta_boxed.json` with `text.cta` = your own fixed CTA
   wording, identical on every post. Slides 2+ also need `text.brand_tag` =
   your channel's short positioning line and `text.watermark` = your handle or
   brand name, both kept identical across posts (slide 1's brand tag comes from the
   `tiktok_question_overlay.json` box of the same name — don't duplicate a
   watermark on slide 1, that style doesn't have one). Watch punctuation at
   run boundaries — attach a trailing comma/period to the end of the run it
   belongs to (`"Cost of Equity,"`) rather than starting the next run with
   it (`", plus"`), or the renderer inserts a stray space before it.
5. Render:
   ```bash
   python3 scripts/generate_slides.py --content <spec.json> --out output/<name>/
   ```
   Read back slide 1, one teaching slide, the mistake slide, and the CTA
   slide before uploading — confirm legibility (slide 1's brand tag and
   question both stay inside the upper 45% of the canvas, same check as
   Workflow C step 4) and that punctuation reads clean.
6. Upload all slide PNGs, comma-joined, as TikTok's `-m` (a "picture" post,
   not a video):
   ```bash
   postiz upload output/<name>/slide_01.png | jq -r '.path'
   ```
   (repeat per slide, then join the returned paths with commas for `-m`).
7. **Caption is now short** — the teaching content lives on the slides, not
   the caption. Max ~2 lines (a one-line hook/tease + the CTA line), then
   hashtags: `#investmentbanking #finance #interviewprep #wallstreet
   #banking`. This replaces the old numbered-caption-shared-with-Instagram
   convention for TikTok specifically — Instagram's own caption (Workflow C)
   is unaffected.
8. **Settings** — default is **public** (`privacy_level: "PUBLIC_TO_EVERYONE"`),
   matching the "Non-negotiable rules" section above.
   `{"privacy_level":"PUBLIC_TO_EVERYONE","duet":true,"stitch":true,"comment":true,"autoAddMusic":"yes","brand_content_toggle":false,"brand_organic_toggle":false,"video_made_with_ai":false,"content_posting_method":"DIRECT_POST"}`.
   Only switch to `"privacy_level":"SELF_ONLY"` if the user explicitly asks
   to go back to private for a specific video. If the user asks for a
   **draft** specifically, that means a real TikTok-native draft —
   `content_posting_method: "UPLOAD"` instead (real API call, 24h expiry,
   every setting except a `title` field is discarded — see
   the note above and tell the user the expiry
   before creating it). Either way:
   ```bash
   postiz posts:create -c "<short caption + hashtags>" \
     --settings '<settings object per above>' \
     -m "<comma-joined slide image paths>" \
     -s "<ISO8601 date>" -t schedule \
     -i <YOUR_TIKTOK_INTEGRATION_ID>
   ```
9. Log in `drafts/log.md` (post ID, clip used for slide 1, photos used for
   the rest, slide roles used).
10. **Verify it actually published.** `QUEUE` at creation time does not mean
    it will go live — TikTok posts fail silently into `state: "ERROR"` at a
    rate of roughly 1 in 3 (see the 2026-08-08 audit entry in
    `drafts/log.md`), and Postiz neither retries nor notifies. Either poll
    until the post leaves `QUEUE`, or rely on the cron check below.

## Catching failed posts

Postiz can take **~30 minutes past the scheduled time** to flip a failed publish
from `QUEUE` to `ERROR`, so a post that is merely late is not a separate
problem — it is this one mid-transition. Don't act on a late `QUEUE` until that
lag has passed.

`scripts/check_post_health.py` reports any post in `ERROR`, plus any post
still sitting in `QUEUE` more than 40 minutes past its slot:

```bash
python3 scripts/check_post_health.py --days 2   # exits 1 if anything is wrong
```

`scripts/post_health_cron.sh` wraps it for cron: appends to
`drafts/post_health.log` and raises a macOS notification on failure. Installed
in the user's crontab as of 2026-08-08, running at 6:25/11:25/17:25 Pacific,
about 25 minutes after each 8am/1pm/7pm Central slot.

**Recovering a failed post**: delete it, re-upload the already-rendered slides
from its `output/` folder, and recreate it with the same caption and settings
(step 8 above). Do not rebuild the media — it is not the cause, and all four
recorded failures republished successfully from the identical bytes. Reposting
is still a real public API call, so it needs the user's go-ahead like any other.
**This is the TikTok-specific finding** (silent async publish failures, ~1 in
3 since 2026-08-05) — see the Instagram-specific exception immediately below,
where identical-bytes retries did *not* work and something had to change.

**Instagram recovery, when a same-content retry also fails, 2026-08-16.**
Instagram `ERROR` is rare (2 on record total, vs. dozens of clean posts) — a
first failure is still most likely a one-off, recover it exactly like the
TikTok case above (identical bytes, no changes). **But if the identical-bytes
retry ALSO errors, don't retry a 3rd time with the same settings** — the
Beta Stock Move post (2026-08-16) did this twice in a row on the exact same
video + audio, while every other Instagram post around it published cleanly
(ruling out a general outage) and `ffprobe` showed the video file itself was
structurally normal (valid H.264/AAC, both streams present, nothing like the
2026-07-19 no-audio-stream case). That left the Instagram `audio.id` as the
one thing unique to the failing post. **Fix that worked**: re-upload the same
video, but attach a *different*, previously unused audio track via a fresh
`audioSearch` call, rather than reusing the same track ID a third time. Not
confirmed as the definitive root cause (Postiz's API genuinely exposes no
error/message field on a post object — checked the raw JSON directly, not
just filtered CLI output — so there is no way to see the actual rejection
reason from here), but it is the best-supported theory and it worked. **The
user separately flagged that Postiz's own troubleshooting guidance lists
"duplicate text" as a real rejection category** — both failed attempts on
this post reused the identical caption, and the fix here only varied the
audio, not the caption, so that variable is still untested; if a future
same-content Instagram retry fails a 2nd time, try varying the caption
wording too, not just the audio track, and check the Postiz web dashboard's
per-post tooltip if the user has access — that's the one place the actual
error message lives, not the CLI.

**Historical note (no longer current):** between 2026-07-31 and 2026-08-03,
TikTok posts were a straight copy of the Instagram Reel's rendered video
(silent audio, same file/caption/schedule) — see `drafts/log.md`'s
2026-08-01/02/03 batch entries for what was actually built under that
scheme.
That approach is what's being reverted here.

**`UPLOAD` mode confirmed working with a future `-s` date, 2026-08-04**: the
settings schema still requires every field (`privacy_level`, `duet`,
`stitch`, `comment`, `autoAddMusic`, `brand_content_toggle`,
`brand_organic_toggle`, `content_posting_method` — checked via
`postiz integrations:settings <tiktok-integration-id>`), even though TikTok
only keeps `title` (≤90 chars, a separate settings field from `-c`) once
`content_posting_method` is `"UPLOAD"`. Post landed `QUEUE` in Postiz at the
correct future date on the first real test — no issue scheduling ahead.

## Workflow C — Building the Instagram Reel video

This is the actual video-build pipeline, originally developed for Instagram
Reels (see the 2026-07-21/07-27
`drafts/log.md` batch notes for its history). **As of 2026-08-03 this is
Instagram-only again** — TikTok reverted to its own photo-slideshow build,
see Workflow B above.

**On-screen text overhaul, 2026-08-03, Instagram only, explicit user spec**
(see `styles/ig_question_overlay.json`'s `_note` for the full pixel/hex
spec): replaces the old time-gated multi-segment overlay with **one static
image, stamped once at frame 1 and held for the whole clip — no animation,
no transitions, no on-screen CTA.** Three fixed layers, always in this
order:
**There are two of these layers** (see "Content format" below):
1. **Brand tag** (top) — your channel's short fixed positioning line, small,
   white at 70% opacity, letter-spaced. Same every video, not authored
   per-post.
2. **Question** — the specific question this post is about, **always in
   quotation marks** if you keep that convention, white text, each line on
   its own solid dark-gray highlight box, positioned where the old hook
   layer used to start (see `styles/ig_question_overlay.json`'s `_note`).
   There's no on-screen CTA layer anymore — the CTA lives only in the
   caption (see the CTA rule below).
3. **All text stays in the upper 45% of the canvas** (top 864px of 1920) so
   the clip's own visual (typing/headset) stays clear underneath — check
   this on the extracted frame in step 4 below, don't just trust the auto-
   shrink.

**hook capped at 3 lines, 2026-08-07, explicit user instruction, both
platforms** ("make sure it is maximum 3 lines. The ones u posted right now
are 4 lines and its covering my face"). `hook` was `auto_shrink: false`
(fixed at 48px no matter how long the hook text was) — a long hook could
wrap to 4 lines and cover the subject's face in the clip. Now
`auto_shrink: true`, `min_font_size: 30`, and a new `max_lines: 3` property
the renderer shrinks the font down to the 30px floor until the wrapped text
fits in 3 lines or fewer. **`max_lines` is a new capability in
`scripts/generate_slides.py`'s `fit_text()`** — when a box sets it, line
count (not pixel height) becomes the fit criterion, since the real
constraint here is "don't run past N lines," not any particular height
value. Only `hook` sets `max_lines` on either platform's style file;
every other box is unaffected (defaults to the old height-based behavior).
When writing a hook, keep it reasonably short regardless — 3 lines at a
30px floor is still meant to look like an intentional confident headline,
not a last-resort shrink to fit an overlong sentence; if a hook needs the
floor size to fit, it's a signal to write it tighter, not a green light to
always write long ones.

**`technical_question` capped at 3 lines too, 2026-08-12, explicit user
instruction, both platforms** ("The question text cannot exceed 3 lines,
same as the old confrontational hook"). Applied to the other on-screen text
layer, same idea as `hook`'s cap: `technical_question` was
`auto_shrink: false` (fixed at 42px regardless of length) on both
`styles/ig_question_overlay.json` and `styles/tiktok_question_overlay.json`.
First pass (same day) copied `hook`'s exact mechanism — `auto_shrink: true`,
`min_font_size: 28`, `max_lines: 3` — and used it to fix the 15 already-scheduled
posts by shrinking their font. **This was wrong and reverted the next day.**

**Corrected 2026-08-13, explicit user instruction** ("When i say stay within
3 lines, i dont mean make the font smaller. Keep the font at 42px, dont
shrink the font. To make it 3 lines, shorten the words in the
question/make it more concise"). `technical_question` is back to
`auto_shrink: false`, fixed `font_size: 42`, no `min_font_size`/`max_lines`
on both style files (those two properties are inert anyway once
`auto_shrink` is off — see `generate_slides.py`'s `draw_text_box()`/`fit_text()`:
with `auto_shrink: false`, `min_size` collapses to `start_size`, so the fit
loop returns on its very first pass regardless of line count; `max_lines`
never gets a chance to trigger a shrink). **The 3-line cap is enforced by
wording discipline, not rendering**: draft the question, test-render it at
the fixed 42px, and if it wraps past 3 lines, shorten the sentence itself
(drop a clause, use a shorter synonym or acronym already established
elsewhere — e.g. "TEV" instead of "Enterprise Value" — cut a redundant
phrase) rather than letting any mechanism shrink the font. Same
"write it tighter" principle already documented for `hook`, just
without a font-size fallback this time. **A self-contained question (every
number the viewer needs, per the 2026-08-10 rule below) still has to fit
in 3 lines at 42px** — if it genuinely can't, that's a signal to simplify
the scenario or use fewer variables, not to let it run long or shrink the
font.

**On 2026-08-12, every already-scheduled Instagram post (15 total) was
audited against the cap and 7 were reposted using the (since-reverted)
font-shrink fix; on 2026-08-13, all Instagram + TikTok posts scheduled for
2026-08-14 and later were re-audited against the corrected fixed-42px rule
and re-reworded/reposted where needed** — see `drafts/log.md` for the exact
before/after wording on each.

**Both platforms' `brand_tag` also moved up 50px, same instruction,
same day**: Instagram `y=330→280`, TikTok `y=350→300` (TikTok keeps its
existing +150px offset from Instagram's position, now 300 vs. 280 instead
of 350 vs. 330).

**Active workflow:** Instagram is the only active channel by default. The agent
selects a supported two-line pairing (`brand_tag` + numbered statement) and
writes the caption, then **shows that copy in the chat and waits for approval**
(see "Copy approval" in `AGENTS.md`). Once approved it renders, QAs, uploads,
and creates the post with `-t schedule` as a real public post without asking
again.

**Credibility-led title rule, added 2026-08-29:** every Reel's top `brand_tag`
must be specific about the account owner's relevant credibility. Include an
identity fact established in `instagram/style_guide.md`, selected to match the
topic. A generic label such as "career advice," "money lessons," or
"things I learned" is not sufficient on its own. Do not invent a company,
job title, certification, exact tenure, or any other credential not already
established. Keep the title to at most two lines and confirm its fit in the QA
frame before upload.

1. Pick a topic (see "Content format" above for your own topic-scope
   rules — the original's IB-specific exclusions don't apply here). Write
   the on-screen question and the full caption — master audience rule and
   `knowledge/`-sourcing requirement all still apply (see
   `tiktok/style_guide.md`). **Captions must be genuinely elaborated AND
   structured as a numbered list (1-4 or 1-5), with the CTA visibly on its
   own final line** (see "Content format" below for the exact structure).
   This is Instagram's own on-screen text now — TikTok's separate
   photo-slideshow render (Workflow B) needs its own numbered-listicle slide
   breakdown from the same topic/caption, not a reuse of just the hook +
   question.
   Exact copy does not require user pre-approval for Instagram drafts. Keep all
   substance grounded in `knowledge/`, then render and visually inspect before
   uploading.
2. Pick a clip, least-used-first, never by hand:
   ```bash
   python3 scripts/pick_clip.py
   ```
   Prints the chosen filename from `clips/` and updates
   `clips/clips_usage.json`. If a new clip gets added, no position/category
   tagging needed here (unlike `photos/`) — it's a single undifferentiated
   pool.
3. Build the video with the static overlay:
   ```bash
   python3 scripts/build_ig_reel.py --clip <filename in clips/> \
     --brand-tag "<first line from the approved pairing>" \
     --question "<on-screen question, incl. quotation marks if you want them>" \
     --highlight-color "<hex from the 9-color rotation>" \
     --out output/<name>/<name>.mp4
   ```
   `--highlight-color` (added 2026-08-05) sets that post's `brand_tag` +
   `technical_question` highlight color per the 9-color rotation — see the
   rotation note above for the current position; omit it only if deliberately
   falling back to the style file's baked-in default.
   Renders one transparent overlay PNG via `generate_slides.render_slide()`
   against `styles/ig_question_overlay.json` (brand tag + question,
   bundled Montserrat from `fonts/`, per-line highlight boxes), composites it onto the clip for its **entire** duration
   (no time-gating), mixes in a silent AAC track sized to the clip's real
   duration (5-8s, matches the clip — no more CTA-driven duration math), and
   writes the final `.mp4`.
4. Extract and look at one frame before uploading (there's only one static
   frame now, not one per segment) — confirm the hook and question both fit
   on their highlight boxes, stay legible, and stay inside the upper 45%:
   ```bash
   ffmpeg -i <video> -ss 2 -vframes 1 -y <frame>.png
   ```
   then Read the frame.
5. Upload the rendered video:
   ```bash
   postiz upload output/<name>/<name>.mp4 | jq -r '.path'
   ```
6. Create the Instagram post as a real public Postiz scheduled post. The copy
   was already approved in chat, so no further confirmation is needed here:
   ```bash
   postiz integrations:trigger <your-instagram-integration-id> audioSearch \
     -d '{"q":""}'

   postiz posts:create -c "<full numbered caption, CTA on its own final line>" \
     --settings '{"post_type":"post","audio":{"id":"<random returned track id>"}}' \
     -m "<uploaded media path>" \
     -s "<ISO8601 date>" -t schedule \
     -i <your-instagram-integration-id>
   ```
   **Music rule updated 2026-08-29:** the account was changed to an Instagram
   business account so music selection should now be available. Every Reel
   must use a real track returned by `audioSearch`; an empty query is the
   default when any random/trending track is acceptable. Select distinct
   tracks within a three-Reel batch when enough results are available. The
   earlier 2026-08-22 no-audio fallback is retired. Never invent or guess an
   audio ID. If Postiz authentication is expired, `audioSearch` is unavailable,
   or the search returns no usable result, stop before `posts:create` and report
   the blocker. Do not publish a silent Reel.
7. Log the Instagram draft in `drafts/log.md`: Postiz ID, clip, audio track,
   and intended slot. Confirm its state is `DRAFT` with `postiz posts:list`.

## Content format

**Current format.** The audience, Reel structure, and the
on-screen pairing bank are in `instagram/style_guide.md`. For
Instagram, the first line of a pairing is rendered in the existing
`brand_tag` box and the second line is rendered in the existing
`technical_question` box. The second line is now a numbered statement, not a
question, and the advice itself belongs in the caption. The `--question`
command-line option and `technical_question` JSON box name remain unchanged
only for compatibility. Every first line must include the account owner's
topic-relevant credibility; generic positioning titles are prohibited.

**The format**: a static on-screen overlay — brand tag plus a single on-screen
question — held for the whole clip, no separate hook layer and no on-screen
CTA (see `styles/ig_question_overlay.json`'s `_note` and Workflow C for the
exact layers and positions). TikTok's slide 1 mirrors it, plus its own
teaching/mistake/CTA slides (Workflow B). The rules that apply to that
on-screen question and the caption under it:

- **No dashes anywhere in on-screen text.** Covers every rendered-to-canvas
  text piece on both platforms — `technical_question`, and TikTok's
  `heading`/`body` teaching/mistake/CTA text — not caption copy, which is
  unaffected (an em dash convention in captions is fine, this is on-screen
  only). No hyphens, en dashes, or em dashes (`-`, `–`, `—`) in any of these.
  Rewrite around them: a comma, a period splitting one sentence into two, or
  restructuring the clause all work — e.g. `You only get one shot at this —
  do you take it?` becomes `If you only get one shot at this, do you take
  it?`. Compound
  adjectives that would normally hyphenate (e.g. "far-in-the-future") should
  be reworded too, not just have the hyphen silently dropped (which would
  misspell the phrase) — same "rewrite around it" approach. Splitting into
  two plain words is the accepted fix for short compounds and numeric
  ranges specifically — "year-end" → "year end", "10-year" → "10 year", a
  numeric range like "7-10%" → "7% to 10%" (spelling out "to" rather than
  dropping the hyphen bare). Caught by test-rendering the frame before
  upload, not by reading the text alone — worth reviewing every question
  for hyphens, en dashes, and numeric ranges before the first render, not
  after.
- **On-screen text stays short — the question only, nothing else.** Full
  breakdowns/explanations belong in the caption, never on screen. "Keep it
  simple, this is a skim not a read" — enforced by the static overlay itself
  (see Workflow C) rather than by any length limit on the caption.
- **The on-screen question must be self-contained; the caption must only
  answer it.** Don't hold back a number/fact the viewer needs for the
  caption to reveal later — if answering the question requires a figure (a
  price, a rate, a starting balance), that figure belongs in the question,
  not introduced fresh in the caption. Write the caption as if the reader
  already fully understands the setup (they do — they just read it on
  screen) and jump straight to the reasoning/math. A warning sign when
  drafting: if a caption's first point reads like "step one: here's the
  scenario," a number in that sentence probably belongs on screen instead.
- **`technical_question` must fit 3 lines at its fixed 42px** — see
  `styles/ig_question_overlay.json`'s `_note` for why this is a wording
  problem, not a rendering one (auto-shrink is deliberately off). Test-render
  before treating a draft as final.
- **Caption structure**: numbered list (as many points as the topic actually
  has), each point a real worked explanation (not a bare restatement of the
  on-screen text), CTA as its own clearly separated final line.
  - **Numbers are keycap emoji, not plain digits**: `1️⃣` `2️⃣` `3️⃣` `4️⃣` `5️⃣`,
    not `1.` `2.` `3.`.
  - Favor shorter sentences and plainer word choices within each point —
    depth and simplicity aren't in tension, explain fully, just in plain,
    short sentences rather than dense ones ("write for a skim, not a read").
  - TikTok gets its own shorter, tighter pass, not just a length trim — more
    concise phrasing per point than the Instagram version, and always keep a
    full blank line between every numbered point.

  Example shape (Instagram):
  ```
  <1-2 sentence intro, simple sentences>

  1️⃣ <first point, real explanation, plain language>

  2️⃣ <second point, real explanation, plain language>

  3️⃣ <third point, real explanation, plain language>

  4️⃣ <fourth point, real explanation, plain language>

  <your own CTA line here>
  ```

**Define these before drafting anything**, and record them right here in this
section: which topics are in and out of bounds for your niche, a standing topic
list to check against so you don't repeat yourself, and the caption CTA wording
every post ends on.

## Setup checklist

Nothing here generates content until these are done:

- [ ] Postiz account connected; integration ID and handle filled into
      "Connected accounts" above and in `AGENTS.md`
- [ ] Source material added to `knowledge/` and inventoried in
      `knowledge/README.md`
- [ ] Background footage added to `clips/`, one entry per filename seeded in
      `clips/clips_usage.json`
- [ ] Photos added to `photos/rotation/`, one position entry each in
      `photos/rotation_positions.json`, at least one tagged `middle`
- [ ] Audience, perspective, and topic mix filled into
      `instagram/style_guide.md`, plus your own pairing bank
- [ ] Your own brand tag, watermark, and fixed on-screen CTA wording chosen
      (Workflow B step 4 for TikTok, Workflow C for Instagram)
- [ ] Topic scope, standing topic list, and caption CTA recorded in "Content
      format" above
- [ ] Swipe-file examples gathered and voice documented in
      `tiktok/style_guide.md` (and `linkedin/style_guide.md` if you use it)
- [ ] Posting cadence and slot times confirmed
