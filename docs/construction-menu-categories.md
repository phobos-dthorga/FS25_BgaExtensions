# Construction Menu Categories

This document records how `FS25_BgaExtensions` should group its placeables in the FS25 construction menu.

## Observed Pattern

The local Corn Production Pack uses a clean construction-tab pattern:

- declare a tab in `modDesc.xml` under `<constructionCategories>`
- point each placeable store brush at that tab with `<brush><tab>...</tab></brush>`
- keep the vanilla construction category, such as `production` or `buildings`

That is enough for the current GBW need. The Corn Production Pack archive also contains a generic Lua helper for adding construction categories and tabs, but the active `modDesc.xml` uses normal tab declarations. Do not add a Lua hook unless a future FS25 test proves the built-in tab declaration is insufficient.

## Current GBW Tabs

| Vanilla category | GBW tab | Purpose |
| --- | --- | --- |
| `production` | `gbwBgaProduction` | Biomass intake and BGA feedstock process buildings. |
| `production` | `gbwBgaCompatibility` | Optional compatibility add-on process buildings. Declared in core so multiple add-ons can share one tab. |
| `production` | `gbwFuelProcessing` | Dry fuel processing buildings such as straw pelletizing. |
| `buildings` | `gbwFuelStorage` | Dry fuel yards and future fuel-storage buildings. |

## Rules

- Prefer custom tabs inside vanilla construction categories.
- Avoid creating custom top-level construction categories unless the menu truly needs them.
- Give each GBW process family a readable tab before adding many more placeables.
- Keep tab names stable after release so existing saves and player habits are not disturbed.
- Optional add-ons should use `gbwBgaCompatibility` for BGA-adjacent compatibility placeables unless a future add-on truly needs its own family tab.
- Do not copy third-party menu scripts when FS25 XML can express the category layout.
