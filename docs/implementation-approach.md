# Implementation Approach

This document explains how `FS25_BgaExtensions` should be built, tested, and expanded.

## Goal

Add richer biomass-to-BGA gameplay while staying compatible with Farming Simulator 25, PlanET Modular BGA, and common map/mod ecosystems.

The preferred player experience is simple:

1. Install the required dependency mod when a feature needs one.
2. Install `FS25_BgaExtensions` as its own mod.
3. Place GBW-owned companion modules in-game.
4. Feed additional biomass through those modules into the target BGA system.

Players should not need to edit, rebuild, or replace another author's mod.

## Architectural Style

Use companion modules first.

The mod should add its own placeables, recipes, and compatibility behavior beside the systems it integrates with. For PlanET support, this means GBW-owned intake or preprocessing modules that output PlanET-compatible internal feedstocks.

Prefer this order:

1. Existing vanilla fillTypes and base-game behavior.
2. Dependency-provided runtime fillTypes, when the dependency is declared.
3. GBW-owned placeables and recipes.
4. GBW-owned custom fillTypes only when existing fillTypes cannot represent the gameplay cleanly.
5. Lua hooks only when data-driven XML cannot safely express the feature.

Avoid this by default:

- editing another mod's XML
- repackaging another mod
- monkey-patching existing third-party placeables
- copying third-party assets into this repository
- adding one-off fillTypes for every crop or waste stream
- adding custom bales before the load-order behavior is proven safe

## PlanET Method

For PlanET-specific features, treat `FS25_PlanET_BGA_Modular` as a required framework.

Current method:

- declare `FS25_PlanET_BGA_Modular` as a dependency for PlanET-specific modules
- declare `pdlc_strawHarvestPack` when a feature uses Straw Harvest pellet fillTypes or HALLSYS heat-plant routing
- use its registered internal fillTypes as the contract, especially `SILAGE_IN` and `SUGARBEETCUT_IN`
- use PlanET models by dependency reference when their visual role matches the GBW process
- use Straw Harvest `STRAW_PELLETS`, `HAY_PELLETS`, and `MOLASSES` for pellet logistics when bridging dry biomass to the HALLSYS Pellet Heat Plant ecosystem
- keep vanilla `WOODCHIPS` out of the production-point intake; handle it through the dedicated dry fuel yard silo
- add GBW-owned modules that convert expanded biomass inputs into those internal fillTypes
- let PlanET's own fermenters, generators, storages, and distributors continue doing their normal work
- let the HALLSYS Pellet Heat Plant remain the destination for pellet fuel
- keep all GBW balancing and recipes in `FS25_BgaExtensions`

This gives compatibility without touching the PlanET or Straw Harvest packages.

## Resource Use

Use resources in tiers.

### Primary Technical Resources

- FS25 local XML schemas:
  - `shared/xml/schema/modDesc.xsd`
  - `shared/xml/schema/placeable.xsd`
  - `shared/xml/schema/fillTypes.xsd`
- FS25 base-game XML examples:
  - vanilla BGA production point definitions
  - vanilla fillType definitions
  - vanilla bunker silo behavior
- In-game testing:
  - new-save smoke tests
  - log review
  - buy/place/fill/produce/load checks

These are the authority for whether a file shape is acceptable.

### Dependency Resources

For dependency mods such as PlanET:

- inspect XML and fillTypes to understand the integration contract
- use registered fillType names at runtime when the dependency is declared
- use behavior patterns as reference material
- reference installed dependency assets from XML only when the dependency is required and the path is tested
- do not copy dependency assets or source files into this repository without clear license permission

For the current PlanET proof of concept, the dependency resources are internal fillTypes plus referenced PlanET bunker, fermenter, and store-icon assets. The placeable XML remains GBW-owned and the dependency remains the source of truth for its own assets.

### Reference Policy

Referencing is allowed; vendoring is not.

Use references such as `$data/...` or `$moddir$RequiredMod/...` when they point to content the player must already have installed. This keeps ownership clear and avoids duplicating third-party or DLC files inside the GBW package.

The GBW release zip should contain only GBW-owned files. A required dependency should remain the source of truth for its own assets, fillTypes, placeables, and scripts.

### Project Resources

