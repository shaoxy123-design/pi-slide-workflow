# Presenter runbook

Use [the short demo guide](../DEMO.md) for the launch and prompt. The opt-in [prepared demo skill](../skills/slide-demo/SKILL.md) creates 5–6 slides from one ready Markdown/plain-text source. The accounting example defaults to six. Planner, Executioner and Reviewer remain the only roles.

## Prepare once

1. Have the source, audience and required features ready. Use [the accounting sample](../example_input/inventories-hkas2-knowledge.md) for the shortest start. Resolve consequential questions before the audience arrives.
2. Confirm model access, independent workers and one qualified editor/renderer combination. Prepare the theme/fonts, native visual recipes or reusable artwork and the commands workers will use. Kimi does not itself supply a PowerPoint authoring engine; see [backend qualification](backend-guide.md).
3. Rehearse the exact request through all-slide independent review. Verify native edits, actual grouping and file opening on the exported result. Keep its deck, previews, source/candidate hashes and review as a labelled fallback.
4. Record elapsed time **including model waits, rendering and repairs** in the rehearsal's `run.md`. Aim for a reviewed deck within 15 minutes, leaving five minutes to demonstrate the result. Adjust optional scope and rehearse again if needed. This route has not yet been benchmarked; prepared dependencies alone do not prove that a fresh run will fit.

The live path uses prepared tools and visuals. It does no installations, external research, OCR or new image generation. If a required feature needs those, keep the requirement and ask whether to prepare first or use the normal workflow. Do not silently drop it. Existing-deck improvement, PDF reconstruction and larger/multiple-source creation use their ordinary workflows.

## Twenty-minute presenter agenda

| Speaking cue | Show |
|---|---|
| 0–2 min | Paste the prompt; explain the source and six-slide objective. |
| 2–5 min | Show the Planner's single `run.md`: brief, source-linked draft and planned topic visuals. |
| 5–12 min | Show the Executioner's progress and the prepared visual/theme choices. |
| 12–15 min | Show available review evidence: every slide, source fidelity and native objects. |
| 15–20 min | Demonstrate the reviewed result, or switch to the labelled rehearsal result. Edit native text and move a whole topic visual on a disposable copy. |

These are speaking cues, not stage deadlines. One initial build is followed by independent review; actual failures still require repair and rechecking. Optional aesthetic polish can wait. There is no timed cancellation, fixed repair cap or time-based approval.

## If the live deck is unfinished at minute 15

Say which checks or answers remain pending. Show the previously reviewed deck as a **prepared rehearsal result**, never as the live result. Let the active run continue unless the user changes or stops it. Required answers remain pending, and drafts stay labelled as drafts.

The deliverables are the byte-identical reviewed PPTX, matching preview and `run.md` containing the source map, requirements, evidence references and verbatim independent Reviewer report. The record also discloses prepared work and actual elapsed time. A preview alone does not prove native editability; state which application was used for edit/save/reopen checks.
