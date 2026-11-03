"""Offline handoff and native production gate regression tests; all references are synthetic."""
from datetime import timedelta
import importlib.util
from pathlib import Path
import tempfile
import unittest

from evolution.learn import FACETS, Learning, date, now, read, write
from jp_shorts.agent_brief import export_brief
from jp_shorts.core import initialise, select
from jp_shorts.intelligence import analyze, decide, import_bundle, start_run
from jp_shorts.reach import bundle_from_result
from test_intelligence import plan, reach_response, vidiq
from test_research import niche


SKILL = Path(__file__).resolve().parents[1] / ".claude/skills/research-next-video"
spec = importlib.util.spec_from_file_location("video_packets", SKILL / "scripts/handoff.py")
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


class AgentHandoffTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.project = Path(tmp.name) / "private"
        initialise(self.project)
        write(self.project / "niches.json", {"niches": [niche()]})
        home = Path(tmp.name) / "repo/evolution"
        write(home / "config.json", {"schema_version": 1, "repository": "example/fixture", "branch": "main"})
        self.engine = Learning(home)

    def decision(self, mode="topic", selected=True):
        if mode == "topic":
            select(self.project, "fixture")
        research = plan(mode)
        start_run(self.project, research)
        if selected:
            import_bundle(self.project, vidiq())
            import_bundle(self.project, bundle_from_result(research["candidates"][0], "youtube",
                          {"query": "試験用"}, reach_response(), now()))
        analysis = analyze(self.project)
        decide(self.project, {"status": "selected" if selected else "insufficient_evidence", "decided_by": "claude",
               "rationale_en": "Offline exercise only.", "unknowns_en": "Actual demand unknown.",
               "selected_candidate_id": "fixture" if selected else None, "input_sha256": analysis["input_sha256"],
               "comparisons": [{"candidate_id": c["id"], "rationale_en": "Fixture comparison.",
                                "evidence_ids": c["evidence_ids"]} for c in analysis["candidates"]]})

    def begin(self, has_frames=True):
        self.run = self.engine.begin(self.project, "fixture", "ja", "JP", "short")
        data = read(self.run["evidence_template"])
        raw = ".evolution/runs/" + self.run["run_id"] + "/raw/"
        meta, words, watch = (raw + f for f in ("metadata.json", "spoken.json", "watch.json"))
        vid = "VIDEOID0001"
        stamp = data["collected_at"]
        write(self.project / meta, {"id": vid, "channelId": "fixture-channel", "vph": 15,
                                    "publishedAt": (date(stamp) - timedelta(days=2)).isoformat()})
        write(self.project / words, {"text": "Synthetic untimed opening and payoff."})
        write(self.project / watch, {"text": "Synthetic visual note at 0:02."})
        gap = {"status": "unavailable", "reason": "Not in the test sample."}
        facets = {f: gap.copy() for f in FACETS}
        facets["script"] = {"status": "observed", "method": "transcript", "source": {"file": words},
                            "observation": "The opening passage introduces the question."}
        if has_frames:
            facets["frames"] = {"status": "observed", "method": "video_analysis", "source": {"file": watch},
                                "observation": "At 0:02 an object enters the frame.", "timestamps": [2]}
        data["discovery"].update(status="ok", method="Offline fixture only.", metric="vph", sources=[{"file": meta}])
        data["videos"] = [{"id": vid, "channel_id": "fixture-channel", "scope": data["scope"], "content_verified": True,
                           "scope_basis": "Offline synthetic example.", "observed_at": stamp, "duration_seconds": 25,
                           "metadata": {"file": meta, "pointer": ""}, "metric_value": 15, "facets": facets}]
        self.engine.refresh(self.project, data)
        return export_brief(self.project, self.engine)

    def test_untimed_script_to_exact_editor_input_and_native_gate(self):
        self.decision()
        brief = self.begin()
        writer = handoff.process("writer", self.project, brief)
        self.assertEqual(writer, handoff.process("writer", self.project, brief))
        script = self.project / "script.ja.txt"
        script.write_text("元の原稿", encoding="utf-8")
        editor = handoff.process("editor", self.project, brief, script.name)
        self.assertEqual(editor, handoff.process("verify", self.project, brief))
        self.assertEqual(read(editor)["paired_examples"], ["VIDEOID0001"])
        board = self.project / "board.md"
        board.write_text("Original storyboard", encoding="utf-8")
        application = {"run_id": self.run["run_id"], "facets": {
            facet: {"artifact": script.name if facet == "script" else board.name,
                    "decisions": [], "fallback_reason": "No active rules in the fixture."} for facet in FACETS}}
        with self.assertRaisesRegex(ValueError, "Bind both agent"):
            self.engine.apply(self.project, application)
        application["production_inputs"] = [p.relative_to(self.project).as_posix() for p in (writer, editor)]
        self.engine.apply(self.project, application)
        self.assertEqual(self.engine.verify(self.project)["status"], "verified")
        script.write_text("改稿した原稿", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Stale editor"):
            handoff.process("verify", self.project, brief)
        with self.assertRaisesRegex(ValueError, "current production script"):
            self.engine.apply(self.project, application)
        handoff.process("editor", self.project, brief, script.name)
        self.engine.apply(self.project, application)
        self.assertEqual(self.engine.verify(self.project)["status"], "verified")
        write(self.project / "research/active.json", {"run_id": "different"})
        with self.assertRaisesRegex(ValueError, "input changed"):
            handoff.process("verify", self.project, brief)
        with self.assertRaisesRegex(ValueError, "input changed"):
            self.engine.verify(self.project)

    def test_visual_evidence_cannot_be_inferred_from_a_script(self):
        self.decision()
        brief = self.begin(has_frames=False)
        handoff.process("writer", self.project, brief)
        with self.assertRaisesRegex(ValueError, "timestamped frame"):
            handoff.process("editor", self.project, brief, "script.ja.txt")

    def test_niche_only_stops_before_a_writing_assignment(self):
        self.decision("niche")
        with self.assertRaisesRegex(ValueError, "specific topic"):
            export_brief(self.project, self.engine)

    def test_insufficient_evidence_cannot_release_either_role(self):
        self.decision(selected=False)
        with self.assertRaisesRegex(ValueError, "Insufficient evidence"):
            export_brief(self.project, self.engine)

    def test_provider_and_freshness_guards_on_portable_briefs(self):
        self.decision()
        name = self.begin()
        filename = self.project / name
        brief = read(filename)
        only_vidiq = [s for s in brief["decision"]["sources"] if s["provider"] == "vidiq"]
        write(filename, {**brief, "decision": {**brief["decision"], "sources": only_vidiq}})
        with self.assertRaisesRegex(ValueError, "Cite both"):
            handoff.process("writer", self.project, name)
        write(filename, {**brief, "valid_until": (date(now()) - timedelta(hours=1)).isoformat()})
        with self.assertRaisesRegex(ValueError, "expired"):
            handoff.process("writer", self.project, name)


if __name__ == "__main__":
    unittest.main()
