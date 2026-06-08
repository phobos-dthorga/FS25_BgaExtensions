# Guarded Compatibility Pattern

Optional integrations must not make the core mod fragile.

FS25 `modDesc.xml` dependencies are hard dependencies, and production XML does not provide a simple optional-fillType wrapper. That means optional materials cannot be safely dropped into the core production XML.

## Current Status

Optional compatibility packages are active:

| Package | Provider dependency | Route |
| --- | --- | --- |
| `FS25_BgaExtensions_PotatoWasherCompat` | `FS25_potatoWasher` | `POTATO_WASHED` -> `PHB_WET_BIOMASS_MASH` |
| `FS25_BgaExtensions_OrchardsGreenhousesCompat` | `FS25_orchardsAndGreenhouses_crossplay` | `ORGANICWASTE` -> `PHB_WET_BIOMASS_MASH` or `COMPOST` |

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

- check whether the fillType exists
- check whether the provider mod is active where practical
- avoid mutating existing third-party placeables unless the API is proven stable
- update production-chain mappings safely in multiplayer
- produce no log warnings when the provider is absent

3. Documentation-only holding state

For uncertain or unstable ecosystems, document the candidate and do not ship active behavior yet.

## First Candidate Route

| Candidate | Intended route | Guard requirement |
| --- | --- | --- |
| `POTATO_WASHED` | `POTATO_WASHED` -> `PHB_WET_BIOMASS_MASH` | Implemented in `FS25_BgaExtensions_PotatoWasherCompat`, which requires `FS25_potatoWasher`. |

Current balance matches the normal potato wet-mash route. Washing already has its own upstream cost and should not turn potatoes into premium energy crop magic.

## Later Candidates

| Candidate | Intended route | Notes |
| --- | --- | --- |
| `ORGANICWASTE` | Wet substrate or compost route | Implemented in `FS25_BgaExtensions_OrchardsGreenhousesCompat`, which requires `FS25_orchardsAndGreenhouses_crossplay`. |
| `COMPOST` | Waste substrate or farm loop | Implemented as an output in `FS25_BgaExtensions_OrchardsGreenhousesCompat`; keep broader compost routes provider-specific. |
| `RICE_HUSK` | Low-value fibrous residue | Emergency route only. Better as cleanup gameplay than premium energy. |

## Definition Of Done

A guarded compatibility slice is not done until:

- missing provider mod produces no error or warning
- present provider mod exposes the intended recipe or module
- the produced material can enter the existing Phobos/PlanET path
- the game log is clean of new Phobos warnings
- the release notes name the optional provider clearly

Maize+/MaizePlus remains parked and is not part of this pattern until a future explicit decision.
