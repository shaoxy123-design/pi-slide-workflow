---
name: ppt-plan
description: Use when planning improvements to an existing PowerPoint deck, choosing slide scope or resolving content and editability requirements.
---

# Plan slide improvements

Read [shared rules](../../AGENTS.md) and [contracts](../../docs/contracts.md). Inspect the actual deck and request before proposing changes.

1. Identify source format. For PDF, follow [PDF intake](../../docs/pdf-input.md) before invoking PPTX scripts. For PPTX, inventory slide count/order, hidden slides, text, notes, tables, charts/data, equations, hyperlinks and embedded media. Inspect representative renders and every slide selected for structural work. Identify inherited raster content and unsupported objects; separate limitations from proposed changes.
2. Translate the request into requirement IDs with exact user wording, selected slides, MUST/SHOULD/MAY priority, acceptance checks and CLEAR/ASSUMED/BLOCKED status. Explicitly requested features default to MUST. Default content policy is `preserve_exact`; permissions name exact objects and allowed changes, not an unrestricted rewrite flag.
3. Use `question_me` for missing decisions that affect correctness, scope, permission or feasibility. Resolve critical questions before dependent work. For optional style questions, recommend a default and continue independent work. Do not re-ask answered questions.
4. Plan improvements across the user's selected slides, all slides by default. Use an aggressive topic-by-topic visual pass: identify meaningful blocks (objective, claim, comparison, process, evidence, takeaway), their exact source text and teaching function. Consult the [visual bank](../../docs/visual-bank.md). Plan a distinct relevant visual for each block where it improves comprehension or recall; retain existing useful visuals and explain omissions. Recompose to make room before dropping a useful visual. Do not treat every line as a separate block, nor apply an arbitrary icon quota. Explicit requests for visuals in each block are MUST requirements. Keep captions native and reuse existing wording; never delete content to fit artwork.
5. Record style once: follow supplied branding; otherwise use readable academic typography, strong contrast, consistent margins and ample space. Choose one edit backend and renderer from available tools. Preserve complex native objects instead of recreating them for style.
6. Write `plan.json` and `state.json`, including source hash, selected slides, requirement/authorization lists, proposed actions, inherited limits and tool paths. Include `visual_blocks` with topic, teaching function, source text/object references, visual choice, semantic basis and coverage intent. Require one already-grouped native object or single picture per topic visual, with an actual selectable parent in delivery evidence. State the compact plan to the professor and proceed within existing authorization. Do not add local workflow deadlines or timed cutoffs.

Local runs have no implicit slide, asset or repair-round cap. Plan batches for larger decks while preserving the full requested scope. The 5–10-slide suggestion belongs only to demo preparation. If unreadable source data prevents a faithful editable reconstruction, ask for source data or confirmation of flagged values; never guess.

Every new user instruction updates the affected requirement and invalidates related plan/review evidence. Carry accepted decisions across agent handoffs and context changes in `state.json`.

For reusable reference layouts, use `scripts/layout_catalog.py` following [reference layouts](../../docs/reference-layouts.md). Inspect up to three advisory matches and record the chosen layout; text capacity never authorizes shortening. Resolve execution object IDs from the actual backend inventory, not the reference's OOXML shape IDs. Require per-source backend qualification before editing.
