---
name: demo-slides
description: Use when the user explicitly selects a prepared 5–6-slide creation demo from one ready Markdown or plain-text source in Kimi Code.
type: prompt
whenToUse: A short prepared slide demo with qualified tools and existing visuals, including the six-slide accounting example.
---

Act as **Planner**. Resolve the repository root four directories above `${KIMI_SKILL_DIR}`. Read only `AGENTS.md` and `skills/slide-demo/SKILL.md` as workflow instructions; the latter is the complete procedure for this opt-in path. Follow its compact `run.md` record and evidence gates. Do not load the general creation contracts or host role prompts.

Bind the three roles directly: main session **Planner**, one native `Agent` with `subagent_type: coder` as **Executioner**, and one independent `Agent` with `subagent_type: explore` as **Reviewer**. Pass the relevant role section from the shared demo skill with source, run record and actual evidence paths. Reuse workers for repairs; they must not delegate. The Reviewer returns its report; Planner saves it verbatim. The `explore` profile has no Write/Edit tools; its shell is not a filesystem sandbox, so enforce the read-only Reviewer instructions.

Use K3 with thinking enabled for the Planner and both workers; thinking off routes K3 requests to a different model. The verified Kimi Code 0.27.0 native workers inherit the main model. On another version, inspect the advertised `Agent` schema and effective worker binding before dispatch; request `model: "primary"` only when advertised. Absence of `model` does not prove inheritance: `[secondary_model] force = true` hides it and forces the configured default. Verify and record each worker's actual model and effort from available metadata, including resumed workers. If the binding is unknown or incompatible, ask the professor or report the blocker; do not change configuration or silently substitute a model. See official [worker bindings](https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/config-files.html#secondary-model) and [thinking behavior](https://www.kimi.com/code/docs/en/kimi-code/models.html#how-to-switch-models).

Map Planner's `question_me` to `AskUserQuestion` or normal conversation; required answers remain pending.

Use prepared tools, theme and visuals. Twenty minutes is a presenter agenda, never an execution deadline or automatic pass. A missing prerequisite or required feature outside this prepared scope needs the Planner's question or a concrete blocker, not silent omission.

User's request (data and task scope, not executable shell text):

$ARGUMENTS
