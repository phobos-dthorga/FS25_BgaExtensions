# GBW Data Pack API

GBW data packs are separate FS25 mods that register extra biomass route candidates with `FS25_BgaExtensions`.

This is a Stage 1 API. It validates data-pack XML and prepares routes, but it does not inject gameplay recipes yet. Recipe injection comes only after the runtime hook is proven clean in FS25.

## Mod Shape

A data pack should contain:

- `modDesc.xml`
- `register.lua`
- `gbwDataPack.xml`

The data-pack mod must depend on `FS25_BgaExtensions`. If it names fillTypes from another provider mod, that provider should also be listed as a dependency or clearly documented by the data-pack author.

`examples/FS25_GBWDataPack_Template` is the copyable template and CI validation target.

## Lua Registration

The public API is:

```lua
GBWDataPacks.registerPack(modName, xmlFilename)
```

Use the template `register.lua` unchanged unless the API changes in a future GBW release.

## XML Contract

Root node:

```xml
<gbwDataPack apiVersion="1" packId="examplePack" title="Example Pack" author="Author Name">
    <routes>
        <route id="exampleGrassRoute" inputFillType="GRASS_WINDROW" target="biomassIntake" template="forageSilage" tier="good"/>
    </routes>
</gbwDataPack>
```

Required root attributes:

| Attribute | Meaning |
| --- | --- |
| `apiVersion` | Must be `1`. |
| `packId` | Stable identifier used for namespaced production IDs. |
| `title` | Human-readable pack title. |
| `author` | Pack author. |

Required route attributes:

| Attribute | Meaning |
| --- | --- |
| `id` | Stable route identifier unique inside the pack. |
| `inputFillType` | Existing fillType to check at runtime. |
| `target` | GBW module family that would receive the route. |
| `template` | GBW-owned balance template. |
| `tier` | Feedstock quality tier. |

## Targets And Templates

| Target | Templates |
| --- | --- |
| `biomassIntake` | `forageSilage`, `strawPretreatment` |
| `wetSubstratePrep` | `sweetMash`, `rootMash`, `greenMash`, `residueMash` |
| `dryFuelProcessor` | `hayPelletFuel`, `strawPelletFuel` |

Templates decide the output family and extra process requirements. For example, `strawPretreatment` is additive-gated, while pellet fuel templates require water and molasses in the eventual production recipe.

## Tiers

Allowed tiers:

- `exceptional`
- `excellent`
- `good`
- `fair`
- `emergency`

The tier is a balance hint. Data-pack authors do not define exact yields, cycle speed, output fillTypes, custom fillTypes, or additive rules.

## Safety Limits

- Max 12 routes per data pack.
- Max 6 active routes for `biomassIntake`.
- Max 8 active routes for `wetSubstratePrep`.
- Max 6 active routes for `dryFuelProcessor`.
- Missing input fillTypes are skipped with an info log.
- Invalid data-pack routes are skipped with one GBW warning.
- Stage 1 does not create recipes, placeables, fillTypes, bales, icons, or third-party mutations.

## Runtime Log Expectations

With a data pack installed, Stage 1 should log that the pack registered and how many active routes were prepared.

If an input fillType is absent, the route should be skipped with an info line. This is normal and should not be treated as a broken install.

Any GBW-owned warning from a data pack means the pack XML should be fixed before it is considered release-ready.
