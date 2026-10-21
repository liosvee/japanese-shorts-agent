# Delivery validation — 21 October 2026

## Completed

- Python 3.12.14: 32 offline tests passed.
- Real FFmpeg/FFprobe renders produced H.264/AAC output at 1080x1920.
- A frame from an additional synthetic render was inspected: caption placement
  and sizing were visible and within the portrait frame.
- Japanese unspaced text split into bounded cues using supplied character timing.
- Japanese caption rendering rejected a missing explicit font file.
- Keyword tests preserved missing values, separated incompatible sources and
  rejected invalid values and the wrong target market.
- User niche selection and project reinitialisation guards were exercised.
- YouTube mocks verified pagination bounds, deduplication, duration filtering,
  absent statistics, and verified-only shortlists.
- ElevenLabs mocks exercised exact request payloads, changed-plan rejection,
  duplicate-job prevention, polling and unknown outcomes without paid retries.

## Not exercised live

- Claude Code execution: the Claude executable was not installed in this build environment.
- YouTube API authentication or live discovery: no local API key was configured.
- Keyword-provider integration: this release imports sourced CSV data; it has no
  built-in vidIQ/Google Ads traffic API adapter.
- Paid ElevenLabs generation, current voice availability, credits or billing.
- Actual Japanese font glyph rendering: no Japanese font was installed here.
  Configure a Japanese font and inspect a real export before production.
- Japanese narration pronunciation, translation quality or fluent editorial review.
- Live niche research, revenue outcomes, Shorts performance or publishing.

The saved synthetic media is only a technical check, not a produced Japanese
Short. No API credits were consumed by these tests. GitHub Actions is configured,
but has not run remotely because this project has not yet been uploaded.
