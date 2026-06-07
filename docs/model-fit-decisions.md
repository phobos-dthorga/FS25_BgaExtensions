# Model Fit Decisions

This document records placeable model choices that affect gameplay clarity.

## Retired From Shop: Small Dry Fuel Yard

Starting with `v0.2.8.0`, `placeables/phobos/planetDryFuelYard.xml` is no longer listed as a shop item.

Reason:

- it reuses PlanET's small bunker model, `PlanET_Bunker_Klein.i3d`
- that model includes a rotating blade
- a rotating blade reads as active mixing, chopping, feeding, or processing
- the current dry fuel yard is only a passive silo for `WOODCHIPS` and `STRAW_PELLETS`

That visual language is a poor fit for combustion fuel storage. It can make the player expect a production point, which is exactly the confusion this mod should avoid.

The XML file remains in the package for now so disposable saves that already placed the small yard have a better chance of loading cleanly. Do not re-add it to `modDesc.xml` unless one of these becomes true:

- the small model is repurposed as a real dry fuel processor
- a cleaner small storage model replaces it
- the blade animation can be disabled cleanly without modifying PlanET assets

## Repurposed: Wet Substrate Prep And Dry Fuel Processor

Starting with `v0.2.9.0`, the same small PlanET bunker model is used by `placeables/phobos/planetWetSubstratePrep.xml`.

That is a better visual fit because Wet Substrate Prep is an active mixing and conditioning process. The rotating blade now reinforces the gameplay role instead of contradicting it.

Starting with `v0.2.10.0`, `placeables/phobos/planetDryFuelProcessor.xml` also uses the small PlanET bunker model. This is acceptable because straw pelletizing is an active dry-material process rather than passive fuel storage.

Starting with `v0.2.11.0`, the optional Potato Washer compatibility add-on uses the same small PlanET bunker model for washed potato mash. This is also an active wet-material preparation process, so the mixer visual language remains appropriate.

## Current Placeable Model Fit

| Store item | Model | Current fit |
| --- | --- | --- |
| Wet Substrate Prep | `PlanET_Bunker_Klein.i3d` | Good active mixing/conditioning fit. |
| Washed Potato Prep add-on | `PlanET_Bunker_Klein.i3d` | Good active wet-material preparation fit. |
| Dry Fuel Processor | `PlanET_Bunker_Klein.i3d` | Acceptable active dry-material processing fit. |
| Medium Dry Fuel Yard | `PlanET_Bunker_Mittel.i3d` | Acceptable passive bunker storage. |
| Large Dry Fuel Yard | `PlanET_Bunker_Gross.i3d` | Acceptable passive bunker storage. |
