# By-Product Integration Audit

Observed on 2026-06-07 against the current `FS25_BgaExtensions` source tree and the local FS25 mods folder.

## Audit Goal

By-products should help the wider farm loop when they naturally can. The mod should prefer materials that are already useful in vanilla FS25, DLC, maps, or loaded mods before adding new fillTypes.

This keeps the design practical:

- fewer custom fillTypes
- fewer fragile dependencies
- better compatibility with trailers, spreaders, greenhouses, BGAs, and sell points
- less risk of creating isolated production chains that only talk to themselves

## Current GBW Outputs And Handled Materials

The current PlanET-compatible preparation modules produce or handle these materials:

| Output | Source process | Current use | Audit status |
| --- | --- | --- | --- |
| `SILAGE_IN` | Chaff, silage, grass, hay, low-yield straw pretreatment | PlanET modular fermenter input | Good as a PlanET-owned handoff only. Do not expose as general farm material. |
| `MANURE_IN` | Manure intake | PlanET modular fermenter input | Good as a PlanET-owned handoff only. |
| GBW mash families | Wet Substrate Prep from sugar crops, roots, greens, and organic residue | GBW staging materials, then fermented into `SUGARBEETCUT_IN` | Good internal GBW intermediaries. Keep them internal until a real storage/logistics use appears. |
| `SUGARBEETCUT_IN` | GBW Fermentation Vessel mash fermentation | PlanET modular fermenter input | Good as final PlanET wet-substrate handoff. |
| `STRAW_PELLETS` | Dry Fuel Processor straw pelletizing | Straw Harvest HALLSYS Pellet Heat Plant, pellet-compatible systems, and assisted GBW fermentation | Strong cross-mod by-product/fuel route. Keep heat logistics meaningful and BGA use additive-gated. |
| `HAY_PELLETS` | Dry Fuel Processor hay pelletizing | Straw Harvest pellet-compatible systems and assisted GBW fermentation | Useful dual-purpose route; better BGA substrate than straw pellets, but still below prepared silage. |
| `WOODCHIPS` | Player-delivered vanilla material | Medium and large dry fuel yard storage for combustion logistics | Stored outside the BGA intake so it does not trigger production-point storage warnings. |

The mod does not yet produce a farm-wide residue such as `COMPOST` or `DIGESTATE` directly. That is probably correct for now: PlanET should own BGA digestion outputs, while GBW owns preparation and routing.

`METHANE` and `ELECTRICCHARGE` are BGA energy products, not general-purpose GBW fuel inputs. Keep them in the BGA/export layer unless a future dedicated energy module proves they can be stored or routed cleanly.

## Confirmed Local Compatibility Materials

These fillTypes or process outputs were found in the current local stack and are relevant to future by-product design.

| Material | Seen in local stack | Best use for GBW | Dependency posture |
| --- | --- | --- | --- |
| `DIGESTATE` | Vanilla BGAs and medium BGA package | Fertilizer output from true BGA digestion | Do not duplicate. Use only when GBW owns a standalone digester later. |
| `METHANE` | Vanilla BGA systems and PlanET output stages | Sale/fuel output from BGA modules | Let PlanET/vanilla own it unless adding standalone gas handling. |
| `ELECTRICCHARGE` | Vanilla and BGA/generator systems | Sale/charge output from generators | Let generator modules own it. |
| `STRAW_PELLETS` | Straw Harvest runtime dependency | Dry combustion fuel and assisted BGA substrate | Required dependency is acceptable for features that output it. |
| `HAY_PELLETS` | Straw Harvest runtime dependency | Dry combustion fuel and assisted BGA substrate | Verified through save data and Straw Harvest hay pellet pallets. |
| `MOLASSES` | Straw Harvest runtime dependency | Pellet manufacture input | Keep in Dry Fuel Processor, not Fermentation Vessel, to avoid UI clutter. |
| `WOODCHIPS` | Vanilla sawmills, heating plants, many forestry mods | Combustion fuel, not normal anaerobic substrate | Prefer heating. BGA route should be poor or optional. |
| `COMPOST` | `FS25_orchardsAndGreenhouses_crossplay`, `FS25_Nordkirchen_x4`, `FS25_The_Mechet` | Greenhouse/fertilizer/organic residual loop | Implemented as an optional output in the Orchards/Greenhouses add-on. Do not define casually. |
| `COMPOST_RAW` | `FS25_The_Mechet` | Map-specific compost precursor | Treat as optional detected input, not a GBW baseline. |
| `ORGANICWASTE` | `FS25_orchardsAndGreenhouses_crossplay`, `FS25_Potato_Chips_Factory_MF` | Food/produce processing residue | Implemented in the optional Orchards/Greenhouses add-on as wet mash or compost input. |
| `POTATO_WASHED` | `FS25_potatoWasher` | Wet substrate equivalent to potato | Implemented in the optional `FS25_BgaExtensions_PotatoWasherCompat` add-on. |
| `RICE_HUSK` | `FS25_RicePackagingFactory` | Low-value fibrous residue | Emergency/pretreated dry substrate or combustion candidate. |
| Maize+/MaizePlus corn residues | Parked | None in active development | Do not implement until a future explicit decision says the FS25 ecosystem is production-ready. Do not target `FS25_cornProductionPack`. |

