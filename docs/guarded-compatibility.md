# Guarded Compatibility Pattern

Optional integrations must not make the core mod fragile.

FS25 `modDesc.xml` dependencies are hard dependencies, and production XML does not provide a simple optional-fillType wrapper. That means optional materials cannot be safely dropped into the core production XML.

## Current Status

Optional compatibility packages are active:

| Package | Provider dependency | Route |
| --- | --- | --- |
| `FS25_BgaExtensions_PotatoWasherCompat` | `FS25_potatoWasher` | `POTATO_WASHED` -> `GBW_ROOT_MASH` |
| `FS25_BgaExtensions_OrchardsGreenhousesCompat` | `FS25_orchardsAndGreenhouses_crossplay` | `ORGANICWASTE` -> `GBW_RESIDUE_MASH` or `COMPOST`, runtime-gated waste-aware mash prep side-streams, plus GBW Compost Bay logistics |

`POTATO_WASHED` still must not be referenced by the core mod. It is safe only inside the add-on because that add-on declares `FS25_potatoWasher` as a hard dependency.

`ORGANICWASTE` and `COMPOST` still must not be referenced by the core mod. They are safe only inside provider-specific add-ons because those add-ons declare the provider as a hard dependency.

## Acceptable Patterns

1. Separate compatibility package

Create a small add-on package that depends on:

- `FS25_BgaExtensions`
- the optional provider mod
- any required target framework

This is the safest data-driven XML route because the optional fillType becomes a hard dependency only for the add-on, not for the core mod.

2. Runtime-guarded Lua integration

Use Lua only after the relevant FS25 APIs are verified against local source or proven examples. A guarded integration must:

- expose a user setting when the feature affects visible shop or recipe availability
- treat the setting as permission, not proof the feature can run
- check whether the provider mod is active where practical
- check whether the fillType exists
- check required provider assets or shop XML before registering new surfaces
- avoid mutating existing third-party placeables unless the API is proven stable
- update production-chain mappings safely in multiplayer
- produce no log warnings when the provider is absent

For shop-facing features, the preferred order is: setting enabled, provider active, required fillTypes/assets registered, then register or reveal the shop item. Setting changes apply on the next save load unless a live mutation path has been separately proven safe. The setting must never delete already placed test objects; it only controls new shop availability.

3. GBW data pack

Use the Stage 1 data-pack API when a route can be described as a simple input fillType plus a GBW-owned template. This is intended for community extension packs, but Stage 1 validates route data only and does not inject gameplay recipes yet.

4. Documentation-only holding state

For uncertain or unstable ecosystems, document the candidate and do not ship active behavior yet.

## First Candidate Route

| Candidate | Intended route | Guard requirement |
| --- | --- | --- |
| `POTATO_WASHED` | `POTATO_WASHED` -> `GBW_ROOT_MASH` | Implemented in `FS25_BgaExtensions_PotatoWasherCompat`, which requires `FS25_potatoWasher`. |

Current balance matches the normal potato wet-mash route. Washing already has its own upstream cost and should not turn potatoes into premium energy crop magic.

## Later Candidates

| Candidate | Intended route | Notes |
| --- | --- | --- |
| `ORGANICWASTE` | Wet substrate or compost route | Implemented in `FS25_BgaExtensions_OrchardsGreenhousesCompat`, which requires `FS25_orchardsAndGreenhouses_crossplay`. |
| `COMPOST` | Waste substrate or farm loop | Implemented as an output and compost-bay workflow in `FS25_BgaExtensions_OrchardsGreenhousesCompat`; keep broader compost routes provider-specific. |
| `RICE_HUSK` | Low-value fibrous residue | Emergency route only. Better as cleanup gameplay than premium energy. |

The Orchards/Greenhouses add-on may also emit small `ORGANICWASTE` side-streams from wet/root/green mash preparation. That does not make `ORGANICWASTE` a GBW-owned fillType. Starting with `v0.2.22.0`, the prep XML remains packaged for early-save compatibility, but the shop item is registered only when `Waste-aware organic side-streams` is enabled and the provider/fillType checks pass.

## Definition Of Done

A guarded compatibility slice is not done until:

- missing provider mod produces no error or warning
- present provider mod exposes the intended recipe or module
- the produced material can enter the existing GBW/PlanET path
- the game log is clean of new GBW warnings
- the release notes name the optional provider clearly

For data packs, the pack must also pass the `gbwDataPack.xml` validator and use only documented templates, targets, and tiers.

Maize+/MaizePlus remains parked and is not part of this pattern until a future explicit decision.
