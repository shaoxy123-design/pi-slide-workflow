# Attribution and release contents

The [MIT license](LICENSE) covers the project-authored workflow instructions,
utilities, original native visual recipes, their rendered previews, and the
synthetic [demo material](examples/demo-materials.md), and original instructional
summaries in [example_input/](example_input/) included in this release.

The [HKAS 2 inventory example](example_input/inventories-hkas2-knowledge.md) is
a self-contained instructional summary prepared from a supplied teaching note.
Its source title and date are retained for attribution. The original note and
external accounting standards are not bundled or relicensed by this project.

The workflow draws on planning and independent review ideas from
[claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow)
and layout/reference-analysis ideas from
[PPTAgent](https://github.com/icip-cas/PPTAgent). The specific design adaptations
are recorded in [reference adaptation](docs/reference-adaptation.md). These
references do not make their source code or assets part of this release.

[Pi](https://github.com/earendil-works/pi), [Kimi Code](https://github.com/MoonshotAI/kimi-code), PowerPoint and other
authoring/rendering tools are separately obtained dependencies governed by
their own terms. The optional backend imports `@oai/artifact-tool` only when
that runtime is available; its implementation is not bundled or relicensed.
The host packages contain workflow skills, launchers and adapter code, not host
executables, models, credentials or a slide-rendering application. The Pi package
derives its shared workflow from [Kimi Slide Workflow](https://github.com/shaoxy123-design/kimi-slide-workflow)
and retains that project's MIT notice. The [local decision approach](docs/fast-decisions.md)
borrows Jev's intuition without including Jev code, models or an API dependency.

User-supplied decks, papers, datasets, portraits, logos, run history and local
generated artwork are excluded from the public release. Their owners' rights
and applicable terms are unchanged. Adding the MIT license to this workflow
does not license a user's source materials or third-party assets.

Product and project names identify compatible tools and references; this is
an independent community workflow with no official affiliation to Moonshot AI,
Z.ai, Pi or Jev.
