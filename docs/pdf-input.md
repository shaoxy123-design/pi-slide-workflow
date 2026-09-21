# PDF input: proposed intake design

This procedure is for faithful reconstruction and improvement of existing slides. If the user instead requests a new presentation synthesized from a paper/report or other PDF material, use [materials-to-deck](../workflows/materials-to-deck/README.md); verify source evidence directly without requiring a page-for-page PPTX intermediate.

PDF can be a source for the workflow, but it needs an editable reconstruction before normal slide improvement. **This document describes a design; PDF ingestion and conversion are not implemented in this repository.** The current scripts accept PPTX. Keep the existing **Planner → Executioner → Reviewer** structure and existing skills.

## Planner: classify and lock the source

Inspect the PDF and distinguish three cases:

| Source | Intake decision |
|---|---|
| PDF exported from slides | Reconstruct each page as an editable slide, preserving page order and content by default. |
| Scanned or image-only slide PDF | Extract text with OCR, then validate it against page renders. OCR output is provisional, especially for equations, numbers, units and citations. |
| Paper, chapter or report PDF | Turning prose into slides normally requires selection, summarization and a new structure. Obtain explicit permission and record that scope before changing content. |

Use the existing `question_me` function when page scope, intended slide structure, unreadable material, chart data, equation meaning, or requested editability is unresolved. Ask for missing source data or clarification when necessary; do not guess scientific content. Clear slide-PDF reconstruction can proceed within the user's existing request.

Retain the untouched original PDF and page renders. Create a baseline containing verified exact text, numerical values, units, citations, equations, table cells and chart evidence, with a source-page-to-slide map. Preserve raw extraction/OCR output separately from validated text, and record any extraction corrections. The PDF and its rendered pages remain the reference throughout the run.

## Executioner: reconstruct editable slides

Use an available, qualified conversion or reconstruction tool, then inspect its actual output. Adobe documents PDF-to-PowerPoint conversion and OCR for scanned material, but those capabilities do not establish fidelity for a particular file. See [Adobe's PDF-to-PowerPoint guidance](https://www.adobe.com/acrobat/how-to/pdf-to-powerpoint-pptx-converter.html).

Recreate core text as native text, tables as native tables, equations as editable equations, and charts as native charts with trustworthy data. Reconstruct requested diagrams with editable elements. Do not use a whole-slide image as the deliverable or add invisible text behind a page screenshot to claim editability.

If chart values cannot be recovered reliably, seek the underlying data through `question_me`. If equation transcription is uncertain, resolve it before accepting reconstruction. A replaceable picture of a chart or equation does **not** satisfy full core editability. Any exception needs explicit user permission, recorded with its affected objects. Illustrative artwork may remain a separate replaceable image under the existing artwork rules.

## Reviewer: qualify reconstruction before improvement

Independently compare the reconstructed PPTX with the original PDF, its renders and the validated page map. Check every page's text and scientific content, verify native object types, and exercise representative edits. Resolve missing content, OCR mistakes, data changes and raster substitutes before accepting the reconstruction.

Check word boundaries as well as character coverage. Ignoring all whitespace can hide joined words, while separate native objects can split a correctly rendered label. Resolve these cases against the PDF and actual slide renders. Inspect small footers or dense evidence at an enlarged scale when full-slide previews are inconclusive.

Only after this PDF→PPTX review passes should the Planner create the normal PPTX guard baseline and begin slide improvement. A later guard pass shows preservation relative to that reconstructed PPTX; it cannot establish faithful PDF conversion. Final review must still consult the original PDF.

## Local work and demo timing

Local mode has no time controls. The under-30-minute target concerns demo rehearsal logistics only. Count extraction, reconstruction and the independent PDF→PPTX review when claiming end-to-end PDF timing. If a PPTX was prepared beforehand, disclose the preconversion and label the measured demo as improvement from that prepared PPTX.
