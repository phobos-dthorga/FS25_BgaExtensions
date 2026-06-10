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
- Verify the role and handling support of every fillType before first use. A fillType name alone does not prove whether it is a normal product, loose windrow material, bale material, liquid, internal process handoff, map-owned material, or technical/category-only concept.
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
- Production points when trying to modify existing vanilla/map productions instead of defining a GBW-owned placeable.

For this project, prefer adding our own placeable production path first. Patch existing map or third-party systems only through guarded optional integrations.

## Trigger Roles And Material Handling

Observed source:

- `FS25_orchardsAndGreenhouses_crossplay.zip`
- Greenhouse XML uses a water-specific unload marker, a normal unload trigger for `WATER`, and separate `palletTrigger` entries for water, compost, and liquid fertilizer.
- Base-game `mapUS/wagonBuilder/wagonBuilder.xml` uses a `palletTrigger` with `$data/shared/assets/marker/markerIconPallet.i3d` for pallet-delivered products.
- Base-game `$data/placeables/shared/sellingStationGeneric/sellingStationProducts.i3d` provides a compact generic pallet-capable unloading pad.
- Base-game `SILAGE_ADDITIVE` is supplied through a pallet fill unit.
- Observed on 2026-06-10 while fixing the `GBW Process Supply Hub`.

### Constraint To Respect

Trigger names are not just labels. Their node placement and trigger type need to match how the material is normally delivered.

- Water logistics may need the water marker, `$data/shared/assets/marker/markerIconWater.i3d`, and a water-specific unload trigger positioned for tankers or water carriers.
- Pallet, container, and big-bag materials should use `palletTrigger` support when the player is expected to deliver them as pallets or containers.
- Do not assume a pallet-delivered production input needs a matching bulk `unloadTrigger`. Some greenhouse-style systems combine material unload roots and pallet triggers, while vanilla product stations can use `palletTrigger` directly for pallet-delivered products.
- A pallet marker can be separate from the actual `palletTrigger` shape. This is useful when the trigger volume should sit at pallet height, while the marker should be easy to see at ground level.
- Bale trigger nodes are not a safe substitute for pallet handling. They can have the wrong collision mask, size, or visual placement even if the XML shape looks similar.
- Bunker or mixer unload trigger nodes can be visually wrong on a tank/storage model, even when the XML validates.
- When a placeable's base I3D, trigger node mapping, or trigger geometry changes, test with a freshly placed instance. Existing savegame instances may keep old placement state or make it harder to tell whether the new scene nodes are being used.

### Design Implication For This Mod

When adding a new placeable that accepts supplies, inspect a working vanilla, DLC, or local-mod example for that material class before selecting trigger nodes. For GBW supply logistics, `WATER` uses a water-marked unload path on the Process Supply Hub, while `SILAGE_ADDITIVE` and `MOLASSES` use a separate Process Pallet Dock with `markerIconPallet.i3d` and `palletTrigger`.

The `v0.2.19.2` wrapper attempt is a negative example: it made the PlanET model invisible and still presented a bulk unload icon for pallet-supplied materials. Do not graft a bulk trailer unload path onto pallet supplies as a shortcut. Split the logistics role or use a proven pallet-capable model.

## Open Verification Tasks

- Verify current FS25 behavior for custom bale registration against local LUADOC, sample mods, and an unmodified base-game map.
- Confirm whether any safe runtime hook exists for custom bale/fillType loading order. Do not assume one exists.
- Test the smallest possible custom fill type plus BGA intake path before expanding the biomass registry.
