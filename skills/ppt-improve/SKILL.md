---
name: ppt-improve
description: Use when improving existing slides through the Planner, Executioner and Reviewer workflow while preserving content and editable PowerPoint output.
---

# PPT improvement workflow

Read [shared rules](../../AGENTS.md), [defaults](../../workflow.defaults.json), and the [Planner role](../../agents/planner.md). Resolve repository references relative to this file; keep the project together.

For a new host, bind capabilities with the [host adapter contract](../../docs/host-adapter.md); Pi setup is in [Pi integration](../../docs/pi-integration.md). These are integration instructions, not installed tools. A request to develop the workflow itself uses the [development handoff](../../docs/agent-handoff.md) rather than starting a deck run.

1. Create a unique run directory and immutable source copy; record its SHA-256. Load `ppt-plan` to inspect, clarify and write the compact plan. Do not wait for an additional approval when the request already authorizes the planned edits. Record elapsed time only if useful; it never controls local execution.
2. Confirm the editing and rendering tools are usable. A no-edit round trip on a copy should preserve content and special objects. Resolve missing capabilities within the host's permissions or report the specific limitation. For a demo, prepare and qualify the backend beforehand.
3. For PPTX input, establish the baseline with `scripts/pptx_guard.py snapshot`. Save baseline renders and inspect source native objects, especially equations, charts, images containing text and animations. For PDF input, first follow [PDF intake](../../docs/pdf-input.md): independently qualify reconstruction against the original PDF before establishing a PPTX baseline. The baseline alone does not prove editability or PDF conversion fidelity.
4. Delegate to the Executioner using [handoff contracts](../../docs/contracts.md). It loads `ppt-edit` and `ppt-visuals` when applying the default block-level visual pass; explicit requests without visual work may skip the latter. Include planned block coverage and bank selections. While it works, the Planner may prepare report paths and requirements, but never concurrently write the deck.
5. When a complete candidate, renders and execution log are ready, delegate independent assessment to the Reviewer using `ppt-review` and the original request. The Executioner must not continue editing during review. No passing evidence means no final label.
6. Send actionable findings to the same Executioner for repair and recheck the actual repaired candidate. Continue until required checks pass or a concrete blocker prevents progress. Do not repeat unchanged failures or keep polishing already-passing optional details. Preserve the last verified version and report unresolved required work honestly.
7. Before delivery, verify the source hash still matches and the review hash matches the final PPTX. Deliver `improved.pptx`, a preview, and a brief change/review report; retain assets and edit source in the run directory.

Local runs have no workflow deadline, timed phase transitions, fixed repair cap or automatic time-based cancellation. Demo duration is a presentation constraint, not a workflow acceptance gate.

Only three roles are needed. If the host cannot spawn agents, use labeled sequential role passes and disclose the lack of independent review. Refer to [the demo runbook](../../docs/demo-runbook.md) only when preparing or presenting the demo.
