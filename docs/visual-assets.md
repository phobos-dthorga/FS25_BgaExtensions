# Visual Assets

This document records the custom visual assets used by `FS25_BgaExtensions`.

## Current Assets

| Asset | Path | Purpose |
| --- | --- | --- |
| Mod icon | `mod/icon.dds` | FS25 mod list icon. |
| Potato Washer Compat icon | `addons/FS25_BgaExtensions_PotatoWasherCompat/icon.dds` | Reuses the Phobos mod icon for the optional add-on package. |
| Orchards/Greenhouses Compat icon | `addons/FS25_BgaExtensions_OrchardsGreenhousesCompat/icon.dds` | Reuses the Phobos mod icon for the optional add-on package. |
| Wet biomass mash HUD icon | `mod/hud/fillTypes/hud_fill_phbWetBiomassMash.dds` | ChatGPT-generated custom HUD image for `PHB_WET_BIOMASS_MASH`, built as DDS with mipmaps to avoid runtime texture warnings. |
| Wet biomass mash source image | `assets/source/fillTypes/hud_fill_phbWetBiomassMash.png` | Transparent PNG source used to build the DDS HUD icon. |

The previous fillType HUD art was preserved on branch `asset-backup/original-filltype-icons` before replacement.
The original pink chroma-key ChatGPT source was preserved on branch `asset-backup/ai-chroma-source-v0.2.14.0`; `main` keeps only the transparent source and the game-facing DDS.

## Style

Visual additions should be small, legible at FS25 HUD sizes, and clear about what the material represents.

For now:

- use custom icons for Phobos-owned fillTypes
- use DDS with built mipmaps for runtime HUD textures
- keep source artwork under `assets/source/` and build game-facing DDS files with `tools/build_filltype_icons.py`
- keep PlanET store icons when the placeable reuses PlanET models through the declared dependency
- do not copy or edit dependency-owned icons
- avoid custom 3D decals, textures, or model edits until the gameplay modules settle

The active PlanET-style process and storage placeables intentionally reuse PlanET bunker store icons because they reuse PlanET bunker models through the declared dependency.

See `docs/model-fit-decisions.md` for retired or hidden placeables whose models do not currently match their gameplay role.

## Asset Licensing

Phobos-owned visual assets are covered by the repository asset license, CC BY-NC-SA 4.0, unless a file states otherwise.

The wet biomass mash icon was generated with ChatGPT image generation, then chroma-keyed locally to transparency and converted to DDS. The raw chroma-key source is intentionally kept out of `main` to avoid mistaking it for a game-facing asset. Prompt:

```text
Square Farming Simulator 25 HUD icon for a custom fillType named Wet Biomass Mash. Centered clean agricultural biogas icon: green plant mash, teal wet droplet, small fermentation bubbles, subtle leaf swirl. Polished readable game icon, no text, no logos, no frame, no watermark. Perfectly flat solid #ff00ff background only for chroma-key removal, no shadows or gradients, subject must not contain #ff00ff.
```
