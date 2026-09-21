# Inventory Valuation: Cost, Net Realisable Value and Write-downs

## Teaching brief

- **Topic:** Inventories under HKAS 2.
- **Audience:** Students beginning financial accounting who understand assets, expenses and profit or loss.
- **Language:** English.
- **Suggested deck:** Six slides for a short classroom demonstration.
- **Learning outcome:** Explain how inventory cost is determined, compare cost with net realisable value, and describe the effect of a write-down or reversal.
- **Source basis:** A faithful summary of the supplied accounting concept note dated 16 June 2026, identified as S1 below. No new numerical case or exam-frequency claim is added.

## 1. The measurement rule: lower of cost and NRV

**Key message:** Inventory is measured at the lower of cost and net realisable value (NRV), with the comparison made at each reporting date.

`Inventory carrying amount = lower of cost and NRV`

- Cost and NRV are different measures; calculate each before comparing them.
- If NRV falls below cost, inventory must be written down to NRV.
- Apply the comparison item by item, or to appropriate groups of similar items. Do not offset losses on some lines against gains on others by testing all inventory as one pool.

**Visual idea:** One grouped native comparison diagram with two inputs, “Cost” and “NRV,” feeding a “Use the lower amount” box. Keep the formula as editable text.

**Evidence:** S1, first bullet and “Why it matters / where it bites,” discussion of the NRV test.

## 2. Determine cost: what belongs in inventory?

**Key message:** Inventory cost includes costs that bring goods to their present location and condition, subject to the exclusions below.

| Include in inventory cost | Expense rather than include in inventory |
|---|---|
| Purchase price, import duties and transport, net of trade discounts | Abnormal waste |
| Direct labour used in conversion | Storage, unless needed before a further production stage |
| A systematic allocation of fixed and variable production overheads | Administrative overheads not related to production |
| Other directly attributable costs | Selling and distribution costs |

**Important qualification:** Allocate fixed production overheads using normal capacity; do not lose this qualification when simplifying the slide.

**Visual idea:** Two clearly labelled areas, “Inventory cost” and “Expense,” each with one grouped native visual. Use an editable comparison table for the accounting content.

**Evidence:** S1, second and third bullets; normal-capacity qualification in “Why it matters / where it bites.”

## 3. Assign cost using the appropriate method

**Key message:** The nature of the inventory determines which cost-assignment methods are appropriate.

| Inventory type | Method |
|---|---|
| Non-interchangeable items or items specific to a project | Specific identification |
| Interchangeable items | First-in, first-out (FIFO) or weighted average |

- Apply the chosen formula consistently to inventories of similar nature and use.
- LIFO is prohibited under the framework described in this note.

**Visual idea:** A grouped decision tree: “Non-interchangeable or project-specific?” → Yes: “Specific identification”; otherwise: “FIFO or weighted average.” A separate editable label can state “LIFO prohibited.”

**Evidence:** S1, fourth bullet.

## 4. Calculate NRV: expected selling proceeds after remaining costs

**Key message:** NRV is more than an expected selling price.

`NRV = estimated selling price − estimated costs to complete − estimated costs to sell`

- Use the estimated selling price in the ordinary course of business.
- Deduct the costs still needed to complete the inventory.
- Deduct the estimated costs to sell it.

**Common mistake:** Comparing cost with selling price alone omits the completion and selling costs required by the NRV calculation.

**Visual idea:** One grouped native formula diagram with three labelled blocks and subtraction signs. Use symbols and labels only; no invented amounts.

**Evidence:** S1, fifth bullet. The common mistake follows directly from that definition.

## 5. Recognise a write-down and assess any later reversal

**Key message:** A fall in NRV can reduce inventory and profit; a later recovery can reverse the previous write-down within its limit.

| Situation | Accounting effect described in the source |
|---|---|
| NRV is below cost | Write inventory down to NRV; charge the write-down to profit or loss. |
| The conditions causing the write-down reverse | Reverse the prior write-down through profit or loss, subject to the original-cost ceiling. |

