# Conversion Process

This document defines the planned biomass conversion flow for `FS25_BgaExtensions`.

## Core Principle

Do not force every organic crop into vanilla `SILAGE`.

Some materials genuinely belong in a silage pathway. Others are better represented as wet biomass, grain mash, organic waste, or pretreated low-grade substrate. The mod should preserve those differences while still making many more organic materials useful for BGA energy production.

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
- organic waste and compost rawstock

Preferred behavior:

- Process through a Phobos-owned biomass preparation production.
- Output should be a Phobos-owned intermediate substrate, not vanilla `SILAGE`, unless testing proves vanilla silage is the better gameplay compromise.
- The substrate then feeds a Phobos-owned BGA intake or a guarded optional BGA integration.

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
- maize stalks and stalk pellets
- woodchips and poplar, if included at all

Preferred behavior:

- Require pretreatment before BGA use.
- Output low-grade substrate at poor conversion rates.
- Keep this lane optional or late-stage. It is useful for cleanup gameplay, not premium power generation.

## First Playable Implementation

The first implementation should be deliberately narrow:

1. Add one Phobos-owned production point: Biomass Preprocessor.
2. Add one Phobos-owned intermediate fill type: `PHB_BGA_SUBSTRATE`.
3. Let the preprocessor convert selected high-confidence inputs into `PHB_BGA_SUBSTRATE`.
4. Add one Phobos-owned BGA or BGA intake production that consumes `PHB_BGA_SUBSTRATE`.
5. Keep vanilla `SILAGE`, `MANURE`, `LIQUIDMANURE`, and `SUGARBEET_CUT` behavior intact.

Initial input set:

- `GRASS_WINDROW`
- `DRYGRASS_WINDROW`
- `CHAFF`
- `SUGARBEET_CUT`
- `POTATO`
- `BEETROOT`
- `CARROT`
- `PARSNIP`

Optional detected inputs for the first expansion:

- `ALFALFA`
- `ALFALFA_WINDROW`
- `CLOVER`
- `CLOVER_WINDROW`
- `FIELDGRASS`
- `SILAGEMAIZE`
- `ORGANICWASTE`
- `COMPOST_RAW`

## Why Not Patch Vanilla BGAs First?

Patching existing BGAs sounds attractive, but it makes the mod fragile:

- vanilla and map BGAs may have different XML layouts
- third-party BGAs may use internal fill types
- load order can affect custom fill types and related systems
- players may stack multiple BGA mods

The safer path is to ship a self-contained Phobos conversion chain first, then add optional integrations once the substrate and balancing model are proven.

## Fill Type Caution

`PHB_BGA_SUBSTRATE` should not require custom bales in the first version.

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

