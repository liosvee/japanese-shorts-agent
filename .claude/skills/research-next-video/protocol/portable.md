# Use in another Claude Code repository

Copy the entire research-next-video skill directory into .claude/skills/, or install it once at ~/.claude/skills/research-next-video/. Optional project agents live in .claude/agents/ in the distribution repository. A general-purpose Claude Code subagent can carry each assignment in SKILL.md when the named agents are absent. The research and packet protocol runs on Python 3.10+ with its standard library. Live research needs vidIQ access and a configured Agent-Reach installation or attributable current exports of both.

## Use the existing learning system first

If the host has evolution/WORKFLOW.md, reuse its sample ranking, refresh, sync and apply/verify commands. Its config determines the destination and valid scope. Read its real filenames. The jp_shorts.agent_brief adapter is specific to the Japanese Shorts repository. In other repositories, translate the host's active topic decision, top-N results and run snapshot into the contract below. Bind both active-run pointer files when they exist. Never point another repository at the Japanese repository's knowledge destination.

## When there is no host learning system

1. Use a project directory ignored by Git. Verify with git check-ignore before capturing exports. Put raw responses, private briefs, the decisions and receipts in this directory. Use one unique run directory per new video, for example PROJECT/.video-research/runs/RUN/. Save a current-run pointer in PROJECT/.video-research/active.json and include it among the hashed inputs. Reuse that run on resume.
2. Save every candidate, query, public URL, observation date, provider, unit, scope, format verification and raw-file pointer. Keep a comparison for all candidates and Claude's reasoned selected or insufficient_evidence decision. Compare only like metrics. If the decision is a niche, scope future learning to it and make a separate topic decision before assigning a video.
3. Read the last tracked snapshot for the exact niche/language/market/format. Save a revised sanitized JSON snapshot at video-knowledge/SCOPE.json (a stable slug or hash) with a revision, scope, UTC review date, evidence coverage, active rules, hypotheses and retirements. Store generic observations, original applications, public video URLs, independent channel counts, counterevidence and expiry. Three independent channels with relevant observations qualify a rule for trial; expire after 30 days without renewed support. Retain the original dates for carried-over rules. For no new support, record the review and explicit gap and make no new rule. Copy the snapshot and a short writing/visual brief into the private run.
4. The coordinator synchronizes **only the reviewed scoped knowledge file** to the host's configured origin/branch. Check the tracked diff and exact destination; omit raw responses, frames, provider account data, user identifiers, keys and private paths. Use a path-limited commit and ordinary fast-forward push. Fetch the target head first. If the branch has unrelated unpublished commits or unrelated staged files, leave synchronization pending. Preserve unrelated work. If the remote moved, resolve the new revision before retrying; never force-push. Verify the path/content on the remote or report local/pending. No repo or write permission means that remote sync remains pending.
5. Use the private handoff contract below. On receiving the writer's script and editor's storyboard, make a private application receipt mapping each rule to the exact script passage or shot ID and actual file, or to a concrete exclusion. Hash both packets and the actual script, storyboard and production plans with the helper's hash command. Recompute/compare before rendering. Require production to read those exact files. Check rendered frames against the plan when rendering is in scope.

## Brief format

The host adapter emits this contract automatically in Japanese Shorts Agent. Elsewhere the coordinating Claude writes research-brief.json in the private run. Empty arrays and placeholder strings below illustrate shape only and must be replaced with verified evidence before an assignment.

~~~json
{
  "schema_version": 1,
  "run_id": "<unique run ID>",
  "valid_until": "<earliest applicable UTC evidence or rule expiry>",
  "scope": {"niche":"<niche>", "language":"<language>", "market":"<market>", "format":"short"},
  "decision": {
    "kind":"topic", "status":"selected", "title":"<selected topic>", "reason":"<choice and runner-up>",
    "unknowns":"<what would reverse the decision>", "max_age_days":14,
    "sources":[
      {"provider":"vidiq","url":"<actual report or video URL>","file":"<saved relative result>","collected_at":"<UTC date>"},
      {"provider":"agent-reach","url":"<actual result URL>","file":"<saved relative result>","collected_at":"<UTC date>"}
    ]
  },
  "cohort":{"metric":"vph","age_days":[0,7],"method":"<query, age band, verification, candidate count and exclusions>"},
  "learning":{"revision":1,"knowledge":"<private copy of scoped knowledge JSON>","brief":"<private writing and visual brief>"},
  "ranked_videos":[],
  "input_hashes":{}
}
~~~

Use viewCount, vph or outlierScore for the ranking metric. Sort eligible top-N descending by that one metric, breaking ties by video ID. Each ranked row contains the real 11-character YouTube id, channel_id, metric_value, duration_seconds, script and frames. An observed facet contains status = observed, method, observation, source = {"file":"project-relative path"}, and timestamps in seconds when known. Allowed script methods are transcript and video_analysis. For an untimed transcript cite a real passage position in the observation and leave timestamps empty. Allowed frame methods are video_analysis and frame_inspection; both require time anchors. For frame_inspection also include frame_files pointing to the images actually inspected. An unavailable facet contains status = unavailable and a concrete reason.

Populate input_hashes from `python PATH/TO/handoff.py hash PROJECT PATH1 PATH2 ...`. Include each cited source file, inspected frame, native or portable current-run pointer, immutable decision, cohort metadata, knowledge copy and writing/visual brief. Keep paths relative to PROJECT. Select a freshness limit appropriate to the research, normally 14 days for topic evidence and at most 90. Set valid_until within that limit and within any active rule's expiry. Follow [the handoff commands](packets.md). The helper validates structure, freshness and artifact identity. Claude still verifies semantic claims against the captured material.