**Reversal limit:** A reversal cannot increase inventory above its original cost. It is a reversal of the earlier write-down, not permission to recognise an unrestricted upward revaluation.

**Visual idea:** One grouped native two-stage diagram: “NRV falls → Write-down” followed by “Conditions recover → Limited reversal.” Label the original-cost ceiling explicitly; do not add numerical data.

**Evidence:** S1, sixth bullet. The ceiling explanation paraphrases the source's original-cost limit.

## 6. Apply the decision sequence and check understanding

**Decision sequence**

1. Identify which costs qualify for inclusion.
2. Assign those costs using the appropriate method.
3. Estimate selling price, completion costs and selling costs to calculate NRV.
4. Compare cost with NRV at the appropriate item or group level.
5. Recognise any write-down; assess any subsequent reversal within the original-cost limit.

**Three quick checks**

| Question | Answer |
|---|---|
| Should selling costs be added to inventory cost? | No. They are excluded from inventory cost. Estimated costs to sell are also deducted when calculating NRV. |
| Is NRV simply the expected selling price? | No. Deduct estimated completion and selling costs. |
| Can a reversal raise inventory above original cost? | No. The original-cost ceiling remains. |

**Visual idea:** One grouped five-step checklist. Keep the questions and answers as editable text; answers may be placed in speaker notes for classroom discussion.

**Evidence:** Teaching synthesis of S1's six bullets and its discussion of item-level testing.

## Instructions for the Kimi slide workflow

This section is a presentation brief, not accounting content to display on a slide.

- Use sections 1–6 as the six-slide teaching sequence. Use the first slide for the topic title and measurement rule; no separate title-only slide is needed.
- Faithful paraphrasing and reorganisation are allowed. Preserve the formulas, exclusions, qualifications, method restrictions and reversal limit.
- Use only the accounting content supplied here. Do not invent numerical examples, exam statistics, additional accounting rules or comic dialogue.
- Add useful visuals proactively. Keep each topic visual as one selectable native group or one separate replaceable picture. Do not scatter its components into many loose objects.
- Keep the body text, tables, formulas and diagram labels native and editable. Keep body text separate from artwork.
- Put a short source note, “Source: supplied HKAS 2 concept note (16 June 2026),” on each slide or in its speaker notes. Full source metadata belongs in the source map, not on the teaching canvas.
- Check accounting fidelity, readability, grouped visuals and editability before delivery. The slide count is a teaching scope; it is not a workflow time limit.

### Ready-to-paste command

Run from the Kimi workflow repository root:

```text
/skill:demo-slides Use example_input/inventories-hkas2-knowledge.md to create six editable English slides for students beginning financial accounting. Follow the six teaching sections and their visual suggestions. Preserve the formulas, accounting qualifications and source attribution. Use native editable text, tables and diagrams, with each topic visual delivered as one grouped object or one separate picture. Review the deck before delivering the PPTX, matching preview and compact run report.
```

The Markdown file is self-contained as slide input. If you move it to a colleague's computer, replace the input path in the command with its new location.

The demo shortcut assumes a prepared editor, renderer, theme and visuals. See [the demo guide](../DEMO.md) for the 20-minute presenter agenda and rehearsal requirements. Use `/skill:create-slides` instead for an ordinary creation run with the full workflow records.

## Source record

**S1 — Supplied teaching note**

- Title: `Inventories - HKAS 2`.
- Source note date: `2026-06-16`.
- Provenance: This self-contained original instructional summary was prepared from a supplied accounting concept note. Its teaching sequence, quick checks and visual suggestions organise that material for a slide-workflow demonstration.
- The original teaching note and external accounting standards are not bundled with this example.
- This summary reflects the supplied note; it has not been independently updated against current standards. No new research was conducted for this sample.

Public demonstration input. This summary does not change the rights or permissions attached to the original teaching materials or external standards.
