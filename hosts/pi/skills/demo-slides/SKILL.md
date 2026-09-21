---
name: demo-slides
description: Run a prepared 5–6-slide creation demo in Pi with GLM 5.3 Flash or GLM 5.3 planning and independent Flash visual workers, using one ready text source.
---

Act as Planner on the selected main model (Flash by default, or GLM 5.3). The repository root is four directories above this skill directory. Read [AGENTS.md](../../../../AGENTS.md), the complete [compact demo procedure](../../../../skills/slide-demo/SKILL.md), and the thin [Pi Planner binding](../../agents/planner.md). Do not load the full creation contract chain.

Verify the native `slide_worker` and `question_me` tools. Use `mode: demo` and `task_kind: visual` for one Flash Executioner and one separate Flash Reviewer. Pass frozen draft/source locations, all original source paths, actual backend/render commands and output paths. Reviewer receives the candidate path/hash and all renders/native evidence. Reuse role/task contexts for repairs; workers must not delegate.

Keep exactly three logical roles. Use supplied visual ideas first and optional local batch lookup only where useful. No Jev model/API is needed. Save the plan/source map and verbatim review in run.md, with actual model and hash evidence. Twenty minutes is the presenter agenda; required questions and review gates remain intact.
