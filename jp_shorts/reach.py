"""Read-only adapter for Agent-Reach's reviewed v1 JSON result envelope."""
import json
import math
import shutil
import subprocess

from elmarketing.jobs import digest, write_json
from .core import now, read
from .intelligence import CHANNELS, current_run, import_bundle, source_url

UPSTREAM_COMMIT = "14c213405669414492bda0f8d52cc6531d062c45"
METRICS = {"view_count": ("views", "count"), "like_count": ("likes", "count"),
           "comment_count": ("comments", "count"), "duration": ("duration", "seconds")}


def search_command(channel, query, limit=5, timeout=30):
    if channel not in CHANNELS:
        raise ValueError("Unsupported Agent-Reach channel.")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("Use a result limit from 1 to 20.")
    if type(timeout) is not int or not 1 <= timeout <= 45:
        raise ValueError("Use a timeout from 1 to 45 seconds.")
    # Options end before the query. Search text cannot inject flags or shell code.
    return ["agent-reach", channel, "search", "--limit", str(limit),
            "--timeout", str(timeout), "--", query]


def bundle_from_result(candidate, channel, request, response, collected_at):
    if (not isinstance(response, dict) or type(response.get("schema_version")) is not int
            or response.get("schema_version") != 1):
        raise ValueError("Unsupported Agent-Reach JSON schema; use the documented 1.6 CLI.")
    if response.get("channel") != channel or response.get("action") != "search":
        raise ValueError("Agent-Reach returned an unexpected channel or action.")
    if type(response.get("ok")) is not bool:
        raise ValueError("Agent-Reach response lacks a boolean ok field.")
    bundle = {"provider": "agent-reach", "tool": channel + ".search",
              "candidate_id": candidate["id"], "collected_at": collected_at,
              "request": request, "response": response, "records": [],
              "adapter_reference_commit": UPSTREAM_COMMIT}
    if not response["ok"]:
        error = response.get("error")
        if not isinstance(error, dict):
            raise ValueError("Agent-Reach failure response lacks an error object.")
        bundle.update(status="error", error_code=str(error.get("code") or "UPSTREAM_ERROR"))
        return bundle
    items = response.get("items")
    if not isinstance(items, list):
        raise ValueError("Agent-Reach success response lacks an items array.")
    dropped = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            dropped += 1
            continue
        try:
            url = source_url(item.get("url"))
        except ValueError:
            dropped += 1
            continue
        title = item.get("title")
        record = {"title": title if isinstance(title, str) and title.strip() else url, "source_url": url,
                  "pointer": f"/items/{index}", "text": item.get("text"),
                  "scope": {"platform": "YouTube" if channel == "youtube" else channel,
                            "market": "unknown", "language": "unknown", "period": "snapshot",
                            "format": "unknown"},
                  "scope_basis_en": "Japanese query is a search hint only. Market, language and Shorts format are not verified.",
                  "metrics": []}
        raw = item.get("raw")
        if channel == "youtube" and isinstance(raw, dict):
            for key, (name, unit) in METRICS.items():
                value = raw.get(key)
                if key in raw and (value is None or (type(value) in (int, float) and math.isfinite(value) and value >= 0)):
                    record["metrics"].append({"name": name, "value": value, "unit": unit,
                                              "kind": "observed", "pointer": f"/items/{index}/raw/{key}"})
        bundle["records"].append(record)
    bundle["dropped_items_without_usable_public_url"] = dropped
    bundle["status"] = "ok" if bundle["records"] else "empty"
    return bundle


def collect(project, channels=("youtube", "web"), limit=5, retry_failed=False):
    folder, plan = current_run(project)
    if (folder / "decision.json").exists():
        raise ValueError("This run is decided; start a new research run.")
    if not channels or len(channels) != len(set(channels)):
        raise ValueError("Choose at least one channel, without duplicates.")
    for channel in channels:
        search_command(channel, "validation", limit)
    executable = shutil.which("agent-reach")
    results = []
    for candidate in plan["candidates"]:
        for channel in channels:
            request = {"channel": channel, "action": "search", "query": candidate["query_ja"], "limit": limit}
            job = folder / "collections" / (digest({"candidate": candidate["id"], **request})[:24] + ".json")
            previous = read(job) if job.exists() else None
            if previous and (previous["status"] in {"ok", "empty"} or not retry_failed):
                results.append({"candidate_id": candidate["id"], "channel": channel, "cached": True, **previous})
                continue
            write_json(job, {"status": "running", "started_at": now()})
            instant = now()
            failure = None
            try:
                if executable is None:
                    failure = "NEED_SETUP"
                else:
                    command = search_command(channel, candidate["query_ja"], limit)
                    command[0] = executable
                    process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                             errors="replace", timeout=45, shell=False)
                    if len(process.stdout.encode("utf-8")) > 5_000_000:
                        failure = "OUTPUT_TOO_LARGE"
                    else:
                        response = json.loads(process.stdout)
                        bundle = bundle_from_result(candidate, channel, request, response, instant)
                        if process.returncode != 0 and bundle["status"] in {"ok", "empty"}:
                            failure = "EXIT_STATUS_MISMATCH"
            except subprocess.TimeoutExpired:
                failure = "TIMEOUT"
            except (OSError, ValueError, TypeError):
                failure = "UNSUPPORTED_OR_INVALID_RESPONSE"
            if failure:
                # Do not save stderr, login material, or unstructured diagnostic output.
                bundle = {"provider": "agent-reach", "tool": channel + ".search", "candidate_id": candidate["id"],
                          "collected_at": instant, "request": request, "response": {}, "records": [],
                          "status": "unavailable" if failure == "NEED_SETUP" else "error", "error_code": failure}
            saved = import_bundle(project, bundle)
            write_json(job, saved)
            results.append({"candidate_id": candidate["id"], "channel": channel, "cached": False, **saved})
    return {"collections": results, "note": "Read-only searches. Failed/blocked calls are recorded; no automatic retry, installation, login or paid transcription."}
