# Integration Strategy

This document defines how `FS25_BgaExtensions` should integrate with other FS25 mods, especially `FS25_PlanET_BGA_Modular`.

For the full build workflow, validation method, and resource policy, see `docs/implementation-approach.md`.

## Core Rule

Ship companion modules, not edits to other mods.

`FS25_BgaExtensions` should work alongside supported mods by adding GBW-owned placeables, recipes, and compatibility logic. It should not modify, repackage, or redistribute another author's mod files.

## PlanET Integration

For PlanET-specific features, treat `FS25_PlanET_BGA_Modular` as the BGA framework:

- declare a dependency when a feature requires PlanET fillTypes or behavior
- use PlanET's registered fillTypes as integration points, such as `SILAGE_IN` and `SUGARBEETCUT_IN`
- add GBW-owned intake, preprocessing, storage, or routing modules that feed PlanET's existing modules
- keep GBW recipes and balancing in this repository
- avoid monkey-patching PlanET's existing placeables unless in-game testing proves a stable, release-safe API exists

The current proof of concept follows this model by adding GBW PlanET Biomass Intake, Wet Substrate Prep, Fermentation Vessel, and fuel-logistics modules that convert selected vanilla biomass into PlanET internal feedstocks.

## Straw Harvest / HALLSYS Integration

For pellet heat features, treat `pdlc_strawHarvestPack` as the owner of the HALLSYS Pellet Heat Plant and pellet fillTypes.

- declare `pdlc_strawHarvestPack` when a feature uses `STRAW_PELLETS`, `HAY_PELLETS`, or `MOLASSES`
- output `STRAW_PELLETS` and `HAY_PELLETS` as dry-fuel handoffs to the HALLSYS Pellet Heat Plant ecosystem
- keep the HALLSYS plant itself dependency-owned and unmodified
- do not copy Straw Harvest XML, models, textures, icons, scripts, or sounds into this repository
- keep pellet BGA use additive-gated, premium versus matching raw hay/straw pretreatment, and still below prepared silage throughput so the heat route remains meaningful

The current proof of concept keeps assisted straw BGA pretreatment in the biomass intakes, moves pellet production to a focused Dry Fuel Processor, stores pellets in dry fuel yards, and allows pellet BGA use only through water-and-additive-assisted fermentation. Pellet liters are treated as compressed upstream biomass, so their fermenter output is balanced against raw-material equivalent instead of liter-for-liter pellet volume.

## Asset And Licensing Boundary

Using another mod as a dependency is not the same as copying it.

Allowed by default:

- depending on another mod by filename
- using fillTypes or gameplay registrations that exist at runtime
- referencing installed base-game, DLC, or dependency-owned assets from GBW XML when the owning content is required
- documenting compatibility behavior and required dependencies

Not allowed without clear license permission:

- copying another mod's XML, models, textures, icons, scripts, or sounds into this repository
- redistributing another mod's assets inside a GBW package
- publishing a patched version of another author's mod

## Reference, Do Not Vendor

The preferred safety boundary is to reference installed resources, not vendor them.

Acceptable references:

- `$data/...` paths for base-game resources
- `$moddir$SomeRequiredMod/...` paths for assets owned by a declared dependency
- registered fillTypes and runtime behavior exposed by an installed dependency

Requirements for dependency-owned references:

- the dependency must be declared or the feature must be guarded
- the referenced path must be tested in-game
- the GBW package must still contain only GBW-owned files
- attribution should be documented when a dependency meaningfully enables a feature

Do not copy dependency XML, models, textures, icons, scripts, or sounds into this repository merely because they can be referenced. Keep the original package as the insular safety net.

Prefer base-game assets or GBW-owned assets for release packages. Use dependency-owned references only when they are technically useful and the dependency relationship is explicit.

## Rebuild Policy

Do not require players to rebuild or edit `FS25_PlanET_BGA_Modular`.

For development, packaging can be automated from this repository. For release, ship `FS25_BgaExtensions.zip` as a normal add-on mod. Players should install it alongside PlanET and leave the original PlanET package untouched.

## Future Optional Integrations

If the mod later supports multiple BGA systems, keep integrations isolated:

- PlanET-specific recipes can depend on PlanET
- vanilla or standalone recipes should not require PlanET
- map/mod crop support should be guarded by fillType detection or separate compatibility modules where needed
- custom fillTypes should be added only when an existing vanilla or dependency-provided fillType cannot represent the gameplay cleanly

This keeps the mod release-friendly, easier to debug, and less likely to break when other mods update.
