# Conversion Process

This document defines the planned biomass conversion flow for `FS25_BgaExtensions`.

## Core Principle

Do not force every organic crop into vanilla `SILAGE`.

Some materials genuinely belong in a silage pathway. Others are better represented as wet biomass, grain mash, compost/organic residuals, or pretreated low-grade substrate. The mod should preserve those differences while still making many more organic materials useful for BGA energy production.

For the first proof of concept, prefer the smallest useful compatibility layer. The installed PlanET modular BGA already uses internal feedstocks, so forage and manure lanes feed those internal PlanET lanes directly.

The wet crop lane now uses a dedicated Wet Substrate Prep placeable and one Phobos-owned intermediary, `PHB_WET_BIOMASS_MASH`, before handing material to PlanET as `SUGARBEETCUT_IN`. This avoids presenting spinach, peas, roots, and produce waste as if they were sugar beet.

## Fermentation Priority

Recipe rates treat output amount as usable downstream BGA value, not literal mass preservation. Real-world chemistry should guide the direction of the balance, but Farming Simulator-style production ratios are allowed to be a little gamey.

Conservation of mass should be lightly respected: avoid absurd transformations, but do not force every recipe to conserve liters or tonnage. If a route is clearer, more fun, or better balanced with a modestly game-friendly ratio, prefer that over strict mass accounting.

Fermented or already conditioned materials should be easier for the digester to use. They should therefore run faster and keep more useful output value than unfermented shortcuts.

Unfermented materials that would normally be ensiled, mashed, inoculated, or otherwise conditioned can still be accepted for gameplay convenience, but they should run slower and yield less final BGA feedstock. `SILAGE_ADDITIVE` may restore some of that lost convenience on these lanes, either through slightly better yield, slightly better throughput, or both. It should not make an unfermented lane stronger than using properly fermented material.

See `docs/integration-strategy.md` for the companion-module rule that governs PlanET and future third-party integrations.

See `docs/energy-carrier-strategy.md` for the rule that separates biomass preparation, combustion fuel logistics, BGA digestion, and energy export into different building families.

## Conversion Lanes

### Lane 1: Vanilla-Compatible Silage

Use this for materials that already fit the FS25 bunker silo model or are close enough:

- `CHAFF`
- `GRASS_WINDROW`
- `DRYGRASS_WINDROW`
- optional map forage crops such as `ALFALFA_WINDROW`, `CLOVER_WINDROW`, `FIELDGRASS`, `SILAGEMAIZE`

Preferred behavior:

- Reuse vanilla bunker silo behavior where possible.
- Add optional Phobos-owned production recipes only where a map/mod crop cannot enter the vanilla bunker route safely.
- Output should be `SILAGE` when the input is truly ensiled forage.

### Lane 2: Wet Biomass Substrate

Use this for wet, sugary, starchy, or produce-waste materials:

- potatoes and washed potatoes
- sugar beet and chopped sugar beet
- carrots, parsnips, beetroot, onions
- sugarcane
- fruit and vegetable waste
- compost and organic residuals

Preferred behavior:

- Process through a Phobos-owned biomass preparation production.
- Output should be a Phobos-owned intermediate substrate, not vanilla `SILAGE`, unless testing proves vanilla silage is the better gameplay compromise.
- The substrate then feeds a Phobos-owned BGA intake or a guarded optional BGA integration.
- Prefer `COMPOST` when present because maps may already support it as a handled/spreadable material. Treat `COMPOST_RAW` and `ORGANICWASTE` as detected aliases or fallback inputs, not as fillTypes this mod should define separately.

### Lane 3: Whole-Crop And Grain Mash

Use this for cereal or grain crops that can be diverted to energy but should not outperform food/feed use:

- wheat, barley, oat
- rye, green rye, triticale, spelt
- sorghum
- rice
- dry maize

Preferred behavior:

- Whole-crop/green-cut variants can go toward silage-like substrate at good efficiency.
- Dry grain diversion should require milling, soaking, or mashing and should be less profitable than dedicated energy crops.
- This lane should have higher processing cost or lower yield to prevent easy money loops.

### Lane 4: Residue And Pretreatment

Use this for fibrous residues and emergency feedstocks:

- straw
- flax straw
- crop windrow residue
- rice husk
- woodchips and poplar, if included at all

Preferred behavior:

- Require pretreatment before BGA use.
- Output low-grade substrate at poor conversion rates.
- Keep this lane optional or late-stage. It is useful for cleanup gameplay, not premium power generation.
- Treat `WOODCHIPS` primarily as combustion fuel. Do not send it to the digester by default, and keep it in the dry fuel yard silo rather than inside a BGA intake production point.

## First Playable Implementation

The first implementation should be deliberately narrow:

1. Add Phobos-owned companion production points: PlanET Biomass Intake, Wet Substrate Prep, and Dry Fuel Processor.
2. Depend on `FS25_PlanET_BGA_Modular` and `pdlc_strawHarvestPack` for the proof of concept.
3. Convert selected high-confidence vanilla inputs into PlanET internal feedstocks.
4. Use `SILAGE_IN` for forage-like biomass and `SUGARBEETCUT_IN` for wet/starchy/root biomass.
5. Use existing `STRAW_PELLETS` for the dry heat route to the HALLSYS Pellet Heat Plant.
6. Avoid adding any new fillTypes until a standalone or non-PlanET pathway genuinely needs one.

Initial input set:

- `GRASS_WINDROW`
- `DRYGRASS_WINDROW`
- `CHAFF`
- `SUGARBEET_CUT`
- `POTATO`
- `BEETROOT`
- `CARROT`
- `PARSNIP`

