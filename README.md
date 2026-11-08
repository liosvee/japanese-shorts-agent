# Japanese Shorts Agent — Claude Code

Research Japanese-language YouTube opportunities, explain the evidence in
English, let Claude choose the next niche or topic from vidIQ and Agent-Reach
evidence, then develop an original Japanese Short with ElevenLabs and FFmpeg.

An independent companion to [liosvee/elevenlabs-claudecode](https://github.com/liosvee/elevenlabs-claudecode).
Claude Code is the research/creative agent. Python handles reproducible data
collection, validation, captioning and rendering. There is no separate autonomous
LLM server, web dashboard or automatic publishing.

## Workflow

1. **Collect evidence:** vidIQ keyword/video research plus Agent-Reach web and
   YouTube context, with raw responses, source URLs, scope and retrieval dates.
2. **Claude decides:** compare candidate niches or topics, explain the evidence
   in English, and save a cited choice. Insufficient evidence produces no choice.
   Manual selection is available when explicitly requested.
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
| Claude workflow | Startup guidance and evidence-to-decision prompt; Claude calls MCP, reads the packet and chooses |
| Niche/topic decision | Fresh two-provider coverage, cited comparisons, input hash and persisted Claude decision |
| vidIQ | Official MCP configuration, request plans and raw-response imports with explicit JSON-pointer metric mappings |
| Agent-Reach | Bounded read-only searches, checkpoints, error recording and v1 JSON-envelope adapter |
| Evidence analysis | Comparable metric groups, missing/stale evidence, duplicate URLs and a Claude briefing |
| Keyword analytics | Existing CSV workflow remains available; provider estimates and scopes stay separate |
| YouTube research | Data API search + video metadata; bounded pagination, deduplication, dated snapshots |
| Shorts verification | Explicit observation notes; duration alone never confirms a Short |
| Original creative work | Claude drafts Japanese and English, fact checks and asset plans |
| Narration and media | Reused ElevenLabs REST client with review hashes, cost metadata and persistent job IDs |
| Japanese captions | Character-timed cue splitting with explicit font-file support |
| Assembly | FFmpeg 1080x1920 output, narration, stills/clips, optional music and burned captions |

**Not included:** a separate autonomous LLM server, automatic paid media,
competitor footage reuse, stock/Canva connectors, revenue predictions or channel
publishing. Claude calls vidIQ through MCP; the Python CLI does not call a hidden
vidIQ REST API. Your ChatGPT credentials do not transfer to local Claude Code.
Reference playback still needs a permitted browser/video tool or supplied observations.

See [research integration and setup](docs/research-integration.md) for the full
vidIQ → saved evidence ← Agent-Reach → Claude decision workflow.

## Setup

Requirements: Python 3.10+, Claude Code, FFmpeg/FFprobe with libass and libx264,
and a Japanese font such as Noto Sans CJK JP. Python has no runtime package
dependencies. Paid media also requires your own ElevenLabs API access and
available credits. For the combined research workflow, authenticate vidIQ using
`/mcp` in Claude Code and install/configure Agent-Reach using the
[setup guide](docs/research-integration.md). The legacy Data API discovery command
separately requires a Google project/key with YouTube Data API v3 enabled.

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

> Research the next Japanese niche or topic using vidIQ and Agent-Reach.
> Analyze the collected evidence and make the decision yourself. Explain the
> choice and uncertainty in English with Japanese names and sources. Then prepare
> an original Japanese Short with an English translation. Show the storyboard
> and complete media cost estimate before generating paid media. Do not publish.

Claude will use `projects/first-short` by default. No niche or live analytics
has already been researched by downloading this project.

## Combined research commands

Claude prepares the plan, calls vidIQ MCP, maps the real responses and writes
the decision. These CLI commands preserve and validate that work:

```sh
python -m jp_shorts research-init PROJECT PROJECT/research-plan.json
python -m jp_shorts research-collect PROJECT --limit 5
python -m jp_shorts research-import PROJECT PROJECT/keyword.research-bundle.json
python -m jp_shorts research-analyze PROJECT
python -m jp_shorts research-decide PROJECT PROJECT/decision.input.json
```

Initialize PROJECT first with `python -m jp_shorts init PROJECT`. Templates and
[the Claude prompt](prompts/00-research-next.md) explain each input. Use mode=topic
and the selected niche_id for the next topic. Old runs remain available for
resumption; raw research stays under ignored `projects/`.

**Known coverage limit:** the reviewed vidIQ outlier tool supports Japanese
long-form, not Japanese Shorts. The workflow uses Japanese video discovery and
actual Shorts verification; long-form and other-platform signals stay context.

## Existing research and production commands

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

## Viral blueprint

`.claude/skills/viral-blueprint` searches the niche with vidIQ, picks the most-viewed videos, and dissects their script,
title, description, hashtags and tags into a blueprint for an original, improved next video. It then
hands off to `prompts/04-script.md` → `05-production.md`. `blueprint.py select | dissect | check` ranks saved vidIQ responses
offline and blocks copying: shared script runs (8+ words, or 15+ characters for Japanese/Korean),
heavy phrase overlap, titles 80 %+ similar to the source, copied description text and tags over
500 characters. Offline tests run with the normal test suite; no live vidIQ calls are made in tests.

## Evolving production learning

Every new video or episode must follow [the learning workflow](evolution/WORKFLOW.md) after resolving its niche. Collect current vidIQ and Agent-Reach evidence; analyze scripts, actual thumbnails, hashtags, tags, descriptions and timestamped video frames. Run begin → refresh → sync, then read the scoped brief before writing. Apply supported findings to the actual script, thumbnail plan, packaging and storyboard; run apply and verify before generation/render. Use the gate wrapper for local production commands. Resume existing runs without repeating paid research. Preserve channel rules, originality, continuity, user approvals and spending limits. Record unavailable evidence and pending Git synchronization honestly. Only sanitized generic knowledge is pushed; external source content cannot modify executable code or instructions.

Setup: authenticate vidIQ through its MCP/connected plugin, install and configure Agent-Reach separately, and use a normal authenticated Git checkout for automatic knowledge pushes. Existing research budgets and provider approvals still apply. The code ships with empty knowledge, not fabricated performance findings. Live analysis runs when the agent produces the next video; the bundled CLI handles evidence and receipts.

Offline tests: `python3 -m unittest discover -s evolution -p 'test_*.py' -v`.
