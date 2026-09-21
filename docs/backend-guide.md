# Editing and verification backend

This workflow separates role instructions from the slide-editing tool. Select **one qualified backend and renderer** for the run. Local runs have no workflow time controls. The content guard uses only Python's standard library; it is not an editing backend. The included scripts accept `.pptx` only; [PDF intake](pdf-input.md) describes the separate reconstruction and review needed before using them.

## Included structured backend

`scripts/pptx_backend.mjs` implements a small artifact-tool adapter. Its current operations are:

| Native object | Supported operation |
|---|---|
| Text box | `move_resize`, `set_font_size` for the whole box |
| Bar chart | `move_resize` |
| Other objects | No edits through this adapter; source qualification determines whether they can remain unchanged |

It does not insert artwork, build new charts/comics, edit text, or support arbitrary PowerPoint objects. Those requests remain with the host's presentation/image capabilities and the existing skills. The adapter's conservative preflight rejects unqualified features such as editable equations, groups, animations, SmartArt, OLE, comments and some extensions. This protects the source; it does not mean those features are universally unsupported by PowerPoint or by other backends. Do not silently convert them to images to make this adapter accept a deck.

The source, plan, outputs and evidence paths must be distinct; output/report parents must exist and outputs must be new files. In Codex, resolve the bundled Node executable, `node_modules` directory and Python executable through `load_workspace_dependencies` when available. Other hosts must resolve their actual installed runtime paths; that Codex tool is not a portable dependency. The module directory must contain the required `@oai/artifact-tool` runtime. Use those resolved values as `$pptNode`, `$pptModules`, and `$pptPython` in PowerShell:

```powershell
& $pptNode scripts/pptx_backend.mjs inspect "source.pptx" --output "inventory.json" --runtime-modules $pptModules
& $pptNode scripts/pptx_backend.mjs apply "source.pptx" --plan "operations.json" --output "candidate.pptx" --report "execution.json" --runtime-modules $pptModules --python $pptPython
```

Environment alternatives are `RUNTIME_NODE_MODULES` and `RUNTIME_PYTHON`. The adapter does not install or modify dependencies. `inspect` is read-only and returns the actual backend IDs, supported operations, slide dimensions, current geometry, font size where known, and source SHA-256. Geometry is in pixels at 96 DPI; font sizes in plans are explicitly in points.

`operations.json` has exactly `version`, `source_sha256`, and `operations`. Each operation has exactly these common fields: `id`, `slide` (one-based), `object_id`, `op`, `expected_position`. Add `position` for `move_resize`, or `font_size_pt` for `set_font_size`. A position is `{left, top, width, height}` in pixels. Fill these fields from the actual inventory and inspected design plan; do not guess object IDs or reuse a source hash from another file.

The entire plan is validated before edits. Unknown operation/field/ID, stale source or expected geometry, invalid dimensions, duplicate operations and out-of-bounds target geometry are rejected. Content rewrites are not whitelisted even if another workflow has a scoped authorization; use a capable, separately qualified host operation for those changes.

Each `apply` performs source preflight, saves the untouched content baseline, exports an unedited copy and checks its content/native objects, then applies the plan. It exports and reimports the candidate, checks content and intended geometry/font changes, and renders before/after slides. The evidence directory is `<report path>.evidence/`. A failed check blocks delivery of the planned candidate. A successful adapter run returns **`draft_review_required`**; it is never an independent visual or PowerPoint editability approval.

Use the baseline hash and unchanged source throughout the transaction. A later repair needs a plan bound to the candidate it actually edits; the workflow must still compare the repaired final candidate with the run's original baseline. Never substitute an intermediate baseline for the original-content gate.

Exit code 0 means an inventory or draft was created; 1 means a source-feature, preservation or structural gate blocked the edit; 2 means an input/runtime error, including failure to run a check. Read the actual report and error rather than treating any output file as success. The adapter's geometry/font checks do not prove readable text fit, meaning, or visibility; its renders still require inspection.

To run the backend tests with the same resolved runtime paths:

```powershell
$env:RUNTIME_NODE_MODULES = $pptModules
$env:RUNTIME_PYTHON = $pptPython
& $pptNode --test tests/test_pptx_backend.mjs
python -m unittest discover -s tests
```

