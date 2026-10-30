# State, review and resumption

Project files are intentionally outside Git by default:

| Stage | Files | Next action |
| --- | --- | --- |
| Initialised | state.json, blank scripts, niches.json | Create a candidate research plan |
| Collection | research/runs/ID/plan.json, evidence/*.json, collections/*.json | Collect vidIQ MCP and Agent-Reach results |
| Analysis | analysis.json, claude-brief.md | Claude compares candidates and cites evidence |
| Claude decision | decision.json, state.json.research_decision, optional next_topic | Continue to keyword/reference work, or record insufficient evidence |
| Manual shortlist (only if requested) | niches.ranked.json, source notes | User selection |
| Chosen | state.json.selected_niche | Keyword analytics |
| Keywords | keywords.csv, keywords.ranked.json, keyword.json | YouTube discovery |
| References | research/youtube-TIMESTAMP.json, reference-analysis.md | Original script |
| Script | script.ja.txt, script.en.txt, claims.json, storyboard.json, packaging.md | Review exact script and media budget |
| Generation | speech.plan.json; outputs/*/plan.json and job.json | Collect existing jobs |
| Assembly | render.json, final MP4, captions, .qa.json, qa.md | User review |

The research CLI persists niche choice. It is not a full database/workflow
engine. Claude uses the files and conversation to resume, and must not declare
later stages completed because state.json exists. Source files and current
script content are authoritative. If a script changes, regenerate its plan and
obtain approval covering the change. Do not reuse an earlier narration silently.

Selection cannot change to a different niche within the same project: create a
new project to avoid mixed evidence. Re-running init on an existing directory
fails instead of overwriting. API discovery creates a new timestamped snapshot;
verification annotates that snapshot. Preserve raw source exports separately.

Evidence quality is a reasoning responsibility. JSON validation can enforce
required fields and comparability labels, but cannot prove truth, originality,
fluent Japanese, legitimate rights or the authenticity of an approval.


Default research follows [the combined integration](research-integration.md).
Fresh research runs preserve earlier evidence and decisions. An existing niche
constrains next-topic research. A choice updates research state only; it never
authorizes paid production. Resume the active run and inspect raw responses
before repeating provider calls.
