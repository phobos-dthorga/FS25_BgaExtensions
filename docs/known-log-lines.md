# Known Log Lines

This ledger records FS25 log observations that affect development decisions.

Current log checked on 2026-06-07:

`D:\synologydrive\phobosdthorga\cloudstation drive\google drive\gekko-data\Documents\My Games\FarmingSimulator2025\log.txt`

## Healthy Lines

| Log pattern | Meaning |
| --- | --- |
| `Available mod: ... (Version: 0.2.3.0) FS25_BgaExtensions` | The packaged mod was visible to the game. |
| `Load mod: FS25_BgaExtensions` | The mod was selected and loaded in the tested save. |
| `Info: Loaded 1 fill types from mod: FS25_BgaExtensions` | Phobos `PHB_WET_BIOMASS_MASH` registered. |
| `Load mod: FS25_PlanET_BGA_Modular` and `Loaded 9 fill types` | PlanET dependency was present and its fillTypes loaded. |
| `Loaded 3 fill types from mod: pdlc_strawHarvestPack` | Straw Harvest pDLC dependency was present and loaded. |

## Phobos Findings

| Log line | Status | Action |
| --- | --- | --- |
| `Input filltype 'PHB_WET_BIOMASS_MASH' is not supported by unloading station` | Phobos warning found in `v0.2.3.0`. | Fixed in `v0.2.3.1` by allowing `PHB_WET_BIOMASS_MASH` on the intake unload triggers. |
| `storage fillType 'WOODCHIPS' not used as a production input or output` | Phobos warning found in `v0.2.3.0`. | Fixed in `v0.2.3.1` by removing storage-only wood chip handling from production-point XML. `v0.2.5.0` provides small, medium, and large dry fuel yard silos for wood chip and straw pellet storage. |

## Pending Test Targets

For `v0.2.5.1`, smoke-test all three dry fuel yard sizes:

- buy and place small, medium, and large yards
- unload `WOODCHIPS`
- unload `STRAW_PELLETS`
- load both materials back out
- confirm the visible fill plane behaves acceptably
- check the log for Phobos-owned warnings or errors

## User Test Confirmation

On 2026-06-07, the user reported that the current tested package works correctly: inputs appear correct visually within the bunkers, processes work as expected, and the checked game log appeared clean.

Treat this as successful proof-of-concept confirmation for the PlanET biomass intake path. Continue using disposable saves for new feature slices.

## External Or Unattributed Lines

| Log line | Current interpretation | Action |
| --- | --- | --- |
| `Error: Index not found: unloadTriggerMarker` | Appeared near map/Corn Production Pack/Nordkirchen placeable loading, with no Phobos path in the line. | Monitor, but do not assume Phobos ownership. |
| `Error: Index not found: aiLoadingNode` | Same context as above. | Monitor. If it repeats in a minimal Phobos test save, investigate immediately. |
| `FS25_varioMaster... has invalid fillType 'ALFALFA_WINDROW'` and similar clover/alfalfa lines | Another mod references optional map crop fillTypes that are absent in the loaded context. | Evidence for guarded compatibility. Do not add optional fillTypes to Phobos core XML. |
| `Missing sample 'turnOn' in SprayerNodeData` / `turnOff` | Repeated external equipment warning. | Ignore for Phobos unless it appears in a minimal test set. |
| `FS25_RGC_Productions... #unit is not supported anymore` | External mod uses an older XML attribute. | Ignore for Phobos. |

## Review Habit

After each disposable-save test:

1. Search for `FS25_BgaExtensions`.
2. Search for `Warning (` paths that include `FS25_BgaExtensions`.
3. Search for `Error:` near the time Phobos placeables are placed or loaded.
4. Add new findings here with date, version, interpretation, and action.

Do not normalize warnings as harmless if they come from Phobos XML. Either fix them, document why they are acceptable, or remove the feature that causes them.
