# Runtime Smoke Tests

Use these checks after installing a prerelease package in a disposable FS25 save.

The goal is to prove that the current Phobos placeables can be bought, placed, filled, run, unloaded, and closed without Phobos-owned log warnings or errors. Full balance testing can wait until the basic runtime path is quiet.

## Test Setup

- Use a disposable save.
- Enable `FS25_BgaExtensions`, `FS25_PlanET_BGA_Modular`, and Straw Harvest.
- Prefer the same map and mod set for repeated tests so new log lines are easier to compare.
- Do not test against an important career save until the disposable save is clean.

## Startup Checks

- The save loads without a Phobos-owned `Error:` or `Warning`.
- The shop shows:
  - Phobos PlanET Biomass Intake - Small
  - Phobos PlanET Biomass Intake - Medium
  - Phobos PlanET Biomass Intake - Large
  - Phobos PlanET Dry Fuel Yard - Small
  - Phobos PlanET Dry Fuel Yard - Medium
  - Phobos PlanET Dry Fuel Yard - Large
- All six items can be placed and sold in the disposable save.

## Biomass Intake Checks

Test at least one intake size first. If it passes, repeat placement and a smaller sample on the other two sizes.

For `v0.2.7.0` and later, confirm the intake capacity values are visibly larger than the earlier prerelease values. This is a storage/logistics change only; recipe speed and yield should remain unchanged.

| Route | Minimum check | Expected result |
| --- | --- | --- |
| Chaff substrate | Unload `CHAFF`, start chaff substrate. | `SILAGE_IN` is produced and can be loaded out. |
| Additive bonus | Unload `CHAFF` or `GRASS_WINDROW` plus `SILAGE_ADDITIVE`, start the matching additive recipe. | Output route works and the recipe is readable in the UI. |
| Prepared silage | Unload `SILAGE`, start prepared silage intake. | `SILAGE_IN` is produced. |
| Grass and hay | Unload `GRASS_WINDROW` and `DRYGRASS_WINDROW`. | Both accepted by the intake and produce `SILAGE_IN`. |
| Straw pretreatment | Unload `STRAW`, start straw pretreatment. | Low-yield `SILAGE_IN` route works. |
| Straw pelletizing | Unload `STRAW`, start straw pelletizing. | `STRAW_PELLETS` are produced and can be loaded out. |
| Manure | Unload `MANURE`, start manure intake. | `MANURE_IN` is produced. |
| Wet mash crops | Unload one root crop plus one produce crop such as `SPINACH`, `PEA`, or `GREENBEAN`. | `PHB_WET_BIOMASS_MASH` is produced. |
| Wet mash conditioning | Start wet mash conditioning. | `SUGARBEETCUT_IN` is produced and can be loaded out. |

## Dry Fuel Yard Checks

Run these on small, medium, and large yards:

- Unload `WOODCHIPS`.
- Load `WOODCHIPS` back out.
- Unload `STRAW_PELLETS`.
- Load `STRAW_PELLETS` back out.
- Confirm capacities are small 160,000 l, medium 320,000 l, and large 600,000 l.
- Confirm the visible fill plane looks acceptable for both materials.
- Confirm the yards do not create production-point storage warnings.

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
