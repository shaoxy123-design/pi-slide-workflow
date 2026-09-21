---
name: ppt-edit
description: Use when applying an agreed improvement plan to an existing PowerPoint deck while preserving content and editable objects.
---

# Edit the working deck

Read [shared rules](../../AGENTS.md), the run plan and [backend guide](../../docs/backend-guide.md). Work only on a copy in the run's build directory.

1. Reuse original slide objects, masters and theme where supported. Apply one style specification in batches. Preserve exact text, symbols, table cells, chart values/labels/data associations, notes and links. Keep slide count/order and unchanged-slide behavior intact.
2. Improve hierarchy, alignment, spacing, contrast and balance. Reposition/rescale objects without distorting evidence. Keep reading order, units, footnotes and qualifications legible. Dense content can use better column allocation and whitespace; do not silently summarize, shrink it into unreadability, or move it to notes.
3. Keep text, tables, charts and requested diagrams native. Retain editable equations and embedded data. An SVG or screenshot is not automatically an editable diagram. Preserve unsupported objects through a faithful backend or leave their source slide unchanged and report the limitation.
4. Load `ppt-visuals` for the planned topic-block visual pass. Use existing source figures and data where possible and consult the reusable bank. Recompose around meaningful visuals while preserving every required word. Deliver each topic visual already packaged as one top-level native group or single separate picture. Keep diagram labels native inside the group and body text outside it. Record parent/child names; never leave the professor to assemble loose components. Do not merge pictures into a slide background or bake required text into artwork.
5. Track every change by slide/object and requirement ID. Record inherited image-only elements and any authorized content differences separately. Preserve existing notes; keep workflow commentary out of slides and notes. Store provenance separately unless adding a citation is required, in which case record that explicit additive exception.
6. Export a complete candidate early, render it, and run `pptx_guard.py compare`. Check readability at presentation size, overflow and objects outside the canvas. Fix build defects before handing off. Passing machine checks does not approve the deck.

Hand off the whole candidate when export and execution checks are ready. Do not edit while the Reviewer assesses it. For each repair, change what the findings require, then regenerate affected renders and the full comparison. Never overwrite a passing version with an unreviewed one. Returning to the original slide is a valid fallback, but any reversion creates a new candidate requiring recheck; disclose incomplete improvement requirements. No timed cutoff or fixed repair limit applies locally.

For PDF input, follow [PDF intake](../../docs/pdf-input.md). Reconstruction needs a capable host backend and independent comparison against the PDF; the included PPTX adapter is not a PDF converter.

Include candidate path/hash, changed slides, content differences, assets, source/edit log, renders, guard report and unresolved issues in `execution.json`.

For supported formatting operations, use the structured backend described in [backend guide](../../docs/backend-guide.md). Bind operations to the source hash, observed object IDs and expected geometry. Run inexpensive geometry checks during execution and inspect affected-slide renders before handoff. Reject unsupported operations; do not turn a failed qualification into permission to rebuild or flatten the source.
