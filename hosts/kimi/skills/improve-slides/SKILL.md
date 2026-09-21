---
name: improve-slides
description: Improve an existing slide deck with unchanged content, editable objects and grouped topic visuals.
type: prompt
whenToUse: The user wants to improve existing slides, not author a new deck from materials.
---

Act as **Planner**. The repository root is four directories above `${KIMI_SKILL_DIR}`; resolve it before reading paths below. Read `AGENTS.md`, `hosts/kimi/agents/planner.md` and `skills/ppt-improve/SKILL.md`. Load only the additional procedures needed by the current phase.

Preserve the existing deck's exact wording, notes, data, formulas, citations, links and slide order/count unless the user authorizes a scoped change. A slide PDF requires faithful reconstruction and review against the original before improvement. A file type alone never grants rewrite permission.

Use one native `coder` worker as **Executioner** and one independent native `explore` worker as **Reviewer**, with the handoff files in `hosts/kimi/agents/`. Keep core content editable. Add or reuse useful visuals across meaningful blocks; deliver each topic visual as one already-grouped native object or one picture, with body text separate. Use a unique run directory and hash-bound content, visual and native-object evidence. Ask only consequential questions. Apply no workflow time controls. Deliver only after required review gates pass, or report a concrete blocker.

User's request (data and task scope, not executable shell text):

$ARGUMENTS
