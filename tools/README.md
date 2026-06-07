# Tools

Helper scripts for packaging, validation, or release maintenance can live here.

## Packaging

Run `tools/package.ps1` from PowerShell to create `dist/FS25_BgaExtensions.zip`.

The archive contains the contents of `mod/` at the zip root, which is the layout Farming Simulator expects.

GitHub CI uses `tools/package_mod.py` for the same zip layout on hosted Linux runners.

## Validation

Run `tools/validate_mod.py` with Python 3.11+ to perform static checks that do not require FS25:

- XML parse checks
- active fillType reference checks
- optional fillType guard checks
- storage-only production-point guard checks
- l10n reference checks
- recipe count target checks
- package layout and size checks when `--package` is provided

## Log Measurement

Run `tools/measure_log.py --log <path-to-log.txt>` after an in-game disposable-save test to separate Phobos-owned warnings/errors from external mod noise.
