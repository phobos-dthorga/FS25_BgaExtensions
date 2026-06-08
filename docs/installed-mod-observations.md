# Installed Mod Observations

Observed against:

Local FS25 mods folder supplied by the maintainer.

Scan date: 2026-06-06.

## Scan Notes

- 486 zip archives were found.
- 18 archives were zero-byte/cloud placeholders and were skipped.
- Zip archives were inspected in place through their manifests and XML streams. No persistent extraction directory was created.
- The scan focused on crop, fill type, BGA, silage, bale, animal food, map, and production XML.

## Relevant Crop And Biomass Findings

| Mod or map | Relevant declarations or hits | Design impact |
| --- | --- | --- |
| `FS25_The_Mechet.zip` | `ALFALFA`, `ALFALFA_FERMENTED`, `ALFALFA_WINDROW`, `CLOVER`, `CLOVER_FERMENTED`, `CLOVER_WINDROW`, `COMPOST`, `COMPOST_RAW`, `FIELDGRASS`, `GREENRYE`, `MUSTARD`, `MUSTARD_CUT`, `RYE`, `RYE_CUT`, `SILAGEMAIZE`, `SPELT`, `SPELT_CUT`, `TRITICALE`, `TRITICALE_CUT`, `VETCHRYE`, `WINTERBARLEY`, `WINTERWHEAT` | Strong evidence that alfalfa/clover/cereal whole-crop integrations should be first-class optional map integrations. |
| `FS25_Szpakowo_pc.zip` | `ALFALFA`, `ALFALFA_WINDROW`, `BUCKWHEAT`, `CLOVER`, `CLOVER_WINDROW`, `DRYALFALFA`, `DRYALFALFA_WINDROW`, `DRYCLOVER`, `DRYCLOVER_WINDROW`, `FIELDGRASS`, `FLAX`, `FLAX_STRAW`, `GREENRYE`, `MUSTARD`, `MUSTARDCOVER`, `RYE`, `RYE_CUT`, `SILAGEMAIZE`, `SPELT`, `SPELT_CUT`, `TRITICALE`, `TRITICALE_CUT`, `VETCHRYE` | Confirms dry forage aliases and residue names we should support cautiously. |
| `FS25_Nordkirchen_x4.zip` | `COMPOST`, `FIELDGRASS`, `GREENRYE`, `HUMUSACTIVE`, `MUSTARD`, `RYE`, `RYE_CUT`, `SILAGEMAIZE`, `SPELT`, `SPELT_CUT`, `TRITICALE`, `TRITICALE_CUT`, `VETCHRYE` | Supports whole-crop cereal and compost optional integration. |
| `FS25_Osweiler.zip` | `FIELDGRASS`, `GREENRYE`, `HUMUSACTIVE`, `MUSTARD`, `RYE`, `RYE_CUT`, `SILAGEMAIZE`, `SPELT`, `SPELT_CUT`, `TRITICALE`, `TRITICALE_CUT`, `VETCHRYE` | Similar crop family to Nordkirchen; treat these as common map-maker names. |
| `FS25_calmsden.zip` | `LINSEED`, `LINSEED_CUT` | Add linseed as an oilseed/green-chop optional integration. |
| `FS25_CombineXP.zip` | `ALFALFA`, `CLOVER`, `GREENRYE`, `ONION`, `POPPY`, `RYE`, `SILAGEMAIZE`, `SPELT`, `TRITICALE`, `VETCHRYE`, `WINTERBARLEY`, `WINTERWHEAT` | Useful compatibility signal, but this appears to be a script/data support mod rather than a map-owned crop source. |
| `FS25_cornProductionPack.zip` | `MAIZECOB`, `MAIZECOBWASTE`, `MAIZEGERM`, `MAIZESTALKS`, `MAIZESTALKS_PELLETS` | Observation only. Do not target this mod for integration, and do not proceed with Maize+/MaizePlus work until a future explicit decision. |
| `FS25_orchardsAndGreenhouses_crossplay.zip` | `APPLE`, `APRICOT`, `COMPOST`, `CUCUMBER`, `GREENPEPPER`, `ONION`, `ORGANICWASTE`, `PEAR`, `PLUM`, `WATERMELON` | Strong source for compost/organic residual and wet produce substrate integrations. Prefer `COMPOST` over `ORGANICWASTE` for compatibility with spreading/handling support. |
| `FS25_PlanET_BGA_Modular.zip` | `SILAGE_IN`, `MANURE_IN`, `SUGARBEETCUT_IN`, `RAWMETHANE`, `DIGESTATE1`, `DIGESTATE2`, `DIGESTATE3` | BGA-adjacent, but likely internal to that mod. Do not integrate until its loading and API behavior are studied. |
| `FS25_swathingPlus.zip` | `RICELONGGRAIN_CUT`, `SORGHUM_CUT`; keyword hits for alfalfa/clover | Supports cut-crop aliases for our registry. |
| `FS25_RicePackagingFactory.zip` | `RICE_HUSK`, `RUSKED_RICE` | Rice byproducts can be substrate candidates, with husk treated as low-value fibrous residue. |
| `FS25_potatoWasher.zip` | `POTATO_WASHED` | Treat washed potatoes as equivalent to potatoes for wet substrate. |
| `FS25_OldCornDryer.zip` | `DRY_MAIZE` | Dry maize belongs in the lower-value grain mash route. |

## Follow-Up

- Re-scan after adding or removing major maps.
- Do not treat detected fill type names as safe to load blindly. Runtime existence checks are still required.
- Study `FS25_PlanET_BGA_Modular.zip` separately before attempting compatibility with its internal BGA fill types.
- Keep maize/corn-residue integrations parked. Do not revisit them as implementation work until the user explicitly decides Maize+/MaizePlus is production-ready enough to target.
