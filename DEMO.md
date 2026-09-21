# A 20-minute slide demo

**Open the project, paste one prompt, show Planner → Executioner → Reviewer.** This prepared demo creates 5–6 editable slides from one ready Markdown or plain-text source. The included accounting example uses six slides.

## Start in Pi + GLM 5.3 / Flash

Follow the [Pi setup and offline check](hosts/pi/README.md), launch `.\hosts\pi\start.ps1`, and use `/skill:demo-slides Use example_input/inventories-hkas2-knowledge.md to create 6 slides.` Flash plans the content by default (`-MainModel glm-5.3` is optional); Flash assembles the visual deck and a separate Flash Reviewer inspects the actual renders and source/native evidence. There are still three logical roles. No Jev account or additional routing call is required.

## Start in Kimi Code Desktop + K3

Open the whole repository as the Desktop workspace. Use the **[Windows GUI guide and copyable prompt](hosts/kimi/DESKTOP.md)**. Start a normal task with K3 thinking enabled; the prompt binds Planner, Executioner and Reviewer without Swarm mode. Check account access and rehearse in the actual GUI before presenting.

## Start in Kimi Code CLI + K3

Open the whole repository in PowerShell:

```powershell
.\hosts\kimi\start.ps1
```

Then paste into Kimi:

```text
/skill:demo-slides Use example_input/inventories-hkas2-knowledge.md to create 6 slides.
```

For Codex, use the same prepared setup and ask: `Read AGENTS.md and skills/slide-demo/SKILL.md. Use example_input/inventories-hkas2-knowledge.md to create 6 slides.` Host tools and independent workers must already be qualified.

## Prepare before presenting

- Confirm access to the selected host/models and independent workers. For Pi on another PC, follow [NEW-PC.md](hosts/pi/NEW-PC.md) and run `start.ps1 -Check`. Qualify one editor, one renderer, an installed font/theme and suitable visual-bank recipes or prepared artwork.
- Rehearse this exact source and setup through independent review. Measure the total including model waits; aim for a reviewed result by minute 15. This route has **not been benchmarked** and cannot guarantee fresh inference finishes within 20 minutes.
- Keep the reviewed rehearsal deck, preview and review ready. The live demo performs no installs, research, OCR or new image generation. Required features needing that work require preparation or a scoped decision with the professor.

## Show three things

Routine choices use supplied visual ideas and optional local batch lookup; no Jev account or extra model is needed. See [fast local decisions](docs/fast-decisions.md) if explaining this design choice to colleagues.

1. **Planner:** one brief, six-slide plan and source locations in `run.md`; questions only for consequential ambiguity.
2. **Executioner:** native text and useful topic visuals, each already one group or picture. Build all slides together using the prepared theme.
3. **Reviewer:** independent inspection of every slide, source fidelity, coverage, editability, grouped visuals and the actual exported file. Repair concrete failures; defer optional polish.

Deliver the reviewed PPTX, matching preview and `run.md`, which combines the source map and report and retains the raw Reviewer response. Demonstrate native edits and moving a grouped visual on a disposable copy.

At minute 15, the presenter may switch to a **clearly labelled, previously reviewed rehearsal deck** while the live run continues. Twenty minutes is the speaking agenda, not a workflow deadline, repair cap or automatic pass.

For other work, choose the normal [new-deck workflow](workflows/materials-to-deck/README.md) or [existing-slide improvement](skills/ppt-improve/SKILL.md). See the [presenter runbook](docs/demo-runbook.md) and [Kimi setup details](hosts/kimi/README.md).
