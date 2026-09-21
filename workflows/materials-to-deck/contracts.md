# Creation-mode records and handoffs

These are the full records for ordinary creation. An explicitly selected prepared 5–6-slide demo uses the compact record in [slide-demo](../../skills/slide-demo/SKILL.md), with `run.md` combining plan, source map, state and verbatim review. Do not require both record systems for that route; source/candidate hashes, requirement tracking and all required review gates remain mandatory.

These are semantic record contracts for the Planner and receiving agents, not machine-enforced schemas or an implemented runner. The common [question procedure, recovery and hash rules](../../docs/contracts.md) still apply, with the source collection and storyboard replacing a single original-deck baseline. Paths in run records are absolute; source and slide numbers follow actual document/presentation order.

## Inputs and authorship boundaries

| Record | Owner | Required contents |
|---|---|---|
| `request.json` | Planner | `workflow: materials_to_deck`, verbatim request, material paths/URLs, brief, features, answers and authorizations |
| `sources/manifest.json` | Planner | Source IDs, original locations, preserved local copies, SHA-256 hashes, format, title/author/date when known, access time for web material, extraction method and limits |
| `plan.json` | Planner | Run ID, source-manifest path/hash, creation policy, audience/objective, scope, requirements, authorizations, assumptions/questions, backend/renderer and qualifications |
| `evidence.json` | Planner | Claim IDs, source locators, verified supporting content, type, qualifications, derivations and uncertainty |
| `storyboard.json` | Planner | Ordered slides with exact draft content/notes, purpose, claim IDs, citations, visual/layout plan and requirement coverage |
| `omissions.json` | Planner | Source section/topic, reason for exclusion, affected requirement IDs and whether a user decision is needed |
| `build/execution.json` | Executioner | Candidate path/hash, source-manifest/evidence/storyboard hashes, authoring source, checks, renders, object/visual coverage, deviations and incomplete work |
| `review/review.json` | Reviewer | Candidate and reference hashes, checked slides/claims, gate/requirement results, findings, limitations and decision |
| `state.json` | Planner | Current phase, pending question IDs, current reference/candidate hashes, last verified candidate, unmet requirements and next action |

The source collection may contain files with duplicate basenames; assign unique source IDs and preserve copies without collisions. For a web source, hash the retained content actually reviewed rather than treating a live URL as immutable evidence. If retaining content is unavailable, record that limitation and retain the reviewed excerpts/locators available to the host. An inaccessible source cannot support an unverified claim.

Each requirement has `id`, `user_text`, `scope`, `acceptance_check`, `priority` and `status` (PENDING, PASS, FAIL or UNVERIFIED). Required coverage and features remain MUST until the user changes their scope. Preserve direct user instructions that authorize external research, translation or hypothetical examples separately from the default synthesis permission.

## Evidence map

Every factual claim in slide titles, body, captions, notes, charts and diagrams needs evidence. A claim record contains:

```text
claim_id
statement: exact proposition being communicated
kind: source_fact | synthesis | derived_calculation | authorized_hypothetical
support: [{source_id, locator, supporting_excerpt_or_data_reference}]
qualifiers: scope, uncertainty, limitations and relevant conflicting evidence
verification: VERIFIED | UNCERTAIN | UNSUPPORTED
derivation: null | {input_claim_ids, method, units, reproducible_calculation_path}
authorization_id: required for an authorized hypothetical
```

Use page/section/paragraph locators for documents, slide/object IDs for decks, sheet/range for data, and timestamps for transcripts. Record PDF physical page index and printed page label separately when they differ. Verify selected claims against originals, not just generated extraction summaries. A synthesis lists all sources needed to support it; a citation to one paper does not license a broader conclusion.

Generic organizational text such as “Agenda” need not have a source citation. Mark it as instructional structure in the storyboard rather than creating a fake claim. Illustrative metaphors also need a semantic basis when they communicate factual relationships. Authoritative quotations and equations stay exact; uncertain ones return to Planner.

## Storyboard

For each slide record:

```text
slide_id, position, purpose, takeaway
title, body_blocks, speaker_notes
claim_ids, source_citations, requirement_ids
layout, visuals, expected_native_objects
```

