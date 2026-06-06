# Design Notes

## Initial Concept

Extend Farming Simulator 25 BGA gameplay with richer production, management, or integration systems.

## Open Questions

- Which BGA systems should the first version change?
- Should the first milestone focus on production chains, placeables, scripts, balancing, or UI?
- Should the mod support base-game BGAs only, custom placeables, or both?

## Decisions

- Repository name: `FS25_BgaExtensions`.
- Initial visibility: public.
- Author: `phobosgekko`.
- First implementation direction: PlanET-compatible biomass intake modules, followed by registry-driven biomass pathways and optional compatibility layers.
- PlanET integration strategy: depend on `FS25_PlanET_BGA_Modular` where needed, use its registered runtime fillTypes as integration points, and ship Phobos-owned companion modules without editing or redistributing PlanET files.
- Straw Harvest integration strategy: depend on `pdlc_strawHarvestPack` when using pellet fillTypes, route `STRAW_PELLETS` toward the HALLSYS Pellet Heat Plant, and keep raw straw BGA pretreatment deliberately inefficient.

## Working References

- Implementation approach: `docs/implementation-approach.md`.
- Biomass crop ranking: `docs/biomass-crop-ranking.md`.
- Conversion process: `docs/conversion-process.md`.
- Integration strategy: `docs/integration-strategy.md`.
- Draft biomass crop registry: `mod/config/biomassCropRegistry.xml`.
- Installed mod observations: `docs/installed-mod-observations.md`.
