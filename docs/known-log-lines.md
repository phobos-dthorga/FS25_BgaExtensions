# Known Log Lines

This ledger records FS25 log observations that affect development decisions.

Current log checked on 2026-06-10:

Local FS25 `log.txt` supplied by the maintainer.

## Healthy Lines

| Log pattern | Meaning |
| --- | --- |
| `Available mod: ... (Version: 0.2.3.0) FS25_BgaExtensions` | The packaged mod was visible to the game. |
| `Load mod: FS25_BgaExtensions` | The mod was selected and loaded in the tested save. |
| `Info: Loaded 4 fill types from mod: FS25_BgaExtensions` | The four GBW mash fillTypes registered. |
| `Load mod: FS25_PlanET_BGA_Modular` and `Loaded 9 fill types` | PlanET dependency was present and its fillTypes loaded. |
| `Loaded 3 fill types from mod: pdlc_strawHarvestPack` | Straw Harvest pDLC dependency was present and loaded. |

## GBW Findings

The first entries in this table are pre-GBW historical lines from versions before `v0.2.15.0`.

| Log line | Status | Action |
| --- | --- | --- |
| Legacy wet-mash unloading-station warning | GBW warning found in `v0.2.3.0`. | Fixed in `v0.2.3.1`; `v0.2.15.0` replaced the legacy wet-mash fillType with family mash fillTypes. |
| `storage fillType 'WOODCHIPS' not used as a production input or output` | GBW warning found in `v0.2.3.0`. | Fixed in `v0.2.3.1` by removing storage-only wood chip handling from production-point XML. `v0.2.5.0` added dry fuel yard silos; `v0.2.8.0` keeps only medium and large variants in the shop. |
| Legacy wet-mash HUD PNG raw-format warning and CPU mip generation | GBW warning found in `v0.2.6.0`. | Fixed in `v0.2.7.1` by replacing runtime PNG HUD references with DDS textures. |
| `hud_fill_gbw*Mash.dds raw format` | GBW warning found in `v0.2.15.0`; all four mash HUD icons loaded as uncompressed DDS and generated repeated performance warnings. | Fixed in `v0.2.15.1` by rebuilding mash HUD icons as PlanET-style DXT5 DDS files and changing validation to reject uncompressed HUD DDS files. |
| Root `icon.dds raw format` warnings for GBW packages | GBW performance warning found during `v0.2.19.1` log triage. | Fixed in `v0.2.19.2` by rebuilding core, add-on, and data-pack-template mod icons as DXT5 DDS files and extending validation to reject raw `modDesc.xml` icons. |
| Process Supply Hub unload trigger was too small, too low, and inside the object | Runtime visual/interaction issue reported in `v0.2.19.0`. | Water side fixed in `v0.2.19.1` by replacing mixer unloading with a water-marked unload trigger. |
| Process Supply Hub pallet trigger still used a poor visual/interaction point | Runtime visual/interaction issue reported in `v0.2.19.1`. | Fixed in `v0.2.19.2` by moving to a GBW wrapper I3D with a dedicated pallet trigger shape and separate marker. |
| `Input filltype 'MOLASSES' is not supported by unloading station` and same for `SILAGE_ADDITIVE` | GBW warning found in `v0.2.19.1` log triage. | Fixed in `v0.2.19.2` by pairing the pallet trigger with an exact-fill unload root for pallet-supplied materials. |

## Pending Test Targets

For `v0.2.19.2`, smoke-test the Process Supply Hub pallet trigger hotfix:

- confirm core FS25_BgaExtensions loads as version `0.2.19.2`
- confirm `GBW Process Supply Hub` appears under `GBW BGA`
- confirm the water unload marker is visible and accessible outside the object
- confirm `WATER` unloads from a water carrier
- confirm the pallet unload marker is visible and accessible outside the object on a freshly placed hub
- confirm `SILAGE_ADDITIVE` and `MOLASSES` unload through pallet/container handling
- confirm no unsupported-unloading-station warning appears for `MOLASSES` or `SILAGE_ADDITIVE`
- confirm `WATER`, `SILAGE_ADDITIVE`, and `MOLASSES` can be loaded
- confirm dispatcher outputs can be set to distributing
- confirm distributed supplies feed the Dry Fuel Processor, Fermentation Vessel, and biomass-intake additive routes
- confirm no GBW-owned warnings or errors appear in the FS25 log

The user reported `v0.2.18.0` testing complete before the Process Supply Hub slice. A follow-up log scan showed no GBW-owned warnings or errors; observed errors and warnings were external to GBW.

## User Test Confirmation

On 2026-06-07, the user reported that the current tested package works correctly: inputs appear correct visually within the bunkers, processes work as expected, and the checked game log appeared clean.

Treat this as successful proof-of-concept confirmation for the PlanET biomass intake path. Continue using disposable saves for new feature slices.

## External Or Unattributed Lines

| Log line | Current interpretation | Action |
| --- | --- | --- |
| `Error: Index not found: unloadTriggerMarker` | Appeared near map/Corn Production Pack/Nordkirchen placeable loading, with no GBW path in the line. | Monitor, but do not assume GBW ownership. |
| `Error: Index not found: aiLoadingNode` | Same context as above. | Monitor. If it repeats in a minimal GBW test save, investigate immediately. |
| `FS25_varioMaster... has invalid fillType 'ALFALFA_WINDROW'` and similar clover/alfalfa lines | Another mod references optional map crop fillTypes that are absent in the loaded context. | Evidence for guarded compatibility. Do not add optional fillTypes to GBW core XML. |
| `Missing sample 'turnOn' in SprayerNodeData` / `turnOff` | Repeated external equipment warning. | Ignore for GBW unless it appears in a minimal test set. |
| `FS25_RGC_Productions... #unit is not supported anymore` | External mod uses an older XML attribute. | Ignore for GBW. |

## Review Habit

After each disposable-save test:

1. Search for `FS25_BgaExtensions`.
2. Search for `Warning (` paths that include `FS25_BgaExtensions`.
3. Search for `Error:` near the time GBW placeables are placed or loaded.
4. Add new findings here with date, version, interpretation, and action.

Do not normalize warnings as harmless if they come from GBW XML. Either fix them, document why they are acceptable, or remove the feature that causes them.
