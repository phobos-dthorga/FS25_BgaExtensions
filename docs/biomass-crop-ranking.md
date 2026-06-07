# Biomass Crop Ranking

This table ranks crops and common map-maker crop families for a biomass -> silage/substrate -> BGA pathway.

Ranking is based on expected anaerobic digestion usefulness, practical ensiling behavior, crop volume, moisture/starch/sugar balance, and gameplay value. It is not a sale-price ranking.

Base-game observations checked on 2026-06-06 against local FS25 install files:

- `data/maps/maps_fruitTypes.xml`
- `data/maps/maps_fillTypes.xml`
- `data/maps/maps_bales.xml`
- `data/placeables/brandless/bunkerSilos/*/bunkerSilo*.xml`
- `data/placeables/planET/bga*/bga*.xml`

Installed mod observations are recorded in `docs/installed-mod-observations.md`.

## Implementation Bias

- Prefer bulk substrate and placeable production paths before custom bales.
- Use base-game `SILAGE` where the material naturally fits the vanilla bunker silo model.
- Use a future intermediate substrate for materials that are wet, starchy, sugary, oily, or otherwise fermentable but not really silage.
- Treat common map-maker crops as optional integrations. Register them only when their fill types exist.
- Keep custom fill types minimal because fill types, heightTypes, bales, animal food, and map recipes can have loading-order or map-ownership constraints.
- Keep Maize+/MaizePlus and Corn Production Pack integration out of scope until a future explicit decision.

## Ranked Crop Table

