# Fast local decisions with Kimi or Pi

We borrow one idea from [LangChain's Jev article](https://www.langchain.com/blog/building-a-harness-with-jev): reserve generative reasoning for decisions that need it, and handle routine choices through a small structured interface. Jev itself is a classifier that can evaluate several questions together. This workflow uses **local rules and catalog search**, with no Jev model, TypeSafe key, LangChain dependency or external classification request.

## Keep the three roles

**Planner** makes one coherent slide plan, using supplied visual ideas and the prepared theme first. It can run one local batch lookup for unresolved topic blocks. **Executioner** builds the planned slides together. **Reviewer** independently verifies the actual output and reports concrete repairs. A lookup helper is a tool, not another agent.

| Routine decision | Cheap starting point | When the host model must decide |
|---|---|---|
| Supplied visual idea | Reuse it when supported by the source and brief | It conflicts with content, readability or editability |
| Explicit comparison, formula, branch or sequence | Use the corresponding prepared native diagram/layout | The source does not establish that relationship |
| Reusable topic artwork | Batch-search the local bank | Candidates need semantic assessment, or nothing matches |
| Source/candidate identity and native-object inventory | Run existing deterministic checks | Evidence is missing, differs or requires visual interpretation |
| Repeated optional design choice | Keep the choice already recorded in the plan | New requirements or a concrete review finding invalidate it |

Do not ask a new model question for every block or reopen settled choices. Record the chosen recipe ID or native visual plan beside its source location in the existing plan/`run.md`. Revisit affected choices when the source, brief, catalog or candidate changes. No extra decision agent or separate approval record is required.

## Batch visual-bank lookup

When a batch would help, the Planner writes a small tool input inside the private run directory. This is optional working data, not another required workflow record:

```json
{
  "schema_version": 1,
  "blocks": [
    {"id": "s1-tool", "query": "electronic calculator"},
    {"id": "s2-rule", "query": "inventory net realisable value"}
  ]
}
```

```powershell
python scripts/visual_bank.py batch runs/demo/visual-blocks.json --limit 3
```

Use the actual run path. Optional `block_type` restricts each block to an existing catalog tag; omit it if unsure. The helper reads the catalog once and returns every block, compact candidate IDs/usage cautions, explicit `match` or `no_match`, and the catalog hash. `--limit` controls shortlist size only. Scores rank lexical overlap; they are **not confidence probabilities**. Review each candidate's semantic fit and resolve its actual recipe from the catalog before drawing.

`no_match` leaves the visual task open: plan a suitable native group or prepared picture, or resolve a real content/feasibility conflict through `question_me`. It never means skip required visual coverage. The accounting source already supplies six visual ideas, so it often needs no lookup at all.

## Evidence and limits

Local matches never authorize content edits, satisfy required questions, select a different model, approve tool calls or pass a deck. Source preservation, native editability, grouping and all-slide independent review remain required. Use the existing run record for actual timing; this change reduces repeated decisions but does not establish a 20-minute generation benchmark or Jev-level inference speed.

The [Pi package](../hosts/pi/README.md) also uses a fixed, user-requested routing table: content tasks inherit the selected main model (GLM 5.3 Flash by default, or GLM 5.3) and visual tasks always use GLM 5.3 Flash. Role and task kind select the model without another model call. This explicit host policy is separate from visual-search scores. Missing model/image support is reported; lexical matches never change the route or grant permission to skip checks.
