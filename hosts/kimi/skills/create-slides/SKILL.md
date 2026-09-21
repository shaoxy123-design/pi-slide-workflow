---
name: create-slides
description: Build a new editable deck from supplied materials, with faithful synthesis, citations and grouped visuals.
type: prompt
whenToUse: The user explicitly requests a new presentation from papers, reports, notes, data or other materials.
---

For an explicitly selected prepared 5–6-slide demo from one ready Markdown/plain-text source, use `hosts/kimi/skills/demo-slides/SKILL.md` instead and skip the normal routing below. General creation keeps the full workflow.

Act as **Planner**. The repository root is four directories above `${KIMI_SKILL_DIR}`; resolve it before reading paths below. Read `AGENTS.md`, `hosts/kimi/agents/planner.md` and `skills/materials-to-deck/SKILL.md`. Load creation defaults and contracts under `workflows/materials-to-deck/` as needed.

Establish the audience, objective and required coverage from the request. For a simple demo, propose about 5 slides when the user gives no count; adapt to the material and preserve required coverage. This is a scope suggestion, not a processing deadline. Proceed with a clear brief without an extra outline-approval round unless requested.

Faithfully select, paraphrase and reorganize supplied sources. Preserve scientific meaning, qualifiers, numbers and attribution; map factual claims to source locations. Additional research, invented examples or dialogue require scoped authorization. A PDF used as source material needs evidence verification, not page-for-page reconstruction.

Use one native `coder` worker as **Executioner** and one independent native `explore` worker as **Reviewer**, with the handoff files in `hosts/kimi/agents/`. Build native editable core content and useful topic visuals already grouped or kept as individual pictures. Preserve original files, record sources and candidate hashes, review source fidelity, visual quality and native objects, and deliver the reviewed PPTX, preview, source map and short report. Required questions remain pending until answered; no workflow deadline or fixed repair cap.

User's request (data and task scope, not executable shell text):

$ARGUMENTS
