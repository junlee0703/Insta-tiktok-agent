# Agent Instructions — Instagram + TikTok Content Agent

Read and follow this file before doing work anywhere in this repository. These
instructions apply to the entire repository tree. Codex reads `AGENTS.md`
natively, and so does Claude Code.

**This is a reusable base for an AI video content pipeline.** The rendering
scripts, overlay styles, publishing workflows, and QA rules are all here and
working. None of the content is: no niche, no brand, no knowledge base, no
photos or clips, no connected accounts. That part is yours.

Fill in before generating anything:

1. **[brand.md](brand.md)** — your Postiz integration IDs, posting schedule,
   topic scope, fixed CTA copy, and the autopilot switch. Never post to an
   integration you did not configure. Run `python3 scripts/check_setup.py` to
   see what is still missing.
2. **Source material in `knowledge/`** — the only permitted source of substance
   for content, per Hard Rule 5.
3. **Background footage in `clips/`**, and for TikTok, photos in
   `photos/rotation/` with an entry each in `photos/rotation_positions.json`.
4. **Audience, perspective, and topic mix** in `instagram/style_guide.md`,
   including the identity facts the credibility-led titles draw on.
5. **Your topic-scope rules** — which topics are in and out of bounds for your
   niche, and the caption CTA wording you want on every post.

Automates social posts via the `postiz` CLI. Full detail lives in
[playbook.md](playbook.md) — read it before doing any content work in this
folder.

## First run: setting someone up

**Assume the user has never opened a terminal.** Many arrive here having just
installed Claude Code and nothing else. Meet them there.

**Run `python3 scripts/check_setup.py` at the start of any session** where the
user asks for content, asks for help, or says anything like "set me up" or
"get started". It reports every missing item at once.

If anything is missing, do not error out and do not paste the raw checklist at
them. Say what is missing in one plain sentence, offer to fix it, and then walk
through it one item at a time. **Ask about their channel, not about config
fields.** Not "paste your Instagram integration ID" but "let's connect your
Instagram, I'll start the login and you approve it in the browser." Not "fill
in the Audience section" but "who are you making these for, and who is the
person speaking in them?"

**Write every answer into the files yourself**, then show them what you wrote
and invite corrections. Never make them hand-edit a file unless they ask to.

Order that works:

1. **Dependencies.** Install whatever the checker reports missing: Pillow via
   `pip install -r scripts/requirements.txt`, then ffmpeg and jq through the
   system package manager. Explain each in one line. Do not make them research
   anything.
2. **Postiz.** Run `postiz auth:login` and tell them to approve it in the
   browser. Then run `postiz integrations:list` and write the Instagram ID and
   handle into `brand.md` yourself. If the list comes back empty, explain they
   need to connect an Instagram **business** account inside Postiz first, and
   that a personal account cannot be posted to through the API.
3. **Their channel.** Ask what it is about, who it is for, and who is speaking
   and why anyone should listen to them. Write it into "Audience and
   positioning" in `instagram/style_guide.md`. **Spend real time here.** Every
   later rule depends on it, and a vague answer produces vague content.
4. **Source material.** Explain Hard Rule 5 plainly: everything the videos say
   has to come from files they provide, and you will not invent facts to fill
   a gap. Ask them to put notes, documents, or PDFs into `knowledge/`.
5. **Footage.** They need background video in `clips/`, and photos in
   `photos/rotation/` only if they want TikTok. Describe what works: ordinary,
   candid, loosely on theme, not polished. Once the files exist, seed
   `clips/clips_usage.json` and `photos/rotation_positions.json` yourself.
6. **Fixed copy and schedule.** Ask for their caption CTA, on-screen brand tag,
   watermark, and posting times. Write them into `brand.md`.
7. **Re-run the checker** and show them a clean result.

Then offer to make **one** video, not three, and show them the copy before
anything is rendered.

**Never publish during setup.** A first run ends with the user seeing output,
never with a live post.

## Hard rules