- `docs/biomass-crop-ranking.md` defines feedstock priority and balancing intent.
- `docs/conversion-process.md` defines conversion lanes and first recipes.
- `docs/integration-strategy.md` defines the companion-module rule.
- `docs/dependency-contract.md` defines required dependency fillTypes and asset contracts.
- `docs/guarded-compatibility.md` defines how optional fillTypes are allowed to enter the project.
- `docs/data-pack-api.md` defines the public Stage 1 route-registration API for third-party data packs.
- `docs/performance-targets.md` defines performance tripwires and the required action when a target is missed.
- `docs/measurement-and-automation.md` defines how the performance targets are measured and what CI can automate.
- `docs/energy-carrier-strategy.md` defines which building family owns combustion fuels, BGA energy products, and digestate.
- `docs/construction-menu-categories.md` defines where GBW placeables appear in the FS25 construction menu.
- `docs/model-fit-decisions.md` records model choices that are hidden or retired because their visual language misleads the player.
- `docs/visual-assets.md` defines the custom visual asset policy.
- `docs/known-log-lines.md` records observed log messages and actions.
- `docs/release-process.md` defines pre-release and hotfix cadence.
- `docs/issue-management.md` defines when testing and follow-up work belongs in Issues, including duplicate avoidance.
- `docs/fs25-engine-constraints.md` records engine/load-order cautions.
- `mod/config/biomassCropRegistry.xml` is a draft data registry for future expansion.

## FillType Policy

FillTypes are a limited resource.

Use existing fillTypes wherever they are technically and thematically close enough. For example:

- use PlanET `SILAGE_IN` for prepared forage biomass in PlanET-specific modules
- use PlanET `SUGARBEETCUT_IN` for wet or starchy biomass in PlanET-specific modules
- use Straw Harvest `STRAW_PELLETS` and `HAY_PELLETS` for dry pellet fuel when the pellet heat route is active
- prefer `COMPOST` if it exists on a map/mod because other equipment may already support it
- treat `COMPOST_RAW` and `ORGANICWASTE` as detected aliases or fallback inputs, not fillTypes this mod should define casually

### Parked Maize Work

Maize+/MaizePlus integration is out of scope until the FS25 releases are production-ready, locally installed, and explicitly chosen as a target. Do not add Maize+/MaizePlus recipes, dependency entries, registry placeholders, compatibility packages, or tests before that decision.

`FS25_cornProductionPack` remains an observation source only. Do not target its fillTypes or naming model in shipped GBW content.

Add a GBW custom fillType only when it provides a clear gameplay boundary that cannot be represented well by vanilla or dependency-provided types.

### First-Use Verification

Do not introduce a fillType into recipes, storage, triggers, ranking tables, registries, or recommendations just because the name looks right.

Before first use, verify:

1. Where it is defined: vanilla data, a declared dependency, a map, another optional mod, or GBW XML.
2. What it represents in-game and what its real-world analogue is.
3. Whether it is a usable material or an internal-only handoff.
4. What handling support exists: bulk, liquid, pallet, bale, heap, forage wagon, mixer wagon, shovel/fork, tanker, hayloft, sell point, or production input/output.
5. Whether it needs runtime detection, a hard dependency, or a GBW-owned fallback.
6. Whether bales, ground tipping, animal food, forage mixing, or map-owned recipes create load-order or compatibility risk.
7. For production-point inputs, whether FS25 expects bulk/liquid unloading, pallet/container handling, or both; verify with a working example before adding trigger nodes.

Good verification sources include `data/maps/maps_fillTypes.xml`, `data/maps/maps_densityMapHeightTypes.xml`, bale XML, vehicle fillUnits/additives, placeable storage/loading XML, local dependency XML, and observed game-log behavior.

If a fillType is safe only in a narrow context, document that boundary. For example, PlanET internals such as `SILAGE_IN` are valid PlanET handoffs, not general farm commodities.

### Storage-Only Materials

Do not add storage-only materials to production-point storage merely to make a yard buffer. FS25 warns when a production point stores a fillType that is not used as a production input or output.

The `v0.2.3.0` wood chip experiment proved this. `WOODCHIPS` now belongs in the dry fuel yard silo, not inside the PlanET biomass intake production point.

The `v0.2.19.x` Process Supply Hub tests proved that a production input can look visually deliverable while still failing FS25's unloading behavior, and that wrapper I3Ds around dependency shapes can fail visually. Validate trigger coverage statically, then confirm it with the game log and a freshly placed runtime test.

## Implementation Workflow

Use this workflow for each feature:

1. Define the target gameplay loop.
2. Identify whether the feature is standalone, vanilla-compatible, or dependency-specific.
3. Confirm every required fillType exists and verify its actual role using the first-use checklist above.
4. Prefer a GBW-owned companion placeable over patching an existing one.
5. Choose the correct process building family from `docs/energy-carrier-strategy.md`.
6. Place the store item in the correct tab from `docs/construction-menu-categories.md`.
7. Keep recipes small and readable.
8. Validate XML against local FS25 schemas.
9. Package from `mod/` using `tools/package.ps1`.
10. Test in a fresh save before touching an existing save.
11. Review the game log and document any hard lessons.
12. Check the feature against `docs/performance-targets.md`.
13. Tune balancing after the loop works end to end.

