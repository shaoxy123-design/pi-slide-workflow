# Slide workflows in Kimi Code + K3

**Using the Windows GUI?** Open the whole repository in Kimi Code Desktop and follow [DESKTOP.md](DESKTOP.md), including its plain copyable prompt. The launcher below starts the CLI and does not configure Desktop's model or skill discovery.

For the **CLI**, open the whole repository in PowerShell and start:

```powershell
.\hosts\kimi\start.ps1
```

For the prepared six-slide demo, paste into Kimi:

```text
/skill:demo-slides Use example_input/inventories-hkas2-knowledge.md to create 6 slides.
```

This opt-in path uses one ready Markdown/plain-text source, prepared tools and existing visuals. It keeps one `run.md` for the plan, source map, requirements and verbatim independent review. Prepare and rehearse before presenting; aim for a reviewed result by minute 15 of a 20-minute slot, including model waits. The route has not been benchmarked and fresh inference timing is not guaranteed. At minute 15 the presenter may show a labelled, previously reviewed rehearsal deck while the live run continues.

For ordinary work, choose one command and supply the files:

```text
/skill:improve-slides Improve "C:/path/lecture.pptx"; keep the content unchanged.
/skill:create-slides Use examples/demo-materials.md to create 5 slides for university colleagues.
```

For your own new deck, replace the sample path and describe the audience and objective. Local work has no processing deadline or fixed repair cap.

## The three roles

| Workflow role | Native Kimi Code binding | Responsibility |
|---|---|---|
| **Planner** | Main Kimi session | Understand the brief, ask necessary questions, dispatch work and deliver |
| **Executioner** | Built-in `Agent` type `coder` | Build/edit the PPTX, create grouped visuals and produce evidence |
| **Reviewer** | Built-in `Agent` type `explore` | Independently inspect sources, the candidate, previews and native objects; return findings |

Use only these three logical roles. Reuse the Executioner for repairs and return the revised candidate to the Reviewer. The demo skill binds these profiles directly using the shared demo procedure; ordinary workflows use the handoff instructions in `agents/`. Those files do not register new agent types. `explore` has image reading and read-only shell instructions, but its shell access is **not a filesystem sandbox**. It returns the report to the Planner, which saves it verbatim.

## What stays simple

- **Improve:** preserve exact existing content unless the user authorizes specific changes.
- **Create:** faithfully select and summarize supplied material, with source locations for claims and data.
- **Both:** native editable core content; one actual group or picture per topic visual; useful visual coverage; independent review before delivery.
- **Questions:** Planner maps `question_me` to Kimi's `AskUserQuestion`, or normal conversation if needed. Required answers remain pending until answered.

The three short native skills load their shared procedure on demand. The demo reads only `AGENTS.md` and `skills/slide-demo/SKILL.md` as workflow instructions; ordinary creation and improvement retain their full contracts. No global skill installation is needed.

## Setup check and model

```powershell
.\hosts\kimi\start.ps1 -Check
```

The launcher checks the installed CLI flags and finds the requested K3 alias/model in the usual quoted TOML table format, then uses `--model kimi-code/k3 --skills-dir <this-package>/skills`. `-Check` reports only `K3_ALIAS_AND_FLAGS_CHECKED`; it does not validate the entire configuration, credentials, skill loading or deck tools. It does not install software, sign in, copy credentials or change global configuration. Sign in to Kimi Code normally before the demo if needed. An alternate executable is supported with `-KimiPath`; `-ModelAlias` accepts another configured alias only if its actual model is a recognized K3 ID.

On the checked installation (**Kimi Code 0.27.0**), the selected primary model is inherited by the built-in workers; no secondary-model pool exists. Newer versions can have a secondary-model pool or forced worker model. The Planner must verify the effective model and thinking settings; a hidden model parameter does not prove primary-model inheritance. Use `model: "primary"` only when advertised, and never substitute a different model silently. Configuration validation is not authentication or a live inference test. See [current model binding](https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/config-files.html#secondary-model).

The CLI launcher was checked against **Kimi Code 0.27.0**; that check does not validate a newer Desktop runtime. Current documentation includes custom `--agent`/`--agent-file` support that the checked CLI does not expose, so the package uses its supported built-in bindings. The Desktop guide separately documents the current GUI entry point and requires verifying available tools there.

## Files and prerequisites

```text
hosts/kimi/
  DESKTOP.md                  # Windows GUI setup and plain demo prompt
  start.ps1                    # Safe interactive launch; -Check makes no model request
  skills/improve-slides/SKILL.md
  skills/create-slides/SKILL.md
  skills/demo-slides/SKILL.md   # Prepared 5–6-slide creation demo
  agents/planner.md            # Shared Kimi handoff procedure
  agents/executioner.md
  agents/reviewer.md
```

Kimi supplies agent tools, not a PowerPoint authoring/rendering engine. Before a real demo, qualify the local tools in [backend guide](../../docs/backend-guide.md): one editor, one renderer and native-object inspection. Prepare the theme/fonts and suitable native visual recipes or artwork. The repository's structured editor supports limited existing-PPTX operations; it is not a general deck creator. Codex-only presentation/image tools do not automatically exist in Kimi. The demo performs no installs, research, OCR or new image generation. Required features needing them require preparation or a scoped decision to use the ordinary workflow; missing evidence cannot pass review.

Deliver a reviewed `.pptx`, matching preview and report from a unique `runs/<run-id>/` directory. In demo mode, `run.md` combines the source map/report and preserves the raw Reviewer response; ordinary creation has its full source map and reports. Read [the demo guide](../../DEMO.md) for the presenter flow and [host adapter contract](../../docs/host-adapter.md) for extension details.

## Reference and validation scope

Verified 2026-09-15 against the installed executable and official [skill format and commands](https://moonshotai.github.io/kimi-code/en/customization/skills), [agents](https://moonshotai.github.io/kimi-code/en/customization/agents), [K3 configuration](https://moonshotai.github.io/kimi-code/en/configuration/config-files) and [CLI overrides](https://moonshotai.github.io/kimi-code/en/configuration/overrides.html). The [legacy repository](https://github.com/MoonshotAI/kimi-cli) directs new users to Kimi Code.

Local validation checks the launcher and native skill syntax using the installed executable's embedded parser, without inference. Private test records are not included in the public source release. These checks do not establish live role execution or deck acceptance; no K3 inference or deck-generation benchmark is claimed by this package setup.
