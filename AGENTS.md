# FS25_BgaExtensions Agent Notes

These notes guide AI/code-agent work in this repository.

## Source Awareness

The repository `TheCodingDad-TisonK/FS25_SoilFertilizer` contains a useful `CLAUDE.md` with FS25 modding practices and hard-won implementation notes:

- Source: https://github.com/TheCodingDad-TisonK/FS25_SoilFertilizer/blob/main/CLAUDE.md
- Author: TisonK / TheCodingDad-TisonK
- License observed on 2026-06-06: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International, via that repository's `LICENSE` file.

Because the upstream license includes NoDerivatives, do not copy, remix, or adapt that document into this repository. Use it as an external reference only, with attribution.

## FS25 API Rule

Do not guess FS25 Lua APIs from memory. Before adding or changing any FS25 Lua API call, class usage, lifecycle hook, specialization, GUI call, save/load call, network event, economy call, or placeable interaction, verify against local FS25 references or proven source examples.

If local references are not yet configured for this repository, pause and ask for their location before implementing API-sensitive code.

## Known FS25 Constraints

Read `docs/fs25-engine-constraints.md` before designing custom fill types, bales, animal feed integration, forage mixer recipes, tippable heaps, or map-owned XML integrations.

Current caution: a standard mod may not be able to globally add custom ingredients to map-owned animal food/forage mixer data, and custom bales for mod-defined fill types may require map-native integration because of FS25 bale/fillType loading order behavior.

## Local References To Configure

Add project-specific paths here once available:

- FS25 Community LUADOC:
- FS25 Lua scripting examples:
- Farming Simulator 25 mods folder:
- Farming Simulator 25 log file:
- GIANTS Editor:

## Architecture Preferences

- Keep `modDesc.xml` as the explicit entry point for Lua source files.
- Prefer a small `src/main.lua` loader that sources modules in dependency order.
- Load utilities and constants before gameplay systems.
- Keep gameplay/business rules separate from UI.
- Use constants for fill types, production names, XML keys, event names, and tuning values.
- Keep modules focused and small enough to review comfortably.
- Prefer append/prepend hook patterns that preserve compatibility with other mods.
- Add cleanup paths for any hook, event, or global state installed by the mod.

## Multiplayer And Save Safety

- Treat multiplayer as a first-class concern when changing gameplay state.
- Server-authoritative changes should be performed on the server and synced to clients.
- Client UI should request changes; it should not directly mutate authoritative state.
- Save/load XML changes must be version-conscious and resilient to missing values.

## Implementation Discipline

- Check the game log after test launches.
- Document any API uncertainty instead of filling gaps with invented calls.
- Prefer narrow commits with clear messages.
- Avoid direct pushes to stable branches once a development branch workflow is introduced.
