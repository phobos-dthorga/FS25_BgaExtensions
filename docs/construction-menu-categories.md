# Construction Menu Categories

This document records how `FS25_BgaExtensions` should group its placeables in the FS25 construction menu.

## Observed Pattern

The local Corn Production Pack uses a clean construction-tab pattern:

- declare a tab in `modDesc.xml` under `<constructionCategories>`
- point each placeable store brush at that tab with `<brush><tab>...</tab></brush>`
- keep the vanilla construction category, such as `production` or `buildings`

That is enough for the current Phobos need. The Corn Production Pack archive also contains a generic Lua helper for adding construction categories and tabs, but the active `modDesc.xml` uses normal tab declarations. Do not add a Lua hook unless a future FS25 test proves the built-in tab declaration is insufficient.

## Current Phobos Tabs

| Vanilla category | Phobos tab | Purpose |
| --- | --- | --- |
| `production` | `phobosBgaProduction` | Biomass intake and BGA feedstock process buildings. |
| `production` | `phobosBgaCompatibility` | Optional compatibility add-on process buildings. |
| `production` | `phobosFuelProcessing` | Dry fuel processing buildings such as straw pelletizing. |
| `buildings` | `phobosFuelStorage` | Dry fuel yards and future fuel-storage buildings. |

## Rules

- Prefer custom tabs inside vanilla construction categories.
- Avoid creating custom top-level construction categories unless the menu truly needs them.
- Give each Phobos process family a readable tab before adding many more placeables.
- Keep tab names stable after release so existing saves and player habits are not disturbed.
- Optional add-ons may declare their own Phobos compatibility tab when the core mod should not expose provider-specific items.
- Do not copy third-party menu scripts when FS25 XML can express the category layout.
