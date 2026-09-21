# Compare measured outcomes fairly

Use this protocol after rehearsing the editing backend. It compares **improvement of an existing deck**, our intended task. It does not test general presentation generation, install PPTAgent/DeepPresenter, run either external system, or establish that our workflow is better. No real benchmark measurements ship with this repository.

## One task, identical constraints

1. Choose a 5–10-slide source deck and retain its SHA-256. Start with an ordinary lecture, then separately test a dense equation deck and a chart/table deck. Use only services authorized for that deck; reuse existing authorization rather than asking again.
2. Freeze a UTF-8 `task-spec.json` before running any system. Include selected slides, exact requested operations, content-change permissions, required feature IDs and acceptance checks, source object IDs requiring editability, inherited raster evidence, reference assets, clarification answers, measurement procedure, model settings and allowed tool access. Hash its **exact file bytes**. Every compared attempt receives the same source and task specification.
3. Record exact system version/commit, role-specific model IDs and versions, renderer/version, hardware, account limits, reference access and warm/cold cache state. Do not silently treat PPTAgent and DeepPresenter as the same implementation. Match controllable conditions; disclose differences. If a system cannot improve an existing PPTX under these constraints, record that limitation instead of substituting a generation task.
4. Rehearse dependency setup before recording runs and measure its elapsed time separately. Measure each run from when the source and frozen request are handed to the system until the reviewed artifact and report are available, or the run is ended. Include clarification waits, generation, retries, export, rendering, manual intervention, review and repair in elapsed time. Do not reset the measurement after a failed attempt. Post-run benchmark scoring can be measured separately, but a later correction to the delivered artifact must be counted as a correction and cannot retroactively improve the recorded result. Measurement introduces no deadlines, cutoffs or interruption behavior into the local workflow.
5. Use the same predeclared repetitions for each system, preferably at least three for rehearsal, and alternate/randomize system order. Retain failed, blocked and partial attempts. Use one unique `run_id` for every attempt. A repetition is another attempt at the same task, not another dataset.
6. Have the Reviewer examine the exported PPTX and its render. Run the same content guard, compare reading order/meaning and teaching usefulness, and inspect every required native object. Retain source and candidate hashes with the reports and renders. Use anonymized output order for blind visual assessment where possible. The Reviewer never edits the deck. Corrective edits belong to the Executioner and count toward the run.

