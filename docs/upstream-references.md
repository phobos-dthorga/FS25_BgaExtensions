# Upstream References

## FS25_SoilFertilizer Guidance

The `CLAUDE.md` file from `TheCodingDad-TisonK/FS25_SoilFertilizer` is an important external reference for this project.

- Document: https://github.com/TheCodingDad-TisonK/FS25_SoilFertilizer/blob/main/CLAUDE.md
- Repository: https://github.com/TheCodingDad-TisonK/FS25_SoilFertilizer
- Author: TisonK / TheCodingDad-TisonK
- License observed on 2026-06-06: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International.
- License URL: https://creativecommons.org/licenses/by-nc-nd/4.0/

## Use Boundary

The upstream license allows sharing the original unmodified work for non-commercial purposes with attribution, but it does not allow distributing modified derivatives. For that reason, this repository does not include a copy or adapted version of the upstream `CLAUDE.md`.

Use the source as an external reference. When the source provides a useful lesson, re-check it against FS25 documentation, local references, or direct testing before implementing.

## Lessons To Carry Forward

- Verify FS25 Lua APIs against current references before writing code.
- Treat local LUADOC and proven working FS25 scripts as stronger evidence than model memory.
- Keep module loading order explicit and intentional.
- Keep hooks compatible with other mods and provide cleanup where possible.
- Separate UI presentation from authoritative gameplay state changes.
- Treat multiplayer, save/load, and missing-data paths as normal cases, not edge cases.
- Use constants and schema-like definitions for settings, XML keys, fill types, and tuning values.
- Keep localization and user-facing text organized from the start.
- Check game logs as part of the development loop.

