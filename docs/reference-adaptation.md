# What we adapted from the reference workflow

Inspected on 2026-09-08. These are design adaptations, not a copy of the upstream framework or a claim of API compatibility. The source focuses on academic work including Beamer/Quarto; this project focuses on preserving editable PowerPoint decks.

| Verified source feature | Our adaptation |
|---|---|
| [Plan-first requirements and clarification](https://github.com/pedrohcgs/claude-code-my-workflow/blob/main/.claude/rules/plan-first-workflow.md) use priority/clarity labels and user questions | One compact plan with MUST/SHOULD/MAY, CLEAR/ASSUMED/BLOCKED and a Planner-owned `question_me` procedure; defaults for optional preferences |
| [Orchestrator preflight](https://github.com/pedrohcgs/claude-code-my-workflow/blob/main/.claude/rules/orchestrator-protocol.md) collects interactive configuration before dispatch | Resolve required choices before dependent work; pass scope, permissions, paths and constraints once |
| [Slide-excellence](https://github.com/pedrohcgs/claude-code-my-workflow/blob/main/.claude/skills/slide-excellence/SKILL.md) selects relevant review work and includes a fast mode | Three logical agents; six small skills loaded on demand; one Reviewer covers relevant dimensions |
| [Slide-auditor](https://github.com/pedrohcgs/claude-code-my-workflow/blob/main/.claude/agents/slide-auditor.md) performs read-only slide review | Independent Reviewer reports slide/object, severity, evidence and remedy; never edits the deck |
| [Orchestrator loop](https://github.com/pedrohcgs/claude-code-my-workflow/blob/main/.claude/rules/orchestrator-protocol.md) verifies, reviews, fixes and rechecks | Repair concrete findings and refresh checks tied to the actual candidate hash; no fixed local repair cap or time controls |
| [Repository overview](https://github.com/pedrohcgs/claude-code-my-workflow) preserves plans and session records | Minimal `request.json`, `plan.json`, `state.json` and review evidence survive handoffs without a memory subsystem |

PowerPoint-specific additions: exact content preservation by default; scoped user authorizations; native-object editability checks; retained chart/workbook/equation evidence; a read-only OOXML guard; separate replaceable artwork with editable captions; and a demo rehearsal/runbook.

We omit unrelated research agents, Beamer–Quarto conversion, deployment, memory councils, broad environment permission settings and endless optional-polish loops. Required fixes receive further repair/recheck as needed. Routine, already-authorized formatting does not need an additional plan approval. Questions remain necessary for missing facts, conflicting constraints or actual content permission.

The under-30-minute demo slot is a practical presentation limitation, **not a workflow policy, upstream runtime promise or measured benchmark**. Local execution has no time controls. Quality is decided by zero unresolved blockers and fulfilled required checks, not an aggregate aesthetic score or elapsed time.

## PPTAgent and DeepPresenter additions

The [PPTAgent paper](https://aclanthology.org/2025.emnlp-main.728/) motivates cached reference-layout analysis and structured element editing. This repository now has a read-only reference layout extractor/matcher and a narrow source-bound editing adapter. Their effectiveness on real lecture decks still needs measurement.

DeepPresenter's [design role](https://github.com/icip-cas/PPTAgent/blob/main/deeppresenter/roles/Design.yaml) and [inspection tools](https://github.com/icip-cas/PPTAgent/blob/main/deeppresenter/tools/reflect.py) motivate checks during execution. We keep inexpensive geometry checks and rendered-slide inspection, plus the separate Reviewer, within our existing three roles.

[PPTEval](https://aclanthology.org/2025.emnlp-main.728/) motivates separate quality dimensions. Our [comparison protocol](benchmark-protocol.md) adds original-content preservation, native-object editability, completion time and manual corrections, and refuses to infer superiority from unmatched tasks or unknown evidence. We have not run PPTAgent/DeepPresenter or a side-by-side real-deck benchmark.