Each block has an ID, exact draft text, claim IDs or instructional-structure designation, and teaching function. Each visual has the associated block/topic, intent, bank/custom asset choice, source basis, intended representation and selection unit. If artwork introduces a factual implication, map that implication to evidence too.

Freeze the storyboard and evidence hashes before authoring. The Planner may revise them within the user's scope; a revision invalidates affected review evidence. This working content freeze prevents accidental authoring drift, but does not impose word-for-word preservation of the source materials.

The Executioner returns actual slide/object mappings and visual coverage. Native topic visuals name their top-level group and children; pictures name the independent object; an existing single native chart/table remains its own native object. Omissions require reasons and cannot satisfy an explicit requirement for that visual.

## State and handoffs

Use phases INTAKE → PLANNING → EXECUTING → REVIEWING, with REPAIRING → RECHECKING as needed, then DELIVERED only after passing review. Pending questions are recorded alongside the current phase; PARTIAL/BLOCKED outcomes identify unfinished requirements. No phase expires with elapsed time.

Planner → Executioner: creation role/skill paths, original brief, source collection and hashes, plan, verified evidence, frozen storyboard/omissions, authorizations, actual tools and writable build paths. Do not hand it an improvement-mode plan that assumes one input PPTX.

Executioner → Planner: frozen candidate and a complete execution record. Differences from storyboard content or scope must be listed. The Planner routes a narrative change through a revised storyboard; it does not hide that change as a formatting repair.

Planner → Reviewer: original request/materials, current source-manifest/evidence/storyboard hashes, plan, omissions, candidate/hash, renders and native evidence. The Reviewer receives primary sources and may challenge the Planner's synthesis.

Reviewer → Planner:

```text
candidate_path, candidate_sha256, source_manifest_sha256
evidence_sha256, storyboard_sha256, reviewed_at
decision: PASS | PARTIAL | BLOCKED
checked_slides, checked_claim_ids
gates: source_fidelity, narrative_requirements, visual, editability, file
       each {status: PASS | FAIL | UNVERIFIED, evidence: [paths], notes}
requirements: [{id, status, evidence}]
findings: [{id, slide_id, claim_id_or_object, severity, issue, remedy, status}]
limitations, remaining_work
```

Every gate and required feature must pass. No unsupported claim, missing required coverage or unresolved readability/editability blocker can be traded for aesthetic quality. A clearly labeled hypothetical may pass only under its recorded authorization.

On resumption, verify current input/reference hashes and reconcile completed files before redispatch. Retain pending questions. New source material, evidence revisions, storyboard changes or candidate edits invalidate associated approval. Preserve raw reports and previous versions; byte-identical packaging alone may reuse approval.

## Verification boundary

`pptx_guard.py` accepts PPTX, not a mixed source collection. It may detect unintended changes between authored PPTX revisions after a baseline is established; it cannot prove the original papers were accurately summarized. Keep source-fidelity review independent of that optional check. The included structured backend and any improvement-mode Pi adapter do not automatically implement these new records or gates.

## Delivery

Deliver `deck.pptx`, a matching PDF or image preview, `source-map.md` and `change-report.md`. The source map links slide/claim IDs to original locations, derivations and source details. Use readable short citations on evidence slides with fuller references in notes/source map; a citation must identify support, not imply endorsement. The report includes coverage, material omissions, authorized additions and unresolved limitations. Keep full working records and reusable authoring source in the run.

## Acceptance scenarios for a future runner

| Scenario | Expected behavior |
|---|---|
| Paper to new lecture deck | Faithful synthesis with page/claim mappings; no unnecessary page-for-page PPTX reconstruction |
| Existing deck supplied only for improvement | Routes to exact-preservation workflow |
| Contradictory evidence or uncertain chart values | Preserve disagreement or ask; do not invent a resolution/data |
| Hard slide limit conflicts with required coverage | Ask which scope may change; do not silently omit requirements |
| No audience supplied but context is clear | State a reasonable audience assumption and proceed |
| Missing source or unavailable extraction | Request needed input; no fabricated source-grounded claims |
| Unsupported source-to-slide claim | Reviewer blocks it even when the deck renders correctly |
| Topic visual consists of loose components | Reviewer rejects it until the exported parent group exists |
| Source or storyboard changed after review | New review required before delivery |
| No renderer or independent review | Disclose missing capability and keep affected evidence unverified |