## XML Duplication Note

The small, medium, and large intake XML files intentionally duplicate recipe structure for now.

Do not abstract or generate those files until balancing has settled and the repeated shape becomes a maintenance problem. Clear, inspectable XML is more useful during proof-of-concept tuning than a clever generator that hides the exact recipes being tested.

## Legacy Placeable XML

`modDesc.xml` is the current shop surface. A placeable XML file may still remain packaged after it is removed from `storeItems` when keeping that path helps early disposable saves load cleanly.

Do not delete legacy placeable XML just to tidy the package. First confirm no published prerelease used the path, or intentionally break compatibility in a documented release.

`v0.2.22.0` applies this to `wasteAwareWetSubstratePrep.xml`: the XML and l10n stay packaged so `v0.2.21.0` test saves have the best chance to load, but the placeable is no longer a static `storeItem`.

`v0.2.15.0` is an intentional breaking pre-release cleanup: old pre-GBW placeable paths, legacy hidden all-in-one intake XML, and the hidden small dry fuel yard XML were removed while the project moved to GBW identifiers and the four mash-family fillTypes.

## Runtime-Gated Optional Features

New provider-sensitive GBW features must use this pattern when they are not simply hard-dependency XML inside a proven add-on:

- user setting permits the feature
- provider mod is active
- required fillTypes and assets are registered
- only then register shop items, recipes, or other runtime paths

The setting is a preference, not a runtime guarantee. If the provider or fillType is absent, the feature stays hidden with an info log rather than a warning. Shop and recipe availability changes should apply on the next save load unless live mutation has been separately proven safe.

## Testing Method

A feature is not considered proven until it passes a new-save smoke test.

Minimum smoke test:

- mod appears in the in-game mod list
- required dependency is enforced or clearly documented
- placeable appears in the shop
- placeable can be bought and placed
- accepted inputs can be delivered
- production recipes appear and can be activated
- outputs are created in the expected fillTypes
- outputs can be loaded, distributed, or consumed by the target BGA system
- the log has no relevant errors or repeated warnings
- no performance target has a known hard miss

For PlanET modules, also test that generated internal feedstocks can be moved into or consumed by PlanET's own downstream modules.

## Balancing Method

Use maize silage as the baseline, then tune by feedstock quality.

General direction:

- exceptional forage and dedicated energy crops should be strong
- wet/starchy biomass should be useful but not automatically superior to food/feed uses
- residues and straw should be salvage gameplay, not premium energy generation
- compost and waste materials should be convenient compatibility routes where they already exist

Avoid easy money loops. If a route consumes saleable food crops, it should have a reason to exist beyond pure profit.

## Release Method

Release as a separate `FS25_BgaExtensions.zip`.

Do not release patched versions of dependencies. Do not ask players to rebuild another author's mod. If a feature needs PlanET, declare the dependency and document it clearly.

Release packages should contain only:

- GBW-owned XML, scripts, docs, and assets
- allowed base-game references via `$data` paths
- allowed dependency references via `$moddir$...` paths when that dependency is explicit
- no copied third-party mod assets unless licensing has been checked and recorded

## When To Use Lua

Lua is appropriate when XML cannot express a feature safely, such as:

- runtime fillType detection for optional map/mod crops
- guarded optional compatibility when a dependency may or may not be present
- shared helper behavior that belongs in `FS25_GBWLib`
- diagnostics for in-game testing

Lua should remain thin and boring. Data-driven XML should carry simple recipes and placeables whenever it can.

The GBW data-pack API is the first Lua surface in this repository. Stage 1 may validate and prepare routes only. Do not enable runtime recipe injection until a disposable-save test proves production-point mapping, save/load behavior, and multiplayer synchronization remain clean.

The Orchards/Greenhouses waste-aware prep gate is the first shop-facing runtime gate. It may load a GBW-owned store item, but it must not patch third-party placeables or delete already placed objects.

## Future Expansion

After the PlanET proof of concept is tested, expand in small steps:

1. Add more vanilla inputs to the PlanET intake if balance supports them.
2. Prove the Stage 1 data-pack loader with a disposable-save test.
3. Add optional common-map forage inputs such as alfalfa and clover through guarded compatibility or data-pack routes.
4. Add compost-aware waste intake only where `COMPOST` is detected.
5. Consider a standalone GBW substrate path only if PlanET-specific routing is too narrow.
6. Add custom fillTypes only after existing types stop being good enough.

Every expansion should preserve the same rule: GBW modules work alongside other systems; they do not overwrite them.
