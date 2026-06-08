# FS25_BgaExtensions

Farming Simulator 25 mod project for extending biogas plant gameplay.

## Status

This repository is the staging ground for early design and implementation. The mod shape is intentionally minimal while the first gameplay loop is proven.

## Working Goals

- Explore BGA-related gameplay extensions for Farming Simulator 25.
- Keep the mod source clean, versioned, and package-ready.
- Document design decisions as they are made.

## Repository Layout

- `mod/` - Farming Simulator mod source files.
- `docs/` - design notes, references, and planning documents.
- `tools/` - local helper scripts for packaging or maintenance.
- `addons/` - optional compatibility add-ons with their own provider dependencies.

## Release Rhythm

Each shipped mod version should get a GitHub release and retain its old releases as the project timeline. See `docs/release-process.md`; `tools/release.ps1` builds a versioned package, creates a `vX.Y.Z.W` tag, and publishes a GitHub prerelease by default.

## Current Design Direction

The current implementation provides PlanET-compatible biomass intake modules, a Wet Substrate Prep module, a Dry Fuel Processor, and scaled dry fuel yards. The intake modules convert forage, manure, and low-grade straw routes into the internal feedstocks used by `FS25_PlanET_BGA_Modular`; Wet Substrate Prep handles wet/root/produce crops before handing them to PlanET as beet-cut substrate; Dry Fuel Processor converts straw into `STRAW_PELLETS`; and the dry fuel yards store `WOODCHIPS` and `STRAW_PELLETS` for heat-plant logistics.

Maize+/MaizePlus integration is parked until a production-ready FS25 release is installed and explicitly selected as a target. Corn Production Pack remains observation-only.

The broader design remains registry-driven for later optional integrations. Optional add-ons are shipped separately so provider fillTypes such as `POTATO_WASHED`, `ORGANICWASTE`, and `COMPOST` never enter core XML without their providers. See `docs/implementation-approach.md`, `docs/integration-strategy.md`, `docs/dependency-contract.md`, `docs/guarded-compatibility.md`, `docs/performance-targets.md`, `docs/measurement-and-automation.md`, `docs/runtime-smoke-tests.md`, `docs/issue-management.md`, `docs/energy-carrier-strategy.md`, `docs/construction-menu-categories.md`, `docs/model-fit-decisions.md`, `docs/visual-assets.md`, `docs/known-log-lines.md`, `docs/biomass-crop-ranking.md`, `docs/conversion-process.md`, and the draft registry at `mod/config/biomassCropRegistry.xml`.

## Author

phobosgekko

## License

This project uses dual licensing:

- **Code** (Lua scripts, XML definitions, tools, and documentation): [MIT License](LICENSE)
- **Assets** (textures, icons, images, models, and other media): [CC BY-NC-SA 4.0](LICENSE-CC-BY-NC-SA.txt)

Forks and addons are encouraged. Code is permissively licensed for integration. Assets are protected from commercial use and must preserve attribution and ShareAlike terms.
