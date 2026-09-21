# Run state and handoff contracts

The host executes these contracts through its actual tools. JSON files are compact run records, not messages to an external service. Paths in records should be absolute. Use UTC ISO timestamps for traceability; optional elapsed-time measurements do not control execution or acceptance.

These are semantic contracts maintained by the Planner, not JSON Schemas enforced by a bundled runner. Existing utilities validate only their own inputs/outputs. For a future adapter, follow [host bindings](host-adapter.md); introduce explicit schema versions and compatibility handling if implementing machine validation. Do not silently migrate historical run evidence.

## Request and plan

`request.json` preserves the original request and clarification answers. Start with `examples/request.local.json`, replacing the example input with the actual supplied path. An absent source deck is a missing input, not an invitation to invent lecture content. For PDF input, follow [PDF intake](pdf-input.md), which requires a separately qualified reconstruction step; current scripts accept PPTX only.

`plan.json` contains:

| Field | Meaning |
|---|---|
| `run_id`, `source_path`, `source_sha256` | Immutable identity of the run and input |
| `started_at` | Run timestamp for traceability; no target, deadline or timed cutoff fields |
| `source_format`, `reconstruction` | PPTX or PDF; for PDF include original hash, page map, reconstructed PPTX/hash and independent conversion-review evidence |
| `content_policy`, `editability` | Default `preserve_exact` and `native_core_replaceable_artwork`; include any scoped overrides |
| `selected_slides`, `slide_count` | One-based presentation order, including hidden slides; don't assume file numbering is order |
| `requirements` | Each has `id`, `user_text`, `priority`, `clarity`, `scope`, `acceptance_check`, `status`; begin with PENDING, then use PASS, FAIL or UNVERIFIED based on review evidence |
| `authorizations` | Each has `id`, exact `user_instruction`, `scope`, `allowed_change`, `before`, `after_or_constraint`; empty by default |
| `assumptions`, `questions` | Stated safe defaults and outstanding question IDs |
| `style` | Single font/color/layout specification following source branding |
| `layout_catalog_path`, `reference_source_sha256` | Optional cached reference layouts, bound to their source; matches are advisory |
| `slide_actions` | Each has `slide`, `requirement_ids`, `action`, `visual_type`, `required` |
| `visual_blocks` | Each has `slide`, `block_id`, exact source text/object references, `topic`, `teaching_function`, planned visual/bank ID, `semantic_basis`, `required` and intended coverage |
| `visual_policy`, `visual_bank_path` | Default proactive topic-block coverage; scoped user override and actual reusable catalog path |
| `inherited_limits` | Image-only text/charts, unsupported native objects, uncertain reconstruction |
| `backend`, `renderer`, `tool_constraints` | Actual available tools, resolved paths and validated limitations |

Priorities: MUST for user-required work; SHOULD for desired quality; MAY for optional embellishment. Clarity: CLEAR, ASSUMED, BLOCKED. Elapsed time never changes priority. An authorization is scoped to exactly what the user requested, including when the permission came in the initial request. Do not request it twice.

## question_me

Conceptual signature:

```text
question_me(questions: Question[1..3]) -> answered | pending

Question = {
  id: string,
  question: string,
  reason: string,
  affected_scope: [slide/object identifiers],
  required: boolean,
  choices: [concrete answer options],
  default: null | safe default,
  independent_work: string
}
```

The Planner runs the following **adapter procedure**; this is pseudocode, not an executable tool definition:

```text
For each proposed question:
  Reuse an existing answer if present.
  If it is required, set default to null and pause dependent work.
  If optional, choose a safe default that does not expand authorization.

Present questions using a host tool available and permitted for this question
type and collaboration mode; otherwise ask in conversation.
If the tool is asynchronous, save question IDs and continue independent work.
If the tool blocks, await its result; do not count pending as answered.
If no tool is available, ask the necessary question in conversation.

On reply: save the user's answer, update scoped requirements, resume work.
After a reasonable opportunity to reply: use an announced safe optional default.
While a required answer is missing: keep it pending and pause dependent work.
```

