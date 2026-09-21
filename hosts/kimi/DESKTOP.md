# Kimi Code Desktop: Windows demo

Open the **whole repository** in Kimi Code Desktop. The Windows GUI was released on September 17, 2026; this guide was checked against official documentation on September 21. Desktop execution and six-slide timing have not been verified locally. [Release notes](https://www.kimi.com/code/docs/kimi-code/whats-new.html)

## Before the audience arrives

1. Create a new session, choose the repository folder above the message box, and confirm the workspace. Select **K3** in the model picker. Send a small read-only request, such as reading the first heading of the accounting input, to confirm this account can actually make a model request. [Desktop quick start](https://www.kimi.com/code/docs/kimi-code-desktop/getting-started.html)
2. Keep **thinking enabled**. Try **Low** during rehearsal if available; retain the setting that produces a reviewed result. Turning thinking off routes requests to K2.8 Preview, even when K3 was selected. Choose the model/settings before the task rather than changing them mid-run. [Model configuration](https://www.kimi.com/code/docs/kimi-code/models.html)
3. Use a normal task for this prepared brief. Leave Plan, Goal and Swarm modes off; the prompt already specifies the three roles. For a workspace you have reviewed, **Ask when needed / 必要时询问** permits routine work while retaining questions and sensitive-operation approvals. [Task modes](https://www.kimi.com/code/docs/kimi-code-desktop/using-desktop.html), [approval modes](https://www.kimi.com/code/docs/kimi-code-desktop/getting-started.html)
4. Qualify the local editor and renderer, then rehearse the exact six-slide task through review. Keep its reviewed PPTX and preview ready. A successful model ping proves access only. See [DEMO.md](../../DEMO.md) for the 20-minute presenter agenda and fallback.

## Paste this into Desktop

```text
Read AGENTS.md and skills/slide-demo/SKILL.md. Use the prepared demo route.
Create 6 editable English slides for beginning accounting students from
example_input/inventories-hkas2-knowledge.md.

Act as Planner. Use one native Agent coder as Executioner and one independent
Agent explore as Reviewer; reuse them for repairs and do not let them delegate.
Use K3 with thinking enabled for both workers. Select model "primary" only if
the tool supports it; verify the effective binding if model choice is hidden.
Report unavailable tools or model binding as a blocker. The Reviewer must not
modify the source or candidate; save its returned report verbatim in run.md.

Use prepared tools and visuals, preserve the source's accounting qualifications,
and keep each topic visual as one group or separate picture. Deliver the
reviewed PPTX, matching preview and run.md. Ask only consequential questions.
```

This plain prompt avoids relying on skill discovery. The CLI launcher registers `hosts/kimi/skills/` with `--skills-dir`; opening the folder in Desktop does not apply that flag. Project skill discovery uses standard locations such as `.kimi-code/skills/` and `.agents/skills/`. No skill copying or global configuration change is needed for the prompt above. [Skill discovery](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html)

## What to show

The prepared procedure reuses supplied visual ideas and batches unresolved catalog lookups locally. It borrows the structured-decision idea from Jev without adding an API or another agent; see [fast local decisions](../../docs/fast-decisions.md).

Show the Planner's brief, the Executioner's output, and the independent Reviewer report. Desktop's Background Agent panel can expose worker model and thinking settings; confirm those before describing the run as all-K3. A forced secondary model can hide model selection, so absence of an `Agent.model` argument alone proves nothing. [Desktop agent panel](https://www.kimi.com/code/docs/kimi-code-desktop/using-desktop.html), [secondary model binding](https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/config-files.html#secondary-model)

Preview rendered images or PDF in Desktop, then open the reviewed PPTX in PowerPoint. On a disposable copy, edit a text box and move/resize one grouped visual. Twenty minutes remains the speaking slot; an unfinished or unreviewed deck is not a completed result.
