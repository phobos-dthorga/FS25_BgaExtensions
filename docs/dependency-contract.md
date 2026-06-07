# Dependency Contract

This document records what `FS25_BgaExtensions` expects from required dependencies and what must stay optional.

## Required Dependencies

| Dependency | Why it is required | Contract used by Phobos | Verification source |
| --- | --- | --- | --- |
| `FS25_PlanET_BGA_Modular` | PlanET-specific intake modules use PlanET internal feedstocks and PlanET bunker assets. | `SILAGE_IN`, `MANURE_IN`, `SUGARBEETCUT_IN`, plus referenced PlanET bunker models and store icons. | Local mod XML and game log on 2026-06-07: loaded as version `1.0.0.1`, with 9 fillTypes loaded. |
| `pdlc_strawHarvestPack` | Straw pellet output targets the HALLSYS Pellet Heat Plant ecosystem. | `STRAW_PELLETS` and installed pDLC runtime support for straw pellet handling. | Game log on 2026-06-07: available pDLC version `1.1.0.0`, with 3 fillTypes loaded. |

## Phobos-Owned Contract

| FillType | Owner | Use |
| --- | --- | --- |
| `PHB_WET_BIOMASS_MASH` | `FS25_BgaExtensions` | Internal wet/root/produce staging material before handoff to PlanET `SUGARBEETCUT_IN`. |

`PHB_WET_BIOMASS_MASH` is not meant to become a broad farm commodity yet. It exists to avoid pretending every wet crop is sugar beet while still keeping the PlanET handoff simple.

## Base Game Materials

The core placeables may reference vanilla materials such as `CHAFF`, `SILAGE`, `GRASS_WINDROW`, `DRYGRASS_WINDROW`, `STRAW`, `MANURE`, `SUGARBEET_CUT`, `SUGARCANE`, `POTATO`, `BEETROOT`, `CARROT`, `PARSNIP`, `SPINACH`, `PEA`, `GREENBEAN`, and `SILAGE_ADDITIVE`.

Before a new vanilla-looking name is added, still verify it in local game data. The name being familiar is not enough.

## Optional Materials

These are not core dependencies and must not appear in core XML unless their provider becomes a declared dependency:

| Candidate | Source seen locally | Current posture |
| --- | --- | --- |
| `POTATO_WASHED` | `FS25_potatoWasher` | First guarded compatibility candidate. |
| `COMPOST` | Maps and greenhouse/orchard packs | Optional compatibility only. Prefer because other systems may already handle it. |
| `ORGANICWASTE` | Greenhouse/orchard and potato-chip packs | Optional compatibility only. Do not define in Phobos. |
| `RICE_HUSK` | Rice packaging factory | Optional low-value residue route. |

## Rule

If core XML references a dependency-owned fillType, that dependency must be declared in `modDesc.xml`.

If a fillType belongs to a map or optional mod, use one of these patterns:

- a separate compatibility package with explicit dependencies
- a runtime-guarded Lua integration after the FS25 API path is proven safe
- no active recipe yet, only documentation

Do not put optional fillTypes directly into the core placeable XML. The current game log already shows why: other mods that reference absent alfalfa/clover fillTypes generate invalid fillType warnings.
