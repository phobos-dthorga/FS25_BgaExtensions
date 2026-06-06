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
- First implementation direction: registry-driven biomass pathways, starting with bulk substrate and vanilla-compatible silage flows before custom bales.

## Working References

- Biomass crop ranking: `docs/biomass-crop-ranking.md`.
- Draft biomass crop registry: `mod/config/biomassCropRegistry.xml`.
- Installed mod observations: `docs/installed-mod-observations.md`.
