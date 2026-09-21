# Host adapter contract

This document describes how another agent host should execute the workflow. The capability names below are **conceptual interfaces**, not functions exported by this repository. The shipped utilities retain their own CLI and report formats.

## Bind capabilities before editing

Record the actual tools, executable paths, versions and qualification evidence in the run plan's `backend`, `renderer` and `tool_constraints` fields. Do not copy a Codex tool name or a previous machine's path into Pi and assume it is available.

| Capability | Input | Result/evidence | If unavailable |
|---|---|---|---|
| Inspect source | Source path/hash | Slide order, content baseline, object inventory, source renders | Pause work that depends on missing source facts |
| Ask professor | Contract question IDs and scope | Answered/pending records; scoped authorization only when actually given | Use conversation; keep required questions pending |
| Dispatch role | Role file, compact handoff, permissions, output paths | Session/task ID and completion or failure evidence | Disclose sequential fallback and lack of independence |
| Edit/export | Qualified source, plan, authorizations | New candidate, hash and edit source/log | Qualify another method or report the specific blocker |
| Render/inspect visuals | Frozen candidate/hash | All slide previews plus readable inspection views | Visual gate remains UNVERIFIED |
| Inspect native objects | Frozen candidate/hash | Object types, content/data, groups and interaction evidence | Editability gate remains UNVERIFIED |
| Check content | Original baseline, candidate, original source | Unmodified machine report plus adjudication of differences | Content gate remains UNVERIFIED |
| Package | Passing review and exact candidate | Byte-identical final PPTX, matching preview and report | Keep the candidate as a draft |

Permission enforcement is a host responsibility. Prompts establish role ownership but are not a filesystem sandbox. A Reviewer with unrestricted shell execution can technically write files; do not describe that setup as enforced read-only access. Prefer a read-only source/candidate mount or restricted tools plus a report-only writer when implementing an adapter.

## Handoff protocol

Use the fields in [contracts](contracts.md#handoffs). The transport may be a subagent message, a separate process or an SDK session; the acceptance conditions are the same.

1. Planner resolves repository and run paths and passes the original request, scoped plan and immutable references. Workers do not depend on hidden conversation history.
2. Executioner writes uniquely named candidate/evidence files, computes the candidate hash after all edits, and returns an execution record. It stops writing that candidate.
3. Planner verifies the files and hashes before dispatching Reviewer. A successful process exit alone is not a complete handoff.
4. Reviewer reads the original request before the edit narrative and returns its own gate results. Missing evidence is UNVERIFIED. An Executioner report cannot double as the independent review.
5. Planner dispatches repairs with finding IDs and the exact input candidate. Every repair is still checked against the original source baseline.
6. Planner verifies the passing review hash against final output bytes before marking DELIVERED.

Keep rich evidence on disk; return its paths and a concise result through the host. Truncated messages do not excuse missing evidence. A future adapter should reject stale/cross-run handoffs and use unique handoff IDs to avoid duplicate dispatch after an interruption. These checks are currently Planner procedures, not an implemented scheduler.

## Runtime boundaries

- **Editor:** qualify one backend for the actual source, including a no-edit round trip. A library that generates a new PPTX does not necessarily preserve an existing one.
- **Renderer:** choose one rendering application/engine for comparable source/candidate previews. A PDF rasterizer can expose its exported pages for inspection; it does not replace PowerPoint-native evidence.
- **Images:** use an actual available generator, existing suitable artwork or native recipes. If a requested visual requires an unavailable capability, record the unmet requirement rather than silently downgrading it.
- **Native groups:** the visual must already have a selectable parent. Testing by grouping loose shapes first proves the wrong behavior. Move/resize the delivered parent and test editable children on a disposable copy.
- **Paths:** derive the repository root at runtime. Resolve Markdown links relative to their containing file, CLI paths relative to the declared working directory, and run-record paths to absolute paths. Keep the repository together.
- **Operations:** `plan.json` is the semantic plan; `operations.json` is the narrow backend's validated edit instruction set. They are not interchangeable. Its `execution.json` is a backend report; the Executioner must supply the workflow handoff fields separately or link it as evidence.

## Adapter acceptance scenarios

Before claiming a new host adapter works, demonstrate these behaviors with synthetic fixtures and then a representative real deck:

| Scenario | Required observation |
|---|---|
| Clear formatting request | Proceeds under existing authorization; source remains unchanged |
| Shorten bullets + exact preservation | Required question is persisted; dependent rewrite waits |
| Question dialog dismissed or headless | No fabricated answer; resumption preserves pending question |
| Visual for each topic block | Coverage matches actual exported groups/pictures; body text remains readable |
| Loose components supplied as final | Review rejects the missing parent object |
| Candidate changes after review | Packaging refuses the stale approval |
| Worker crashes or returns malformed report | No final label; existing evidence is retained and next action recorded |
| Restart after completed edit but lost response | Existing files/hashes are reconciled before a new edit is dispatched |
| No renderer or no independent reviewer | Missing capability and affected gates are disclosed |
| PDF source | Separate conversion evidence is required before improvement |

Use exactly the three logical roles throughout. Do not copy an upstream four-agent scout/planner/worker/reviewer chain into this workflow.