| Rank | Crop or crop family | FS25/base fill types or common names | Preferred pathway | BGA value | Implementation notes |
| --- | --- | --- | --- | --- | --- |
| Exceptional | Maize/corn whole crop | `MAIZE`, `CHAFF`, common: `SILAGEMAIZE` | Forage harvest to `CHAFF`, bunker to `SILAGE`, then BGA | 1.00 baseline | Core baseline. Vanilla forage harvester already converts maize to chaff, and bunker silos already accept chaff. |
| Exceptional | Grass and meadow forage | `GRASS`, `MEADOW`, `GRASS_WINDROW` | Mow to windrow, bunker to `SILAGE`, then BGA | 0.85-0.95 | High-volume, repeatable, already fits the vanilla silage loop. |
| Exceptional | Alfalfa/lucerne | Common: `ALFALFA`, `ALFALFA_WINDROW`, `ALFALFA_FERMENTED`, `DRYALFALFA`, `DRYALFALFA_WINDROW`, `LUCERNE` | Optional whole-crop forage silage or green biomass substrate | 0.85-0.95 | Very common in map/mod ecosystems. Should be a first optional integration once fill type detection exists. |
| Exceptional | Clover and mixed forage legumes | Common: `CLOVER`, `CLOVER_WINDROW`, `CLOVER_FERMENTED`, `DRYCLOVER`, `DRYCLOVER_WINDROW`, `VETCHRYE`, `FIELDGRASS` | Optional whole-crop forage silage or green biomass substrate | 0.80-0.92 | Related to alfalfa in design terms. Good silage candidate, but exact names vary by map. |
| Exceptional | Sugar beet, chopped beet, beet pulp | `SUGARBEET`, `SUGARBEET_CUT`; common: `BEETPULP` | Chop/pulp to wet biomass substrate; BGA direct or via substrate | 0.80-0.95 | Vanilla BGAs already consume `SUGARBEET_CUT`. Treat whole beet as needing chopping/pulping. |
| Excellent | Sorghum whole crop | `SORGHUM`, `CHAFF` | Forage harvest to chaff or energy-crop substrate | 0.75-0.90 | Good drought-style energy crop. Vanilla forage conversion exists. |
| Excellent | Whole-crop cereals | `WHEAT`, `BARLEY`, `OAT`; common: `RYE`, `RYE_CUT`, `GREENRYE`, `TRITICALE`, `TRITICALE_CUT`, `SPELT`, `SPELT_CUT`, `WINTERBARLEY`, `WINTERWHEAT` | Green chop to chaff/whole-crop silage | 0.70-0.88 | Strong fit for silage when harvested green. Keep separate from dry grain diversion. |
| Excellent | Potatoes and starchy roots | `POTATO`; common: `SWEETPOTATO` | Wash/chop/mash to wet biomass substrate | 0.70-0.86 | Excellent fermentable starch, but not a true silage crop. Should not require bales. |
| Excellent | Beets, carrots, parsnips, onions | `BEETROOT`, `CARROT`, `PARSNIP`; common/DLC: `ONION` | Chop/shred to wet biomass substrate | 0.65-0.82 | Wet, sugary root/vegetable stream. Good as co-substrate with silage/manure. |
| Excellent | Sugarcane | `SUGARCANE` | Chop/crush to sugary biomass substrate | 0.65-0.82 | High sugar and biomass, but fibrous. Better as substrate than vanilla silage. |
| Excellent | Compost and organic residuals | Common: `COMPOST`, `COMPOST_RAW`, `ORGANICWASTE` | Waste substrate or co-digestion stream | 0.60-0.82 | Prefer `COMPOST` because maps may already support spreading, heaps, and handling for it. Treat `ORGANICWASTE` as an alias/fallback, not a new compatibility layer. |
| Good | Hay and dry grass | `DRYGRASS`, `DRYGRASS_WINDROW` | Bunker to `SILAGE`, or rehydrate to substrate | 0.55-0.75 | Vanilla bunker silos already accept `dryGrass_windrow`. Lower priority than fresh grass. |
| Good | Sunflower whole crop | `SUNFLOWER`, `CHAFF` | Forage harvest to chaff or oilseed biomass substrate | 0.55-0.75 | Vanilla forage conversion exists. Good biomass, but keep oilseed economics in mind. |
| Good | Peas, field peas, beans | `PEA`, `GREENBEAN`; common: `FIELDPEA`, `FIELDBEAN`, `HORSEBEAN` | Wet green biomass or produce-waste substrate | 0.50-0.72 | Useful co-substrate. High moisture means it should not be the sole pathway. |
| Good | Spinach and leafy greens | `SPINACH`; greenhouse/common: `LETTUCE`, `NAPACABBAGE` | Wet green biomass substrate | 0.45-0.68 | Good organic mass but watery. Balance with lower throughput/yield. |
| Good | Rice and long grain rice | `RICE`, `RICELONGGRAIN` | Whole-crop or grain mash substrate | 0.45-0.68 | Starchy and fermentable, but wet-field logistics make it less universal than maize/cereals. |
| Good | Millet, buckwheat, similar small grains | Common: `MILLET`, `BUCKWHEAT` | Whole-crop silage or grain mash substrate | 0.45-0.65 | Common multifruit candidates. Add only by detected fill type. |
| Good | Oilseed crops as whole crop | `CANOLA`, `SOYBEAN`; common: `FLAX`, `LINSEED`, `LINSEED_CUT`, `MUSTARD`, `MUSTARD_CUT` | Green chop or oilseed biomass substrate | 0.45-0.65 | Fermentable but economically sensitive. Do not let them become a profit exploit. |
| Fair | Dry cereal grain diversion | `WHEAT`, `BARLEY`, `OAT`, `SORGHUM`, `MAIZE`, `RICELONGGRAIN` | Mill/soak to energy mash substrate | 0.35-0.60 | Biologically plausible but should be expensive/inefficient compared with selling or feeding. |
| Fair | Grapes, olives, fruit produce | `GRAPE`, `OLIVE`; greenhouse: `STRAWBERRY`, `TOMATO` | Waste/pomace style substrate | 0.30-0.55 | Whole fruit should be a fallback. Pomace/waste products would be better if a map/mod exposes them. |
| Fair | Hemp and high-fiber annuals | Common: `HEMP` | Chopped green biomass substrate | 0.30-0.55 | High biomass but can be fibrous. Keep below forage crops. |
| Fair | Hops and specialty crops | Common: `HOPS`, `LAVENDER`, herbs | Organic waste substrate | 0.20-0.45 | Include only when a map makes them available in bulk. Not a core path. |
| Emergency only | Straw and grain residues | `STRAW`; common: `RYE_STRAW`, `TRITICALE_STRAW` | Pretreated dry biomass substrate | 0.15-0.35 | Lignocellulosic and slow. Useful for cleanup or low-grade co-digestion, not premium energy production. |
| Emergency only | Poplar and woody biomass | `POPLAR`, `WOODCHIPS` | Combustion fuel or pretreatment-only biomass route | 0.05-0.20 | Better suited to heating than BGA. Do not store wood chips passively inside a production point; use a future dedicated combustion storage/module. |
| Emergency only | Cover crop biomass | `OILSEEDRADISH`; common: `MUSTARD`, cover mixes | Green manure salvage route | 0.10-0.30 | Only if the map exposes a harvestable product. Otherwise leave as field agronomy, not BGA feedstock. |
| Emergency only | Rice husk | Common: `RICE_HUSK` | Pretreated dry biomass substrate | 0.05-0.25 | Fibrous residue. More plausible as low-grade emergency substrate than as silage. |