In Codex, use a user-input capability actually available and permitted in the current mode. Mere tool exposure is not permission to use it: a Plan-mode-only tool is not available in Default mode. For a permitted asynchronous text-question tool, map the question to its title/options fields; keep reason, scope and required/default status in the run record. Follow its constraints for required decisions and file requests: ask in normal conversation when the tool is not permitted for the question. Do not manufacture a callable `question_me` tool name.

Example question record:

```json
{
  "id": "Q1",
  "question": "You asked to shorten bullets and preserve every word. Which takes priority on slides 3–5?",
  "reason": "Shortening requires a content change.",
  "affected_scope": ["slide:3", "slide:4", "slide:5"],
  "required": true,
  "choices": ["Keep wording; improve layout", "Allow shorter bullets on slides 3–5"],
  "default": null,
  "independent_work": "Inventory source and improve spacing on slides 1–2."
}
```

## Coordination state

The Planner updates `state.json` at phase boundaries:

```json
{
  "run_id": "demo-001",
  "phase": "PLANNING",
  "repair_round": 0,
  "pending_questions": [],
  "candidate_path": null,
  "candidate_sha256": null,
  "last_verified_path": null,
  "last_verified_sha256": null,
  "completed_requirements": [],
  "unresolved_requirements": [],
  "next_action": "Inspect actual source deck and confirm tool availability."
}
```

Phases are INTAKE → PLANNING → EXECUTING → REVIEWING, followed by REPAIRING → RECHECKING as needed, then DELIVERED when all required checks pass. There is no fixed repair cap. Stop repeating unchanged failures and report the concrete blocker; do not endlessly polish optional details. A run can end PARTIAL or BLOCKED from any phase. BLOCKED means no improvement satisfying required checks can be delivered; PARTIAL means some reviewed work is usable but an explicit requirement remains unmet. These are report outcomes, not permission to bypass a gate. Pending questions are saved for resumption and do not expire.

## Handoffs

Role prompts live in `agents/`; their inputs must be supplied explicitly. Resolve the repository root and role/skill paths for the receiving host. Do not rely on the worker seeing the parent's whole conversation. Planner owns request/plan/state and packaging; Executioner owns deck/build/asset evidence; Reviewer owns review reports and never changes source/candidate files.

Planner → Executioner: role/skill file paths, source and baseline, request and plan, selected slides, authorizations, build/asset paths, backend/renderer, tool constraints and required outputs. For PDF, include the original PDF, page map and conversion evidence.

Executioner → Planner: `execution.json` with candidate path/hash, changed slides, actions and requirement IDs, source/edit-log paths, render paths, content-guard path, content differences, asset manifest, native-object evidence, warnings and incomplete work.

Visual work also supplies `visual-coverage.json`, bound to the candidate hash. Each meaningful block records `slide`, `block_id`, source object/text references, `topic`, `teaching_function`, `semantic_basis`, `bank_id` or custom asset/recipe, actual `object_names`, `representation`, and `status` (`ADDED`, `REUSED`, `RETAINED_EXISTING`, `OMITTED`). Each native topic visual includes `selection_unit: "native_group"`, an actual top-level `group_name`, and `child_names`; artwork uses `selection_unit: "picture"` and `picture_name`. Record the source object for an existing single native chart/table. The delivered group must exist already, not just be possible to create. Omission needs a concrete reason and remains a failed requirement if the professor explicitly requested that block's visual. The Reviewer verifies this record against rendered/native objects; a catalog tag or asset count alone does not satisfy coverage.

Planner → Reviewer: role/skill paths, original request and plan, original/candidate decks and hashes, baseline, actual content check, all renders, execution log, native-object evidence and required-feature list. For PDF, include the original PDF and reconstruction evidence, not just a converted PPTX baseline. Reviewer reads the request before the execution log.