Current biomass intake recipes:

- `CHAFF` -> `SILAGE_IN`
- `CHAFF` + `SILAGE_ADDITIVE` -> improved `SILAGE_IN`
- `SILAGE` -> priority `SILAGE_IN`
- `GRASS_WINDROW` -> `SILAGE_IN`
- `GRASS_WINDROW` + `SILAGE_ADDITIVE` -> improved `SILAGE_IN`
- `DRYGRASS_WINDROW` -> `SILAGE_IN`
- `STRAW` -> `SILAGE_IN` at poor efficiency

Current Dry Fuel Processor recipes:

- `STRAW` -> `STRAW_PELLETS` for the Straw Harvest HALLSYS Pellet Heat Plant

Current Wet Substrate Prep recipes:

- `SUGARBEET_CUT` -> `PHB_WET_BIOMASS_MASH`
- `SUGARCANE` -> `PHB_WET_BIOMASS_MASH`
- `POTATO` -> `PHB_WET_BIOMASS_MASH`
- `BEETROOT` -> `PHB_WET_BIOMASS_MASH`
- `CARROT` -> `PHB_WET_BIOMASS_MASH`
- `PARSNIP` -> `PHB_WET_BIOMASS_MASH`
- `SPINACH` -> `PHB_WET_BIOMASS_MASH`
- `PEA` -> `PHB_WET_BIOMASS_MASH`
- `GREENBEAN` -> `PHB_WET_BIOMASS_MASH`
- `PHB_WET_BIOMASS_MASH` -> `SUGARBEETCUT_IN`
- `PHB_WET_BIOMASS_MASH` + `SILAGE_ADDITIVE` -> improved `SUGARBEETCUT_IN`

Current dry fuel yard storage:

- `WOODCHIPS` and `STRAW_PELLETS` -> medium or large dry fuel yard storage for heat-plant logistics

Optional detected inputs for the first expansion:

- `ALFALFA`
- `ALFALFA_WINDROW`
- `CLOVER`
- `CLOVER_WINDROW`
- `FIELDGRASS`
- `SILAGEMAIZE`
- `COMPOST`
- `COMPOST_RAW`
- `ORGANICWASTE`

Active optional add-on inputs:

- `POTATO_WASHED` -> `PHB_WET_BIOMASS_MASH` in `FS25_BgaExtensions_PotatoWasherCompat`
- `ORGANICWASTE` -> `PHB_WET_BIOMASS_MASH` in `FS25_BgaExtensions_OrchardsGreenhousesCompat`
- `ORGANICWASTE` -> `COMPOST` in `FS25_BgaExtensions_OrchardsGreenhousesCompat`

Generated waste should be conservative:

- use `DIGESTATE` as the normal BGA residue
- use `CHAFF`, `STRAW`, `SUGARBEET_CUT`, or `WOODCHIPS` for coarse byproducts where they are close enough
- use detected mod fillTypes such as `COMPOST`, `COMPOST_RAW`, `ORGANICWASTE`, or `RICE_HUSK` only when they already exist
- keep Maize+/MaizePlus and Corn Production Pack residue work out of active development until a future explicit decision
- avoid adding new one-off waste fillTypes until a real gameplay loop needs them

Energy products should also be conservative:

- let PlanET own `METHANE`, `ELECTRICCHARGE`, and `DIGESTATE` output for now
- do not feed `METHANE` or `ELECTRICCHARGE` back into biomass intake recipes
- add any future methane/electricity handling as a separate energy export module, not as more intake recipes

## Why Not Patch Vanilla BGAs First?

Patching existing BGAs sounds attractive, but it makes the mod fragile:

- vanilla and map BGAs may have different XML layouts
- third-party BGAs may use internal fill types
- load order can affect custom fill types and related systems
- players may stack multiple BGA mods

The safer path is to ship a self-contained Phobos conversion chain first, then add optional integrations once the substrate and balancing model are proven.

## Fill Type Caution

The first proof of concept does not add a broad `PHB_BGA_SUBSTRATE`.

If `PHB_BGA_SUBSTRATE` is added later, it should not require custom bales in its first version.

If a custom fill type is added, keep it tightly scoped:

- used by Phobos-owned production/storage/placeable paths
- no custom bale dependency
- no animal food dependency
- no forage mixer dependency
- no assumption that every map supports ground tipping for it

## Balancing Model

Use maize silage as the baseline.

Suggested initial factors:

- exceptional forage and silage crops: `0.80-1.00`
- excellent wet/starchy substrate: `0.65-0.90`
- good mixed biomass: `0.45-0.75`
- fair diversion crops and byproducts: `0.20-0.60`
- emergency residues: `0.05-0.35`

The exact numbers should be tuned against vanilla BGA recipes after the first XML prototype is testable.

## Current By-Product Guidance

The current implementation now uses one Phobos-owned wet intermediary, `PHB_WET_BIOMASS_MASH`, in the Wet Substrate Prep placeable for wet/root/produce substrates before handing them to PlanET as `SUGARBEETCUT_IN`.

For by-products and farm-adjacent outputs, follow `docs/byproduct-integration-audit.md`:

- prefer existing fillTypes such as `COMPOST`, `DIGESTATE`, `STRAW_PELLETS`, `WOODCHIPS`, `ORGANICWASTE`, and `RICE_HUSK` when they already exist
- avoid defining one-off waste fillTypes unless the gameplay need is clear
- keep PlanET internal fillTypes as PlanET handoffs, not general Phobos farm commodities
- keep Maize+/MaizePlus integration parked until a future explicit decision
