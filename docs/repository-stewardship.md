# Repository Stewardship

## Current Stewardship State

- Public GitHub repository created.
- Initial mod scaffold committed.
- Upstream FS25 guidance documented with attribution and license boundary.
- Issue templates and pull request template are present.
- Dual licensing added to match nearby Phobos Project Zomboid mod repositories.
- Packaging script and GitHub release helper are present.
- GitHub pre-releases are used as the historical timeline for shipped versions.
- Performance targets and decisive-action rules are documented.
- GitHub CI validates source, builds a package artifact, and validates the package.
- Dependabot is configured to watch GitHub Actions versions.
- Visual asset policy and the first custom fillType HUD icon are documented.
- Dry fuel yard storage is offered in small, medium, and large PlanET-style variants.
- Runtime smoke-test and log-triage instructions are documented for disposable-save testing.

## Still To Decide

- Local FS25 reference paths for API validation.
- Branch protection once the project has more contributors.
- Whether release creation should remain local via `tools/release.ps1` or move fully to GitHub Actions.

## License Decision

This repository follows the established pattern from nearby Phobos Project Zomboid mod repositories:

- Code, XML definitions, tools, and documentation: MIT License.
- Assets, textures, icons, images, models, and other media: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.

If a future file needs different treatment, document that exception near the file and in the README.
