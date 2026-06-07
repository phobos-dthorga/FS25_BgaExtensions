# Guarded Compatibility Pattern

Optional integrations must not make the core mod fragile.

FS25 `modDesc.xml` dependencies are hard dependencies, and production XML does not provide a simple optional-fillType wrapper. That means optional materials cannot be safely dropped into the core production XML.

## Current Status

No optional compatibility recipes are active yet.

The first candidate is `POTATO_WASHED`, because it has a clean interpretation: washed potatoes should behave like a wet/starchy substrate. It still must not be referenced by the core intake until its provider is declared or detected safely.

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
| `POTATO_WASHED` | `POTATO_WASHED` -> `PHB_WET_BIOMASS_MASH` | Requires `FS25_potatoWasher` or runtime fillType detection. |

Suggested balance: slightly better or equal to `POTATO`, not dramatically better. Washing should improve cleanliness and handling, not turn potatoes into premium energy crop magic.

## Later Candidates

| Candidate | Intended route | Notes |
| --- | --- | --- |
| `ORGANICWASTE` | Wet substrate or compost route | Do not define this in Phobos. Consume only when provided. |
| `COMPOST` | Waste substrate or farm loop | Prefer this when present because tools/maps may already support spreading and handling. |
| `RICE_HUSK` | Low-value fibrous residue | Emergency route only. Better as cleanup gameplay than premium energy. |

## Definition Of Done

A guarded compatibility slice is not done until:

- missing provider mod produces no error or warning
- present provider mod exposes the intended recipe or module
- the produced material can enter the existing Phobos/PlanET path
- the game log is clean of new Phobos warnings
- the release notes name the optional provider clearly

Maize+/MaizePlus remains parked and is not part of this pattern until a future explicit decision.
