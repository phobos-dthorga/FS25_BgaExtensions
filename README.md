# FS25_BgaExtensions

Farming Simulator 25 mod project for extending biogas plant gameplay.

## Status

This repository is the staging ground for early design and implementation. The mod shape is intentionally minimal until the first gameplay scope is decided.

## Working Goals

- Explore BGA-related gameplay extensions for Farming Simulator 25.
- Keep the mod source clean, versioned, and package-ready.
- Document design decisions as they are made.

## Repository Layout

- `mod/` - Farming Simulator mod source files.
- `docs/` - design notes, references, and planning documents.
- `tools/` - local helper scripts for packaging or maintenance.

## Current Design Direction

The first implementation path is a registry-driven biomass pipeline for expanded BGA inputs. See `docs/biomass-crop-ranking.md` and the draft registry at `mod/config/biomassCropRegistry.xml`.

## Author

phobosgekko

## License

This project uses dual licensing:

- **Code** (Lua scripts, XML definitions, tools, and documentation): [MIT License](LICENSE)
- **Assets** (textures, icons, images, models, and other media): [CC BY-NC-SA 4.0](LICENSE-CC-BY-NC-SA.txt)

Forks and addons are encouraged. Code is permissively licensed for integration. Assets are protected from commercial use and must preserve attribution and ShareAlike terms.
