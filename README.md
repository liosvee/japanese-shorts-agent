# Japanese Shorts Agent — Claude Code

Research Japanese-language YouTube opportunities, explain the evidence in
English, let the user choose a niche, then develop and produce an original
Japanese Short with ElevenLabs and FFmpeg.

An independent companion to [liosvee/elevenlabs-claudecode](https://github.com/liosvee/elevenlabs-claudecode).
Claude Code is the research/creative agent. Python handles reproducible data
collection, validation, captioning and rendering. There is no separate autonomous
LLM server, web dashboard or automatic publishing.

## Workflow

1. **Research five niches:** Japanese names, English interpretations, demand
   evidence, revenue routes, competition and production effort. Rankings are
   editorial assessments, not proof of profit.
2. **User selects one:** the agent stops at this decision and saves the selection.
3. **Analyse keywords:** import sourced analytics, rank comparable Japanese
   YouTube estimates and choose a relevant high-demand keyword.
4. **Inspect Shorts:** collect public YouTube metadata, verify real Japanese
   Shorts, compare performance and inspect their content.
5. **Create an original concept:** Japanese script, English translation,
   fact checks, storyboard and packaging.
6. **Review cost and produce:** approved narration/new media, measured captions,
   vertical MP4 and QA. Publishing remains manual.

## What is implemented

| Component | Implementation and limits |
| --- | --- |
| Claude workflow | CLAUDE.md plus five stage prompts; live research requires Claude's available search/browser tools |
| Niche ranking | Source-required JSON, four explicit editorial assessments, persisted user choice |
| Keyword analytics | CSV import and ranking by comparable provider/platform/market/period; no built-in paid analytics API |
| YouTube research | Data API search + video metadata; bounded pagination, deduplication, dated snapshots |
| Shorts verification | Explicit observation notes; duration alone never confirms a Short |
| Original creative work | Claude drafts Japanese and English, fact checks and asset plans |
| Narration and media | Reused ElevenLabs REST client with review hashes, cost metadata and persistent job IDs |
| Japanese captions | Character-timed cue splitting with explicit font-file support |
| Assembly | FFmpeg 1080x1920 output, narration, stills/clips, optional music and burned captions |

**Not included:** a vidIQ API adapter, automatic competitor video/transcript
downloads, stock/Canva connectors, revenue predictions or channel publishing.
The instructions explain how to use an analytics tool already available to
Claude or import its export. Your ChatGPT connections are separate from local
Claude Code credentials. Reference playback needs an available permitted browser
or video tool, or user-supplied observations/transcripts.

## Setup

Requirements: Python 3.10+, Claude Code, FFmpeg/FFprobe with libass and libx264,
and a Japanese font such as Noto Sans CJK JP. Python has no runtime package
dependencies. Paid media also requires your own ElevenLabs API access and
available credits. YouTube discovery requires a Google project with YouTube
Data API v3 enabled and an appropriately restricted API key.

On Windows, open the extracted project folder in PowerShell. On macOS/Linux,
use a terminal; replace `python` with `python3` if needed.

```sh
python scripts/setup.py
python -m jp_shorts doctor
```

Setup accepts keys through hidden input and preserves existing settings. You may
instead copy `.env.example` to `.env` and edit it locally. Fill out
`MASTER_CONTEXT.md`. Do not paste secrets into chat or commit `.env`.

Open Claude Code in this folder:

```sh
claude
```

Then paste:

> Start Japanese Shorts research. Follow CLAUDE.md. Research five commercially
> promising Japanese-language niches, explain the evidence and uncertainty in
> English, and wait for me to choose one. After I choose, research Japanese
> YouTube keywords and successful Shorts, then prepare an original Japanese
> script with an English translation. Show the storyboard and complete media
> cost estimate before generating paid media. Do not publish.

Claude will use `projects/first-short` by default. No niche or live analytics
has already been researched by downloading this project.

## Commands

Run from the repository root. Replace PROJECT with your project directory.

```sh
python -m jp_shorts init projects/first-short
python -m jp_shorts niches projects/first-short
python -m jp_shorts select projects/first-short CHOSEN_NICHE_ID
python -m jp_shorts keywords projects/first-short projects/first-short/keywords.csv
python -m jp_shorts choose-keyword projects/first-short "日本語キーワード" --group 0
python -m jp_shorts discover projects/first-short --days 90 --pages 2
```

The first ranking command requires researched `niches.json`. The keyword command
requires a populated CSV; see [research/data contract](docs/research.md).
`--pages 2` means up to two pages for each of view-count and newest ordering;
metadata requests are additional. Requests consume the Google project's quota.
No quota rate or guaranteed result coverage is hard-coded.

After actually inspecting a candidate, record the evidence:

```sh
python -m jp_shorts verify PATH_TO_RESEARCH_JSON VIDEO_ID --evidence "Observed in Shorts player; Japanese speech; opening and structure noted in reference-analysis.md" --title-en "Accurate translated title"
python -m jp_shorts shortlist PATH_TO_RESEARCH_JSON
```

Verify records an observation; it cannot prove the person or agent watched the
video. Reference analysis and final quality still require real review.

## Production

See [production](docs/production.md) for cost review, narration, Japanese fonts,
asset generation, rendering and recovery. Example request files are templates;
replace IDs, prompts and cost fields before use. Narration character count is
not an assumed credit price.

```sh
python -m elmarketing voices --search "Japanese"
python -m jp_shorts speech-plan projects/first-short --voice ACTUAL_VOICE_ID
python -m elmarketing review projects/first-short/speech.plan.json
```

Cost initially remains unknown. Enter a current source-backed estimate and
obtain approval before submit. No paid generations are needed for setup or tests.

## Tests and limitations

```sh
python -m unittest discover -s tests -v
```

Tests include mocked provider requests, selection/data guards, Japanese cue
splitting and real local FFmpeg rendering. See [validation](docs/validation.md)
for the delivery-time results and untested live integrations. GitHub Actions
runs the suite on push and pull requests. Do not describe these tests as proof
of business results, Japanese fluency or successful paid API access.

## Upload to your own GitHub repository

Suggested repository name: **japanese-shorts-agent**.

Create an empty repository in GitHub, without an initial README. From this
project folder, after checking that private files are ignored:

```sh
git init -b main
git add .
git commit -m "Add Japanese Shorts research and production workspace"
git remote add origin https://github.com/YOUR_USERNAME/japanese-shorts-agent.git
git push -u origin main
```

Replace YOUR_USERNAME and the repository name as appropriate. If history already
exists, skip init/initial commit. Include hidden project files when transferring
the archive. Do not replace your existing ElevenLabs repository with this one.

See [sources](docs/sources.md), [workflow](docs/workflow.md) and [NOTICE](NOTICE.md).
