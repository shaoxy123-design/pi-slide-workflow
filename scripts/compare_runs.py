#!/usr/bin/env python3
"""Summarize manually measured, matched slide-improvement runs; stdlib only.

This does not run editors, validate the submitted evidence, or select a winner.
"""

import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys
import tempfile


HASH = re.compile(r"[0-9a-fA-F]{64}\Z")
REVIEW_STATES = {"PASS", "FAIL", "UNVERIFIED"}
COUNTS = (
    "unauthorized_content_changes", "required_core_objects", "required_core_objects_checked",
    "editable_core_objects", "missing_required_features", "manual_corrections",
)
METRICS = ("duration_seconds", "setup_seconds", "visual_score", "manual_corrections")
REQUIRED = {
    "task_id", "source_sha256", "task_spec_sha256", "candidate_sha256", "run_id", "repetition",
    "runtime_system", "version", "models", "renderer", "duration_seconds", "setup_seconds",
    "completion_status", "content_guard", "fidelity_review", "visual_score", "visual_review_blind",
    *COUNTS,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def numeric(value, name, *, integer=False):
    if value is None:
        return
    require(type(value) in ((int,) if integer else (int, float)), f"{name}: invalid number")
    require(math.isfinite(value) and value >= 0, f"{name}: must be finite and nonnegative")


def validate_report(item):
    require(isinstance(item, dict), "each report must be an object")
    require(REQUIRED <= item.keys(), f"missing required fields: {sorted(REQUIRED - item.keys())}")
    item = dict(item)
    for key in ("task_id", "run_id", "runtime_system"):
        require(isinstance(item[key], str) and bool(item[key].strip()), f"{key}: nonempty string required")
    for key in ("source_sha256", "task_spec_sha256", "candidate_sha256"):
        if key == "candidate_sha256" and item[key] is None:
            continue
        require(isinstance(item[key], str) and bool(HASH.fullmatch(item[key])), f"{key}: invalid SHA-256")
        item[key] = item[key].lower()
    for key in ("version", "renderer"):
        require(item[key] is None or (isinstance(item[key], str) and bool(item[key].strip())),
                f"{key}: nonempty string or null required")
    models = item["models"]
    require(models is None or (isinstance(models, list) and len(models) > 0
            and all(isinstance(model, str) and bool(model.strip()) for model in models)),
            "models: nonempty string list or null required")
    if models is not None:
        item["models"] = sorted(models)
    permissions = item.get("authorized_content_requirement_ids", [])
    require(isinstance(permissions, list) and all(isinstance(value, str) and value.strip() for value in permissions),
            "authorized_content_requirement_ids: list of nonempty requirement IDs required")
    require(len(set(permissions)) == len(permissions), "authorized_content_requirement_ids: duplicate ID")
    item["authorized_content_requirement_ids"] = sorted(permissions)
    require(type(item["repetition"]) is int and item["repetition"] >= 1, "repetition: positive integer required")
    require(item["completion_status"] in ("COMPLETE", "PARTIAL", "BLOCKED", "FAILED"),
            "completion_status: invalid state")
    for key in ("content_guard", "fidelity_review"):
        require(isinstance(item[key], str) and item[key] in REVIEW_STATES, f"{key}: invalid review state")
    for key in COUNTS:
        numeric(item[key], key, integer=True)
    for key in ("duration_seconds", "setup_seconds", "visual_score"):
        numeric(item[key], key)
    if item["visual_score"] is not None:
        require(1 <= item["visual_score"] <= 5, "visual_score: must be between 1 and 5")
        require(type(item["visual_review_blind"]) is bool, "visual_review_blind: required for a visual score")
    else:
        require(item["visual_review_blind"] is None or type(item["visual_review_blind"]) is bool,
                "visual_review_blind: boolean or null required")
    total, checked, editable = (item[key] for key in
                                ("required_core_objects", "required_core_objects_checked", "editable_core_objects"))
    if total is not None and checked is not None:
        require(checked <= total, "required_core_objects_checked exceeds required_core_objects")
    if checked is not None and editable is not None:
        require(editable <= checked, "editable_core_objects exceeds required_core_objects_checked")
    if total is not None and editable is not None:
        require(editable <= total, "editable_core_objects exceeds required_core_objects")
    return item


def combine(states):
    if "FAIL" in states:
        return "FAIL"
    return "UNVERIFIED" if "UNVERIFIED" in states else "PASS"


def zero_gate(value):
    return "UNVERIFIED" if value is None else ("PASS" if value == 0 else "FAIL")


def adjudication_resolves_differences(item):
    """Validate submitted review bindings; this does not authenticate external evidence."""
    decision = item.get("content_guard_adjudication")
    if not isinstance(decision, dict) or decision.get("decision") != "PASS_WITH_AUTHORIZED_DIFFS":
        return False
    if not isinstance(decision.get("reviewer_id"), str) or not decision["reviewer_id"].strip():
        return False
    for key in ("source_sha256", "candidate_sha256", "task_spec_sha256"):
        value = decision.get(key)
        if not isinstance(value, str) or value.lower() != item[key]:
            return False
    for key in ("guard_report_sha256", "review_report_sha256"):
        value = decision.get(key)
        if not isinstance(value, str) or not HASH.fullmatch(value):
            return False
    count, dispositions = decision.get("guard_difference_count"), decision.get("dispositions")
    if type(count) is not int or count <= 0 or not isinstance(dispositions, list) or len(dispositions) != count:
        return False
    indices = set()
    for disposition in dispositions:
        if not isinstance(disposition, dict):
            return False
        index = disposition.get("guard_difference_index")
        if type(index) is not int or not 0 <= index < count or index in indices:
            return False
        indices.add(index)
        for key in ("judgment", "evidence"):
            value = disposition.get(key)
            if not isinstance(value, str) or not value.strip():
                return False
        classification = disposition.get("classification")
        if classification == "AUTHORIZED_CONTENT_CHANGE":
            if disposition.get("authorization_id") not in item["authorized_content_requirement_ids"]:
                return False
        elif classification != "REPRESENTATIONAL_ONLY" or disposition.get("authorization_id") is not None:
            return False
    return True


def evaluate(item, demo_target_seconds):
    artifact = "PASS" if item["candidate_sha256"] else "UNVERIFIED"
    guard = item["content_guard"]
    if guard == "FAIL":
        guard = "PASS" if adjudication_resolves_differences(item) else "UNVERIFIED"
    fidelity = combine([guard, item["fidelity_review"],
                        zero_gate(item["unauthorized_content_changes"]), artifact])
    total, checked, editable = (item[key] for key in
                                ("required_core_objects", "required_core_objects_checked", "editable_core_objects"))
    if checked is not None and editable is not None and editable < checked:
        editability = "FAIL"
    elif None in (total, checked, editable) or checked != total:
        editability = "UNVERIFIED"
    else:
        editability = "PASS"
    editability = combine([editability, artifact])
    duration = item["duration_seconds"]
    time = ("NOT_APPLICABLE" if demo_target_seconds is None else
            "UNVERIFIED" if duration is None else
            "PASS" if duration <= demo_target_seconds else "FAIL")
    gates = {
        "fidelity": fidelity, "editability": editability,
        "required_features": zero_gate(item["missing_required_features"]), "time": time,
        "completion": "PASS" if item["completion_status"] == "COMPLETE" else "FAIL",
    }
    # Elapsed time is observational, even when the operator selects a demo target.
    gates["delivery"] = combine([value for key, value in gates.items() if key != "time"])
    return gates


def summarize(values):
    observed = [value for value in values if value is not None]
    return {
        "observed_count": len(observed), "missing_count": len(values) - len(observed),
        "mean": statistics.mean(observed) if observed else None,
        "min": min(observed) if observed else None, "max": max(observed) if observed else None,
    }


def system_key(item):
    return json.dumps([item["runtime_system"], item["version"], item["models"], item["renderer"]])


def metadata_match(reports, key):
    if any(item[key] is None for item in reports):
        return None
    return len({json.dumps(item[key]) for item in reports}) == 1


def compare_runs(reports, demo_target_seconds=None):
    numeric(demo_target_seconds, "demo_target_seconds")
    require(demo_target_seconds is None or demo_target_seconds > 0, "demo_target_seconds must be positive")
    require(isinstance(reports, list) and len(reports) > 0, "input must be a nonempty JSON report list")
    reports = [validate_report(item) for item in reports]
    task_keys = ("task_id", "source_sha256", "task_spec_sha256")
    task = {key: reports[0][key] for key in task_keys}
    for item in reports:
        for key in task_keys:
            require(item[key] == task[key], f"task mismatch: {key}")
    inventories = {item["required_core_objects"] for item in reports if item["required_core_objects"] is not None}
    require(len(inventories) <= 1, "required core object inventory mismatch for the same task")
    permissions = {tuple(item["authorized_content_requirement_ids"]) for item in reports}
    require(len(permissions) == 1, "task permissions mismatch: authorized_content_requirement_ids")
    require(len({item["run_id"] for item in reports}) == len(reports), "duplicate run_id")
    attempts = {(system_key(item), item["repetition"]) for item in reports}
    require(len(attempts) == len(reports), "duplicate system/repetition attempt")
    runs = [dict(item, gates=evaluate(item, demo_target_seconds)) for item in reports]
    grouped = {}
    for run in runs:
        grouped.setdefault(system_key(run), []).append(run)
    systems = []
    for group in grouped.values():
        system = {key: group[0][key] for key in ("runtime_system", "version", "models", "renderer")}
        system.update({
            "run_count": len(group), "repetitions": sorted(item["repetition"] for item in group),
            "delivery_gate_counts": dict(Counter(item["gates"]["delivery"] for item in group)),
            "metrics": {key: summarize([item[key] for item in group]) for key in METRICS},
            "blind_visual_score": summarize([
                item["visual_score"] if item["visual_review_blind"] is True else None for item in group
            ]),
        })
        systems.append(system)
    return {
        "schema_version": 2, "task": task, "dataset_count": 1, "run_count": len(runs),
        "system_count": len(systems), "demo_target_seconds": demo_target_seconds,
        "models_match": metadata_match(runs, "models"),
        "renderers_match": metadata_match(runs, "renderer"),
        "matched_repetitions": len(systems) > 1 and len({tuple(s["repetitions"]) for s in systems}) == 1,
        "overall_winner": None, "statistical_significance_assessed": False,
        "limitations": [
            "Manually supplied measurements are summarized, not independently verified.",
            "One matched task is one dataset; repetitions do not increase dataset_count.",
            "Means exclude null observations; missing counts and failed attempts remain visible.",
            "Matching model labels do not establish identical settings, hardware, cost, or tool access.",
            "No causal, statistical-significance, or overall-superiority claim is made.",
            "Delivery gates do not certify visual quality; inspect scores and reviewer evidence separately.",
            "Elapsed time and any explicitly selected demo target never affect delivery gates or control execution.",
        ],
        "systems": systems, "runs": runs,
    }


def write_new_json(path, payload):
    """Publish a complete file via a non-overwriting hard link on a local filesystem."""
    path = Path(path)
    require(path.suffix.lower() == ".json", "output must have a .json suffix")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".comparison-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)  # Atomic and fails if the destination already exists.
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", type=Path, help="JSON array of measured reports for one matched task")
    parser.add_argument("--output", required=True, type=Path, help="new JSON output path; parent must exist")
    parser.add_argument("--demo-target-seconds", "--deadline-seconds", dest="demo_target_seconds", type=float,
                        default=None, help="optional post-run elapsed measurement target; no default or run control")
    args = parser.parse_args()
    try:
        reports = json.loads(args.reports.read_text(encoding="utf-8-sig"))
        result = compare_runs(reports, args.demo_target_seconds)
        write_new_json(args.output, result)
    except (OSError, ValueError, TypeError) as error:
        print(f"comparison error: {error}", file=sys.stderr)
        return 2
    print(f"Wrote {args.output}: {result['run_count']} runs, {result['dataset_count']} matched task; no overall winner.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
