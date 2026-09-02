# Instagram + TikTok Content Agent

A content pipeline you run by talking to an AI coding agent. You bring a niche,
some notes, and your own footage. It writes the copy, renders the videos, and
publishes them.

**See what it makes:** [@dinoreach](https://instagram.com/dinoreach) on
Instagram. Every video on that account came out of this pipeline.

## Start here

Install [Claude Code](https://claude.com/claude-code), open it, and paste this:

```
Clone https://github.com/junlee0703/Insta-tiktok-agent.git, read its AGENTS.md, and walk me through setting it up.
```

That is the whole setup. It downloads the code, installs what is missing,
connects your account, and asks about your channel in plain language. It writes
every config file for you, and posts nothing while setting up.

Then say `make 1 vid`. You see the exact wording before anything goes live.

## You need Postiz

**Nothing publishes without it.** Postiz is how the agent reaches Instagram and
TikTok. There is no other path, unless you have your own Instagram/TikTok API
access (takes weeks/months to get).

### Sign up: [postiz.pro/dinoreach](https://postiz.pro/dinoreach)

Connect your Instagram inside Postiz before you start. It has to be a
**business** account, not personal, or the API cannot post to it. Switching is
free and takes a minute in the Instagram app settings.

You also need two things nobody can automate:

- **Your own footage** for `clips/`. Short background clips, ordinary phone
  video, loosely on theme. Unpolished is correct.
- **Something to say** for `knowledge/`. Notes, documents, or PDFs. The agent
  will not invent facts, so an empty folder means it stops and asks.

Setup takes fifteen minutes. Filming and writing what you know takes a weekend.
That is the honest split.

## What it does

- Renders 1080x1920 Reels and TikTok carousels with text overlays
- Writes captions grounded only in your `knowledge/` files
- Rotates clips, photos, and highlight colors so nothing repeats
- Uploads, schedules, attaches music, verifies the post actually went live
- Catches posts that fail silently, which happens more often than you expect

## How approval works

Say `make 3 vids`. It writes the on-screen text and captions for all three,
shows them to you, and waits. Change the wording as much as you like. Once you
approve, it renders and publishes all three publicly without asking again.

Set `autopilot: on` in `brand.md` to skip even that.

## Yours vs base

| Edit freely | Leave alone |
|---|---|
| `brand.md`, `knowledge/`, `clips/`, `photos/rotation/`, style guides | `scripts/`, `styles/`, `playbook.md`, `AGENTS.md` |

Keeping that line means `git pull` brings you fixes without touching your
content. To keep your own copy on GitHub, make an empty repo and run:

```bash
git remote set-url origin https://github.com/<you>/<your-repo>.git
git remote add upstream https://github.com/junlee0703/Insta-tiktok-agent.git
```

<details>
<summary>Setting up by hand instead</summary>

```bash
git clone https://github.com/junlee0703/Insta-tiktok-agent.git
cd Insta-tiktok-agent
pip install -r scripts/requirements.txt
postiz auth:login
python3 scripts/check_setup.py
```

`check_setup.py` lists everything still missing. Fill in `brand.md`, add source
material to `knowledge/`, add footage to `clips/`, and fill in the audience
section of `instagram/style_guide.md`. The full checklist is at the bottom of
`playbook.md`.

</details>

## Notes

Runs on macOS and Linux. Needs Python 3.9+, ffmpeg, and jq; setup installs them.

Provided as is, and issues may not be answered. If something breaks, run
`python3 scripts/check_setup.py` first.

MIT licensed. See [LICENSE](LICENSE).
