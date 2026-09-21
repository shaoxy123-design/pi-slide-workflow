# Slide workflows in Pi + GLM 5.3 Flash

Use **GLM 5.3 Flash as Planner** by default, or select **GLM 5.3**. Visual work always runs in independent **Flash** worker contexts. The same content, editability, grouped-visual and independent-review rules apply. We reuse the [local decision approach](../../docs/fast-decisions.md); no Jev model, API key or routing service is involved.

## Start

On another Windows PC, follow [NEW-PC.md](NEW-PC.md) first. With Pi installed and your GLM provider configured, open the whole repository in PowerShell:

```powershell
.\hosts\pi\start.ps1 -Check
.\hosts\pi\start.ps1
```

Then paste:

```text
/skill:demo-slides Use example_input/inventories-hkas2-knowledge.md to create 6 slides.
```

For ordinary work:

```text
/skill:create-slides Use examples/demo-materials.md to create 5 slides for university colleagues.
/skill:improve-slides Improve "C:/path/lecture.pptx"; preserve all content.
```

The launcher defaults to `-MainModel glm-5.3-flash`, provider `zai` and thinking `high`. Flash-only mode requires only that exact model in your catalog. To use GLM 5.3 as Planner and for content workers, pass `-MainModel glm-5.3` to both the check and launch commands; this mode requires both models. Start a new run when changing the main model. Use `-Provider zai-coding-cn` only if that is the provider you configured. `-Thinking` accepts `low`, `high` or `max`, but preflight also requires support in the installed SDK/model metadata. Pi 0.84.2's bundled GLM 5.3 entry clamps `max` to `high`, so use `high` with that metadata. Worker receipts record the selected SDK level; provider-side application remains unverified until rehearsed. `-PiPath` and `-PiPackagePath` support a different installed npm location. No installation, provider switch, sign-in or global configuration edit is performed by the launcher. Normal Pi startup still uses Pi's own settings and trust behavior.

For another shell, the equivalent explicit loading command is:

```sh
pi --provider zai --model glm-5.3-flash --thinking high --no-extensions -e ./hosts/pi/extension.ts --no-skills --skill ./hosts/pi/skills --no-prompt-templates
```

The extension verifies the effective model binding before dispatch. A missing model or image capability is a blocker, not permission to use a different model.

## Roles and fixed model routing

| Logical role | Model | Work |
|---|---|---|
| **Planner** | Flash by default; GLM 5.3 selectable | Brief, source-linked draft, consequential questions, handoffs and delivery |
| **Executioner** | Flash for `visual`; selected main model for `content` | Sole deck writer; visual/layout assembly uses the Planner's frozen content |
| **Reviewer** | Separate Flash context for `visual`; separate selected-main context for `content` | Independent source/native evidence checks and inspection of actual renders |

GLM 5.3 accepts text only. Flash accepts image inputs and produces text/code; it is not an image-generation service. Both require reasoning enabled. Content worker contexts disable image input on either model; only independent inspection of actual renders in a visual Reviewer context can pass the visual gate. [GLM 5.3](https://docs.z.ai/guides/llm/glm-5.3), [Flash](https://docs.z.ai/guides/vlm/glm-5.3-flash)

The prepared demo normally needs just the main Planner, one Flash Executioner and one independent Flash Reviewer. The Reviewer checks original content and native evidence as well as every render. A separate content phase on the selected main model is available when needed; it is not an extra mandatory demo call. All sessions belong to the same three logical roles.

`task_kind` selects the model through a fixed table, with no classification call. Use supplied visual ideas first, optionally batch unresolved bank lookups, freeze choices in the existing plan, then build all slides together. Unclear semantics stay with the Planner. Flash gets complete source and evidence references, not just the writer's description.

## What is executable

`extension.ts` registers `slide_worker` and `question_me` through Pi's extension API. Worker contexts are independent SDK sessions, reused separately by run, mode, role and task kind. Dispatch is serialized. The worker cannot delegate; Reviewer has read and shell tools but no edit/write tool. **Shell access is not a filesystem sandbox.** Source/candidate hash checks detect changes; they do not make files immutable.

The extension stores transport/session records under the private run's `pi/` directory. Keep the workflow plan and verbatim review in `run.md` for the demo, or in the ordinary mode's records. A successful tool call means a worker returned; it is not deck acceptance. Required content, visual, native-object and final hash gates remain Planner/Reviewer responsibilities.

`question_me` uses Pi's interactive dialog when available. Dismissed or headless questions remain pending, with no timed default. For an answer received in ordinary conversation, Planner updates the matching record in `<run>/pi/questions.json` with the verbatim answer and `status: answered`, preserving its question fields and fingerprint, and records the scoped decision in the workflow record. It must never invent an answer. While a required question is pending, Planner can continue independent preparation; this thin adapter conservatively holds worker dispatch for that run.

## Preparation and verification limits

The adapter was checked against Pi **0.84.2**. That tested installation's bundled catalog lacked `glm-5.3-flash`; this does not establish the catalog state on another PC. Run the check there. Use a catalog exposing Flash (and GLM 5.3 if selected as main), or configure a missing model through [Pi's custom-model mechanism](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md). Confirm Flash is marked with image input. This package does not silently alter your model configuration.

The offline check is not authentication or inference. Prepare a real editor, renderer, fonts and native visual recipes, then rehearse through independent review in the intended Pi environment. No live GLM deck run or 20-minute result is claimed. [Backend preparation](../../docs/backend-guide.md), [presenter guide](../../DEMO.md)

## Package

```text
hosts/pi/
  start.ps1, check.mjs       # Launch and offline model/runtime check
  extension.ts, core.mjs     # Native tools and dispatch helpers
  agents/                   # Thin Planner/Executioner/Reviewer instructions
  skills/demo-slides/       # Prepared 5–6-slide creation route
  skills/create-slides/     # Ordinary materials-to-deck route
  skills/improve-slides/    # Exact-preservation improvement route
```

The portable contracts remain in the shared workflow. This package is a host adapter; it supplies neither a universal PowerPoint backend nor a PDF importer. Pi's extension/SDK interfaces can change across versions; offline harness tests do not establish a live deck run. [Pi extensions](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md), [skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)