PowerShell can record the hashes without modifying the files:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath "runs/benchmark-task/source.pptx"
Get-FileHash -Algorithm SHA256 -LiteralPath "runs/benchmark-task/task-spec.json"
```

## Measurement report

Save a JSON **array** of reports to `runs/<comparison-id>/runs.json`. Each report needs all fields below; use `null` for unknown measurements, never zero. This is a format example with placeholder hashes and **no measured results**. Replace the identity fields and evidence before using it as a real report.

```json
[
  {
    "task_id": "lecture-layout-01",
    "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "task_spec_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "candidate_sha256": null,
    "run_id": "workflow-01",
    "repetition": 1,
    "runtime_system": "our-workflow",
    "version": null,
    "models": null,
    "renderer": null,
    "duration_seconds": null,
    "setup_seconds": null,
    "completion_status": "BLOCKED",
    "content_guard": "UNVERIFIED",
    "fidelity_review": "UNVERIFIED",
    "unauthorized_content_changes": null,
    "required_core_objects": null,
    "required_core_objects_checked": null,
    "editable_core_objects": null,
    "missing_required_features": null,
    "visual_score": null,
    "visual_review_blind": null,
    "manual_corrections": null
  }
]
```

| Field | Meaning |
|---|---|
| `task_id`, `source_sha256`, `task_spec_sha256` | Must match across all reports in one comparison. Changed requirements or clarification answers need a new frozen task and matched reruns. |
| `candidate_sha256` | SHA-256 of the actual reviewed output, or `null` when unavailable. Every reported check must refer to this same candidate. |
| `runtime_system`, `version`, `models`, `renderer` | Keep these separate. Use the exact commit/version; `models` is a list such as `["planner:provider/model@version", "executioner:provider/model@version", "reviewer:provider/model@version"]`. Unknown metadata is `null`. |
| `duration_seconds`, `setup_seconds` | Finite, nonnegative elapsed seconds, or `null`; setup is reported separately and never silently discarded. |
| `completion_status` | `COMPLETE`, `PARTIAL`, `BLOCKED` or `FAILED`; a fast partial result is not a completed delivery. |
| `content_guard` | `PASS`, `FAIL` or `UNVERIFIED` for the read-only check of its supported OOXML coverage. A guard pass does not establish semantic preservation. |
| `fidelity_review` | `PASS`, `FAIL` or `UNVERIFIED` for human/independent comparison of wording, numbers, equations, data, notes, citations, links, reading order and meaning, allowing only the recorded changes. |
| `unauthorized_content_changes` | Count of distinct violated content items using the same counting rule in the frozen specification, or `null` when not established. |
| `required_core_objects` | Total inventory from the frozen task, including core native objects to preserve and required new editable objects. Identified source object IDs keep the denominator stable. Known totals must match across reports. |
| `required_core_objects_checked` | Number of inventory objects whose editability was conclusively inspected. Missing or flattened required objects count as checked failures once their absence/rasterization is established. |
| `editable_core_objects` | Number of those checked objects passing native editability. Must be ≤ checked ≤ total. Replaceable illustrations do not count as editable charts/equations. |
| `missing_required_features` | Count of unmet required feature IDs, including failed readability requirements; use `null` if the checklist was not completed. |
| `visual_score`, `visual_review_blind` | Optional visual assessment from 1 (unusable) to 5 (excellent), with a required boolean disclosure when scored. Use a predeclared rubric covering legibility, hierarchy, coherence and teaching usefulness. Record qualitative findings alongside the score. Nonblind scores are excluded from `blind_visual_score` summaries. |
| `manual_corrections` | Count of human edit operations needed to meet requirements under a predeclared rule, or `null`. Keep operation details, elapsed time and whether corrections occurred during or after the run. |

### Guard differences and scoped authorization

Keep `content_guard` equal to the **raw machine result**, including `FAIL` when the checker finds differences. Never replace it with a reviewer decision. A guard difference alone neither grants authorization nor establishes that the content change was unauthorized.

Two fields are optional under the default content lock:

- `authorized_content_requirement_ids`: the content-edit permission IDs copied from the frozen task, default `[]`. All reports for that task must declare the same IDs. They are scoped permissions, not a blanket rewriting allowance.
- `content_guard_adjudication`: the Reviewer's explicit disposition, default absent/null. It is **required to resolve a raw guard `FAIL` into a passing fidelity gate**. Its decision must be `PASS_WITH_AUTHORIZED_DIFFS`, with a named Reviewer, matching source/candidate/task hashes, hashes of the raw guard and signed/named review reports, and a disposition for every difference in that raw guard report.

This illustrative report fragment shows the exact format; the hashes and evidence are placeholders, not real approval:

```json
{
  "authorized_content_requirement_ids": ["REQ-C1"],
  "content_guard": "FAIL",
  "content_guard_adjudication": {
    "decision": "PASS_WITH_AUTHORIZED_DIFFS",
    "reviewer_id": "Reviewer:identified-reviewer",
    "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "candidate_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    "task_spec_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "guard_report_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
    "review_report_sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "guard_difference_count": 1,
    "dispositions": [
      {
        "guard_difference_index": 0,
        "classification": "AUTHORIZED_CONTENT_CHANGE",
        "authorization_id": "REQ-C1",
        "judgment": "Matches the exact correction authorized by REQ-C1 on the specified slide/object.",
        "evidence": "review.json#REQ-C1"
      }
    ]
  }
}
```

`guard_difference_count` is the complete positive count of entries in the raw guard report's `differences` array. `dispositions` must cover each zero-based index exactly once. Each needs a nonempty `judgment` and `evidence` reference. `AUTHORIZED_CONTENT_CHANGE` requires an `authorization_id` in the declared frozen-task permission list and an explanation of how the actual difference matches that exact permission. For formatting representation changes only, use `classification: "REPRESENTATIONAL_ONLY"`, `authorization_id: null`, and evidence establishing equivalence in context (for example, joined text runs with identical displayed text and reading order). This classification cannot authorize rewriting or uncertain content reconstruction.

Even a complete adjudication cannot pass fidelity unless independent `fidelity_review` is `PASS`, `unauthorized_content_changes` is exactly zero, and the candidate hash exists. A missing, blanket, incomplete or mismatched adjudication leaves raw differences unresolved (`UNVERIFIED`); a known unauthorized change or failed independent review remains `FAIL`. An adjudication cannot upgrade an unperformed `UNVERIFIED` guard. The helper validates submitted fields and their bindings; it **does not open the referenced evidence, verify a cryptographic signature, or independently establish permission authenticity**. The Reviewer must verify actual task permissions and reports, and the benchmark operator must retain that evidence.

Additional fields such as `evidence_paths`, `hardware`, `model_settings`, `cost`, `reviewer_notes` and `blocked_reason` are preserved in per-run output. They are not validated by the helper. Do not put credentials in reports.

## Run the comparison

From the repository root, using an existing unique comparison directory:

```powershell
python scripts/compare_runs.py "runs/<comparison-id>/runs.json" --output "runs/<comparison-id>/comparison.json"
python -m unittest discover -s tests -p test_compare_runs.py -v
```

The helper uses only Python's standard library. Inputs are read-only. Output must be a new `.json` file whose parent exists; it is published atomically using a local-filesystem hard link and never overwrites an existing path. Use a filesystem supporting hard links (such as local NTFS); an unsupported filesystem produces an error without substituting a partial-write path. Invalid input exits with code 2; successful summarization exits with code 0 even when the measured runs fail their gates.

Elapsed time is a descriptive metric. **There is no default time limit or time acceptance gate.** With the normal command, `demo_target_seconds` is `null` and each run's `time` comparison is `NOT_APPLICABLE`, including runs with unknown duration. A long local run can pass all quality and completion checks.

For a particular live demo, an operator may explicitly add `--demo-target-seconds <seconds>` to compare already measured elapsed time with that event's target. The legacy alias `--deadline-seconds` has exactly the same measurement-only meaning. A supplied target must be finite and positive. The post-run `time` comparison is `PASS` when elapsed is ≤ the selected target, `FAIL` when greater, or `UNVERIFIED` when duration is unknown. There is no additional under-30-minute condition. This option never schedules, interrupts, shortens or controls a run, and its result is excluded from quality and delivery calculations even when the target is missed.

The JSON includes separate fidelity, editability, required-feature and completion gates, plus their conjunction as `delivery`. The informational `time` comparison is kept alongside them for inspection but is excluded from that conjunction. Unknown quality evidence is `UNVERIFIED`; known violations remain `FAIL` even when another check is unknown. Fidelity needs a raw guard pass or the complete difference adjudication described above, an independent review pass, zero unauthorized changes, and a candidate hash. Editability needs a candidate hash and the complete required inventory checked and editable. A confirmed zero-size native-object inventory passes vacuously; it makes no claim about inherited raster evidence. The `delivery` conjunction covers these recorded measures; it is **not** a substitute for visual acceptance or a certification of the deck. Record readability blockers as unmet required features.

All reports must describe the same task; mismatched source/task hashes, changed known native-object totals, duplicate run IDs and duplicate system/repetition pairs are rejected. Different versions, model sets or renderers form separate system groups. `models_match` and `renderers_match` disclose exact label matching (`null` for unknown); they do not prove controlled conditions. `matched_repetitions` exposes uneven attempt coverage. Means show observed/missing counts, retain all attempts and never impute zero for unknown time or quality.

One invocation reports `dataset_count: 1`; run separately for each deck/task and retain every result. The helper always leaves `overall_winner: null` and does not test statistical significance. First assess whether required preservation/editability/features passed; then compare speed, visual scores, corrections and costs. Describe observed differences for the tested decks and conditions. A handful of rehearsals cannot establish general superiority, and unmeasured conditions remain unmeasured.
