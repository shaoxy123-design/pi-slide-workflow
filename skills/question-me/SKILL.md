---
name: question-me
description: Use when the PPT Planner needs a user decision about ambiguous slide scope, content edits, editability, conflicting requests or missing preferences.
---

# Planner function: question_me

`question_me(questions)` is a workflow procedure mapped to the host's user-input capability, not an installed API. The Planner alone calls it. See the [contract and adapter](../../docs/contracts.md#question_me).

Use ordinary conversation when no structured input tool exists. Pi's optional UI/headless mapping is described in [Pi integration](../../docs/pi-integration.md#question_me-mapping); a dismissed dialog or absent client response remains pending, not answered.

Each question contains `id`, `question`, `reason`, `affected_scope`, `required`, `choices`, `default`, and `independent_work`. Ask at most three short questions together, preferring one. Offer two or three concrete choices when useful, with the recommended option first. Do not ask questions whose answers are in the request, prior answers or source deck.

**Required answers:** conflicting instructions; permission for a content change; unrecoverable facts or symbols; an explicit scope/editability requirement the backend cannot satisfy. Explain the concrete issue and pause only dependent work. The default must be null. Keep the question pending until answered; time elapsed is never authorization. Save state so work can resume after the answer.

**Optional answers:** style, preferred colors, illustration tone or other reversible preferences with a safe default. Give the user an opportunity to respond under the host's interaction rules, continue independent work, and then record the stated default if unanswered. This courtesy is not a run deadline. Use source branding, academic tone and no content edits. Never infer a default that broadens permission.

Examples:

- Required: “Slide 4 is a chart screenshot. To make its data editable I need the original values. Can you provide the data, or should this chart remain an image with the limitation recorded?”
- Required: “You asked to preserve every word and shorten the bullets. Should I keep the wording and change only layout, or may I rewrite the bullets on slides 3–5?”
- Optional: “Which visual tone fits this lecture: academic illustrations (recommended), understated comics, or the current style?”

Record answers verbatim in `request.json`; translate them into scoped requirements/authorizations in `plan.json`. Workers return a question proposal to the Planner, never open competing user conversations. If the user asks for full object editability, do not substitute replaceable pictures without resolving that requirement.
