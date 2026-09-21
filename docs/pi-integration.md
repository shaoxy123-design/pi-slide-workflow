# Pi integration

Start with the [Pi native package](../hosts/pi/README.md). It supplies an explicit extension, three native skills and a Windows launcher for **GLM 5.3 Flash planning by default, optional GLM 5.3 planning, and Flash visual work**. The main Pi session is Planner; SDK worker contexts implement the Executioner and Reviewer roles. Prompt files alone do not register tools.

## Entry points

```powershell
.\hosts\pi\start.ps1 -Check
.\hosts\pi\start.ps1
```

Use `/skill:demo-slides` for the prepared 5–6-slide creation demo, `/skill:create-slides` for ordinary new decks from materials, or `/skill:improve-slides` for exact-preservation improvement. Keep the whole repository intact. Explicit `--skill` paths preserve native Pi discovery while loading shared procedures only when needed. [Pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)

## Host tools

- **`slide_worker`:** dispatch a specific mode, role and content/visual task kind. Pass the original brief, source paths, plan and evidence paths in the handoff. Reviewer requires the frozen candidate path and SHA-256. Worker sessions are reused by run/mode/role/task kind; content and image contexts stay separate.
- **`question_me`:** Planner asks consequential questions through the UI when available. Cancellation and headless operation remain pending; ordinary conversation can collect the actual answer. Transport records persist beneath the run directory.

The thin [Planner binding](../hosts/pi/agents/planner.md) defines the handoff fields. Workers cannot delegate. Dispatch is serialized so the writer and Reviewer do not operate on a changing candidate at the same time. They have independent contexts in a shared process/filesystem. Removing Reviewer edit/write tools is not an OS sandbox while shell access remains available.

The runtime protects the transport and checks file identities. It is not a full automatic scheduler or a replacement for source, native-object and visual review. A worker exit or matching hash never means all quality gates passed. Follow the [host adapter contract](host-adapter.md), preserving the ordinary mode records or the compact demo's `run.md` as appropriate.

## Model and visual boundaries

The route is fixed: `content` inherits the selected main model (`glm-5.3-flash` by default or `glm-5.3`); `visual` always uses `glm-5.3-flash` on the same configured provider. Flash-only mode needs just one model ID, with independent sessions for each role/task kind. Content worker contexts disable image input on either model; they do not pass the visual gate. Use a new run after changing the main model. GLM 5.3 is text-only, so a visual review needs Flash reading actual renders in an independent Reviewer context. Main-model image descriptions and the Executioner's narrative are not visual evidence. The prepared demo can use one Flash build and one independent Flash review, with the selected main model supplying the initial plan. Extra content phases are optional when the work needs them. [GLM 5.3](https://docs.z.ai/guides/llm/glm-5.3), [Flash](https://docs.z.ai/guides/vlm/glm-5.3-flash)

Routine choices reuse supplied visuals and prepared layouts. The local bank can shortlist unresolved topics in one batch. This borrows [Jev's structured-decision intuition](fast-decisions.md) without a Jev API or another routing model.

## Dependencies and validation scope

Pi does not inherit Codex-only slide/image tools. Qualify one real editor, renderer and native-object inspection method before using a source. A code/vision model does not itself supply an image generator or PowerPoint renderer. Follow the [backend guide](backend-guide.md). PDF reconstruction remains a separate required step before improvement.

On Windows, run `.ps1` examples through PowerShell. Pi's shell tool can use a different shell, so inspect its actual configuration before passing commands. Never paste PowerShell syntax into Bash or assume the presence of an Office automation interface. [Pi Windows guide](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/windows.md)

The tested **Pi 0.84.2** SDK is the implementation reference. That installation's bundled catalog lacked `glm-5.3-flash`; the destination PC needs its own check. Follow the [new-PC guide](../hosts/pi/NEW-PC.md). The package checks exact model IDs and image capability rather than silently substituting. Use an appropriately configured/current Pi catalog and verify account access separately. Offline loading and harness tests do not establish live GLM inference, deck acceptance or a 20-minute result.
