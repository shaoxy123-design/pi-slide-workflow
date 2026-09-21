# Topic visuals and reusable blocks

The public visual bank supplies 25 original native drawing recipes and their previews. It helps the three existing agents reuse useful visual ideas; it does not introduce another agent, image service or automatic slide designer. The catalog also supports separate artwork when a local run supplies it with appropriate provenance. Private generated artwork and its local catalog are excluded from this release. See [attribution and release contents](../NOTICE.md).

Default to a visual pass across the meaningful blocks on selected slides. A block can be an objective, claim, process, comparison, evidence figure or takeaway. Identify its topic and teaching function before searching. Add a visual when it helps a reader recognize or remember that idea; retain informative source visuals. Make room through composition, not deleted text. Specific instructions such as “add a visual to each block on slide 3” are required coverage. A user request for fewer or no new visuals overrides this default at its stated scope.

## Find and use

The catalog is `visual-bank/catalog.json`. `scripts/visual_bank.py` searches local metadata without an API, network request or model call:

```powershell
python scripts/visual_bank.py search "teaching learning"
python scripts/visual_bank.py search "agent setup" --block-type objective
python scripts/visual_bank.py batch runs/demo/visual-blocks.json --limit 3
python scripts/visual_bank.py validate
```

Search is lexical and advisory. Inspect the returned preview, `semantic_use` and `avoid_when`, then compare them with the source block. A match does not authorize a new analogy or claim. No match means the Executioner can compose suitable native elements or use the host's actual image tools. It does not require a question unless meaning, content permission or feasibility is unclear.

Use the actual private run path for batch input. [Fast local decisions](fast-decisions.md) documents its small JSON format and no-match handling. Batch output contains compact metadata; resolve previews and drawing recipes from the catalog before use. Reuse an already suitable supplied visual idea instead of searching again.

Each native entry points to a real module/export/recipe ID. Use the module's documented function signature to draw the visual, then package its components as one top-level native group. Deliver that group already assembled: the professor selects once to move or resize the visual, and enters the group only to edit details. Keep body text separate; labels belonging to an evidence diagram may join its group. Preserve aspect ratio, line weight and component relationships. A rendered preview is only for selection, not the editable recipe.

Use `visual-bank/group_components.py` according to the native entry's `recipe.post_export` instructions. The finalizer packages exact named components into actual native groups while preserving their appearance. It handles the exporter-added grouping restrictions on those components and retains unrelated source protections. Never leave loose pieces merely because they could be grouped later.

Save one group specification per visual, using the exact names returned by the recipe:

```json
[{"slide": 3, "group_name": "Topic - AI in learning", "child_names": ["recipe-part-a", "recipe-part-b"], "kind": "illustration"}]
```

Those two child names are schematic; resolve real names from the current build. Then package the exported draft:

```powershell
python visual-bank/group_components.py draft.pptx grouped.pptx --groups-json groups.json --report grouping-report.json
```

The output must be a new file. Supply exact component names and a stable parent name for each topic, following the helper's schema; do not group unrelated source shapes. Existing evidence diagrams may be grouped only with their own labels and with their original geometry/data preserved. The older `unlock_components.py` only removes a restriction; it does not complete grouped packaging and is not the default delivery path.

The helper resolves slide numbers in presentation order. Its current support covers unrotated native shape components; it rejects unsupported geometry rather than guessing. Source banners/evidence/text groups may need an explicit `insert_before` anchor to preserve stacking and text order. Record and visually inspect that choice.

In PowerPoint, test the delivered parent directly without first calling Group: move/resize it with one selection, save/reopen, and verify native child editing. Inspect every topic mapping for one actual top-level group or picture and reject loose fragments. Native object counts or a successful manual grouping test alone do not establish delivery usability.

An existing native chart or table is already a single selectable unit. Preserve it with its data and editability; the grouping default does not require rebuilding it as shapes or a picture.

Each image entry points to its source file with provenance. Insert it as an independent image object, retaining the file so the professor can replace it. The image can be moved, resized and cropped, while captions and required labels remain native text. Do not call its internal painted details editable.

## Choose the visual idea

| Block function | Useful starting point | Meaning to protect |
|---|---|---|
| Teaching or learning objective | Book, learner, relevant tool | Do not imply an unclaimed learning outcome |
| Configuration or setup | Tool/task modules around a system | Connections must not imply unsupported dependency or autonomy |
| Contrast with previous tools | Concrete source-relevant objects | Do not invent a historical sequence, ranking or causal arrow |
| Uncertainty or fluent output | Document/speech with an inspection cue | No fabricated probabilities or categorical correctness verdict |
| Reviewer judgment | Person examining a document | No legal verdict or claim of guaranteed accuracy |
| Process or interaction | Native steps or comic panels | Only the sequence and dialogue supported by source content |
| Quantitative evidence | Native chart/table from supplied data | Never substitute illustrative art for values or invent a scale |

These are selection heuristics, not mandatory metaphors. Avoid generic icon repetition that adds no distinction. Aggressive visual coverage means actively finding useful visual treatments; it does not mean a fixed number of images or covering every blank area. If a default visual cannot fit without harming readability after layout attempts, record a specific omission reason. An explicitly requested visual remains unresolved until satisfied or discussed with the professor.

## Extend and verify

Add an entry only when its actual recipe or asset and preview exist. Use a stable ID, topic tags, block types, semantic use, misuse cautions, representation, relative file paths and provenance. Declare `selection_unit: "native_group"` for native recipes or `"picture"` for artwork, and include the required grouped-export procedure for native recipes. For generated artwork retain the complete generation prompt and known tool/source; do not invent a license. For native recipes retain their source/version or file hash. Do not promote a client's logo, portrait or confidential content into the generic bank.

The read-only validator checks catalog structure, referenced files and any recorded asset hashes. It does not prove visual quality, licensing or native editability. Run the native recipe through the actual backend, render it, and inspect its objects before relying on it.

For every run, record topic-to-visual decisions in `visual-coverage.json` according to [contracts](contracts.md). Bind coverage to the candidate hash and actual object names. The Reviewer checks meaning, readability, coverage and adjustment behavior against the real output. Search scores and asset counts never substitute for that review.
