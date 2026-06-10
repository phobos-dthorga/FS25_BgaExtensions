# Tools

Helper scripts for packaging, validation, or release maintenance can live here.

## Packaging

Run `tools/package.ps1` from PowerShell to create `dist/FS25_BgaExtensions.zip`.

The archive contains the contents of `mod/` at the zip root, which is the layout Farming Simulator expects.

Optional add-ons can be packaged from their source folder:

```powershell
powershell -ExecutionPolicy Bypass -File tools\package.ps1 -SourcePath addons\FS25_BgaExtensions_PotatoWasherCompat
powershell -ExecutionPolicy Bypass -File tools\package.ps1 -SourcePath addons\FS25_BgaExtensions_OrchardsGreenhousesCompat
```

GitHub CI uses `tools/package_set.py` and `tools/package_manifest.json` to build and validate the core package plus every active add-on package. Add new active add-ons to the manifest so local package-set builds and CI stay in sync.

Build and validate the whole package set locally:

```powershell
python tools\package_set.py --suffix ci_local --validate --write-sha256 --write-json
```

Build versioned packages from the manifest:

```powershell
python tools\package_set.py --versioned --validate --write-sha256 --write-json
```

## FillType Icons

Build GBW-owned fillType HUD DDS icons from source PNG artwork:

```powershell
python tools\build_filltype_icons.py
```

The source artwork lives under `assets/source/fillTypes/`. The generated DDS files live under `mod/hud/fillTypes/` so they are included in the FS25 package.

## Validation

Run `tools/validate_mod.py` with Python 3.11+ to perform static checks that do not require FS25:

- XML parse checks
- `modDesc.xml` referenced file checks
- GBW-owned `$moddir$FS25_BgaExtensions/...` asset reference checks
- GBW HUD texture references use DDS rather than runtime PNG files
- GBW-owned fillType HUD icons are 256x256 DXT5-compressed DDS files matching FS25/PlanET HUD texture style
- active fillType reference checks
- optional fillType guard checks
- production input/output trigger coverage checks
- same-fillType dispatcher recipe guard checks
- core fermentation-priority balance checks
- storage-only production-point guard checks
- GBW construction tab checks
- l10n reference checks
- recipe count target checks
- package layout and size checks when `--package` is provided

For an add-on package, pass its source folder:

```powershell
python tools\validate_mod.py --mod-source addons\FS25_BgaExtensions_PotatoWasherCompat
python tools\validate_mod.py --mod-source addons\FS25_BgaExtensions_OrchardsGreenhousesCompat
```

## Log Measurement

Run `tools/measure-log.ps1` after an in-game disposable-save test to separate GBW-owned warnings/errors from external mod noise. It uses the Python triage script when Python is available, falls back to a small PowerShell summary when it is not, and writes `dist/current-log-summary.json` by default.

The wrapper checks `GBW_PYTHON_PATH`, common per-user Python install paths, every discovered `python`, and then every discovered `py`. This avoids the Microsoft Store Python alias when a real Python install is also present.

If the FS25 log is not in the usual Windows Documents path, pass it explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1 -LogPath "D:\path\to\FarmingSimulator2025\log.txt" -FailOnGBWWarning
```

The underlying Python script can also be run directly:

```powershell
python tools/measure_log.py --log "D:\path\to\FarmingSimulator2025\log.txt" --fail-on-gbw-warning
```