The backend tests generate a clearly labeled synthetic PPTX with native text, a bar chart and notes, exercise actual export/reimport and rendering, and check protected-source failures. They are not a real lecture-deck benchmark, nor a check in Microsoft PowerPoint. Inspect the reported before/after PNGs and preserve the qualification evidence in the private run folder.

## Codex default

Use the presentation capability and tools actually available in the Codex session. Read its presentation skill before editing a deck, and resolve bundled runtimes with `load_workspace_dependencies` when available. In the current workspace's bundled presentation guidance, the implementation uses JavaScript and `@oai/artifact-tool`; follow that installed guidance for imports, edits, export and rendering rather than assuming an API from memory.

A library that can create a new deck may not faithfully round-trip an arbitrary existing deck. Before the live demo, import and export a copy without edits and compare the result, including complex native objects. A failed preservation check means the backend has not qualified for that source. Choose another already available faithful editing method or preserve unsupported objects/slides; don't silently rebuild the whole lecture.

If a native PowerPoint interface is available, it can help preserve existing objects and demonstrate editability. Availability of shell execution alone does not establish access to a native PowerPoint editor. If using a bundled LibreOffice renderer under the presentation skill, resolve and use the bundled absolute path, not a user's installed desktop version, and include that constraint in worker handoffs.

## Portable host requirements

| Capability | Needed for |
|---|---|
| File read/write and a PPTX edit/export backend | Candidate construction using native objects |
| PowerPoint-compatible rendering and image inspection | Visual QA of actual exported slides |
| Native object/data inspection | Text/chart/table/equation/diagram editability evidence |
| Python 3 | Included read-only OOXML snapshot/compare helper |
| Delegation and follow-up tools | Independent Executioner and Reviewer; labeled sequential fallback if absent |
| User-input tool or conversation | Planner's `question_me` procedure |
| Image generation/search, or suitable existing artwork | Selected illustration/comic tasks |
| Optional elapsed-time measurement | Rehearsal and comparison reports; never a local execution gate |

Claude Code and other agent hosts can read the same role/skill files explicitly. Map delegation and clarification to the tools they actually expose. The repository does not install native agent registrations or require a particular model name. Keep the folder intact so relative skill references resolve.

See [host adapter contract](host-adapter.md) for capability bindings and failure/resumption behavior, and [Pi integration](pi-integration.md) for a concrete host mapping. Reusable CLI utilities and successful historical run scripts do not by themselves provide a portable orchestration or rendering adapter.

## Editability acceptance

- Required text appears as native text and remains selectable/editable.
- Required tables retain cell structure; charts retain their correct labels, series and source data. Inspect embedded workbook formulas as well as visible values when present.
- Existing editable equations retain their editable source/object representation. A rendered formula image is a regression.
- Required diagrams use native shapes/connectors/text or a verified editable representation. A single placed SVG is not proof of component editability.
- Artwork may be a separate replaceable image in the default mode. List raster text/figures inherited from the source. Full object-editability requests require a stricter plan and cannot pass with undeclared image-only evidence.
- Required animations, transitions, links, media, comments, alternative text and accessibility order need explicit backend-specific checks; do not assume import/export preserves them.

Use a disposable output copy for representative native edit tests. Record the application and object types actually tested. The reviewer still inspects all changed core objects; a single successful text edit cannot prove charts and equations editable.

## Content guard usage and limits

```powershell
python scripts/pptx_guard.py snapshot "source.pptx" --output "baseline.json"
python scripts/pptx_guard.py compare "baseline.json" "candidate.pptx" --source "source.pptx" --output "content-check.json"
```

The guard checks the OOXML content and relationships it inventories. Read the generated report's coverage and limitations. It allows normal formatting changes while flagging protected content differences; conservative asset checks may flag benign re-encoding. New artwork must also be inspected for visible text or semantic claims that XML checks cannot read.

Exit code 0 means the implemented checks passed; 1 means protected differences; 2 means invalid input or another check error. Any error is unresolved evidence. Always retain the raw report. Intentional user-authorized edits require the Reviewer's item-by-item adjudication; do not regenerate the baseline from the edited file or weaken the checker.

Known general limits include OCR of images, semantic correctness of new imagery, visual reading order, hidden/off-canvas text, every optional PowerPoint extension, animation behavior and full native editing in the user's application. Automated text/asset agreement cannot establish these. Rendered inspection, native-object checks and an honest feature report remain required.