## Strong Current Opportunities

1. Compost-aware residual loop

`COMPOST` is the best general-purpose by-product candidate because it already appears in your local map/mod stack and is useful around the farm, especially with advanced greenhouses. A future GBW compost module could accept wet organic by-products and output `COMPOST` only when a dependency or map already provides it.

Recommended posture: optional compatibility module or guarded recipes.

2. Organic waste intake

`ORGANICWASTE` is already produced by the potato chips factory and orchards/greenhouses pack. It should not be a new GBW-defined fillType, but it is a very good optional input.

Recommended routes:

- `ORGANICWASTE` -> `GBW_RESIDUE_MASH` for BGA co-digestion
- `ORGANICWASTE` -> `COMPOST` when `COMPOST` exists

3. Dry fuel route

`STRAW_PELLETS`, `HAY_PELLETS`, and `WOODCHIPS` form a credible combustion family. Straw and hay pellets are produced by the Dry Fuel Processor, and the dry fuel yards store all three fuel materials without putting wood chips inside a BGA intake production point.

Recommended posture: combustion first, BGA only as low-value emergency substrate.

4. Crop-processing residue intake

Rice husks are useful precisely because they are not premium feedstock.

Recommended posture: low yield, low priority, optional.

## Parked Maize+/MaizePlus Policy

Do not implement Maize+/MaizePlus integration yet.

Corn-residue, CCM, and advanced maize-silage ideas should remain parked until the FS25 Maize+/MaizePlus ecosystem is production-ready, locally installed, and explicitly selected as a target. The current local `FS25_cornProductionPack` was useful as an observation source, but it must not become a GBW integration target.

Official ModHub history shows MaizePlus as a silage and feeding overhaul for FS22 with distinct silage families such as grass silage, maize silage, CCM, beetcut silage, and whole-crop silage:

- https://www.farming-simulator.com/mod.php?mod_id=253528

For FS25, official ModHub evidence already shows other mods trying to follow MaizePlus fillType conventions to avoid future conflicts:

- https://www.farming-simulator.com/mod.php?mod_id=342332&title=fs2025

Until a future explicit decision changes this:

- do not add `FS25_cornProductionPack` as a dependency
- do not add Maize+/MaizePlus as a dependency
- do not add Maize+/MaizePlus registry placeholders or compatibility packages
- do not add Corn Production Pack-specific fillTypes to active recipes
- do not copy Corn Production Pack naming as the canonical GBW naming model
- do not revisit corn residues as an implementation task

## Cautions

- Avoid defining `ORGANICWASTE` in GBW. It would fragment compatibility with mods that already define it.
- Avoid making GBW mash fillTypes farm-wide commodities until equipment/storage support is proven useful.
- Avoid turning woody materials into strong BGA feedstock. Use them for heat unless the player explicitly wants an inefficient emergency digester path.
- Avoid custom by-product bales for now. The existing FS25 bale/fillType load-order warning still applies.
- Avoid making PlanET internals such as `SILAGE_IN`, `MANURE_IN`, `SUGARBEETCUT_IN`, `RAWMETHANE`, or `DIGESTATE1` general-purpose GBW materials.

## Recommended Priority Order

1. Monitor `ORGANICWASTE` and `COMPOST` runtime behavior through the optional Orchards/Greenhouses compatibility add-on.
2. Consider a separate Potato Chips organic-waste add-on only if that provider is commonly used and its fillType behavior matches.
3. Monitor `POTATO_WASHED` runtime behavior through the optional Potato Washer compatibility add-on.
4. Add Rice Packaging residue support for `RICE_HUSK`.
5. Add optional `ORGANICWASTE` and `COMPOST` routes only after core placeables remain log-clean.
6. Expand dry combustion processing only when a new residue has one clear, shared fuel route.

## Design Rule Going Forward

Every new GBW process should answer two questions:

1. What useful by-product could this plausibly produce?
2. Is there already a vanilla, DLC, map, or loaded-mod fillType that represents it well enough?

If the answer to the second question is yes, prefer that existing fillType. Add a new GBW fillType only when the material has a clear gameplay role and no existing compatibility material can carry it cleanly.
