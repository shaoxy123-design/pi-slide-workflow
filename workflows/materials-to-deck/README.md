# Materials → editable slide deck

For a prepared 5–6-slide demo targeting a 20-minute presentation, use [DEMO.md](../../DEMO.md) and the compact [slide-demo procedure](../../skills/slide-demo/SKILL.md). That opt-in route replaces this full record/role chain; it retains the same fidelity, editability and independent-review gates. The details below apply to ordinary creation.

A companion to the existing PPT-improvement workflow. Start with papers, reports, notes, data, images, existing slides or supplied web pages; build a coherent deck for the intended audience. The same three logical roles apply: **Planner → Executioner → Reviewer**.

Status: portable workflow instructions and record contracts. Source extraction, deck authoring, rendering and delegation use the host's actual capabilities. This folder does not implement a universal importer or an automatic deck-generation service.

## Choose the right workflow

| Request | Workflow | Content rule |
|---|---|---|
| Improve these existing slides | [PPT improvement](../../README.md#start-a-run) | Preserve exact content and slide order/count unless scoped changes are authorized |
| Turn these materials into a new presentation | This workflow | Select, summarize and reorganize faithfully; preserve claims, data, qualifiers and attribution |
| Convert this slide PDF faithfully to PPTX | [PDF reconstruction](../../docs/pdf-input.md) | Reconstruct and compare every page before improving it |

Select creation mode only when the user requests a new deck from materials. Attaching a PDF alone does not grant permission to summarize it. A source slide deck can be used as material when that is the user's intent; preserve the input file and record which content is reused or omitted.

## Scoped content policy

The new-deck request authorizes faithful selection, paraphrasing, headings, transitions and a new slide structure within the requested topic. Preserve the meaning and strength of evidence: association does not become causation, a tentative finding does not become a certainty, and a subset does not become a universal claim. Retain important limitations and conflicting evidence.

Keep direct quotations exact and identified as quotations. Do not change formulas, numbers, units, categories or reported results. Derived calculations need their inputs, method and units recorded. Never invent values from a chart's appearance. Prefer native charts with verified data; unresolved data reconstruction is a question for the Planner.

The default is supplied sources only. Additional research, translation, fictional examples, invented case studies and comic dialogue need their own scoped authorization. If the user explicitly requests them initially, record that permission and proceed. Newly written headings and explanatory paraphrases grounded in the sources do not require repeated permission.

All original files stay untouched. Native core editability, one selectable group/picture per topic visual, independent review, hash-bound delivery and no local workflow time controls still apply. The existing improvement defaults do not become a blanket rewrite permission.

## Agents and procedures

| Agent | Owns | Procedure |
|---|---|---|
| [Planner](agents/planner.md) | Brief, questions, source inventory, evidence map, narrative and storyboard | Understand audience/objective; map material to teaching points; choose sequence, scope and visual treatment |
| [Executioner](agents/executioner.md) | Native deck, artwork, citations, renders and editability evidence | Build from the frozen storyboard; package topic visuals; export and check actual files |
| [Reviewer](agents/reviewer.md) | Independent source, narrative, visual, editability and file review | Compare claims with original passages/data; verify required coverage and actual exported objects |

The orchestration skill is [materials-to-deck](../../skills/materials-to-deck/SKILL.md). Reuse [question-me](../../skills/question-me/SKILL.md) for Planner questions and the [visual bank](../../docs/visual-bank.md) for artwork and native recipes. Backend and renderer are tools, not additional agents.

## Workflow

1. **Brief.** Establish audience, objective, language, must-cover topics and any slide-count or talk-duration target. Infer safe defaults from the request and materials and state them. Ask only about consequential ambiguity. Talk duration guides content scope; it is not a processing deadline.
2. **Source intake.** Preserve and hash inputs. Assign stable source IDs and extract using available tools. Verify passages, numbers, tables, equations and figure captions against originals. Keep uncertain OCR separate from verified evidence.
3. **Evidence and narrative.** Identify the central message, prerequisites, supporting evidence and takeaways. Map each factual claim to source locations. Record omissions, unresolved contradictions and required coverage. Do not turn each paragraph into a slide.
4. **Storyboard.** For each slide specify its purpose, takeaway title, exact draft text, claim IDs, citations, notes, layout and a useful visual for each meaningful block. Choose the slide count from the brief and material. Preserve must-cover content; ask if a hard count or duration conflicts with it.
5. **Author.** Use one qualified authoring backend and renderer. Build native text, tables, charts, equations and diagrams. Use grouped native visuals or separate pictures, with editable labels and citations. Reuse the visual bank where it fits the topic.
6. **Review and repair.** Independently assess source fidelity, narrative/coverage, visuals, native editability and the actual file. Repair actionable findings and recheck the new candidate hash. A source-text equality check is not the fidelity test for an intentionally summarized deck.
7. **Deliver.** Package only the reviewed PPTX with a matching preview, source map and short report identifying omissions, limitations and any authorized additions.

A clear brief can proceed through the storyboard without an extra approval round. If the user asks to approve the outline, honor that checkpoint. Required questions remain pending; optional style choices use stated safe defaults.

## Materials and capability limits

| Material | Handling |
|---|---|
| Digital PDF, Word or text | Extract passages with page/section locators; verify against the original |
| Scanned PDF or image | OCR if available, then visually verify; unreadable evidence cannot support a claim |
| Spreadsheet or data table | Record sheet/range, units, definitions and calculations before charting |
| Existing PPTX | Inventory slides/notes/data and use source slide/object locators |
| Supplied web page | Retrieve if accessible; record URL, access time and retained evidence; ask for content if unavailable |
| Audio/video | Use an available transcript, or a qualified transcription capability; preserve timestamps and check material uncertainty |

These are intake procedures, not claims that this repository has parsers for every format. A paper PDF used for new authoring does not need a page-for-page PPTX conversion first; its relevant evidence does need verification against the PDF. Faithful slide-PDF conversion remains the separate reconstruction workflow.

## Files and handoffs

```text
workflows/materials-to-deck/
  README.md                    # Scope, policy and execution sequence
  workflow.defaults.json       # Creation defaults only
  contracts.md                 # Source/claim/storyboard and review records
  request.example.json         # Brief template; not a runnable command
  agents/
    planner.md
    executioner.md
    reviewer.md

runs/<unique-run-id>/
  sources/                     # Immutable input copies and source manifest
  request.json                 # User request and verbatim clarifications
  plan.json                    # Scope, requirements, authorizations, tool choices
  state.json                   # Phase, pending questions, current hashes, next action
  evidence.json                # Claims with original source locations
  storyboard.json              # Exact proposed slide text, visuals, citations, notes
  omissions.json               # Exclusions and coverage impact
  build/                       # Candidates, authoring source, checks and renders
  review/                      # Independent reviews tied to candidate/source hashes
  deliverables/                # deck.pptx, preview, source map and report
```

Read [contracts](contracts.md) before dispatch. For Pi or another host, follow [host bindings](../../docs/host-adapter.md) but use these creation role prompts and records. An existing adapter that assumes one `source.pptx`, an original-deck baseline or the improvement role paths needs modification and testing before it can run this mode.

## Start a creation run

> Read skills/materials-to-deck/SKILL.md. Use the supplied materials to create a new editable presentation for [audience], aiming to [objective]. Cover [required topics]. [Optional: slide-count/talk-duration target and style.] Summarize and reorganize faithfully, cite the sources, and proactively add useful visuals. Keep each topic visual as one selectable native group or picture. Use question_me for consequential ambiguities. Apply no workflow time limits. Review source fidelity and editability before delivery.

The placeholders are brief fields to fill, not required boilerplate. Without supplied materials, collect the source input rather than fabricate a source-grounded deck.
