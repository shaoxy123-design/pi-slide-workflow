# Demo on another Windows PC

The default is **GLM 5.3 Flash for Planner, Executioner and Reviewer**, in separate role contexts. GLM 5.3 is an optional main model. Clone the repository; configure credentials locally on the destination PC.

## 1. Prepare before the demo

Install Git for Windows (including Git Bash), Node.js **22.19 or newer**, Python 3 for the content checker, and Pi. The adapter was checked against **Pi 0.84.2**; a matching installation is:

```powershell
npm install -g @earendil-works/pi-coding-agent@0.84.2
git clone https://github.com/shaoxy123-design/pi-slide-workflow.git
cd pi-slide-workflow
```

If Pi is already installed, check that version's SDK with the preflight below before changing anything. These are preparation commands, not actions performed by the launcher. This adapter exposes Bash to workers, so keep Git Bash available even when starting it from PowerShell. [Pi Windows setup](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/windows.md)

Configure your own provider using Pi's normal `/login` flow. Choose the provider matching your account: the launcher defaults to `zai`; use `-Provider zai-coding-cn` for a configured China coding-plan provider. Keep that selection consistent on check and launch. Verify access to the exact `glm-5.3-flash` ID; a similarly named model is not a substitute. Use the endpoint for your account and plan. [Pi models and authentication](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md)

The tested Pi 0.84.2 catalog lacked Flash. If your check reports it missing, use Pi's custom-model mechanism in **`~/.pi/agent/models.json`**, outside this checkout. The model entry must identify `glm-5.3-flash`, enable `reasoning: true`, and include both `text` and `image` in `input`. Follow your provider's API compatibility settings and limits; configuration metadata alone does not establish account access or working image inference. GLM 5.3 is only required if selected as main. The launcher never writes this configuration or copies credentials.

Prepare one authoring backend, one renderer and a native-object inspection method. For a Windows creation demo, a possible stack is Python with `python-pptx` for native slide construction and installed Microsoft PowerPoint for rendering/edit checks; qualify the actual stack before presenting. A fresh clone contains **workflow instructions and visual recipes**, not those applications or a universal deck builder. Pi does not inherit Codex's bundled tools. See the [backend guide](../../docs/backend-guide.md).

## 2. Check and launch

From the cloned repository in PowerShell:

```powershell
.\hosts\pi\start.ps1 -Check
.\hosts\pi\start.ps1
```

The check must report `ready: true`. It reads installed SDK/model metadata without accessing the auth store or calling a model. It does **not** test credentials, inference or rendering. The launcher resolves files relative to the clone and Pi through your PATH; there are no original-computer paths to copy. For a nonstandard npm location, supply `-PiPath` and `-PiPackagePath` with paths on this PC.

To use GLM 5.3 as main instead:

```powershell
.\hosts\pi\start.ps1 -MainModel glm-5.3 -Check
.\hosts\pi\start.ps1 -MainModel glm-5.3
```

Content workers follow that main model; visual workers remain Flash. Keep thinking enabled (`high` is the default). Use a new run after changing the main model. If a local PowerShell policy blocks a downloaded script, follow the PC's approved script-running procedure; no global policy change is part of this setup.

## 3. Rehearse the six-slide example

Paste into the launched Pi session:

```text
/skill:demo-slides Use example_input/inventories-hkas2-knowledge.md to create 6 slides.
```

Confirm that `slide_worker` and `question_me` are present. Rehearse through the independent Reviewer, including Flash reading actual slide images, then open the reviewed PPTX and try editing native text and moving a topic visual on a copy. This is the point at which account access, model image support and the slide toolchain are tested together.

Use the reviewed rehearsal deck as a clearly labelled fallback. Five to six slides and prepared visual choices keep the demo compact; 20 minutes is the presenter's agenda, not a runtime guarantee or a reason to skip review. The ordinary local workflow has no time cutoff. [Presenter guide](../../DEMO.md)

Private inputs, run/session records, local model configuration and credentials are excluded by `.gitignore`. Put private materials under `inputs/` and outputs under `runs/`; keep `example_input/` for intentionally public teaching examples.
