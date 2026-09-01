# Your settings

**This is the only file you need to edit to make this agent yours.** Everything
else in the repo is the shared base: workflow steps in `playbook.md`, hard rules
in `AGENTS.md`, rendering in `scripts/` and `styles/`. Keeping your values here
means you can pull base fixes later without merge conflicts.

Your content lives in `knowledge/`, `clips/`, `photos/rotation/`, and the style
guides. Those are yours too.

---

## Autopilot

```
autopilot: off
```

**`off`** — the agent writes the on-screen text and captions and shows them to
you in the chat first. You approve or edit the wording. Once you approve, it
renders and publishes real public posts without asking again. Posts are always
public; the only thing you gate is the copy.

**`on`** — the agent skips the copy approval too and publishes on its own. Only
turn this on after you have watched it produce output you would have posted
yourself. It publishes to a real audience.

## Brand

| Field | Value |
|---|---|
| Brand name | `<Your Brand>` |
| Handle | `@<your-handle>` |

## Connected Postiz integrations

Run `postiz integrations:list` and paste your own IDs here. Never post to an
integration ID you did not put in this table yourself.

| Platform | Integration ID | Profile |
|---|---|---|
| Instagram | `<your-instagram-integration-id>` | `<your-handle>` |
| TikTok | Not used | Not used |
| LinkedIn | Not used | Not used |

## Posting schedule

| Field | Value |
|---|---|
| Timezone | `<e.g. America/Los_Angeles>` |
| Slots per day | `<e.g. 7:00 AM, 12:00 PM, 7:00 PM>` |

## Topic scope

**In bounds** — what this channel is allowed to cover:

- `<topic area>`
- `<topic area>`

**Out of bounds** — never make content about these, even if `knowledge/`
mentions them:

- `<topic area>`

**Standing topic list** — topics already covered, so you don't repeat yourself.
Add a line per published topic:

- `<date>` — `<topic>`

## Fixed copy

Written once, reused verbatim on every post. Changing these mid-run makes your
feed look inconsistent, so settle them early.

| Where | Your wording |
|---|---|
| Caption CTA (final line of every caption) | `<e.g. Follow @yourhandle for more>` |
| On-screen brand tag (top of every slide) | `<your short positioning line>` |
| Watermark (bottom right, TikTok slides 2+) | `<your handle or brand name>` |
| TikTok CTA slide text | `<your fixed closing call to action>` |
