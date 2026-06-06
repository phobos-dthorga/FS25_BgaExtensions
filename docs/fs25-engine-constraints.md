# FS25 Engine And Map Integration Constraints

These notes track FS25 behavior that can affect the design of BGA, biomass, silage, bale, and production-chain features.

## Custom Fill Types, Bales, And Map-Owned Data

Observed source:

- CCM Production Pack, author Kastor [D-S-Agrarservice], version `1.0.1.0`.
- ModHub page: https://www.farming-simulator.com/mod.php?mod_id=360184&title=fs2025
- KingMods mirror/metadata page: https://www.kingmods.net/en/fs25/mods/77698/ccm-production-pack
- FS25.net page originally reviewed: https://fs25.net/ccm-production-pack-v1-0/
- Observed on 2026-06-06.

### Constraints To Respect

- Custom tippable heaps use map heightType capacity. Adding several new ground-tip materials can hit map limits, especially in heavy mod sets.
- Direct animal feeding and forage mixer recipes may be map-owned. A standard mod may not be able to globally add custom feed ingredients to `animalFood.xml` or map recipes.
- Custom bale support for mod-defined fill types can be blocked by FS25 load order behavior. The CCM pack warns that custom CCM baling only works on maps where those bale definitions are integrated natively into the map.

### Design Implications For This Mod

- Prefer bulk/liquid/pallet/placeable production paths before adding custom bale workflows.
- Keep new fill types and heightTypes minimal. Reuse base-game fill types where that produces acceptable gameplay.
- Do not promise universal custom-bale support from a standard mod unless testing proves it works on a normal, unmodified map.
- If custom biomass bales become important, treat them as a separate feature requiring explicit map integration, a map-extension prefab, or a clear compatibility warning.
- Avoid making expanded BGA input depend on animal feeding or forage mixer integration. Those can be optional later layers, not the core path.

### Broader Applicability

The same class of issue can apply anywhere FS25 loads definitions in a specific order or expects map-owned XML to be complete before standard mods are evaluated. Treat these as cautious zones:

- `fillTypes.xml` and fill type categories.
- `heightTypes` and ground-tip heaps.
- `bales.xml` and custom bale definitions.
- `animalFood.xml` and husbandry feed recipes.
- Forage mixer recipes and map-specific mixing rules.
- Placeable storage and loading stations that whitelist fill types.
- Production points when trying to modify existing vanilla/map productions instead of defining a Phobos-owned placeable.

For this project, prefer adding our own placeable production path first. Patch existing map or third-party systems only through guarded optional integrations.

## Open Verification Tasks

- Verify current FS25 behavior for custom bale registration against local LUADOC, sample mods, and an unmodified base-game map.
- Confirm whether any safe runtime hook exists for custom bale/fillType loading order. Do not assume one exists.
- Test the smallest possible custom fill type plus BGA intake path before expanding the biomass registry.
