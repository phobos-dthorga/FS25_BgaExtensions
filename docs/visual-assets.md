# Visual Assets

This document records the custom visual assets used by `FS25_BgaExtensions`.

## Current Assets

| Asset | Path | Purpose |
| --- | --- | --- |
| Mod icon | `mod/icon.dds` | FS25 mod list icon. |
| Wet biomass mash HUD icon | `mod/hud/fillTypes/hud_fill_phbWetBiomassMash.dds` | Custom HUD image for `PHB_WET_BIOMASS_MASH`, built with mipmaps to avoid runtime texture warnings. |

## Style

Visual additions should be small, legible at FS25 HUD sizes, and clear about what the material represents.

For now:

- use custom icons for Phobos-owned fillTypes
- use DDS with built mipmaps for runtime HUD textures
- keep PlanET store icons when the placeable reuses PlanET models through the declared dependency
- do not copy or edit dependency-owned icons
- avoid custom 3D decals, textures, or model edits until the gameplay modules settle

The active dry fuel yards intentionally reuse PlanET bunker store icons because they reuse PlanET bunker models through the declared dependency.

See `docs/model-fit-decisions.md` for retired or hidden placeables whose models do not currently match their gameplay role.

## Asset Licensing

Phobos-owned visual assets are covered by the repository asset license, CC BY-NC-SA 4.0, unless a file states otherwise.
