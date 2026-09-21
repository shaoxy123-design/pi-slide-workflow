---
name: ppt-visuals
description: Use when adding an illustration, data figure or comic to improve an existing lecture slide under an explicit content policy.
---

# Illustrations, figures and comics

Read the run's visual actions and [shared rules](../../AGENTS.md). Default to proactive coverage of meaningful topic blocks. Use [the visual bank](../../docs/visual-bank.md) to find reusable native recipes or actual artwork, then verify the match against the block's source wording. Aim for a recognizable visual idea for each block; an existing informative visual can already satisfy it. If a visual would mislead, repeat another visual without benefit, or make content unreadable after layout attempts, record that reason. Explicitly requested block visuals cannot be quietly omitted.

Identify what the block is doing before choosing an asset: teaching/learning may suit a book-and-learner scene; configuration may suit an agent with task tiles; verification may suit a document under inspection. Processes require source-supported sequence, and evidence requires supplied data. These are candidates, not automatic analogies. Favor a coherent visual vocabulary across the slide while differentiating each block's meaning. A colored badge alone is insufficient for a requested topic illustration.

| Visual | Use it for | Editable implementation |
|---|---|---|
| Illustration | A concrete object, setting or already-described concept | Separate replaceable artwork; native title/captions |
| Figure | Quantitative evidence or a relationship explicitly supported in the deck | Native chart with supplied data or editable diagram with supported labels |
| Comic | A sequence, contrast or interaction already present in the material | Separate character artwork; native panels, bubbles and text |

Preserve content and meaning. No invented data, causal arrows, examples, dialogue, conclusions or numerals. Under the content lock, move existing wording into native captions/bubbles only when its context and reading order are retained; do not duplicate, rewrite or delete it. An uncaptioned illustration can improve appeal without new factual text. Ask the Planner before adding new explanatory copy or an analogy that changes the lesson.

Use the host's available image-generation or image-search tools for illustrative artwork. If the host provides a relevant image skill, load it for the asset task only. Specify subject, academic tone, aspect ratio, placement, empty space, palette, and **no text/numbers**. Inspect every image for misleading content, garbled symbols and unwanted labels. Keep diagrams and data charts native; never use an image model to generate evidence values.

Batch assets with a consistent style and do independent layout work while a supported tool processes artwork. Local runs have no asset cap or timed image-generation cutoff. If a tool fails or is unavailable, use suitable user-supplied assets with known provenance where they satisfy the request; otherwise report the limitation. Required comic/illustration requests remain incomplete if omitted.

Record source URL or generation prompt, asset path, tool/source, intended slide, any usage terms known, alt text and editability class in `assets/manifest.json`. Do not claim unknown licensing. Keep factual-image citations where required; preserve original notes and record any authorized appended attribution. Save images separately so the professor can replace them.

For reusable native recipes, record the bank ID, recipe/version or file hash, palette, bounding box and actual parent/child names in `visual-coverage.json`. Package each topic visual as one already-grouped native object before delivery. The user should select once to move or resize it and enter the group only to edit details. Use one separate picture for raster artwork. Do not leave loose components, deliver merely groupable parts, or delegate grouping to the professor. Keep body text separate; labels belonging to a native diagram may join its group. Separate pictures remain croppable and replaceable. Retain their source files. Neither a single SVG image nor a bitmap is automatically component-editable.

Verify adjustment in the exported file, not just the authoring model. Some exporters add grouping locks to native shapes. Use the bank's grouping finalizer, scoped to exact recipe names, to create the actual group and handle necessary restrictions. Preserve unrelated source protections. Inspect parent-child structure and test moving/resizing existing groups without first assembling them; then check native child edits on a disposable copy in the target editor. If grouping is unavailable, report the capability gap rather than passing loose components.

Reuse a verified bank entry before generating an equivalent asset. Add a new reusable entry when no suitable match exists and the result generalizes beyond this deck: include topic tags, block types, semantic use, misuse cautions, provenance, representation, actual recipe/asset and a preview. Keep client logos, portraits and confidential slide content out of the generic bank. Search results and prompts alone are not completed visual assets.

If every part of a visual must be object-editable, use appropriate native elements or genuinely editable vector components supported by the backend. Do not relabel a bitmap or unsplittable SVG as fully editable. If the available capabilities cannot satisfy the scope, return that conflict to the Planner.
