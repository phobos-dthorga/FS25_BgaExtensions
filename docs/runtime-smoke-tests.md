# Runtime Smoke Tests

Use these checks after installing a prerelease package in a disposable FS25 save.

The goal is to prove only what static validation cannot prove: FS25 accepts the placeables at runtime, the UI remains readable, triggers feel right in-game, and no GBW-owned log warnings or errors appear. Full balance testing can wait until the basic runtime path is quiet.

## Reduced Testing Rule

CI now checks the common XML mistakes that previously required extra in-game smoke testing:

- XML parsing and `modDesc.xml` references
- package layout and forbidden repository paths
- known and guarded fillTypes
- l10n references
- construction tabs
- storage-only production-point fillTypes
- production inputs are covered by unload, bale, or pallet triggers
- production outputs are covered by load triggers unless the placeable has a real pallet spawner
- same-fillType dispatcher recipes are allowed only for the Process Supply Hub and Process Pallet Dock
- the Process Supply Hub uses direct PlanET water handling, while the Process Pallet Dock uses a real pallet marker/trigger plus a load-out station rather than bulk unloading
- core fermentation-priority balance rules
- package version alignment and SHA-256 generation

After CI passes, use a targeted disposable-save test instead of retesting every route. Only run the full checklist when a change touches models, triggers, store placement, many recipes, loading stations, shared fillTypes, dependencies, or anything that already produced a runtime warning once.

For documentation-only, tooling-only, or CI-only changes, no in-game test is required.

## Minimum Targeted Pass

For a normal XML recipe or placeable change:

1. Load a disposable save with the changed package and its dependencies.
2. Buy and place only the changed placeable family.
3. Test one representative changed input and one representative changed output.
4. Open the production UI once and confirm the changed recipe is readable.
5. Exit and run the log triage command with `-FailOnGBWWarning`.

If that pass is clean and CI passed, broader personal testing can wait until the next gameplay session.

## Test Setup

- Use a disposable save.
- Enable `FS25_BgaExtensions`, `FS25_PlanET_BGA_Modular`, and Straw Harvest.
- For Potato Washer compatibility tests, also enable `FS25_BgaExtensions_PotatoWasherCompat` and `FS25_potatoWasher`.
- For Orchards/Greenhouses compatibility tests, also enable `FS25_BgaExtensions_OrchardsGreenhousesCompat` and `FS25_orchardsAndGreenhouses_crossplay`.
- For data-pack API tests, also enable `FS25_GBWDataPack_Template`.
- Prefer the same map and mod set for repeated tests so new log lines are easier to compare.
- Do not test against an important career save until the disposable save is clean.

## Startup Checks

- The save loads without a GBW-owned `Error:` or `Warning`.
- The shop shows:
  - GBW PlanET Biomass Intake - Small
  - GBW PlanET Biomass Intake - Medium
  - GBW PlanET Biomass Intake - Large
  - GBW Wet Substrate Prep
  - GBW Fermentation Vessel
  - GBW Process Supply Hub
  - GBW Process Pallet Dock
  - GBW Dry Fuel Processor
  - GBW Dry Fuel Yard - Medium
  - GBW Dry Fuel Yard - Large
- The small dry fuel yard does not appear in the shop.
- All listed items can be placed and sold in the disposable save.

## Biomass Intake Checks

Test at least one intake size first. If it passes, repeat placement and a smaller sample on the other two sizes.

