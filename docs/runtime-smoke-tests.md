# Runtime Smoke Tests

Use these checks after installing a prerelease package in a disposable FS25 save.

The goal is to prove only what static validation cannot prove: FS25 accepts the placeables at runtime, the UI remains readable, triggers feel right in-game, and no Phobos-owned log warnings or errors appear. Full balance testing can wait until the basic runtime path is quiet.

## Reduced Testing Rule

CI now checks the common XML mistakes that previously required extra in-game smoke testing:

- XML parsing and `modDesc.xml` references
- package layout and forbidden repository paths
- known and guarded fillTypes
- l10n references
- construction tabs
- storage-only production-point fillTypes
- production inputs are covered by unload or bale triggers
- production outputs are covered by load triggers
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
5. Exit and run the log triage command with `-FailOnPhobosWarning`.

If that pass is clean and CI passed, broader personal testing can wait until the next gameplay session.

## Test Setup

- Use a disposable save.
- Enable `FS25_BgaExtensions`, `FS25_PlanET_BGA_Modular`, and Straw Harvest.
- For Potato Washer compatibility tests, also enable `FS25_BgaExtensions_PotatoWasherCompat` and `FS25_potatoWasher`.
- For Orchards/Greenhouses compatibility tests, also enable `FS25_BgaExtensions_OrchardsGreenhousesCompat` and `FS25_orchardsAndGreenhouses_crossplay`.
- Prefer the same map and mod set for repeated tests so new log lines are easier to compare.
- Do not test against an important career save until the disposable save is clean.

## Startup Checks

- The save loads without a Phobos-owned `Error:` or `Warning`.
- The shop shows:
  - Phobos PlanET Biomass Intake - Small
  - Phobos PlanET Biomass Intake - Medium
  - Phobos PlanET Biomass Intake - Large
  - Phobos PlanET Wet Substrate Prep
  - Phobos PlanET Dry Fuel Processor
  - Phobos PlanET Dry Fuel Yard - Medium
  - Phobos PlanET Dry Fuel Yard - Large
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
| Straw pretreatment | Unload `STRAW`, start straw pretreatment. | Low-yield `SILAGE_IN` route works. |
| Manure | Unload `MANURE`, start manure intake. | `MANURE_IN` is produced. |
The biomass intakes no longer accept wet/root/produce crops directly, and they no longer produce straw pellets. Those routes belong to Wet Substrate Prep and Dry Fuel Processor.

## Wet Substrate Prep Checks

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Root mash | Unload one root crop such as `POTATO`, `BEETROOT`, `CARROT`, or `PARSNIP`. | `PHB_WET_BIOMASS_MASH` is produced. |
| Produce mash | Unload one produce crop such as `SPINACH`, `PEA`, or `GREENBEAN`. | `PHB_WET_BIOMASS_MASH` is produced. |
| Beet cut mash | Unload `SUGARBEET_CUT`. | `PHB_WET_BIOMASS_MASH` is produced. |
| Wet mash conditioning | Start wet mash conditioning. | `SUGARBEETCUT_IN` is produced and can be loaded out. |
| Wet mash additive conditioning | Unload `SILAGE_ADDITIVE`, start wet mash conditioning with additive. | `SUGARBEETCUT_IN` is produced at the improved additive rate. |

## Dry Fuel Processor Checks

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Straw pelletizing | Unload `STRAW`, start straw pelletizing. | `STRAW_PELLETS` are produced and can be loaded out. |

## Dry Fuel Yard Checks

Run these on medium and large yards:

- Unload `WOODCHIPS`.
- Load `WOODCHIPS` back out.
- Unload `STRAW_PELLETS`.
- Load `STRAW_PELLETS` back out.
- Confirm capacities are medium 320,000 l and large 600,000 l.
- Confirm the visible fill plane looks acceptable for both materials.
- Confirm the yards do not create production-point storage warnings.

## Optional Add-On Checks

Only run these when the matching optional add-on and provider mod are installed.

| Add-on | Minimum check | Expected result |
| --- | --- | --- |
| Potato Washer Compat | Enable `FS25_BgaExtensions_PotatoWasherCompat` with `FS25_potatoWasher`, buy Phobos Washed Potato Prep, unload `POTATO_WASHED`, and start washed potato mash. | `PHB_WET_BIOMASS_MASH` is produced and can be loaded out for the normal Wet Substrate Prep route. |
| Orchards/Greenhouses Compat | Enable `FS25_BgaExtensions_OrchardsGreenhousesCompat` with `FS25_orchardsAndGreenhouses_crossplay`, buy Phobos Organic Residue Prep, unload `ORGANICWASTE`, and start organic waste mash. | `PHB_WET_BIOMASS_MASH` is produced and can be loaded out for the normal Wet Substrate Prep route. |
| Orchards/Greenhouses Compat | Start organic waste composting. | `COMPOST` is produced and can be loaded out for the provider's normal compost/farm loop. |

## Log Review

After exiting the game, run:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1 -FailOnPhobosWarning
```

If your FS25 user folder is not in the usual Windows Documents location, pass the log path explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1 -LogPath "D:\path\to\FarmingSimulator2025\log.txt" -FailOnPhobosWarning
```

The command writes a JSON summary to `dist/current-log-summary.json` by default. Do not upload full logs publicly unless needed, because logs can include local paths and installed mod lists.

## Pass Criteria

A prerelease is ready for broader personal testing when:

- all changed placeables can be bought and placed
- intended inputs are accepted
- intended outputs can be loaded or consumed downstream
- production UI remains readable
- no recurring Phobos-owned hitching is visible
- no Phobos HUD texture raw-format or mip-generation warnings appear
- no Phobos-owned warnings or errors appear in the log

If a Phobos-owned warning or error appears, stop expanding that feature and record the line in `docs/known-log-lines.md`.
