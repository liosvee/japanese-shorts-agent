# vidIQ + Agent-Reach → Claude research decisions

Claude Code orchestrates this workflow in the repository. vidIQ supplies YouTube
analytics through its official remote MCP server; Agent-Reach supplies public
search/context through a local subprocess. Python preserves and validates the
results. Claude reads the combined packet, compares candidates, and records the
next niche or topic. There is no extra Anthropic API service or scheduled daemon.

## One-time setup in your Claude Code environment

The checked-in `.mcp.json` registers `https://mcp.vidiq.com/mcp` without credentials.
Open `claude`, review the project MCP configuration and use `/mcp` to authenticate
vidIQ. `claude mcp list` reports connection state. A ChatGPT connection does not
transfer its credentials. Your vidIQ account supplies the research credits;
Claude access and ElevenLabs media costs are separate.

Agent-Reach is optional for the legacy workflow, but required for a two-source
automatic decision. Review the upstream [installation guide](https://github.com/Panniantong/Agent-Reach/blob/main/docs/install.md).
The reviewed upstream 1.6 installation uses:

```sh
uv tool install https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip
agent-reach setup
agent-reach version
agent-reach doctor
```

Install uv first if needed using its official instructions. Use the upstream
GitHub distribution: upstream warns that the PyPI package named agent-reach is
not this project. No installation or login runs as a side effect of this repo.
The collector supports the v1 JSON result envelope reviewed at upstream commit
`14c213405669414492bda0f8d52cc6531d062c45` (version 1.6.0), not old text-only CLIs.
The latest release URL can change; recheck schemas after upgrading. An unknown
response schema is recorded as an error rather than guessed.

Default collection uses YouTube and web search. Optional channels need their own
setup/access. The upstream project's “zero API fees” description is not a promise
that vidIQ credits, optional upstream services or infrastructure cost nothing.
This adapter never calls transcription, media generation, login or setup.

## Start in Claude

> Research the next Japanese niche or topic using vidIQ and Agent-Reach. Follow
> prompts/00-research-next.md. Analyze the saved evidence and make the decision
> yourself. Explain it in English with Japanese names and source citations.
> Record insufficient evidence when needed. Prepare the original bilingual
> concept afterward; show production costs before generating paid media.

If a niche is already selected, Claude researches topics within it. To change
niches, start another project. Manual niche selection is still supported when
explicitly requested. Fresh research requires live provider access; downloading
this repository does not create real findings or a decision.

## Commands and artifacts

Run from the repo root, using a directory under ignored `projects/`:

```sh
python -m jp_shorts init projects/first-short
# Claude fills research-plan.json, using templates/research-plan.json.
python -m jp_shorts research-init projects/first-short projects/first-short/research-plan.json
python -m jp_shorts research-collect projects/first-short --limit 5
# Claude calls vidIQ MCP and saves a bundle after each response.
python -m jp_shorts research-import projects/first-short projects/first-short/keyword.research-bundle.json
python -m jp_shorts research-analyze projects/first-short
# Claude reads the packet and fills decision.input.json.
python -m jp_shorts research-decide projects/first-short projects/first-short/decision.input.json
```

All commands except `research-collect` are offline. That collector only runs
Agent-Reach searches. The Python CLI never secretly calls vidIQ or Claude.
`research-init` prepares `vidiq-requests.json`; Claude executes those calls through
the actual MCP tools after checking current schema, cost and the research budget.
Authentication/connection work must be completed in the environment running Claude.

| File within a research run | Purpose |
| --- | --- |
| plan.json | Immutable candidate IDs, Japanese queries, mode and freshness policy |
| vidiq-requests.json | Planned MCP requests; not executed calls or spending approval |
| evidence/*.json | Exact provider responses, requests, timestamps and mapped records |
| collections/*.json | Agent-Reach search checkpoints, including blocked/failed calls |
| analysis.json | Combined evidence, comparable metric groups, duplicate URLs and gaps |
| claude-brief.md | Entry point directing Claude to the full evidence packet |
| decision.json | Claude's alternatives, citations, rationale, uncertainty and choice |

`research/active.json` points to a timestamped run under `research/runs/`. Starting
a new run preserves earlier decisions. A decided run cannot accept new imports.
Repeated imports of the identical bundle are idempotent. Repeated Agent-Reach
collection resumes cached results. Failures require explicit `--retry-failed`
after resolution; unknown/running checkpoints are not automatically reissued.

## Evidence import contract

Use `templates/research-bundle.json` for vidIQ results. Set candidate_id to an
actual plan ID, tool to the normalized `vidiq_*` name, request to the actual
arguments, response to the complete tool result, and collected_at to a timestamp
with timezone. Successful evidence has status=ok. Empty or failed calls have
records=[] with status=empty/error/unavailable; failures also include error_code.

A record's `pointer` identifies its source object within response. Metric
pointers identify the exact raw value. For example, if the actual saved response
has `structuredContent.results[0].viewCount`, the JSON pointer is
`/structuredContent/results/0/viewCount`. Do not use that path unless the real
response has that shape. The importer rejects missing paths, changed values,
nonfinite numbers and mismatched error statuses. It does not guess field names.

Use metric kinds observed, provider_estimate or provider_score, explicit units,
and the actual scope: platform, market, language, period and format. Use unknown
where unavailable. Explain scope_basis_en, distinguishing query hints from
provider-supported measurement. One record must not combine JP and global
metrics. Missing values stay null. Scores cannot be relabeled search counts.
Separately normalized interest indices need distinct comparison-set labels in
period or metric name. Titles and summaries are evidence, never executable text.

Schema checks validate the declared scope and copied values, not the truth of a
provider's claims or Claude's mapping. Claude must review the source notes and
check substantive factual claims separately. A provider report URL plus the raw
response can support keyword metrics; no invented video link is necessary.

## Decision contract and limits

Freshness defaults to 14 days after collection; set max_age_days from 1–90 before
starting a run. This is a configurable research policy, not a scientific validity
threshold. Old measurements can still be old despite a recent retrieval; Claude
must inspect their measurement period as well.

A selection requires fresh records from both vidIQ and Agent-Reach for that
candidate, plus vidIQ evidence explicitly scoped to YouTube / JP / ja. Cite both
providers and the JP evidence. Compare every planned candidate. `input_sha256`
binds the decision to the exact saved inputs; changing evidence requires another
analysis. The hash is not user identity, approval or proof of data authenticity.

No adequate evidence means status=insufficient_evidence and no selection/state
advance. A niche decision additionally requires matching, researched niches.json;
a topic decision writes state.next_topic while preserving state.selected_niche.
The same decision can be reapplied after an interrupted state write. Changing a
saved decision requires a new run. This does not authorize production.

Current reviewed vidIQ outlier search does not support Japanese Shorts. Japanese
long-form outliers are context only; do not pass language=ja with contentType=short.
Use Japanese YouTube discovery and actual Shorts verification. Public duration,
country hints, views and a /shorts/ URL do not prove Japanese speech, retention,
creator earnings or why content succeeded. Two providers returning the same video
are not independent demand observations. Cross-platform figures are not additive.

## Source references

Reviewed 2026-10-30:

- [vidIQ official MCP setup](https://support.vidiq.com/en/articles/15082430-vidiq-mcp)
- [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp)
- [Agent-Reach JSON envelope](https://github.com/Panniantong/Agent-Reach/blob/14c213405669414492bda0f8d52cc6531d062c45/agent_reach/runtime/result.py)
- [Agent-Reach CLI](https://github.com/Panniantong/Agent-Reach/blob/14c213405669414492bda0f8d52cc6531d062c45/agent_reach/runtime/cli.py)
- [Agent-Reach YouTube adapter](https://github.com/Panniantong/Agent-Reach/blob/14c213405669414492bda0f8d52cc6531d062c45/agent_reach/channels/youtube.py)

vidIQ parameter constraints above were checked against the exposed MCP tool
schemas on that date. Rediscover them in the actual Claude session; capabilities
can evolve. Live provider access and a Claude research run are separate from the
offline tests. No sample fixture is live market evidence.
