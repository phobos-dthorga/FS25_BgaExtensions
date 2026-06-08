# Repository Stewardship

## Current Stewardship State

- Public GitHub repository created.
- Initial mod scaffold committed.
- Upstream FS25 guidance documented with attribution and license boundary.
- Issue templates and pull request template are present.
- Dual licensing added to match nearby Phobos Project Zomboid mod repositories.
- Packaging script and GitHub release helper are present.
- GitHub pre-releases are used as the historical timeline for shipped versions.
- Release pages are kept as public-facing changelogs; smoke-test checklists and local handoffs belong in GitHub Issues or internal docs.
- New issues are created only for majorly new or unique topics; otherwise update the existing issue's version/checklist/status.
- Performance targets and decisive-action rules are documented.
- GitHub CI validates source, builds package artifacts, validates packages, and writes package-set metadata plus SHA-256 hashes.
- `tools/package_manifest.json` is the active package list for core and add-on CI builds.
- Dependabot is configured to watch GitHub Actions versions.
- Visual asset policy and the first custom fillType HUD icon are documented.
- Original fillType HUD artwork was preserved on branch `asset-backup/original-filltype-icons` before the ChatGPT-generated replacement.
- Raw pink chroma-key AI icon sources are kept off `main`; the v0.2.14.0 source was preserved on branch `asset-backup/ai-chroma-source-v0.2.14.0`.
- Dry fuel yard storage is offered in medium and large PlanET-style variants; the small variant is retained only as packaged compatibility XML because its rotating blade does not fit passive storage.
- Runtime smoke-test and log-triage instructions are documented for disposable-save testing.
- Energy carriers are split by building family before adding methane, electricity, or extra combustion routes.
- Phobos placeables are grouped into custom construction tabs inside vanilla FS25 categories.
- Intake and dry fuel yard storage capacities were doubled as a logistics-quality pass without changing recipe yields.
- Runtime HUD textures use DDS with mipmaps after `v0.2.6.0` exposed raw PNG performance warnings.
- Wet/root/produce processing is split into Wet Substrate Prep so biomass intakes remain focused and under the recipe-count soft target.
- Straw pelletizing is split into Dry Fuel Processor so biomass intakes remain BGA-focused and dry fuel yards remain storage-only.
- Potato Washer compatibility is the first separate add-on package, proving the optional-fillType pattern without weakening core XML.
- Orchards/Greenhouses compatibility adds organic waste and compost routing as a second provider-specific add-on.

## Still To Decide

- Local FS25 reference paths for API validation.
- Branch protection once the project has more contributors.
- Whether release creation should remain local via `tools/release.ps1` or move fully to GitHub Actions.

## License Decision

This repository follows the established pattern from nearby Phobos Project Zomboid mod repositories:

- Code, XML definitions, tools, and documentation: MIT License.
- Assets, textures, icons, images, models, and other media: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.

If a future file needs different treatment, document that exception near the file and in the README.
