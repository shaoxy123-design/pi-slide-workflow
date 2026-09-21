# Development handoff prompt

Read `AGENTS.md`, `README.md`, `workflow.defaults.json` and `docs/agent-handoff.md`.
I want you to build on this existing workflow. Use `docs/architecture.md` and
`docs/contracts.md` as the design reference, and inspect actual code before
claiming a capability exists. For Pi integration, read `docs/pi-integration.md`
and `docs/host-adapter.md` and verify the installed Pi version and APIs.

Preserve exactly three logical roles: Planner, Executioner, Reviewer. Keep
content unchanged by default, native core objects editable, and useful topic
visuals delivered as one existing group or picture each. Preserve the Planner's
question_me behavior and the absence of local time controls.

First identify the implemented pieces, missing dependencies and the smallest
coherent change that fulfills my requested extension. Then implement that
authorized change, update its documentation/examples and verify its behavior.
Keep host-specific integration separate from portable role/skill instructions.
Do not treat a design-only contract or a historical successful run as a working
adapter. Report limitations and the evidence for completion accurately.

If I have not specified the extension to build, ask me for that scope after
inspecting the repository. Do not start a deck-improvement run or modify prior
deliverables merely because they are present here.
