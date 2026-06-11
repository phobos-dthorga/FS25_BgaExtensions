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
- Author identity: `Gekko BioWorks`.
- First implementation direction: PlanET-compatible biomass intake modules, followed by registry-driven biomass pathways and optional compatibility layers.
- PlanET integration strategy: depend on `FS25_PlanET_BGA_Modular` where needed, use its registered runtime fillTypes as integration points, and ship GBW-owned companion modules without editing or redistributing PlanET files.
- Straw Harvest integration strategy: depend on `pdlc_strawHarvestPack` when using pellet fillTypes, route `STRAW_PELLETS` and `HAY_PELLETS` toward pellet heat/logistics, and keep fibrous BGA routes deliberately additive-gated. Assisted pellet fermentation may beat raw hay/straw pretreatment because pellets represent compressed upstream biomass, but it should stay below prepared silage throughput.
- Fermentation priority: fermented or already conditioned feedstocks should process faster and produce more useful downstream BGA substrate than raw materials that would normally need ensiling or conditioning first. Raw shortcuts remain available for gameplay convenience, but they should be slower and lower-yield. `SILAGE_ADDITIVE` should partially recover speed or yield for unfermented lanes where the UI can stay simple, but it should not outperform a properly fermented material.
- Difficult fermentation rule: pelletized fibrous materials and raw straw pretreatment require `SILAGE_ADDITIVE` by default. Pellets also require `WATER` for BGA use; `MOLASSES` is used during pellet manufacture instead of repeated in the fermenter. Pellet balance is based on the raw hay/straw equivalent that made the pellets, not pellet volume alone.
- Conservation of mass: recipe quantities should feel plausible and internally consistent, but only lightly respect real-world mass balance. Farming Simulator already uses game-friendly production ratios, so GBW BGA recipes should prioritize readable gameplay, useful differentiation, and economy balance over strict chemistry.

## Working References

- Implementation approach: `docs/implementation-approach.md`.
- Biomass crop ranking: `docs/biomass-crop-ranking.md`.
- Conversion process: `docs/conversion-process.md`.
- Integration strategy: `docs/integration-strategy.md`.
- Draft biomass crop registry: `mod/config/biomassCropRegistry.xml`.
- Installed mod observations: `docs/installed-mod-observations.md`.