For `v0.2.7.0` and later, confirm the intake capacity values are visibly larger than the earlier prerelease values. For `v0.2.13.0` and later, confirm prepared silage is visibly the fastest and most efficient silage-family route, while direct raw chaff and grass remain useful but lower-yield.

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Chaff substrate | Unload `CHAFF`, start chaff substrate. | `SILAGE_IN` is produced and can be loaded out. |
| Additive bonus | Unload `CHAFF` or `GRASS_WINDROW` plus `SILAGE_ADDITIVE`, start the matching additive recipe. | Output route works, the recipe is readable in the UI, and the route remains below prepared silage efficiency. |
| Prepared silage | Unload `SILAGE`, start prepared silage intake. | `SILAGE_IN` is produced. |
| Grass and hay | Unload `GRASS_WINDROW` and `DRYGRASS_WINDROW`. | Both accepted by the intake and produce `SILAGE_IN`. |
| Straw pretreatment | Unload `STRAW` plus `SILAGE_ADDITIVE`, start assisted straw pretreatment. | Low-yield `SILAGE_IN` route works and remains below grass or hay. |
| Manure | Unload `MANURE`, start manure intake. | `MANURE_IN` is produced. |
The biomass intakes no longer accept wet/root/produce crops directly, and they no longer produce straw pellets. Those routes belong to Wet Substrate Prep and Dry Fuel Processor.

## Wet Substrate Prep Checks

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Sweet mash | Unload `SUGARBEET_CUT` or `SUGARCANE`. | `GBW_SWEET_MASH` is produced. |
| Root mash | Unload one root crop such as `POTATO`, `BEETROOT`, `CARROT`, or `PARSNIP`. | `GBW_ROOT_MASH` is produced. |
| Green mash | Unload one produce crop such as `SPINACH`, `PEA`, or `GREENBEAN`. | `GBW_GREEN_MASH` is produced. |

## Fermentation Vessel Checks

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Mash fermentation | Unload each available mash family into GBW Fermentation Vessel. | `SUGARBEETCUT_IN` is produced and can be loaded out. |
| Additive-assisted fermentation | Unload a mash family plus `SILAGE_ADDITIVE`, start the matching additive route. | `SUGARBEETCUT_IN` is produced at the improved additive rate. |
| Hay pellet fermentation | Unload `HAY_PELLETS`, `WATER`, and `SILAGE_ADDITIVE`, start assisted hay pellet fermentation. | `SILAGE_IN` is produced, the route is readable, and it remains weaker than properly fermented material. |
| Straw pellet fermentation | Unload `STRAW_PELLETS`, `WATER`, and `SILAGE_ADDITIVE`, start assisted straw pellet fermentation. | `SILAGE_IN` is produced, the route is readable, and it stays weaker than the hay pellet route. |
| Additive gate | Try to run a pellet fermentation route without `SILAGE_ADDITIVE`. | No plain pellet fermentation route is available. |
| Visual fit | Place the vessel beside a PlanET BGA layout. | The PlanET fermenter model reads as a fermentation step, not a crop-prep bunker. |

## Process Supply Hub Checks

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Water unload | Unload `WATER` from a water carrier at the water marker. | The marker and trigger are outside the object and water enters storage. |
| Water dispatch | Start process water dispatch and set the output to distributing. | Water can supply the Dry Fuel Processor and Fermentation Vessel without a new GBW fillType. |
| Visual fit | Place a fresh hub. | The PlanET slurry-storage model is visible; no wrapper-model invisibility appears. |
| Stop condition | Watch for same-input/same-output recipe warnings, loops, or UI oddities. | If the pattern misbehaves, do not add internal GBW supply fillTypes without a new design decision. |

## Process Pallet Dock Checks

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Placement | Place a fresh dock. | No `Could not load item` overlay appears and the log has no `No loading station or pallet spawner` error. |
| Pallet marker | Place a fresh dock and inspect the unload marker. | The dock uses the pallet icon, not the trailer/bulk unload icon. |
| Pallet unload | Unload `SILAGE_ADDITIVE` and `MOLASSES` through pallet/container handling at the dock. | Both supplies enter storage and no unsupported-unloading-station warning appears. |
| Output mechanism | Inspect loading/distribution behavior after adding supplies. | Additive and molasses are available through the dock's loading station and can be set to distributing. |
| Additive dispatch | Start silage additive dispatch and set the output to distributing. | Additive can supply biomass-intake additive routes and Fermentation Vessel additive routes. |
| Molasses dispatch | Start molasses dispatch and set the output to distributing. | Molasses can supply Dry Fuel Processor pelletizing routes. |
| Stop condition | If pallet supplies still cannot unload at the dock. | Do not revive the bulk exact-fill workaround; pause for a new trigger investigation. |

