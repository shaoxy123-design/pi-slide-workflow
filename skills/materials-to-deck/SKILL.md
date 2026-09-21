---
name: materials-to-deck
description: Build a new editable slide deck from supplied papers, reports, notes, data or other materials using faithful synthesis, source mapping and independent review. Use for new-deck authoring, not exact-preservation slide improvement or faithful PDF conversion.
---

# Build slides from materials

For an explicitly requested short demo of 5–6 new slides from one ready Markdown/text source, use [slide-demo](../slide-demo/SKILL.md) instead of the full procedure below. It preserves the required gates with compact records and prepared tools; ordinary creation continues below.

Read the [creation workflow](../../workflows/materials-to-deck/README.md), its [defaults](../../workflows/materials-to-deck/workflow.defaults.json) and [contracts](../../workflows/materials-to-deck/contracts.md). Keep repository-relative links anchored to their containing files. This skill is a procedure, not an installed generation tool.

1. Confirm the request is to author a new deck from materials. If the intent is existing-deck improvement, route to `ppt-improve`. Faithful PDF conversion uses the PDF reconstruction procedure. Do not silently choose synthesis when preservation was requested.
2. Act as [Planner](../../workflows/materials-to-deck/agents/planner.md). Preserve sources in a unique run; inspect the brief, materials and available host tools. Record requirements and use `question-me` for consequential ambiguity. State safe optional defaults and proceed within existing authorization.
3. Create the source/evidence map, omissions log and storyboard with exact draft content, citations, notes and topic visuals. Freeze its version/hash after required questions are resolved. Do not impose an extra outline approval unless requested.
4. Dispatch the [Executioner](../../workflows/materials-to-deck/agents/executioner.md) with the creation-mode plan and tools. It builds native editable content, grouped topic visuals, matching renders and object evidence. The supplied narrow improvement backend does not implement new-deck authoring.
5. Dispatch the independent [Reviewer](../../workflows/materials-to-deck/agents/reviewer.md) with original materials, evidence map, storyboard and frozen candidate. Review source fidelity rather than requiring original-material text equality. Repair concrete findings and recheck changed hashes.
6. Package the passing candidate with preview, source map and report. If no independent delegation, rendering or native inspection is available, disclose the limitation and leave affected gates unverified. Do not claim a completed deck without its required evidence.

Reuse the [visual bank](../../docs/visual-bank.md) and [question procedure](../question-me/SKILL.md). Keep exactly Planner, Executioner and Reviewer as logical roles. Local runs have no processing deadline, timed cutoff or fixed repair cap; a requested talk duration only shapes the presentation's content.
