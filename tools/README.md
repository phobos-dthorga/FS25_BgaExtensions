# Tools

Helper scripts for packaging, validation, or release maintenance can live here.

## Packaging

Run `tools/package.ps1` from PowerShell to create `dist/FS25_BgaExtensions.zip`.

The archive contains the contents of `mod/` at the zip root, which is the layout Farming Simulator expects.

Optional add-ons can be packaged from their source folder:

```powershell
powershell -ExecutionPolicy Bypass -File tools\package.ps1 -SourcePath addons\FS25_BgaExtensions_PotatoWasherCompat
```

GitHub CI uses `tools/package_mod.py` for the same zip layout on hosted Linux runners and validates both the core package and active add-on packages.

## Validation

Run `tools/validate_mod.py` with Python 3.11+ to perform static checks that do not require FS25:

- XML parse checks
- `modDesc.xml` referenced file checks
- Phobos-owned `$moddir$FS25_BgaExtensions/...` asset reference checks
- Phobos HUD texture references use DDS rather than runtime PNG files
- active fillType reference checks
- optional fillType guard checks
- storage-only production-point guard checks
- Phobos construction tab checks
- l10n reference checks
- recipe count target checks
- package layout and size checks when `--package` is provided

For an add-on package, pass its source folder:

```powershell
python tools\validate_mod.py --mod-source addons\FS25_BgaExtensions_PotatoWasherCompat
```

## Log Measurement

Run `tools/measure-log.ps1` after an in-game disposable-save test to separate Phobos-owned warnings/errors from external mod noise. It uses the Python triage script when Python is available, falls back to a small PowerShell summary when it is not, and writes `dist/current-log-summary.json` by default.

The wrapper checks `PHOBOS_PYTHON_PATH`, common per-user Python install paths, every discovered `python`, and then every discovered `py`. This avoids the Microsoft Store Python alias when a real Python install is also present.

If the FS25 log is not in the usual Windows Documents path, pass it explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1 -LogPath "D:\path\to\FarmingSimulator2025\log.txt" -FailOnPhobosWarning
```

The underlying Python script can also be run directly:

```powershell
python tools/measure_log.py --log "D:\path\to\FarmingSimulator2025\log.txt" --fail-on-phobos-warning
```
