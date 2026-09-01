# Instagram Reel Style Guide

## Audience and positioning

*(Fill this in before generating any Reel. Every rule below depends on it, and
the agent is instructed to stop and ask rather than invent a persona.)*

- Audience: `<who you are talking to — age range, gender, situation>`
- Channel focus: `<the one thing this channel is about>`
- Source perspective: `<who is speaking and why they have standing on this
  topic>`. These are the established identity facts every credibility-led
  title draws on, so keep them factual — they become on-screen claims.
- All substantive advice must remain grounded in `knowledge/` and framed as
  personal experience, not universal professional advice.
- Topic mix: `<which pillars get more weight, and how a normal three-Reel day
  should be balanced across them>`. Keep enough topic variety to compare
  performance rather than switching every post to the same pillar.

## Reel format

1. Play a background video from `clips/` as the full-screen background.
2. Render the first line of a pairing in the existing `brand_tag` box, using
   its current position and style. This title must include the account owner's
   specific, topic-relevant credibility; generic category labels are not
   allowed.
3. Render the second line in the existing `technical_question` box, using its
   current position and style. Despite the legacy box name, this line is a
   numbered statement, not a question.
4. Put the actual advice in the caption. The on-screen statement only previews
   what the caption contains.
5. Keep the numbered statement concise enough to fit within three lines at the
   fixed 42px size. Do not shrink the font to force a fit.
6. Do not use hyphens, en dashes, or em dashes in on-screen text.

## Standing overlay layout

- Use Montserrat Bold for both the positioning title and numbered topic.
- Keep the positioning title at the top of the Reel.
- Make every positioning title credibility-led. It must explicitly identify the
  account owner using one of the established identity facts from "Audience and
  positioning" above, chosen to fit the topic.
- Never use a generic standalone title such as "career advice," "money
  lessons," or "things I learned." Do not invent an employer, job title,
  certification, exact tenure, or other credential.
- Keep the positioning title to at most two lines. Test-render it at the fixed
  46px size and shorten the wording if it exceeds two lines; do not shrink the
  font.
- Place the numbered topic in the lower section at `y=1080`, below the
  speaker's face and directly above the caption prompt.
- Place the caption prompt at `y=1450` in 50px Montserrat Bold.
- Give the title, numbered topic, and caption prompt the exact same per-post
  highlight color.
- Test-render every Reel and confirm the three text layers neither overlap each
  other nor cover the speaker's face before uploading.

Build with:

```bash
python3 scripts/build_ig_reel.py \
  --clip <background-video-filename> \
  --brand-tag "<first line>" \
  --question "<second line>" \
  --out output/<name>/<name>.mp4
```

`--question` is retained as the command-line option for compatibility, but it
now receives the numbered statement.

## Approved pairing bank

Empty out of the box. Build your own bank before generating Reels, then add to
it as topics prove out.

Each entry is two lines:

```
N. **<credibility-led positioning title: who is speaking and why they have
   standing on this topic>**
   - <numbered statement previewing what the caption delivers>
```

Rules for entries:

- The first line must carry a real credibility marker drawn from "Audience and
  positioning," never a bare category label.
- The second line should promise a specific, countable payoff, e.g. "5 things I
  wish I knew before ...".
- Every entry must be supportable from `knowledge/`. If nothing in `knowledge/`
  backs it, it does not belong in the bank.
