"""Export the current Claude topic decision and reviewed production learning to a private agent brief."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

from evolution.learn import Learning, date, digest, file_hash, local, read, require, write
from .intelligence import analyze, current_run


def export_brief(project, engine=None):
    project = Path(project).resolve()
    research, plan = current_run(project)
    decision = read(research / "decision.json")
    require(decision["status"] == "selected", "Insufficient evidence. No production assignment.")
    require(plan["mode"] == "topic", "Niche selected. Choose a specific topic before assigning a video.")
    analysis = analyze(project)
    state = read(project / "state.json")
    key = decision["selected_candidate_id"]
    require(decision["decided_by"] == "claude" and state["next_topic"]["id"] == key and
            state["research_decision"]["run_id"] == research.name and
            state["research_decision"]["input_sha256"] == decision["input_sha256"] == analysis["input_sha256"],
            "The active topic, evidence and saved Claude decision must agree.")
    chosen = next(c for c in analysis["candidates"] if c["id"] == key)
    require(chosen["ready_for_decision"], "The selected topic no longer has fresh two-provider evidence.")
    cites = next(c["evidence_ids"] for c in decision["comparisons"] if c["candidate_id"] == key)
    cited = [e for e in analysis["evidence"] if e["evidence_id"] in cites and e["candidate_id"] == key and not e["stale"]]
    require({e["provider"] for e in cited} == {"vidiq", "agent-reach"}, "Refresh the selected topic's two-provider citations.")
    require(any(e["provider"] == "vidiq" and all(e["scope"][k] == v for k, v in
                {"platform": "YouTube", "market": "JP", "language": "ja"}.items()) for e in cited),
            "The decision needs a current Japan-scoped YouTube citation.")
    _, folder, run = (engine or Learning()).current(project)
    require(run["phase"] in {"refreshed", "applied"}, "Refresh the active learning run before creating the brief.")
    niche = state["selected_niche"]
    require(niche["id"] == plan["niche_id"] and run["scope"]["niche"] in {niche["id"], niche["name_ja"], niche["name_en"]},
            "The learning niche and selected project niche differ.")
    started = datetime.strptime(research.name.split("-")[0], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    require(date(run["started_at"]) >= started, "Start a new learning run for this topic research run.")
    target = folder / "research-brief.json"
    if target.exists():
        require(read(target)["topic_run_id"] == research.name, "One learning run cannot be reassigned to a different topic run.")
    knowledge = read(folder / "knowledge.json")
    evidence = read(folder / "evidence.json")
    require(digest(knowledge) == run["knowledge_hash"] and digest(evidence) == run["evidence_hash"],
            "The reviewed learning evidence or knowledge changed.")
    hashes = read(folder / "sources.json")
    for name, expected in hashes.items():
        require(file_hash(local(project, name)) == expected, "Learning source changed: " + name)

    def bind(path):
        name = path.relative_to(project).as_posix()
        hashes[name] = file_hash(local(project, name))
        return name

    for path in (project / "research/active.json", project / ".evolution/active.json", research / "plan.json",
                 research / "decision.json", folder / "evidence.json"):
        bind(path)
    for path in sorted((research / "evidence").glob("*.json")):
        bind(path)
    sources = [{"provider": e["provider"], "url": e["source_url"], "collected_at": e["collected_at"],
                "file": bind(research / e["raw_file"]), "evidence_id": e["evidence_id"]} for e in cited]
    expires = [date(e["collected_at"]) + timedelta(days=plan["max_age_days"]) for e in cited]
    expires.append(date(knowledge["updated_at"]) + timedelta(days=30))
    expires.extend(date(rule["expires_at"]) for rule in knowledge["rules"])
    require(min(expires) > datetime.now(timezone.utc), "Refresh expired production learning.")
    by_id = {v["id"]: v for v in evidence["videos"]}
    ranked = []
    for video_id in run["selected_ids"]:
        v = by_id[video_id]
        ranked.append({k: v[k] for k in ("id", "channel_id", "metric_value", "duration_seconds")} |
                      {"script": v["facets"]["script"], "frames": v["facets"]["frames"]})
    brief = {
        "schema_version": 1, "run_id": run["run_id"], "topic_run_id": research.name,
        "valid_until": min(expires).isoformat(), "scope": run["scope"],
        "decision": {"kind": "topic", "status": "selected", "title": chosen["name_en"], "title_ja": chosen["name_ja"],
                     "reason": decision["rationale_en"], "unknowns": decision["unknowns_en"],
                     "max_age_days": plan["max_age_days"], "sources": sources,
                     "comparisons": decision["comparisons"]},
        "cohort": evidence["discovery"], "ranked_videos": ranked,
        "learning": {"revision": knowledge["revision"], "knowledge": bind(folder / "knowledge.json"),
                     "brief": bind(folder / "brief.md")}, "input_hashes": hashes,
    }
    write(target, brief)
    return target.relative_to(project).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    try:
        print(export_brief(parser.parse_args().project))
    except (OSError, ValueError, KeyError, StopIteration, TypeError) as exc:
        print(f"Cannot release the research brief: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
