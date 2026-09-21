"""Synthetic measurement reports: these are not presentation benchmark results."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compare_runs.py"


def report(**changes):
    result = {
        "task_id": "synthetic-task", "source_sha256": "a" * 64,
        "task_spec_sha256": "b" * 64, "candidate_sha256": "c" * 64,
        "run_id": "workflow-1", "repetition": 1,
        "runtime_system": "our-workflow", "version": "test-only",
        "models": ["provider/model@version"], "renderer": "renderer@version",
        "duration_seconds": 1400, "setup_seconds": 120,
        "completion_status": "COMPLETE", "content_guard": "PASS",
        "fidelity_review": "PASS", "unauthorized_content_changes": 0,
        "required_core_objects": 12, "required_core_objects_checked": 12,
        "editable_core_objects": 12, "missing_required_features": 0,
        "visual_score": 4, "visual_review_blind": True,
        "manual_corrections": 0,
    }
    result.update(changes)
    return result


def adjudication(**changes):
    result = {
        "decision": "PASS_WITH_AUTHORIZED_DIFFS", "reviewer_id": "Reviewer:synthetic",
        "source_sha256": "a" * 64, "candidate_sha256": "c" * 64, "task_spec_sha256": "b" * 64,
        "guard_report_sha256": "d" * 64, "review_report_sha256": "e" * 64,
        "guard_difference_count": 1,
        "dispositions": [{
            "guard_difference_index": 0, "classification": "AUTHORIZED_CONTENT_CHANGE",
            "authorization_id": "REQ-C1", "judgment": "Matches the exact permitted correction.",
            "evidence": "review.json#REQ-C1",
        }],
    }
    result.update(changes)
    return result


class ComparisonTests(unittest.TestCase):
    def invoke(self, reports, *args, existing_output=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "runs.json"
            output = root / "comparison.json"
            original = json.dumps(reports)
            source.write_text(original, encoding="utf-8")
            if existing_output is not None:
                output.write_text(existing_output, encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--output", str(output), *args],
                capture_output=True, text=True,
            )
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            text = output.read_text(encoding="utf-8") if output.exists() else None
            return process, text

    def comparison(self, reports, *args):
        process, content = self.invoke(reports, *args)
        self.assertEqual(process.returncode, 0, process.stderr)
        return json.loads(content)

    def test_matched_task_reports_gates_without_claiming_a_winner(self):
        result = self.comparison([
            report(), report(run_id="pptagent-1", runtime_system="PPTAgent"),
        ])
        self.assertEqual(result["dataset_count"], 1)
        self.assertEqual(result["run_count"], 2)
        self.assertIsNone(result["overall_winner"])
        self.assertFalse(result["statistical_significance_assessed"])
        self.assertTrue(result["models_match"])
        self.assertTrue(result["matched_repetitions"])
        self.assertEqual(result["runs"][0]["gates"], {
            "fidelity": "PASS", "editability": "PASS", "required_features": "PASS",
            "time": "NOT_APPLICABLE", "completion": "PASS", "delivery": "PASS",
        })

    def test_unknown_measurements_remain_unknown(self):
        result = self.comparison([report(
            duration_seconds=None, setup_seconds=None, visual_score=None,
            visual_review_blind=None, manual_corrections=None,
            unauthorized_content_changes=None, required_core_objects_checked=None,
            editable_core_objects=None, fidelity_review="UNVERIFIED",
        )])
        self.assertEqual(result["runs"][0]["gates"]["time"], "NOT_APPLICABLE")
        self.assertEqual(result["runs"][0]["gates"]["fidelity"], "UNVERIFIED")
        self.assertEqual(result["runs"][0]["gates"]["editability"], "UNVERIFIED")
        for metric in ("duration_seconds", "setup_seconds", "visual_score", "manual_corrections"):
            summary = result["systems"][0]["metrics"][metric]
            self.assertIsNone(summary["mean"])
            self.assertEqual(summary["observed_count"], 0)
            self.assertEqual(summary["missing_count"], 1)

    def test_guard_pass_cannot_replace_semantic_review(self):
        result = self.comparison([report(fidelity_review="UNVERIFIED")])
        self.assertEqual(result["runs"][0]["gates"]["fidelity"], "UNVERIFIED")
        self.assertEqual(result["runs"][0]["gates"]["delivery"], "UNVERIFIED")

    def test_authorized_diff_adjudication_preserves_raw_guard_failure(self):
        result = self.comparison([report(content_guard="FAIL", authorized_content_requirement_ids=["REQ-C1"],
                                         content_guard_adjudication=adjudication())])
        self.assertEqual(result["runs"][0]["content_guard"], "FAIL")
        self.assertEqual(result["runs"][0]["gates"]["fidelity"], "PASS")

    def test_representational_diff_needs_equivalence_evidence_but_no_content_permission(self):
        decision = adjudication(dispositions=[{
            "guard_difference_index": 0, "classification": "REPRESENTATIONAL_ONLY",
            "authorization_id": None, "judgment": "Text runs joined; displayed text and order unchanged.",
            "evidence": "review.json#equivalence-check",
        }])
        result = self.comparison([report(content_guard="FAIL", content_guard_adjudication=decision)])
        self.assertEqual(result["runs"][0]["gates"]["fidelity"], "PASS")

    def test_blanket_or_incomplete_adjudication_cannot_override_diff(self):
        for decision in (None, {"decision": "PASS_WITH_AUTHORIZED_DIFFS"},
                         adjudication(reviewer_id=""), adjudication(guard_report_sha256=None),
                         adjudication(candidate_sha256="f" * 64), adjudication(task_spec_sha256="f" * 64),
                         adjudication(guard_difference_count=2), adjudication(dispositions=[])):
            with self.subTest(decision=decision):
                result = self.comparison([report(content_guard="FAIL", authorized_content_requirement_ids=["REQ-C1"],
                                                 content_guard_adjudication=decision)])
                self.assertNotEqual(result["runs"][0]["gates"]["fidelity"], "PASS")

    def test_adjudication_requires_actual_scope_and_independent_pass(self):
        for changes in ({"authorized_content_requirement_ids": []}, {"fidelity_review": "UNVERIFIED"},
                        {"unauthorized_content_changes": 1}, {"content_guard": "UNVERIFIED"}):
            with self.subTest(changes=changes):
                item = report(content_guard="FAIL", authorized_content_requirement_ids=["REQ-C1"],
                              content_guard_adjudication=adjudication())
                item.update(changes)
                result = self.comparison([item])
                self.assertNotEqual(result["runs"][0]["gates"]["fidelity"], "PASS")

    def test_task_permissions_cannot_differ_between_matched_reports(self):
        process, output = self.invoke([report(), report(run_id="other", runtime_system="PPTAgent",
                                                       authorized_content_requirement_ids=["REQ-C1"])])
        self.assertNotEqual(process.returncode, 0)
        self.assertIsNone(output)

    def test_measured_fidelity_and_editability_failures_are_visible(self):
        result = self.comparison([report(unauthorized_content_changes=1, editable_core_objects=11)])
        gates = result["runs"][0]["gates"]
        self.assertEqual(gates["fidelity"], "FAIL")
        self.assertEqual(gates["editability"], "FAIL")
        self.assertEqual(gates["delivery"], "FAIL")

    def test_partial_check_of_native_objects_does_not_pass(self):
        result = self.comparison([report(required_core_objects_checked=6, editable_core_objects=6)])
        self.assertEqual(result["runs"][0]["gates"]["editability"], "UNVERIFIED")

    def test_missing_artifact_hash_cannot_establish_verified_delivery(self):
        result = self.comparison([report(candidate_sha256=None)])
        self.assertEqual(result["runs"][0]["gates"]["delivery"], "UNVERIFIED")

    def test_local_run_has_no_default_time_limit(self):
        result = self.comparison([report(duration_seconds=10800)])
        self.assertIsNone(result["demo_target_seconds"])
        self.assertEqual(result["runs"][0]["gates"]["time"], "NOT_APPLICABLE")
        self.assertEqual(result["runs"][0]["gates"]["delivery"], "PASS")
        self.assertEqual(result["systems"][0]["metrics"]["duration_seconds"]["mean"], 10800)

    def test_optional_demo_target_only_reports_elapsed_comparison(self):
        for seconds, expected in ((1799, "PASS"), (1800, "PASS"), (1800.01, "FAIL"), (10800, "FAIL")):
            with self.subTest(seconds=seconds):
                result = self.comparison([report(duration_seconds=seconds)], "--demo-target-seconds", "1800")
                self.assertEqual(result["demo_target_seconds"], 1800)
                self.assertEqual(result["runs"][0]["gates"]["time"], expected)
                self.assertEqual(result["runs"][0]["gates"]["delivery"], "PASS")
        result = self.comparison([report(duration_seconds=7200)], "--deadline-seconds", "7200")
        self.assertEqual(result["runs"][0]["gates"]["time"], "PASS")

    def test_unknown_elapsed_with_optional_target_does_not_affect_quality(self):
        result = self.comparison([report(duration_seconds=None)], "--demo-target-seconds", "1800")
        self.assertEqual(result["runs"][0]["gates"]["time"], "UNVERIFIED")
        self.assertEqual(result["runs"][0]["gates"]["delivery"], "PASS")

    def test_explicit_demo_target_must_be_positive_and_finite(self):
        for target in ("0", "-1", "nan", "inf"):
            with self.subTest(target=target):
                process, output = self.invoke([report()], "--demo-target-seconds", target)
                self.assertNotEqual(process.returncode, 0)
                self.assertIsNone(output)

    def test_setup_is_separate_and_fast_partial_run_is_not_delivery(self):
        result = self.comparison([report(duration_seconds=100, setup_seconds=3000,
                                         completion_status="PARTIAL", missing_required_features=1)])
        gates = result["runs"][0]["gates"]
        self.assertEqual(gates["time"], "NOT_APPLICABLE")
        self.assertEqual(gates["completion"], "FAIL")
        self.assertEqual(gates["required_features"], "FAIL")
        self.assertEqual(gates["delivery"], "FAIL")
        self.assertEqual(result["systems"][0]["metrics"]["setup_seconds"]["mean"], 3000)

    def test_task_mismatches_are_rejected_without_output(self):
        for field, value in (("source_sha256", "d" * 64), ("task_spec_sha256", "e" * 64),
                             ("task_id", "other-task")):
            with self.subTest(field=field):
                process, output = self.invoke([report(), report(run_id="other", **{field: value})])
                self.assertNotEqual(process.returncode, 0)
                self.assertIn("mismatch", process.stderr)
                self.assertIsNone(output)

    def test_same_task_cannot_silently_reduce_editability_inventory(self):
        process, output = self.invoke([
            report(), report(run_id="other", runtime_system="PPTAgent", required_core_objects=1,
                             required_core_objects_checked=1, editable_core_objects=1),
        ])
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("inventory", process.stderr)
        self.assertIsNone(output)

    def test_unknown_model_metadata_does_not_claim_equivalence(self):
        result = self.comparison([report(models=None, version=None, renderer=None)])
        self.assertIsNone(result["models_match"])
        self.assertIsNone(result["renderers_match"])

    def test_nonblind_visual_scores_remain_separate(self):
        result = self.comparison([report(visual_score=5, visual_review_blind=False)])
        self.assertEqual(result["systems"][0]["metrics"]["visual_score"]["mean"], 5)
        self.assertIsNone(result["systems"][0]["blind_visual_score"]["mean"])

    def test_changed_model_or_renderer_is_disclosed(self):
        result = self.comparison([report(), report(run_id="other", runtime_system="PPTAgent",
                                                 models=["different-model"], renderer="other-renderer")])
        self.assertFalse(result["models_match"])
        self.assertFalse(result["renderers_match"])
        self.assertIsNone(result["overall_winner"])

    def test_repetitions_and_missing_metrics_are_not_cherry_picked(self):
        result = self.comparison([
            report(duration_seconds=100),
            report(run_id="workflow-2", repetition=2, duration_seconds=None,
                   completion_status="FAILED", visual_score=None, visual_review_blind=None),
            report(run_id="other", runtime_system="PPTAgent", duration_seconds=200),
        ])
        self.assertFalse(result["matched_repetitions"])
        workflow = next(item for item in result["systems"] if item["runtime_system"] == "our-workflow")
        self.assertEqual(workflow["run_count"], 2)
        self.assertEqual(workflow["metrics"]["duration_seconds"]["mean"], 100)
        self.assertEqual(workflow["metrics"]["duration_seconds"]["missing_count"], 1)
        self.assertEqual(workflow["delivery_gate_counts"]["FAIL"], 1)

    def test_invalid_measurements_and_duplicate_attempts_are_rejected(self):
        invalid = [
            {"duration_seconds": -1}, {"duration_seconds": True}, {"duration_seconds": float("nan")},
            {"visual_score": 6}, {"visual_score": 4, "visual_review_blind": None},
            {"unauthorized_content_changes": 0.5}, {"required_core_objects_checked": 13},
            {"editable_core_objects": 13}, {"source_sha256": "invalid"}, {"repetition": 0},
            {"models": []}, {"completion_status": "probably-done"},
        ]
        for changes in invalid:
            with self.subTest(changes=changes):
                process, output = self.invoke([report(**changes)])
                self.assertNotEqual(process.returncode, 0)
                self.assertIsNone(output)
        for reports in ([report(), report()], [report(), report(run_id="different")]):
            process, output = self.invoke(reports)
            self.assertNotEqual(process.returncode, 0)
            self.assertIsNone(output)

    def test_missing_required_metadata_is_rejected(self):
        item = report()
        del item["task_spec_sha256"]
        process, output = self.invoke([item])
        self.assertNotEqual(process.returncode, 0)
        self.assertIsNone(output)

    def test_existing_output_is_never_overwritten(self):
        process, output = self.invoke([report()], existing_output="original output")
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(output, "original output")

    def test_cli_refuses_non_json_output_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "runs.json", Path(directory) / "comparison.pptx"
            source.write_text(json.dumps([report()]), encoding="utf-8")
            process = subprocess.run([sys.executable, str(SCRIPT), str(source), "--output", str(output)],
                                     capture_output=True, text=True)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn(".json", process.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
