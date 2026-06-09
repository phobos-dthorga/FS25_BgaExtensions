# Dependency Contract

This document records what `FS25_BgaExtensions` expects from required dependencies and what must stay optional.

## Required Dependencies

| Dependency | Why it is required | Contract used by GBW | Verification source |
| --- | --- | --- | --- |
| `FS25_PlanET_BGA_Modular` | PlanET-specific intake, prep, and fermentation modules use PlanET internal feedstocks and PlanET assets. | `SILAGE_IN`, `MANURE_IN`, `SUGARBEETCUT_IN`, plus referenced PlanET bunker and fermenter models and store icons. | Local mod XML and game log on 2026-06-07: loaded as version `1.0.0.1`, with 9 fillTypes loaded. |
| `pdlc_strawHarvestPack` | Pellet output, molasses use, and dry fuel storage target the HALLSYS Pellet Heat Plant ecosystem. | `STRAW_PELLETS`, `HAY_PELLETS`, `MOLASSES`, and installed pDLC runtime support for pellet handling. | Game log and save data on 2026-06-09: pDLC version `1.1.0.0`, 3 fillTypes loaded, plus observed `HAY_PELLETS`, `STRAW_PELLETS`, and `MOLASSES` save entries. |

## GBW-Owned Contract

| FillType | Owner | Use |
| --- | --- | --- |
| `GBW_SWEET_MASH` | `FS25_BgaExtensions` | Sweet wet substrate family for sugar beet cut and sugarcane before Fermentation Vessel handoff to PlanET `SUGARBEETCUT_IN`. |
| `GBW_ROOT_MASH` | `FS25_BgaExtensions` | Root/starchy wet substrate family for potatoes and root crops before Fermentation Vessel handoff to PlanET `SUGARBEETCUT_IN`. |
| `GBW_GREEN_MASH` | `FS25_BgaExtensions` | Leafy/green produce wet substrate family before Fermentation Vessel handoff to PlanET `SUGARBEETCUT_IN`. |
| `GBW_RESIDUE_MASH` | `FS25_BgaExtensions` | Organic residue wet substrate family, currently produced by the Orchards/Greenhouses add-on before Fermentation Vessel handoff to PlanET `SUGARBEETCUT_IN`. |

These GBW mash fillTypes are not meant to become broad farm commodities yet. They exist to avoid pretending every wet crop is sugar beet while still keeping the PlanET handoff simple.

GBW may reference PlanET model and icon paths only while `FS25_PlanET_BGA_Modular` remains a declared dependency. The GBW package must not vendor PlanET assets.

## Base Game Materials

The core placeables may reference vanilla materials such as `CHAFF`, `SILAGE`, `GRASS_WINDROW`, `DRYGRASS_WINDROW`, `STRAW`, `MANURE`, `SUGARBEET_CUT`, `SUGARCANE`, `POTATO`, `BEETROOT`, `CARROT`, `PARSNIP`, `SPINACH`, `PEA`, `GREENBEAN`, `WATER`, and `SILAGE_ADDITIVE`.

Before a new vanilla-looking name is added, still verify it in local game data. The name being familiar is not enough.

## Optional Materials

These are not core dependencies and must not appear in core XML unless their provider becomes a declared dependency:

| Candidate | Source seen locally | Current posture |
| --- | --- | --- |
| `POTATO_WASHED` | `FS25_potatoWasher` | First guarded compatibility candidate. |
| `COMPOST` | Maps and greenhouse/orchard packs | Optional compatibility only. Prefer because other systems may already handle it. |
| `ORGANICWASTE` | Greenhouse/orchard and potato-chip packs | Optional compatibility only. Do not define in GBW. |
| `RICE_HUSK` | Rice packaging factory | Optional low-value residue route. |

## Rule

If core XML references a dependency-owned fillType, that dependency must be declared in `modDesc.xml`.

If a fillType belongs to a map or optional mod, use one of these patterns:

- a separate compatibility package with explicit dependencies
- a runtime-guarded Lua integration after the FS25 API path is proven safe
- no active recipe yet, only documentation

Do not put optional fillTypes directly into the core placeable XML. The current game log already shows why: other mods that reference absent alfalfa/clover fillTypes generate invalid fillType warnings.

## Active Optional Add-Ons

| Add-on package | Required dependencies | Contract used by GBW |
| --- | --- | --- |
| `FS25_BgaExtensions_PotatoWasherCompat` | `FS25_BgaExtensions`, `FS25_PlanET_BGA_Modular`, `FS25_potatoWasher` | `POTATO_WASHED` from Potato Washing System, `GBW_ROOT_MASH` from core GBW, and the small PlanET bunker model. |
| `FS25_BgaExtensions_OrchardsGreenhousesCompat` | `FS25_BgaExtensions`, `FS25_PlanET_BGA_Modular`, `FS25_orchardsAndGreenhouses_crossplay` | `ORGANICWASTE` and `COMPOST` from Orchards And Greenhouses, `GBW_RESIDUE_MASH` from core GBW, and the small PlanET bunker model. |