1. **Never modify anything outside this project folder unless the user
   explicitly authorizes the specific outside target.** The only project path
   in scope is this repository's root and its descendants.
   While working from this project:
   - Do not create, edit, overwrite, move, rename, or delete code or project
     files anywhere outside that path.
   - Never modify a sibling repository, another agent folder, or any other
     workspace merely because it is related, discoverable, or useful as a
     reference.
   - Do not run commands, scripts, formatters, installers, or tools that may
     write to an outside project path. Resolve uncertain targets first; if an
     outside write may occur, stop and ask.
   - Reading an outside file for reference does not authorize changing it.
   - An exception requires an explicit instruction in the current conversation
     that identifies the outside folder or file to change. Inferred intent,
     convenience, urgency, or a broad request to "fix everything" is not
     authorization.
   - Temporary runtime files may be written to the system temporary directory,
     but never use another project or agent folder for temporary output.
2. **Publishing rules differ per platform:**
   - **Instagram**: posts are **real and public**. Never create a Postiz
     draft. The gate is the copy approval described under "Copy approval"
     below: show the user the on-screen text and caption in chat, wait for
     their go-ahead, then render, upload, and create with `-t schedule` as a
     real public post. A past or near-immediate scheduled time may publish as
     soon as Postiz processes it, so treat `-t schedule` as publishing now.
     Always verify the post leaves `QUEUE` and reaches `PUBLISHED`;
     investigate `ERROR` or a stuck queue.
   - **LinkedIn**: always create with `-t draft` in Postiz. LinkedIn has no
     private option — the moment a post is promoted to `schedule` it's
     live to everyone. Never use `-t schedule` for LinkedIn unless the user
     explicitly says to publish a specific post.
   - **TikTok**: default is `-t schedule` (Postiz) with
     `content_posting_method: "DIRECT_POST"` and
     `privacy_level: "PUBLIC_TO_EVERYONE"` in the settings (see
     `playbook.md`'s "Non-negotiable rules" for the full settings object) —
     this **publishes for real, live and public** the moment it's created.
     Only use `SELF_ONLY` if the user explicitly asks to go private for a
     specific video — still tell the user plainly before the API call goes
     out either way, per the transparency rule below.
     - **This is a real API call to TikTok**, so batch-upload spam-detection
       risk applies same as any real post — never create more than one of
       these at once, space them apart.
     - Never promote/create on your own initiative or from inferred urgency
       language like "now"/"rn" — always be explicit about what's about to
       happen before calling the API.
     - **`content_posting_method: "UPLOAD"` exists as a fallback for one
       specific case**: the user wants a real TikTok-native draft in their
       app inbox instead of a live post (e.g. to edit/attach a specific
       sound before it's a real post). If used: **expires in 24 hours** if
       the user doesn't finish it in the app — always tell them this.
       **TikTok discards every setting except title/caption in `UPLOAD`
       mode** — privacy_level, duet, stitch, comment, autoAddMusic, and the
       brand toggles are all silently ignored, tell the user they'll need
       to set those themselves in-app.
     - Confirm which video they mean before creating/promoting if there's
       any ambiguity, and never do more than one at a time.
3. **Media must be uploaded to Postiz first.** `postiz upload <file>` → use the
   returned `.path` in `-m`. Raw local paths are rejected by TikTok/LinkedIn.
4. Don't invent LinkedIn copy or TikTok scripts from scratch until style guides in
   `linkedin/style_guide.md` and `tiktok/style_guide.md` have real content — check
   them first. They ship empty, so if they still are, ask the user for
   example posts first.
5. **Use only this repository's `knowledge/` folder as the source of substance
   for video content.** This applies to Instagram Reels and any future video
   scripts, hooks, titles, overlays, captions, examples, advice, anecdotes,
   themes, and factual claims.
   - Do not add substance from general model knowledge, memory, web research,
     outside files, competitors, or plausible-sounding invention.
   - Every substantive idea in a video must be directly traceable to a file in
     `knowledge/`. Style guides may control voice, pacing, structure, and visual
     presentation only; they are not sources of claims or advice.
   - Rephrasing, shortening, organizing, and combining supported ideas is
     allowed, but do not introduce a new claim, example, detail, statistic,
     reason, consequence, or recommendation that the source does not contain.
   - Preserve first-person lived experience as personal perspective. Do not
     convert personal health, financial, career, parenting, or relationship
     advice into universal or professional claims.
   - If `knowledge/` does not support the requested content, stop and ask the
     user to add source material. Do not fill the gap from anywhere else unless
     the user explicitly authorizes a specific source and asks for it to be
     added to `knowledge/`.
6. **Every Instagram Reel needs a specific credibility-led title at the top.**
   The `brand_tag` must explicitly identify why the account owner has
   perspective on that Reel's topic, using only identity facts established in
   `instagram/style_guide.md`. Match the credential to the topic. Never use a
   generic title such as "career advice," "money lessons," or "things I
   learned" without the credibility marker. Do not invent employers, job
   titles, years of experience, certifications, or other credentials. Keep the
   title concise enough for at most two lines and verify it visually before
   upload.
   - No identity facts are established out of the box. Fill in the "Audience
     and positioning" section of `instagram/style_guide.md` first; if it is
     still blank, stop and ask the user rather than inventing a persona.

## Connected Postiz integrations

**Integration IDs live in [brand.md](brand.md), not here.** No integration is
configured out of the box. The user connects their own Instagram business
account in Postiz, runs `postiz integrations:list`, and pastes the returned ID
and profile into that file. Never post to an integration ID that is not in
`brand.md`. This project uses Instagram only; do not configure or post to
LinkedIn or TikTok unless the user explicitly changes the channel scope.

## Copy approval

**The one gate before publishing is the copy, shown in chat.** Posts themselves
are real and public; there are no Postiz drafts to review.

Before rendering anything, write out in the conversation, for each video:

- the on-screen `brand_tag` (the credibility-led title)
- the on-screen numbered statement
- the full caption, including the final CTA line
- the intended slot time

Then stop and wait. If the user changes wording, revise and show it again. Once
they approve, run the rest of the workflow straight through: render, QA the
frames, upload, create as a real public post, verify state, and log. Do not ask
for further confirmation on visuals, scheduling, or publishing. The copy
approval covers all of it.

**Autopilot** in [brand.md](brand.md) skips even this gate. **Read that value
before creating any post.** `off` (the default) means the copy approval above
is required. `on` means publish without showing copy first, and is only for
someone who has watched this produce output they would have posted themselves.

## Standing command: "make N vids"

**Before starting, run `python3 scripts/check_setup.py`.** If it reports
failures, do not attempt the workflow and do not produce a partial result. Say
what is missing in plain language and offer to set it up (see "First run"
above). An unconfigured repo cannot produce content, and failing halfway
through is worse than not starting.

When the user says **"make 3 vids"**, **"make 1 vid"**, or any count, and setup
is clean, execute the complete Instagram workflow for that many Reels. A first
run after setup should be one, not three.

1. Create N distinct Reels grounded exclusively in `knowledge/`.
2. Use the established Instagram style, clip rotation, highlight rotation,
   caption format, credibility-led `brand_tag`, and all visual QA rules.
3. Assign slots from the schedule configured in [brand.md](brand.md), taking
   the first N of them. If that section is still a placeholder, ask for their
   posting times rather than assuming any.
4. A request arriving before 6:00 AM in that timezone targets the current
   calendar date; at or after 6:00 AM it targets the next calendar date.
5. **Show every set of copy in chat and wait for approval** (see "Copy
   approval" above), unless autopilot is `on`. Revise if asked.
6. Once approved, render and inspect all N videos, upload them to Postiz,
   create them with `-t schedule` as real public posts, verify their states
   and timestamps, and log the results. Do not ask for topic, visual,
   scheduling, upload, or publishing confirmation at this stage; the copy
   approval authorized all of it.
7. Every Instagram Reel must include music. Use Postiz `audioSearch` (an empty
   query is fine for random/trending results), select a track at random, and
   pass the returned `audio.id` in `posts:create`. Vary tracks within a
   a batch when the result set allows it. Never call Meta's Graph API
   directly and never guess a track ID. There is no silent/no-music fallback:
   if Postiz authentication is expired, `audioSearch` is unavailable, or the
   search returns no usable track, do not create the scheduled post. Stop and
   report the blocker so the integration can be reauthenticated or refreshed.

## Version control

- **This is a working copy of a public template, so `origin` may not belong to
  the user.** Before any push, run `git remote -v`. If `origin` still points at
  the upstream repo (`junlee0703/Insta-tiktok-agent`), **do not push.** Their
  local commits are safe either way; pushing is what needs a remote of their
  own. If they want one, have them create an empty GitHub repository, then
  `git remote set-url origin <their repo>` and
  `git remote add upstream https://github.com/junlee0703/Insta-tiktok-agent.git`.
  Never push to a remote the user does not own.
- **Never pull or merge from the upstream template on your own initiative.**
  Upstream carries base updates that can overwrite the user's `brand.md`, style
  guides, and content. Pull from upstream only when the user explicitly asks for
  base updates, and show them what changed before merging.
- Commit the user's work locally as it is produced: `brand.md`, style guides,
  `knowledge/` additions, and the publishing log. Committing is always safe.
  Pushing is what needs the ownership check above.
- Never commit credentials, API keys, `.env` files, Python caches, or generated
  `output/` renders. Source clips, knowledge, styles, scripts, instructions, and
  the publishing log belong in the repository unless the user says otherwise.
- Do not force-push or rewrite history.

## Folder map

**Yours** (edit freely; base updates never touch these): `brand.md`,
`knowledge/`, `clips/`, `photos/rotation/`, and the style guides.
**Base** (leave alone so you can pull fixes): `scripts/`, `styles/`,
`playbook.md`, `AGENTS.md`.

- `brand.md` — every setting you fill in: autopilot switch, Postiz integration
  IDs, schedule, topic scope, and fixed copy. The one file to edit first.
- `playbook.md` — full workflow and command reference
- `linkedin/style_guide.md`, `linkedin/examples/` — trained style + raw swipe
  examples (empty, drop your own in)
- `tiktok/style_guide.md`, `tiktok/examples/` — trained style + raw swipe
  examples (empty, drop your own in)
- `photos/rotation/` — real candid photo backdrop library (your own
  life/work photos) — see `photos/README.md`. Backs TikTok's
  teaching/mistake/CTA slides. See `playbook.md` Workflow B. Empty out of
  the box. Two optional special roles (`fixed_slide_2`, `cta_only`) are
  configured in `photos/rotation_positions.json`, both off by default — see
  `photos/README.md`.
- `photos/rotation_positions.json` — authoritative photo→text-position
  manifest (each photo needs an assigned position — see `photos/README.md`).
  Empty out of the box.
- `photos/rotation_usage.json`, `scripts/pick_photos.py` — always pick
  photos via this script, never by hand. It picks least-used-first,
  tracking counts in the usage file — see `playbook.md` Workflow B step 2.
- `clips/`, `clips/clips_usage.json`, `scripts/pick_clip.py` — real b-roll
  video clips (your own footage) used as Instagram Reels backgrounds and
  TikTok's slide-1 still-frame source — least-used-first picker. Empty out
  of the box; `clips_usage.json` needs one entry per clip filename before
  the picker will run (see that file's `_note`). See `playbook.md`
  Workflow B/C.
- `styles/ig_question_overlay.json`, `styles/tiktok_question_overlay.json`,
  `scripts/build_ig_reel.py` — the on-screen text overlay: brand tag + a
  single on-screen question, stamped once and held for the whole clip. TikTok's version additionally has a `swipe_right` prompt and no
  `caption_below` layer. Both render with the bundled Montserrat faces in
  `fonts/`, so no system fonts are required. See `playbook.md` Workflow C.
- `scripts/generate_slides.py` — stamps variable text onto a photo with Pillow
  (auto-crops any photo to fill the 1080×1920 canvas first). Fully generic,
  keyed entirely off whatever boxes a style JSON defines — nothing in this
  script is hardcoded to any brand-specific text.
- `scripts/calibrate_grid.py` — overlays a coordinate grid on an image to help
  pick/verify text-box positions
- `scripts/check_post_health.py`, `scripts/post_health_cron.sh` — catch posts
  that failed to publish. TikTok in particular fails silently into
  `state: "ERROR"` at a meaningful rate, and Postiz neither retries nor
  notifies, so a dropped post is invisible unless something checks. The cron
  wrapper raises a desktop notification where one is available and always
  writes the log; see `playbook.md` "Catching failed posts". **Always confirm a
  post actually left `QUEUE` — `QUEUE` at creation time does not mean it
  went live.**
- `output/` — generated slideshow images/video, ready for `postiz upload`.
  Doesn't exist yet — created on first render.
- `drafts/log.md` — running log of what's been drafted/posted and its
  Postiz post ID. Empty, starting fresh.
- `knowledge/` — the exclusive source of substance for video content. See
  `knowledge/README.md` for the current source inventory and Hard Rule 5 for
  the sourcing boundary.
- `scripts/check_setup.py` — validates your configuration and reports exactly
  what is still missing. Run it first, and any time something fails.
