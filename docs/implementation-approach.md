# Implementation Approach

This document explains how `FS25_BgaExtensions` should be built, tested, and expanded.

## Goal

Add richer biomass-to-BGA gameplay while staying compatible with Farming Simulator 25, PlanET Modular BGA, and common map/mod ecosystems.

The preferred player experience is simple:

1. Install the required dependency mod when a feature needs one.
2. Install `FS25_BgaExtensions` as its own mod.
3. Place Phobos-owned companion modules in-game.
4. Feed additional biomass through those modules into the target BGA system.

Players should not need to edit, rebuild, or replace another author's mod.

## Architectural Style

Use companion modules first.

The mod should add its own placeables, recipes, and compatibility behavior beside the systems it integrates with. For PlanET support, this means Phobos-owned intake or preprocessing modules that output PlanET-compatible internal feedstocks.

Prefer this order:

1. Existing vanilla fillTypes and base-game behavior.
2. Dependency-provided runtime fillTypes, when the dependency is declared.
3. Phobos-owned placeables and recipes.
4. Phobos-owned custom fillTypes only when existing fillTypes cannot represent the gameplay cleanly.
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
- use Straw Harvest `STRAW_PELLETS` as the dry fuel handoff when bridging straw residues to the HALLSYS Pellet Heat Plant
- add Phobos-owned modules that convert expanded biomass inputs into those internal fillTypes
- let PlanET's own fermenters, generators, storages, and distributors continue doing their normal work
- let the HALLSYS Pellet Heat Plant remain the destination for pellet fuel
- keep all Phobos balancing and recipes in `FS25_BgaExtensions`

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

For the current PlanET proof of concept, the dependency resources are the internal fillTypes. The placeable uses Phobos-owned XML and base-game referenced assets.

### Reference Policy

Referencing is allowed; vendoring is not.

Use references such as `$data/...` or `$moddir$RequiredMod/...` when they point to content the player must already have installed. This keeps ownership clear and avoids duplicating third-party or DLC files inside the Phobos package.

The Phobos release zip should contain only Phobos-owned files. A required dependency should remain the source of truth for its own assets, fillTypes, placeables, and scripts.

### Project Resources

- `docs/biomass-crop-ranking.md` defines feedstock priority and balancing intent.
- `docs/conversion-process.md` defines conversion lanes and first recipes.
- `docs/integration-strategy.md` defines the companion-module rule.
- `docs/fs25-engine-constraints.md` records engine/load-order cautions.
- `mod/config/biomassCropRegistry.xml` is a draft data registry for future expansion.

## FillType Policy

FillTypes are a limited resource.

Use existing fillTypes wherever they are technically and thematically close enough. For example:

- use PlanET `SILAGE_IN` for prepared forage biomass in PlanET-specific modules
- use PlanET `SUGARBEETCUT_IN` for wet or starchy biomass in PlanET-specific modules
- use Straw Harvest `STRAW_PELLETS` for dry straw fuel when the pellet heat route is active
- prefer `COMPOST` if it exists on a map/mod because other equipment may already support it
- treat `COMPOST_RAW` and `ORGANICWASTE` as detected aliases or fallback inputs, not fillTypes this mod should define casually

Add a Phobos custom fillType only when it provides a clear gameplay boundary that cannot be represented well by vanilla or dependency-provided types.

## Implementation Workflow

Use this workflow for each feature:

1. Define the target gameplay loop.
2. Identify whether the feature is standalone, vanilla-compatible, or dependency-specific.
3. Confirm every required fillType exists in vanilla, the declared dependency, or Phobos-owned definitions.
4. Prefer a Phobos-owned companion placeable over patching an existing one.
5. Keep recipes small and readable.
6. Validate XML against local FS25 schemas.
7. Package from `mod/` using `tools/package.ps1`.
8. Test in a fresh save before touching an existing save.
9. Review the game log and document any hard lessons.
10. Tune balancing after the loop works end to end.

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

- Phobos-owned XML, scripts, docs, and assets
- allowed base-game references via `$data` paths
- allowed dependency references via `$moddir$...` paths when that dependency is explicit
- no copied third-party mod assets unless licensing has been checked and recorded

## When To Use Lua

Lua is appropriate when XML cannot express a feature safely, such as:

- runtime fillType detection for optional map/mod crops
- guarded optional compatibility when a dependency may or may not be present
- shared helper behavior that belongs in `FS25_PhobosLib`
- diagnostics for in-game testing

Lua should remain thin and boring. Data-driven XML should carry simple recipes and placeables whenever it can.

## Future Expansion

After the PlanET proof of concept is tested, expand in small steps:

1. Add more vanilla inputs to the PlanET intake if balance supports them.
2. Add optional common-map forage inputs such as alfalfa and clover through guarded compatibility.
3. Add compost-aware waste intake only where `COMPOST` is detected.
4. Consider a standalone Phobos substrate path only if PlanET-specific routing is too narrow.
5. Add custom fillTypes only after existing types stop being good enough.

Every expansion should preserve the same rule: Phobos modules work alongside other systems; they do not overwrite them.
