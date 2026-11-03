---
name: research-next-video
description: Choose the next YouTube topic or niche using vidIQ and Agent-Reach. Learn from competitor scripts and actual video frames on each new production, update scoped repository knowledge, and hand evidence to the scriptwriter and video editor. Use for next-video research, production learning, or an evidence-to-production handoff.
---

# Research the next video

Act as the coordinating Claude session. Own the choice, the repository update and the handoffs. A research-only request ends with a decision and the findings. A request to prepare a video continues to original writing and storyboarding. Run on invocation. Resume an interrupted assignment from its files.

## Start or resume

1. Read the host repository's instructions, production workflow, channel brief and project state. Establish the project, language, market, audience, format, niche (if fixed), decision mode and research budget. Keep distinct channels and series separate. In a new project choose a niche if requested. Inside an established niche choose a topic. A niche alone is insufficient to commission a script.
2. Use a new private run for each new video. For a retry or status check, read its decision, saved queries, pending jobs and receipts first. Reuse previous requests within their audience, age window and authorization. Private raw evidence stays in an ignored project directory.
3. Use [the host workflow](protocol/host.md) in Japanese Shorts Agent. In another repository use its equivalent research and learning workflow, or [the portable protocol](protocol/portable.md). Resolve this skill's scripts relative to this SKILL.md. Read [the evidence rules](protocol/evidence.md) before collecting or delegating.

## Research and choose

4. Assign a foreground evidence researcher to collect from both providers under the stated scope. Give it the run directory, precise candidates, authorized actions and budget. The coordinator executes any connector call unavailable to that agent and passes back the saved results. Collect source records before evaluating them.
5. For each plausible finalist, examine its strongest comparable references before deciding when script or visual feasibility could change the choice. Paraphrase the opening and payoff and record observed visual anchors or the access gap. Compare normally three viable candidates. Cite the retrieved evidence for each, including disconfirming signals. Choose a single candidate on audience fit, measured demand, comparative performance, originality and production feasibility. Explain why the runner-up lost and what would reverse the choice. Keep source observations, estimates, editorial judgments and unknowns separate. When either provider lacks relevant fresh evidence for the choice, record insufficient_evidence and name the missing input. Preserve any partial script and frame findings within their verified niche; hold production. An unavailable provider is never a vote for another candidate.
6. Every fresh run attempts script and moving-image inspection of the leading videos in the declared sample. For niche discovery, sample the leading candidate niches before settling a close call, then update the selected niche's scoped evidence. Use the full ranked sample and list inaccessible finalists. Save findings about script, frames and, where exposed, actual thumbnail, hashtags, tags and description. Avoid fabricating unavailable facets. Refresh the repository's dated creative rules, hypotheses and retirements. Distinguish a local update from one verified on the remote.
7. If asked only for a niche, stop after its decision and learning update. For a full video, resolve a concrete, fresh topic before issuing a writing assignment. Give the user the selected topic, strongest alternative, timestamps or passage anchors, evidence gaps and sync status.

## Pass the work to production

Use the main Claude session to invoke roles in sequence. Prefer the host's assigned agents. This project provides `video-evidence-researcher`, `video-script-writer` and `video-storyboard-editor`. Pass each the explicit project, run, assignment, private artifact paths and finishing condition. Wait for its output, inspect the actual files and only then dispatch the next role. If custom agents are unavailable, use a general-purpose subagent with the same assignment. If no delegation tool exists, perform the roles sequentially in the current session and report that accurately.

| Receiver | Inputs | Acceptance |
| --- | --- | --- |
| Coordinator | Researcher's candidate matrix, ranked sample, source paths, gaps and credit status | Verify both providers, decide, version findings, produce research-brief.json |
| Scriptwriter | Writer packet, brief, applicable script rules and channel constraints | Original script with a truthful hook, fulfilled promise, examples and a relevant next-watch bridge. Map each applicable rule to a real passage or explain its exclusion |
| Storyboard editor | Editor packet, the exact resulting script and the visual evidence | Original shot list with script beats, proposed timings, captions, transitions, asset provenance and visual rule IDs. Label new creative choices separately |
| Coordinator or existing QA agent | Both packets, actual script, storyboard and production plans | Check script/shot alignment, native application receipt and freshness. Inspect rendered frames when rendering is in scope |

Create and check the packets with [the handoff commands](protocol/packets.md). Writer release requires observed script evidence. Editor release also requires timestamped moving-image evidence on at least one of those same ranked videos. If a role is blocked, return the verified work already completed and the precise missing artifact. A hash proves file identity. Report a handoff as received only after the agent returns its output.

Follow the host's normal script review, media budget and publishing policy. A research decision or a valid packet grants no spending permission. If later authorized, compare the channel's own result at a comparable publication age against the experiment's stated measure. Record a counterexample or retirement when warranted.
