# Performance Targets

This document defines the performance and stability tripwires for `FS25_BgaExtensions`.

The point is not to over-measure an early proof of concept. The point is to know when a feature has become too expensive, too noisy, or too broad to keep expanding in its current form.

## Baseline Method

Use a disposable save for measurement.

Record:

- FS25 game version
- map name
- active dependency set
- Phobos version or commit
- whether the save is new or established
- whether `FS25_BgaExtensions` is enabled or disabled

When possible, compare against the same mod set with `FS25_BgaExtensions` disabled. If a clean comparison is not practical, treat the result as an observation rather than a hard benchmark.

Use these evidence sources first:

- FS25 `log.txt` timestamps and warning/error lines
- in-game placement, production, and loading behavior
- obvious UI lag, hitching, or repeated pauses
- package contents and package size

## Targets

| Area | Target | Hard miss | Required action |
| --- | --- | --- | --- |
| Phobos log health | No `Error:` or `Warning (` lines that include `FS25_BgaExtensions` or a Phobos-owned file path. | Any Phobos-owned error or warning in a release candidate, or any repeated Phobos-owned warning during development. | Stop expanding the feature. Fix, remove, or defer the cause before the next release. |
| External log noise | External warnings are documented only when relevant. | A warning initially believed external repeats in a minimal Phobos test set. | Reclassify it as Phobos-risk and investigate before release. |
| Save load impact | No obvious load-time regression. Target under 5 seconds or under 10 percent over baseline, whichever is easier to judge. | More than 10 seconds or more than 20 percent over baseline in a comparable test. | Profile by removal: disable recent feature, split module, remove heavy references, or defer the feature. |
| Runtime behavior | No visible recurring hitching during normal yard use. | Repeated hitches attributable to Phobos placeables, productions, or scripts. | Remove per-frame work, throttle checks, reduce recipe/storage scope, or split the module. |
| Lua runtime work | Prefer no Lua for data-driven recipes. If Lua is used, initialization should be bounded and recurring checks should be throttled. | Per-frame scans of all fillTypes, placeables, vehicles, productions, or active mods. | Block release until rewritten as data-driven XML, event-driven Lua, or a small bounded check. |
| Production UI size | Keep each placeable readable. Soft target: 18 or fewer recipes per placeable. | More than 24 recipes on one placeable, or the in-game production UI becomes awkward to scan. | Split into focused modules such as wet intake, dry residues, pellet fuel, or combustion yard. |
| FillType budget | Use vanilla or dependency fillTypes first. Soft target: 3 or fewer Phobos-owned custom fillTypes during pre-release. | More than 5 Phobos-owned custom fillTypes without a clear handling/storage contract. | Consolidate, convert to vanilla/dependency fillTypes, or move candidates back to documentation. |
| Storage design | Every stored fillType in a production point must be used by a production input or output. | Any storage-only fillType warning in the game log. | Remove the storage entry or implement a real production route/storage module. |
| Optional compatibility | Optional fillTypes never appear in core XML unless their provider is a declared dependency. | Missing-provider warnings from core XML. | Remove from core XML and move to a compatibility add-on, guarded Lua, or documentation-only state. |
| Package size | XML-only releases should remain tiny. Soft target: under 1 MB while no custom media exists. | More than 10 MB without intentional Phobos-owned assets, or more than 25 MB with early assets. | Audit package contents, compress assets, remove accidental files, or reference dependency assets instead of copying. |
| Save data | Avoid custom save data until a feature truly needs it. | Custom Phobos save data grows beyond 50 KB in a normal test save. | Reduce saved state, derive data at load, or remove the feature until it has a tighter model. |
| Multiplayer sync | No custom network sync until a feature needs it. | Repeated custom sync events or multiplayer-only log warnings. | Block stable release for that feature until sync is bounded and tested. |

## Decisive Action Rule

When a hard miss is found:

1. Stop adding scope to that feature.
2. Reproduce in a disposable save if possible.
3. Classify the cause as Phobos-owned, dependency-owned, external, or unknown.
4. Fix the smallest responsible part.
5. If the fix is not small, split the feature into a separate module or remove it from the release.
6. Record the finding in `docs/known-log-lines.md` or the relevant design note.
7. Mention the miss and fix in release notes if a public package already shipped with it.

Do not normalize Phobos-owned warnings as acceptable background noise.

## Release Gate

A pre-release may ship with documented external warnings, but it should not ship with known Phobos-owned hard misses.

A stable release must pass the targets above on a fresh disposable save with the documented required dependencies.
