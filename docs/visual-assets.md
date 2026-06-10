# Visual Assets

This document records the custom visual assets used by `FS25_BgaExtensions`.

## Current Assets

| Asset | Path | Purpose |
| --- | --- | --- |
| Mod icon | `mod/icon.dds` | FS25 mod list icon, built as DXT5 DDS to avoid raw-format warnings. |
| Potato Washer Compat icon | `addons/FS25_BgaExtensions_PotatoWasherCompat/icon.dds` | Reuses the GBW mod icon for the optional add-on package, built as DXT5 DDS. |
| Orchards/Greenhouses Compat icon | `addons/FS25_BgaExtensions_OrchardsGreenhousesCompat/icon.dds` | Reuses the GBW mod icon for the optional add-on package, built as DXT5 DDS. |
| Data Pack Template icon | `examples/FS25_GBWDataPack_Template/icon.dds` | Reuses the GBW mod icon so the copyable template has a normal FS25 mod descriptor, built as DXT5 DDS. |
| Sweet Mash HUD icon | `mod/hud/fillTypes/hud_fill_gbwSweetMash.dds` | ChatGPT-generated custom HUD image for `GBW_SWEET_MASH`, built as PlanET-style DXT5 DDS to avoid runtime texture warnings. |
| Root Mash HUD icon | `mod/hud/fillTypes/hud_fill_gbwRootMash.dds` | ChatGPT-generated custom HUD image for `GBW_ROOT_MASH`, built as PlanET-style DXT5 DDS to avoid runtime texture warnings. |
| Green Mash HUD icon | `mod/hud/fillTypes/hud_fill_gbwGreenMash.dds` | ChatGPT-generated custom HUD image for `GBW_GREEN_MASH`, built as PlanET-style DXT5 DDS to avoid runtime texture warnings. |
| Residue Mash HUD icon | `mod/hud/fillTypes/hud_fill_gbwResidueMash.dds` | ChatGPT-generated custom HUD image for `GBW_RESIDUE_MASH`, built as PlanET-style DXT5 DDS to avoid runtime texture warnings. |
| Mash source images | `assets/source/fillTypes/hud_fill_gbw*Mash.png` | Transparent PNG sources used to build the DDS HUD icons. |

The previous fillType HUD art was preserved on branch `asset-backup/original-filltype-icons` before replacement.
The original pink chroma-key ChatGPT sources were preserved on branch `asset-backup/ai-chroma-source-v0.2.15.0`; `main` keeps only transparent sources and game-facing DDS files.

## Style

Visual additions should be small, legible at FS25 HUD sizes, and clear about what the material represents.

For now:

- use custom icons for GBW-owned fillTypes
- use PlanET-style DXT5 DDS files for runtime HUD textures and `modDesc.xml` root icons
- keep source artwork under `assets/source/` and build game-facing DDS files with `tools/build_filltype_icons.py`
- keep PlanET store icons when the placeable reuses PlanET models through the declared dependency
- do not copy or edit dependency-owned icons
- avoid custom 3D decals, textures, or model edits until the gameplay modules settle

`v0.2.19.1` log triage proved that root `icon.dds` files can produce the same raw-format warnings as fillType HUD textures. Validation now rejects uncompressed `modDesc.xml` icons, not only GBW-owned fillType HUD icons.

The active PlanET-style process and storage placeables intentionally reuse PlanET bunker store icons because they reuse PlanET bunker models through the declared dependency.

See `docs/model-fit-decisions.md` for retired or hidden placeables whose models do not currently match their gameplay role.

## Asset Licensing

GBW-owned visual assets are covered by the repository asset license, CC BY-NC-SA 4.0, unless a file states otherwise.

The mash-family icons were generated with ChatGPT image generation, then chroma-keyed locally to transparency and converted to DDS. The raw chroma-key sources are intentionally kept out of `main` to avoid mistaking them for game-facing assets. Prompt pattern:

```text
Square Farming Simulator 25 HUD icon source for a custom GBW mash fillType. Centered clean agricultural biogas substrate mash with material-specific crop cues, small fermentation bubbles, and subtle wet shine. Polished readable game icon, no text, no logos, no frame, no watermark. Perfectly flat solid #ff00ff background only for chroma-key removal, no shadows or gradients, subject must not contain #ff00ff.
```
