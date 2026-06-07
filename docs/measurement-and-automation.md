# Measurement And Automation

This document explains how `FS25_BgaExtensions` performance and health measurements are collected, which checks can be automated, and which checks still require a local FS25 run.

## Current Automation Layers

| Layer | Where it runs | Current status | What it can prove |
| --- | --- | --- | --- |
| Static validation | GitHub Actions and local tools | Implemented | XML is well-formed, `modDesc.xml` references exist, Phobos-owned asset references resolve, core fillTypes are known, optional fillTypes are not in core XML, storage-only production warnings are prevented, l10n references resolve, recipe count stays below the hard target. |
| Package validation | GitHub Actions and local tools | Implemented | The zip has FS25's expected root layout, avoids repository-only folders, and stays under the XML-only package size target. |
| Log triage | Local machine after an FS25 test | Implemented | Phobos-owned warnings/errors are separated from external mod noise. |
| Runtime smoke test | Local FS25 disposable save | Manual, documented in `docs/runtime-smoke-tests.md` | The placeable can be bought, placed, filled, activated, unloaded, and connected to the intended PlanET or Straw Harvest loop. |
| Load-time comparison | Local FS25 disposable save | Manual with light scripting | A Phobos-enabled test can be compared with a baseline test using the same map/mod stack. |
| Hitching/UI feel | Local FS25 disposable save | Manual | Whether production UI size, yard use, or repeated interactions feel bad in actual play. |
| Full game automation | Local self-hosted runner only, if ever | Not implemented | Hosted GitHub runners cannot launch the user's installed FS25, DLCs, mods, maps, or saves. |

## GitHub CI

The CI workflow runs on pushes, pull requests to `main`, and manual dispatch.

It performs:

1. Checkout.
2. Python setup.
3. Source validation with `tools/validate_mod.py`.
4. Package build with `tools/package_mod.py`.
5. Package validation with `tools/validate_mod.py --package`.
6. Upload of a short-lived CI package artifact.

The CI package is for inspection and disposable-save testing. It is not a GitHub release artifact.

## Dependabot

Dependabot is configured for GitHub Actions. It should raise update pull requests when the workflow action versions move forward.

Review these updates normally. Do not auto-merge action major-version updates until CI passes and the workflow behavior is understood.

## Local Commands

Because this Windows shell may not have `python` on `PATH`, use any working Python 3.11+ interpreter locally. GitHub Actions supplies Python through `actions/setup-python`.

Validate source:

```powershell
python tools/validate_mod.py
```

Build a cross-platform CI-style package:

```powershell
python tools/package_mod.py --output dist/FS25_BgaExtensions_ci.zip
```

Validate source and package:

```powershell
python tools/validate_mod.py --package dist/FS25_BgaExtensions_ci.zip
```

Summarize the FS25 log after a disposable-save test:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1
```

Fail the command when Phobos-owned warnings or errors are present:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1 -FailOnPhobosWarning
```

If FS25 stores `log.txt` outside the usual Windows Documents path, pass it explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File tools\measure-log.ps1 -LogPath "D:\path\to\FarmingSimulator2025\log.txt" -FailOnPhobosWarning
```

## Measurement Recipes

### Static And Package Health

Run before every commit that changes `mod/`, `tools/`, or GitHub workflow files:

1. `tools/validate_mod.py`
2. `tools/package_mod.py`
3. `tools/validate_mod.py --package ...`

CI repeats this after push.

### Disposable-Save Runtime Test

Use this when a feature changes gameplay:

1. Build or download the latest package.
2. Install it beside the declared dependencies.
3. Start a disposable save with the target map and dependency set.
4. Buy and place each changed Phobos placeable.
5. Deliver each intended input class.
6. Activate the changed productions.
7. Confirm outputs can be loaded or consumed downstream.
8. Exit the game and run `tools/measure_log.py`.
9. Record any Phobos-owned warning/error in `docs/known-log-lines.md`.

### Load-Time Comparison

Use this only when a feature adds scripts, many assets, many recipes, or broad compatibility scanning.

Recommended method:

1. Use the same map, save, graphics settings, and mod list.
2. Run three baseline launches without `FS25_BgaExtensions`.
3. Run three launches with `FS25_BgaExtensions`.
4. Measure from clicking start/load to controllable in-game state.
5. Compare the median times.
6. Treat under 5 seconds or under 10 percent over baseline as acceptable.
7. Treat more than 10 seconds or more than 20 percent over baseline as a hard miss.

The FS25 log can help confirm whether the same mod set loaded, but a stopwatch or screen recording is still the most honest measure for player-visible load time.

### Runtime Hitching

Use this when adding Lua, compatibility scanning, many productions, or storage-heavy modules.

Recommended method:

1. Place the affected module.
2. Fill it with several accepted materials.
3. Open and close the production UI repeatedly.
4. Start, stop, and switch recipes.
5. Move vehicles through the yard while productions are active.
6. Watch for recurring pauses, not one-time shader or asset load hitches.
7. Review `log.txt` afterwards.

Repeated hitching attributable to Phobos is a hard miss even if the log is clean.

## What GitHub Cannot Prove

Hosted GitHub runners cannot currently prove:

- whether FS25 accepts a placeable in-game
- whether PlanET or Straw Harvest behave correctly with local installed versions
- whether a map-specific fillType exists
- whether a save loads cleanly after a player has placed the module
- whether production UI feels readable
- whether a vehicle, trigger, or unloading station behaves correctly

Those remain local-game measurements.

## Future Automation Options

Good next steps:

- Add branch protection once CI has proven stable.
- Add a pull request checkbox for disposable-save log review.
- Add a release workflow only after deciding whether GitHub or `tools/release.ps1` owns release creation. Do not run both as release creators.
- Add a local `measure-baseline` helper if load-time comparisons become frequent.
- Add Lua syntax/lint checks once Lua enters the repository.
- Add GIANTS schema validation if a redistributable or easily configured validator becomes available.
- Consider a self-hosted Windows runner only if local game-environment checks become worth the maintenance cost.

## Privacy Note

Game logs include local paths and the user's installed mod list. Do not upload full logs to GitHub automatically. Summaries are safer; full logs should be attached manually only when needed for a bug investigation.
