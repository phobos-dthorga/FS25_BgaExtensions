# Energy Carrier Strategy

This document defines how `FS25_BgaExtensions` should treat fuels, energy products, and process-specific buildings.

## Core Rule

Do not put every energy route into one production point.

Each building family should own one clear process type. This keeps the in-game production UI readable, makes balancing easier, and gives future modules room to expand without creating a recipe wall.

## Current Energy Carrier Roles

| Carrier | Role | Current posture |
| --- | --- | --- |
| `STRAW_PELLETS` | Dry combustion fuel | Active. Produced by Dry Fuel Processor and stored in dry fuel yards. Intended for Straw Harvest HALLSYS heat logistics. |
| `WOODCHIPS` | Dry combustion fuel | Active as storage/logistics only. Keep out of BGA digestion by default. |
| `STRAW` | Raw dry residue | Active. Can become low-grade PlanET substrate or `STRAW_PELLETS`. Better as fuel feedstock than premium BGA material. |
| `METHANE` | BGA energy product | Observe and integrate carefully. Base-game/PlanET BGAs commonly sell it directly. Do not feed it back into biomass prep. |
| `ELECTRICCHARGE` | BGA energy product | Observe and integrate carefully. Base-game/PlanET BGAs commonly sell it directly. Do not treat it as a biomass fuel source. |
| `DIGESTATE` | BGA residue/fertilizer | Let the BGA layer own it. GBW prep modules should not duplicate digestate output unless they become a real digester. |
| `DIESEL` | Fossil fuel | Out of scope unless a future emergency generator feature has a strong gameplay reason. |

## Building Families

### Biomass Intake

Purpose: prepare crops and residues for PlanET-compatible BGA feedstock.

Examples:

- forage and silage material to `SILAGE_IN`
- straw emergency pretreatment to low-yield `SILAGE_IN`

Do not add combustion-only material here unless it is being converted into a real BGA substrate.

### Wet Substrate Prep

Purpose: keep wet, starchy, sugary, root, and produce-waste flows separate from forage/silage handling.

Current route:

- wet crops and produce residues to the appropriate GBW mash family
- mash-family conditioning to `SUGARBEETCUT_IN`

Good future candidates:

- optional `COMPOST` intake where it already exists
- washed potatoes if a loaded mod defines them
- orchard/greenhouse organic residuals when safely detected

This family now has its own Wet Substrate Prep placeable. Keep it separate from forage/manure/straw intake recipes unless a future model or gameplay loop proves a shared module is clearer.

### Dry Fuel Yard

Purpose: store and stage combustion fuels.

Current materials:

- `WOODCHIPS`
- `STRAW_PELLETS`

This should remain storage/logistics first. If fuel conversion expands, use a separate fuel plant rather than turning the yard into another production wall.

### Dry Fuel Processor

Purpose: convert dry residues into combustion fuel.

Current route:

- `STRAW` -> `STRAW_PELLETS`

Possible future routes:

- low-grade straw fuel handling
- pellet-compatible residue conversion if a dependency defines a safe output

Avoid adding many crop-specific pellet recipes unless they share one believable process and one UI label.

### BGA Digestion And Energy Export

Purpose: actual anaerobic digestion and energy production.

Outputs belong here:

- `METHANE`
- `ELECTRICCHARGE`
- `DIGESTATE`

PlanET and base-game BGAs already use this layer. GBW should not duplicate it until there is a clear reason, such as a companion gas engine, energy buffer, or export module that works cleanly with existing fillType handling.

## Process Split Rule

Use this split when adding new features:

| If the feature is about... | Put it in... |
| --- | --- |
| making BGA feedstock from crops | Biomass Intake |
| making wet substrate from roots/waste | Wet Substrate Prep |
| holding wood chips or pellets | Dry Fuel Yard |
| making pellets or dry combustion fuel | Dry Fuel Processor |
| producing methane, electricity, or digestate | BGA Digestion And Energy Export |
| selling or buffering energy products | Energy Export module |

## Methane And Electricity Caution

`METHANE` and `ELECTRICCHARGE` are valid FS25 BGA product fillTypes, but they are not general farm fuels in the same way that `WOODCHIPS` or `STRAW_PELLETS` are handled materials.

Before using either as an input or stored commodity, verify:

1. Whether it can be stored by a normal placeable without log warnings.
2. Whether it can be loaded, unloaded, transported, or only sold directly.
3. Whether using it creates a money loop with existing BGA outputs.
4. Whether PlanET already sells it directly, making a GBW route redundant.
5. Whether a separate energy export module is more readable than adding recipes to existing intakes.

Default answer until proven otherwise: let PlanET sell methane and electricity directly.

## Recipe Budget

Keep each production point focused:

- 18 or fewer recipes is the soft target.
- More than 24 recipes is a hard miss.
- If a building wants more recipes, split the process into another building family.

This rule matters more than strict realism. A realistic process that makes the production UI painful should be split.

## Near-Term Recommendation

Do not add methane/electricity handling yet.

The focused dry fuel processor now exists. The next reasonable gameplay addition is guarded by-product compatibility, not an energy-output loop.

Near-term order:

1. Keep dry fuel yard storage as-is.
2. Keep straw pelletizing in Dry Fuel Processor, not in BGA intakes.
3. Keep `ORGANICWASTE` and `COMPOST` routes in provider-specific add-ons unless runtime detection is proven safe.
4. Add future methane/electricity export only as a separate module after proving the fillTypes can be handled without warnings.