## Dry Fuel Processor Checks

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Straw pelletizing | Unload `STRAW`, `WATER`, and `MOLASSES`, start straw pelletizing. | `STRAW_PELLETS` are produced and can be loaded out. |
| Hay pelletizing | Unload `DRYGRASS_WINDROW`, `WATER`, and `MOLASSES`, start hay pelletizing. | `HAY_PELLETS` are produced and can be loaded out. |

## Dry Fuel Yard Checks

Run these on medium and large yards:

- Unload `WOODCHIPS`.
- Load `WOODCHIPS` back out.
- Unload `STRAW_PELLETS`.
- Load `STRAW_PELLETS` back out.
- Unload `HAY_PELLETS`.
- Load `HAY_PELLETS` back out.
- Confirm capacities are medium 320,000 l and large 600,000 l.
- Confirm the visible fill plane looks acceptable for all stored materials.
- Confirm the yards do not create production-point storage warnings.

## Optional Add-On Checks

Only run these when the matching optional add-on and provider mod are installed.

| Add-on | Minimum check | Expected result |
| --- | --- | --- |
| Potato Washer Compat | Enable `FS25_BgaExtensions_PotatoWasherCompat` with `FS25_potatoWasher`, buy GBW Washed Potato Prep, unload `POTATO_WASHED`, and start washed potato mash. | `GBW_ROOT_MASH` is produced and can be loaded out for the normal Fermentation Vessel route. |
| Orchards/Greenhouses Compat | Enable `FS25_BgaExtensions_OrchardsGreenhousesCompat` with `FS25_orchardsAndGreenhouses_crossplay`, buy GBW Organic Residue Prep, unload `ORGANICWASTE`, and start organic waste mash. | `GBW_RESIDUE_MASH` is produced and can be loaded out for the normal Fermentation Vessel route. |
| Orchards/Greenhouses Compat | Start organic waste composting. | `COMPOST` is produced and can be loaded out for the provider's normal compost/farm loop. |

## Data Pack API Checks

Only run these when testing the Stage 1 data-pack API.

| Route | Minimum check | Expected result |
| --- | --- | --- |
| API load | Enable `FS25_GBWDataPack_Template` beside GBW. | The save loads and the template data pack registers. |
| Known fillType route | Leave the template `GRASS_WINDROW` route enabled. | GBW logs that one active route was prepared. No gameplay recipe should appear yet. |
| Missing fillType route | Leave the template `GBW_MISSING_EXAMPLE` route enabled. | GBW logs an info-level skip, not a warning or error. |
| Stage 1 boundary | Open GBW production UIs. | No data-pack recipes are injected in this version. |

## Log Review

After exiting the game, run:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1 -FailOnGBWWarning
```

If your FS25 user folder is not in the usual Windows Documents location, pass the log path explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1 -LogPath "D:\path\to\FarmingSimulator2025\log.txt" -FailOnGBWWarning
```

The command writes a JSON summary to `dist/current-log-summary.json` by default. Do not upload full logs publicly unless needed, because logs can include local paths and installed mod lists.

## Pass Criteria

A prerelease is ready for broader personal testing when:

- all changed placeables can be bought and placed
- intended inputs are accepted
- intended outputs can be loaded or consumed downstream
- production UI remains readable
- no recurring GBW-owned hitching is visible
- no GBW HUD texture raw-format or mip-generation warnings appear
- no GBW-owned warnings or errors appear in the log

If a GBW-owned warning or error appears, stop expanding that feature and record the line in `docs/known-log-lines.md`.
