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

## Current Design Direction

The first playable implementation is a small PlanET-compatible biomass intake module. It converts selected vanilla biomass inputs into the internal feedstocks used by `FS25_PlanET_BGA_Modular`, can pelletize straw into `STRAW_PELLETS` for the Straw Harvest HALLSYS Pellet Heat Plant, and handles vanilla `WOODCHIPS` as a combustion-yard storage material.

Maize+/MaizePlus integration is parked until a production-ready FS25 release is installed and explicitly selected as a target. Corn Production Pack remains observation-only.

The broader design remains registry-driven for later optional integrations. See `docs/implementation-approach.md`, `docs/integration-strategy.md`, `docs/biomass-crop-ranking.md`, `docs/conversion-process.md`, and the draft registry at `mod/config/biomassCropRegistry.xml`.

## Author

phobosgekko

## License

This project uses dual licensing:

- **Code** (Lua scripts, XML definitions, tools, and documentation): [MIT License](LICENSE)
- **Assets** (textures, icons, images, models, and other media): [CC BY-NC-SA 4.0](LICENSE-CC-BY-NC-SA.txt)

Forks and addons are encouraged. Code is permissively licensed for integration. Assets are protected from commercial use and must preserve attribution and ShareAlike terms.