Reviewer → Planner: `review.json` with:

```text
candidate_path, candidate_sha256, reviewed_at
decision: PASS | PASS_WITH_AUTHORIZED_DIFFS | PARTIAL | BLOCKED
checked_slides: [slide numbers]
gates: {
  content, editability, visual, requirements, file:
    {status: PASS | FAIL | UNVERIFIED, evidence: [paths], notes: string}
}
requirements: [{id, status: PASS | FAIL | UNVERIFIED, evidence}]
findings: [{id, slide, object, severity, issue, remedy, status}]
authorized_differences: [{guard_difference, authorization_id, judgment}]
inherited_limits, remaining_work
```

PASS and PASS_WITH_AUTHORIZED_DIFFS are both deliverable pass states only when every required gate passes and no blocker remains. `PASS_WITH_AUTHORIZED_DIFFS` is a reviewer decision, never a rewritten machine result. Resolve every difference against its actual permission; if alignment cannot be established, the content gate is UNVERIFIED. It is permissible for the stricter guard to flag representational changes, such as equivalent text segmentation, but a human/agent review must establish equivalence in context, with evidence.

Each repair produces a new candidate hash and invalidates previous approval. Do not edit the file after its passing review; copying a byte-identical file into deliverables preserves the hash. A fallback assembled from previous and original slides is also a new candidate and needs review.

`slide_actions` may include `reference_layout_id`. Keep the reference's OOXML shape IDs separate from the target backend's object IDs. Supported machine edits use a separate `operations.json` bound to the source SHA-256 and expected object geometry; see [backend guide](backend-guide.md). A backend rejection is a failed operation, not an implied content authorization.

The structured backend's own report may also be named `execution.json`, but its fields are not this complete workflow handoff. Preserve it as raw backend evidence and link it from the Executioner's workflow record. Likewise, `plan.json` is not accepted as `operations.json`.

## Resumption and handoff validation

These checks are Planner procedures today; an adapter may automate them without weakening the gates.

1. Read the run's request, plan, state and pending questions. Reuse recorded answers and authorizations; never broaden them during recovery.
2. Verify the source against its original hash. Locate the candidate named by state or the latest complete execution record and recompute its hash. Missing or mismatched files are unresolved evidence.
3. Reconcile interrupted work before dispatching again. If an edit finished but its response was lost, inspect existing outputs and checks; do not repeat the edit blindly or overwrite its files.
4. Accept a review only for the exact candidate/hash it names. Required gate and requirement results must be present and supported by accessible evidence. A process exit, partial JSON or free-text claim is insufficient.
5. If required questions remain unanswered, keep dependent work pending. If checks failed, identify an actionable repair or concrete blocker. Save `next_action` before returning control.
6. If a passing candidate already exists, verify byte identity during packaging and resume delivery. A changed candidate returns to review.

Use UTC timestamps to distinguish events, not to expire questions or impose a workflow deadline. Future transports should attach a unique handoff ID and run ID to detect stale or duplicate results; these are adapter metadata, not fields accepted by the existing backend operation parser.

## Delivery

Successful output: `deliverables/improved.pptx`, a matching contact sheet or PDF preview, and `deliverables/change-report.md` linking to the review evidence. Include changed slides, fulfilled user features, scoped content changes (if any), inherited raster/unsupported objects and remaining limitations. Keep asset sources and edit scripts/logs under the run directory so the professor can reuse them.

Local runs have no workflow time-based cancellation or delivery cutoff. If the user stops work or a concrete blocker prevents completion, identify any already reviewed candidate and its remaining limitations. If none exists, retain/return the original plus the plan and findings. Mark unreviewed build files as drafts and keep them outside final deliverables. Never describe this fallback as completed improvement. A demo slot ending does not automatically stop the local run or weaken its checks.
