# Model Fit Decisions

This document records placeable model choices that affect gameplay clarity.

## Retired From Shop: Small Dry Fuel Yard

Starting with `v0.2.8.0`, `placeables/gbw/planetDryFuelYard.xml` is no longer listed as a shop item.

Reason:

- it reuses PlanET's small bunker model, `PlanET_Bunker_Klein.i3d`
- that model includes a rotating blade
- a rotating blade reads as active mixing, chopping, feeding, or processing
- the current dry fuel yard is only a passive silo for `WOODCHIPS`, `STRAW_PELLETS`, and `HAY_PELLETS`

That visual language is a poor fit for combustion fuel storage. It can make the player expect a production point, which is exactly the confusion this mod should avoid.

From `v0.2.8.0` through `v0.2.14.0`, the XML file remained in the package so disposable saves that already placed the small yard had a better chance of loading cleanly.

Starting with the breaking `v0.2.15.0` GBW rebrand, that legacy XML path is removed along with the old pre-GBW placeable paths. Test saves that used the hidden small yard or old identifiers should stay on `v0.2.14.0`, or move forward with a fresh disposable save.

Do not re-add the small dry fuel yard to `modDesc.xml` unless one of these becomes true:

- the small model is repurposed as a real dry fuel processor
- a cleaner small storage model replaces it
- the blade animation can be disabled cleanly without modifying PlanET assets

## Repurposed: Wet Substrate Prep And Dry Fuel Processor

Starting with `v0.2.9.0`, the same small PlanET bunker model is used by `placeables/gbw/planetWetSubstratePrep.xml`.

That is a better visual fit because Wet Substrate Prep is an active mixing and conditioning process. The rotating blade now reinforces the gameplay role instead of contradicting it.

Starting with `v0.2.10.0`, `placeables/gbw/planetDryFuelProcessor.xml` also uses the small PlanET bunker model. This is acceptable because pelletizing is an active dry-material process rather than passive fuel storage.

Starting with `v0.2.11.0`, the optional Potato Washer compatibility add-on uses the same small PlanET bunker model for washed potato mash. This is also an active wet-material preparation process, so the mixer visual language remains appropriate.

Starting with `v0.2.12.0`, the optional Orchards/Greenhouses compatibility add-on uses the same small PlanET bunker model for organic residue preparation. This is acceptable because organic waste mashing and compost routing are active material-handling processes.

Starting with `v0.2.21.0`, the same add-on uses the small PlanET bunker model for Waste-Aware Wet Substrate Prep. This is still an active wet-material preparation process, so the mixer visual language remains appropriate. The `ORGANICWASTE` side-stream is a by-product of prep, not passive storage.

Starting with `v0.2.20.0`, the same add-on adds `placeables/gbw/compostBay.xml`, which references the Orchards/Greenhouses compost silo model and store icon. This avoids using another PlanET bunker for compost. The visual language should read as a physical composting bay or heap, not as BGA machinery.

Starting with `v0.2.16.0`, mash fermentation moves from Wet Substrate Prep into `placeables/gbw/planetFermentationVessel.xml`, which references PlanET's `PlanET_Fermenter100.i3d` model and store icon from the required PlanET Modular BGA dependency.

This is a better visual fit because the process is no longer framed as a bunker mixer magically turning mash into downstream BGA substrate. The tank reads as fermentation or digestion equipment, which matches the biological step.

Starting with `v0.2.19.0`, process supply logistics move into `placeables/gbw/planetProcessSupplyHub.xml`, which references PlanET's `PlanET_GuelleLager.i3d` model and store icon from the same dependency.

This is a good fit for `WATER` because the building already reads as a liquid or process-material storage point. GBW uses it as a production-style distributor so process water can be routed automatically to nearby process buildings.

`v0.2.19.0` reused the model's mixer unload trigger for all three materials. In-game testing showed that trigger was too small, too low, and visually inside the object. Starting with `v0.2.19.1`, the hub uses a water-marked liquid unload path for `WATER`, following the pattern observed in the Orchards/Greenhouses advanced greenhouse XML.

The first pallet implementations reused PlanET's front bale trigger, then tried a small wrapper I3D with custom trigger nodes. In-game testing showed that this was still a poor fit: the wrapper made the PlanET model invisible, and the exact-fill unload root presented a bulk trailer unload icon rather than a pallet handoff for `MOLASSES` and `SILAGE_ADDITIVE`.

Starting with `v0.2.19.3`, `SILAGE_ADDITIVE` and `MOLASSES` move to `placeables/gbw/processPalletDock.xml`, which uses the vanilla generic product unloading pad and `markerIconPallet.i3d`. Do not use bale trigger nodes, wrapper I3Ds, or bulk trailer unload icons as a stand-in for pallet or container logistics.

PlanET terms used in source names:

- `Fermenter`: fermenter.
- `FluessigFermenter`: liquid fermenter.
- `GaerresteLager`: digestate storage.
- `GuelleLager`: slurry or liquid manure storage.
- `Nachgaerer`: secondary or post-digester.
- `Fackel`: flare.
- `Strom Verteiler`: power distributor.

Do not copy PlanET model, texture, or store-icon binary files into GBW unless clear license permission is recorded. Reference them through `$moddir$FS25_PlanET_BGA_Modular/...` while the PlanET dependency is declared. Do not use a GBW wrapper I3D around remote PlanET shape resources unless a future isolated test proves that pattern renders correctly.

The same dependency-reference rule applies to Orchards/Greenhouses assets. Do not copy the compost silo model, shape file, or store icon into GBW while `FS25_orchardsAndGreenhouses_crossplay` is a declared dependency.

## Current Placeable Model Fit

| Store item | Model | Current fit |
| --- | --- | --- |
| Wet Substrate Prep | `PlanET_Bunker_Klein.i3d` | Good active wet-material mixing fit. |
| Fermentation Vessel | `PlanET_Fermenter100.i3d` | Good fermentation-tank fit for mash fermentation. |
| Process Supply Hub | `PlanET_GuelleLager.i3d` | Good process-water storage and distribution fit; water uses a dedicated water-marked unload path. |
| Process Pallet Dock | `sellingStationProducts.i3d` | Plain but reliable pallet/container supply point for `SILAGE_ADDITIVE` and `MOLASSES`; includes a minimal loading station because FS25 requires an output mechanism for dispatcher productions. |
| Washed Potato Prep add-on | `PlanET_Bunker_Klein.i3d` | Good active wet-material preparation fit. |
| Organic Residue Prep add-on | `PlanET_Bunker_Klein.i3d` | Good active residue preparation fit. |
| Waste-Aware Wet Substrate Prep add-on | `PlanET_Bunker_Klein.i3d` | Good active wet-material preparation fit; emits provider-owned `ORGANICWASTE` only in the Orchards/Greenhouses add-on. |
| Compost Bay add-on | Orchards/Greenhouses `compostSilo.i3d` | Good physical composting/logistics fit; avoids another generic PlanET bunker. |
| Dry Fuel Processor | `PlanET_Bunker_Klein.i3d` | Acceptable active dry-material processing fit. |
| Medium Dry Fuel Yard | `PlanET_Bunker_Mittel.i3d` | Acceptable passive bunker storage. |
| Large Dry Fuel Yard | `PlanET_Bunker_Gross.i3d` | Acceptable passive bunker storage. |
