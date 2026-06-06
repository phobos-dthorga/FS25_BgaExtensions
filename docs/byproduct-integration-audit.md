# By-Product Integration Audit

Observed on 2026-06-07 against the current `FS25_BgaExtensions` source tree and the local FS25 mods folder.

## Audit Goal

By-products should help the wider farm loop when they naturally can. The mod should prefer materials that are already useful in vanilla FS25, DLC, maps, or loaded mods before adding new fillTypes.

This keeps the design practical:

- fewer custom fillTypes
- fewer fragile dependencies
- better compatibility with trailers, spreaders, greenhouses, BGAs, and sell points
- less risk of creating isolated production chains that only talk to themselves

## Current Phobos Outputs

The current PlanET-compatible intake modules produce these outputs:

| Output | Source process | Current use | Audit status |
| --- | --- | --- | --- |
| `SILAGE_IN` | Chaff, silage, grass, hay, low-yield straw pretreatment | PlanET modular fermenter input | Good as a PlanET-owned handoff only. Do not expose as general farm material. |
| `MANURE_IN` | Manure intake | PlanET modular fermenter input | Good as a PlanET-owned handoff only. |
| `PHB_WET_BIOMASS_MASH` | Beet cut, sugarcane, roots, spinach, peas, green beans | Phobos staging material, then conditioned into `SUGARBEETCUT_IN` | Good internal Phobos intermediary. Keep it internal until a real storage/logistics use appears. |
| `SUGARBEETCUT_IN` | Wet mash conditioning | PlanET modular fermenter input | Good as final PlanET wet-substrate handoff. |
| `STRAW_PELLETS` | Straw pelletizing | Straw Harvest HALLSYS Pellet Heat Plant and pellet-compatible systems | Strong cross-mod by-product/fuel route. Keep this meaningful. |

The mod does not yet produce a farm-wide residue such as `COMPOST` or `DIGESTATE` directly. That is probably correct for now: PlanET should own BGA digestion outputs, while Phobos owns preparation and routing.

## Confirmed Local Compatibility Materials

These fillTypes or process outputs were found in the current local stack and are relevant to future by-product design.

| Material | Seen in local stack | Best use for Phobos | Dependency posture |
| --- | --- | --- | --- |
| `DIGESTATE` | Vanilla BGAs and medium BGA package | Fertilizer output from true BGA digestion | Do not duplicate. Use only when Phobos owns a standalone digester later. |
| `METHANE` | Vanilla BGA systems and PlanET output stages | Sale/fuel output from BGA modules | Let PlanET/vanilla own it unless adding standalone gas handling. |
| `ELECTRICCHARGE` | Vanilla and BGA/generator systems | Sale/charge output from generators | Let generator modules own it. |
| `STRAW_PELLETS` | Straw Harvest runtime dependency and Corn Production Pack pellet plant | Dry combustion fuel | Required dependency is acceptable for features that output it. |
| `WOODCHIPS` | Vanilla sawmills, heating plants, many forestry mods | Combustion fuel, not normal anaerobic substrate | Prefer heating. BGA route should be poor or optional. |
| `COMPOST` | `FS25_orchardsAndGreenhouses_crossplay`, `FS25_Nordkirchen_x4`, `FS25_The_Mechet` | Greenhouse/fertilizer/organic residual loop | Use when detected or in compatibility modules. Do not define casually. |
| `COMPOST_RAW` | `FS25_The_Mechet` | Map-specific compost precursor | Treat as optional detected input, not a Phobos baseline. |
| `ORGANICWASTE` | `FS25_orchardsAndGreenhouses_crossplay`, `FS25_Potato_Chips_Factory_MF` | Food/produce processing residue | Consume optionally. Prefer converting toward `COMPOST` or wet substrate. |
| `POTATO_WASHED` | `FS25_potatoWasher` | Wet substrate equivalent to potato | Good optional input candidate. |
| `RICE_HUSK` | `FS25_RicePackagingFactory` | Low-value fibrous residue | Emergency/pretreated dry substrate or combustion candidate. |
| `MAIZECOB`, `MAIZECOBWASTE`, `MAIZEGERM`, `MAIZESTALKS`, `MAIZESTALKS_PELLETS` | `FS25_cornProductionPack` | Corn-processing residues, pellet/combustion loops | Good optional integration, but keep below silage value. |

## Strong Current Opportunities

1. Compost-aware residual loop

`COMPOST` is the best general-purpose by-product candidate because it already appears in your local map/mod stack and is useful around the farm, especially with advanced greenhouses. A future Phobos compost module could accept wet organic by-products and output `COMPOST` only when a dependency or map already provides it.

Recommended posture: optional compatibility module or guarded recipes.

2. Organic waste intake

`ORGANICWASTE` is already produced by the potato chips factory and orchards/greenhouses pack. It should not be a new Phobos-defined fillType, but it is a very good optional input.

Recommended routes:

- `ORGANICWASTE` -> `PHB_WET_BIOMASS_MASH` for BGA co-digestion
- `ORGANICWASTE` -> `COMPOST` when `COMPOST` exists

3. Dry fuel and residue route

`STRAW_PELLETS`, `MAIZESTALKS_PELLETS`, and `WOODCHIPS` form a credible combustion family. Straw pellets are already implemented. Corn stalk pellets from the Corn Production Pack are a natural next compatibility candidate.

Recommended posture: combustion first, BGA only as low-value emergency substrate.

4. Crop-processing residue intake

Rice husks and corn residues are useful precisely because they are not premium feedstock. They give players cleanup and salvage gameplay without undercutting proper silage or food production.

Recommended posture: low yield, low priority, optional.

## Cautions

- Avoid defining `ORGANICWASTE` in Phobos. It would fragment compatibility with mods that already define it.
- Avoid making `PHB_WET_BIOMASS_MASH` a farm-wide commodity until equipment/storage support is proven useful.
- Avoid turning woody materials into strong BGA feedstock. Use them for heat unless the player explicitly wants an inefficient emergency digester path.
- Avoid custom by-product bales for now. The existing FS25 bale/fillType load-order warning still applies.
- Avoid making PlanET internals such as `SILAGE_IN`, `MANURE_IN`, `SUGARBEETCUT_IN`, `RAWMETHANE`, or `DIGESTATE1` general-purpose Phobos materials.

## Recommended Priority Order

1. Add optional `ORGANICWASTE` intake where the fillType is detected.
2. Add optional `COMPOST` intake/output routes if the loaded map/mod stack defines `COMPOST`.
3. Add `POTATO_WASHED` as a wet substrate input.
4. Add Corn Production Pack residue support: `MAIZECOB`, `MAIZECOBWASTE`, `MAIZEGERM`, `MAIZESTALKS`, and possibly `MAIZESTALKS_PELLETS`.
5. Add Rice Packaging residue support for `RICE_HUSK`.
6. Consider a dedicated dry combustion companion module for `WOODCHIPS`, `STRAW_PELLETS`, and stalk pellets.

## Design Rule Going Forward

Every new Phobos process should answer two questions:

1. What useful by-product could this plausibly produce?
2. Is there already a vanilla, DLC, map, or loaded-mod fillType that represents it well enough?

If the answer to the second question is yes, prefer that existing fillType. Add a new Phobos fillType only when the material has a clear gameplay role and no existing compatibility material can carry it cleanly.
