# Start here: build on this workflow

Audience: a coding agent extending this repository, including Pi. This is a development handoff, not a request to start editing a lecture deck.

Presenters and colleagues trying the workflow should start with [DEMO.md](../DEMO.md). Host-specific Kimi resources are under [hosts/kimi](../hosts/kimi/README.md); preserve shared workflow rules when maintaining that package.

## Read in this order

1. [Shared rules](../AGENTS.md) and [defaults](../workflow.defaults.json): the professor's constraints.
2. [Architecture](architecture.md): responsibilities, execution sequence, implemented components and gaps.
3. [Contracts](contracts.md): run artifacts, questions, handoffs and delivery gates.
4. [Host adapter](host-adapter.md): map the workflow to actual tools. For Pi, also read [Pi integration](pi-integration.md).
5. Load only the affected role, skill and component documentation before changing it.

For a slide-improvement request, use [ppt-improve](../skills/ppt-improve/SKILL.md) instead. A request to improve this software does not authorize changing previous slide deliverables.

For a new presentation from materials, use [materials-to-deck](../workflows/materials-to-deck/README.md). Its creation-mode contracts allow faithful synthesis and require claim/source review. Existing-deck contracts, original-PPTX baselines and hard-coded improvement role paths cannot be reused unchanged for that mode. Both modes share exactly the same three logical roles.

## Preserve the design decisions

- Exactly three logical roles: the host is **Planner**, **Executioner** writes the deck, **Reviewer** assesses it independently and writes reports. A backend, visual bank, renderer or skill is a procedure/resource, not a fourth agent.
- Exact content preservation is the default. Permission to redesign or add visuals is not permission to rewrite, summarize, invent chart data or alter meaning.
- Add useful visuals proactively across meaningful topic blocks. Each topic visual is delivered as one existing native group or one separate picture. Native children remain editable; body text stays separate except diagram labels. Verify the assembled object, not merely the availability of its parts.
- `question_me` belongs to the Planner. Reuse answers, resolve required ambiguities, and continue independent work where possible. A missing answer never becomes consent.
- Local runs have no workflow time controls. The 20-minute, 5–6-slide demo is a presenter's constraint, not a scheduler setting or quality exception. Its opt-in [compact procedure](../skills/slide-demo/SKILL.md) replaces the full record chain without weakening required gates.
- Preserve source files and old evidence. Each candidate needs content, native-object, visual, requirements and file checks tied to its actual hash.
- PDF reconstruction needs its own comparison against the original PDF. The general PDF importer is still unimplemented.

## What another agent should build next

Choose the item that matches the user's development request; this list is a dependency guide, not authorization to implement everything.

| Extension | Reuse | Concrete acceptance |
|---|---|---|
| Extend/qualify Pi orchestration | [Native Pi package](../hosts/pi/README.md), portable prompts and contracts | Rehearse the requested models on a real deck; extend mechanical record/delivery enforcement without replacing independent quality judgment |
| Portable editing backend | Guard, source-bound operation model, native checks | Qualify no-edit fidelity, preserve protected objects, export grouped topic visuals and matching renders on a real test deck |
| Machine-validated run records | Documented contracts | Add explicit schema versions and migrations; reject missing evidence; read older runs without rewriting them |
| Broader visual bank | Catalog, recipes, grouping helper | Add preview/provenance and semantic fit guidance; deliver one selectable parent; test the exported object |
| PDF intake implementation | PDF reconstruction procedure | Preserve page order/content; flag uncertain extraction; independently review original PDF versus reconstructed PPTX before improvement |

The included structured backend is intentionally narrow. Its rejection of groups or complex objects is not a reason to flatten them, and it cannot insert the visual bank's artwork. Select or build a qualified backend for the requested source; see [backend guide](backend-guide.md).

## Development completion

Explain the requested change and identify the affected files before editing. Preserve existing contracts where possible. When an interface changes, update its consumers, examples and acceptance checks together. Label new design-only interfaces as unimplemented until code and evidence exist.

Run verification appropriate to the change. For documentation, check references, examples, actual CLI flags and skill loading. For executable changes, exercise the affected behavior and report any integration tests unavailable in the host. A previous private-deck run is useful evidence for that deck and environment, not a portable test fixture or proof of general PDF support.

Return changed files, verification results, limitations and the next concrete dependency. Keep changes local unless the user requests a commit, installation or publication.

## Copyable development prompt

Use [examples/build-with-agent.md](../examples/build-with-agent.md) as the initial message in another agent. It makes the distinction between extending the workflow and running it explicit.
