"""Prepare private, evidence-bound assignments. Standard library only; no network."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local(project, name):
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, "Use a project-relative path.")
    target = (project / path).resolve()
    target.relative_to(project)
    return target


def sha(path):
    with path.open("rb") as source:
        h = hashlib.sha256()
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, packet):
    encoded = (json.dumps(packet, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    if path.is_file() and path.read_bytes() == encoded:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = NamedTemporaryFile(dir=path.parent, delete=False)
    tmp = Path(stream.name)
    try:
        with stream:
            stream.write(encoded)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def instant(value):
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(stamp.tzinfo is not None, "Evidence dates must include a time zone.")
    return stamp


def observed(row, facet, inputs):
    item = row[facet]
    if item["status"] == "unavailable":
        require(bool(item["reason"].strip()), "Explain the missing " + facet + " evidence.")
        return False
    methods = {"script": {"transcript", "video_analysis"}, "frames": {"video_analysis", "frame_inspection"}}
    require(item["status"] == "observed" and item["method"] in methods[facet], "Unsupported " + facet + " evidence.")
    require(item["source"]["file"] in inputs and item["observation"].strip(), "Unbound or empty " + facet + " observation.")
    times = item.get("timestamps", [])
    require(isinstance(times, list) and all(type(t) in (int, float) and 0 <= t <= row["duration_seconds"] for t in times),
            "Invalid timestamps for " + facet + ".")
    if item["method"] != "transcript":
        require(times, "Moving-image analysis needs observed timestamps.")
    if item["method"] == "frame_inspection":
        files = item.get("frame_files", [])
        require(files and all(f in inputs for f in files), "Bind the inspected frame files.")
    return True


def prepare(project, brief_path):
    brief = load(brief_path)
    rid = brief["run_id"]
    require(brief["schema_version"] == 1 and re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", rid), "Invalid brief version or run ID.")
    choice = brief["decision"]
    require(choice["status"] == "selected" and choice["kind"] == "topic", "A selected video topic is required.")
    require(all(choice[k].strip() for k in ("title", "reason", "unknowns")), "Complete the decision rationale and uncertainty.")
    now = datetime.now(timezone.utc)
    expires = instant(brief["valid_until"])
    require(expires > now, "The research brief expired. Refresh the research.")
    inputs = brief["input_hashes"]
    require(inputs and all(sha(local(project, name)) == expected for name, expected in inputs.items()),
            "An input changed. Rebuild the brief from current evidence.")
    require(all(brief["scope"][k].strip() for k in ("niche", "language", "market", "format")), "Incomplete audience scope.")
    require(brief["scope"]["format"] in {"short", "long"}, "Use a verified short or long format.")
    require(brief["learning"]["knowledge"] in inputs and brief["learning"]["brief"] in inputs, "Bind the learning snapshot and brief.")
    max_age = choice["max_age_days"]
    require(type(max_age) is int and 1 <= max_age <= 90, "Supply a research freshness window of 1 to 90 days.")
    providers = set()
    for source in choice["sources"]:
        url = urlsplit(source["url"])
        require(url.scheme == "https" and url.hostname and source["file"] in inputs, "Each decision citation needs a URL and a bound source.")
        collected = instant(source["collected_at"])
        require(collected <= now < collected + timedelta(days=max_age), "A cited source is stale or future-dated.")
        require(expires <= collected + timedelta(days=max_age), "The brief outlasts its cited evidence.")
        providers.add(source["provider"])
    require({"vidiq", "agent-reach"} <= providers, "Cite both vidIQ and Agent-Reach for the selected topic.")
    require(brief["cohort"]["metric"] in {"viewCount", "vph", "outlierScore"}, "Choose one ranking metric.")
    rows = brief["ranked_videos"]
    require(len({r["id"] for r in rows}) == len(rows), "Duplicate videos cannot count as independent examples.")
    spoken, paired = [], []
    for row in rows:
        require(re.fullmatch(r"[a-zA-Z0-9_-]{11}", row["id"]) and row["channel_id"], "Missing video or channel identity.")
        require(type(row["duration_seconds"]) in (float, int) and math.isfinite(row["duration_seconds"]) and row["duration_seconds"] > 0,
                "Invalid reference duration.")
        require(type(row["metric_value"]) in (float, int) and math.isfinite(row["metric_value"]) and row["metric_value"] >= 0,
                "Missing or invalid ranking value.")
        script = observed(row, "script", inputs)
        frames = observed(row, "frames", inputs)
        if script:
            spoken.append(row["id"])
            if frames:
                paired.append(row["id"])
    require(spoken, "No observed script from the ranked videos. Hold the writing assignment.")
    require(rows == sorted(rows, key=lambda row: (-row["metric_value"], row["id"])), "Rank by the declared metric, breaking ties by video ID.")
    folder = local(project, "agent-handoffs/" + rid)
    require(folder == project / "agent-handoffs" / rid, "Use a real project handoff directory.")
    packet = {"schema_version": 1, "role": "writer", "run_id": rid, "topic": choice["title"], "scope": brief["scope"],
              "brief": brief_path.relative_to(project).as_posix(), "brief_sha256": sha(brief_path),
              "script_examples": spoken, "deliverable": "original script and rule-to-passage mapping"}
    return folder, packet, paired, inputs


def process(role, project, brief_name, script=None):
    project = Path(project).resolve()
    path = local(project, brief_name)
    folder, writer, paired, inputs = prepare(project, path)
    writer_path, editor_path = folder / "writer.json", folder / "editor.json"
    require(not any(p.is_symlink() for p in (writer_path, editor_path)), "Packet files must be regular project files.")
    if role == "writer":
        save(writer_path, writer)
        return writer_path
    require(writer_path.is_file() and load(writer_path) == writer, "Writer packet missing or stale. Reissue it before dispatch.")
    require(paired, "No ranked video has both script and timestamped frame evidence. Hold the editor assignment.")
    if role == "verify":
        require(editor_path.is_file(), "Editor packet missing.")
        script = load(editor_path)["script"]
    require(script, "Supply the project-relative final script.")
    script_path = local(project, script)
    reserved = {local(project, name) for name in inputs} | {path, writer_path, editor_path}
    relative = script_path.relative_to(project)
    require(script_path not in reserved and not {".evolution", ".video-research", "research", "agent-handoffs"}.intersection(relative.parts),
            "The editor requires an original production script.")
    require(script_path.read_text(encoding="utf-8-sig").strip(), "The production script is empty.")
    script_hash = sha(script_path)
    require(script_hash not in inputs.values(), "A copied source file cannot be the production script.")
    editor = {"schema_version": 1, "role": "editor", "run_id": writer["run_id"], "topic": writer["topic"],
              "writer_packet": writer_path.relative_to(project).as_posix(), "writer_sha256": sha(writer_path),
              "brief": writer["brief"], "brief_sha256": writer["brief_sha256"], "script": relative.as_posix(),
              "script_sha256": script_hash, "paired_examples": paired,
              "deliverable": "original shot list mapped to the exact script and visual evidence"}
    if role == "verify":
        require(load(editor_path) == editor, "Stale editor packet. Reissue it for the revised script and recheck the storyboard.")
    else:
        save(editor_path, editor)
    return editor_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("writer", "editor", "verify", "hash"):
        cmd = sub.add_parser(action)
        cmd.add_argument("project", type=Path)
        if action == "hash":
            cmd.add_argument("paths", nargs="+")
        else:
            cmd.add_argument("brief", help="Project-relative research-brief.json")
        if action == "editor":
            cmd.add_argument("--script", required=True)
    args = parser.parse_args(argv)
    try:
        project = args.project.resolve()
        if args.action == "hash":
            output = {p: sha(local(project, p)) for p in args.paths}
        else:
            packet = process(args.action, project, args.brief, getattr(args, "script", None))
            output = {"status": "verified" if args.action == "verify" else "prepared", "packet": packet.relative_to(project).as_posix()}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