## Excluded For Now

- Cotton lint and cotton bales: mostly fiber and not a useful silage/BGA target.
- Logs and untreated wood: not an anaerobic digestion feedstock without a separate pretreatment fantasy.
- Tiny spice, mushroom, or greenhouse trickle outputs unless a map/mod provides them in bulk.
- Animal products such as milk, eggs, wool, or honey. They are organic, but they do not belong in this crop pathway.

## Waste And Byproduct Table

FillTypes are a scarce resource, so waste streams should reuse vanilla or already-detected mod fill types wherever practical.

| Waste stream | Preferred fillType | Fallback | BGA usefulness | Notes |
| --- | --- | --- | --- | --- |
| Food/produce rejects | `COMPOST` if present | direct recipe input from original crop | Excellent | Prefer `COMPOST` to preserve map/implement compatibility. Use `ORGANICWASTE` only when a loaded mod already defines and uses it. |
| Beet/vegetable trimmings | `SUGARBEET_CUT` for beet-like waste | original root crop | Excellent | Slightly gamey, but close enough and already BGA-relevant. |
| Grain cleaning screenings | `CHAFF` | original grain | Good | Works as a generic dry-ish plant fraction without spending a new fillType. |
| Forage sweepings | `GRASS_WINDROW` or `DRYGRASS_WINDROW` | `CHAFF` | Good | Keep it in the silage lane if it came from forage handling. |
| Fruit pomace | `COMPOST` if present | original fruit crop | Fair | Good optional integration. Do not create `ORGANICWASTE` just to represent this. |
| Rice husk | `RICE_HUSK` if present | `STRAW` | Emergency only | Fibrous residue; useful mostly for cleanup or pretreatment. |
| Straw-like screenings | `STRAW` | none | Emergency only | Low-grade, slow substrate. |
| Woody contamination | `WOODCHIPS` | exclude | Emergency only | Prefer heating use; BGA route should be poor or disabled by default. |
| Digestate output | `DIGESTATE` | none | Output only | Do not create custom digestate variants unless another mod forces it. |

## First Implementation Slice

Start with the least fragile path:

1. Use vanilla-compatible silage materials: `CHAFF`, `GRASS_WINDROW`, `DRYGRASS_WINDROW`, `SILAGE`, `SUGARBEET_CUT`.
2. Add a Phobos-owned bulk substrate path for wet/starchy/sugary biomass.
3. Add optional common map integrations for `ALFALFA`, `CLOVER`, `RYE`, `TRITICALE`, `SPELT`, `MILLET`, `FIELDPEA`, and similar fill types only after runtime detection exists.
4. Avoid custom biomass bales until custom bale loading behavior has been tested on an unmodified map.
