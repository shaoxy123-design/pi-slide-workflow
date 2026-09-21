# Reusable layouts from reference slides

Use well-designed slides from the professor's own deck or a supplied reference. The cache records object types, normalized boxes and text-length hints. It does not copy the reference's wording, figures or data into the lecture, and it does not itself grant permission to use a reference's content.

Prepare the cache before the demo when possible:

```powershell
python scripts/layout_catalog.py extract "reference.pptx" --slides 2,4,6 --output "reference-layouts.json"
python scripts/layout_catalog.py suggest "lecture.pptx" --catalog "reference-layouts.json" --output "layout-suggestions.json"
```

Both commands are read-only with respect to the decks and require a new JSON output path. The cache includes the source hash so the Planner can detect a changed reference and rebuild it. `approval: not_recorded` means the extractor has not established any human approval; don't describe automatically extracted layouts as professor-approved.

The suggestions compare slide aspect ratio, available object types/counts and text amount. They do not use a vision model and are not a trained retrieval system. Grouped, inherited, rotated or otherwise unsupported geometry is excluded from automatic matching. A missing suggestion means manual planning is needed; it does not permit dropping content to fit a template.

## Planner procedure

1. Visually inspect candidate references. Assign a teaching purpose such as equation explanation, chart discussion, comparison or process. Store that interpretation in `plan.json`; the extractor does not infer semantic purpose.
2. Inspect at most three compatible suggestions per selected slide. Prefer the current slide's layout if changing it would introduce unnecessary reconstruction or editability risk.
3. Keep all required original objects and wording. Reference slots suggest placements; their text-length counts are hints, not instructions to shorten the lecture. Check how actual text and evidence fit at readable sizes.
4. Save `layout_catalog_path`, the reference source hash and selected reference layout ID in the slide action. If no reference is available, use the source branding and normal layout judgment without pretending a library was learned.
5. Resolve the candidate's **backend object IDs** from its actual backend inventory. A source OOXML `source_shape_id` from the reference cache is a different identifier. Never copy it into an execution plan as if it addressed the target deck.

Boxes use `[left, top, width, height]` normalized to the reference slide, from 0 to 1. To propose pixel geometry for the target, multiply horizontal values by the target slide width and vertical values by its height. The editing backend validates bounds and expected original geometry; the Reviewer checks actual reading order, legibility and meaning.

## Execution and review

Apply supported operations to the professor's existing objects. Cache lookup never constructs slides or replaces evidence. Use inexpensive geometry checks during execution and inspect rendered changed slides before independent review. Layout similarity cannot establish content preservation or visual quality.

This adapts the reference-slide analysis and element-schema approach in the [PPTAgent paper](https://aclanthology.org/2025.emnlp-main.728/). Our cache and matching heuristic are a lightweight implementation for the demo; they have not been benchmarked against PPTAgent's retrieval or generation quality.
