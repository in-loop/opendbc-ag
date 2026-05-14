# Signal naming guide

Conventions for DBC signal naming in opendbc-ag. New PRs should follow these.

## Frame (BO_) name conventions

| Pattern | When to use | Example |
|---|---|---|
| `<Domain><Function>` | Standard ISO 11783 PGNs from AgIsoStack++ | `WheelBasedSpeedAndDistance`, `AgriculturalGuidanceMachineInfo` |
| `J1939_<Acronym>_<Function>` | SAE J1939 ag-relevant subset | `J1939_EEC1_ElectronicEngineController1` |
| `VDMA_<PGN_HEX>_<Name>` | isobus.net VDMA list-level placeholders | `VDMA_100_Transmission_Control_1` |

Frame names are CamelCase, max 64 characters, no spaces.

## Signal (SG_) name conventions

- **CamelCase** (no underscores within words except where idiomatic; `_` is reserved as a section separator, e.g. `EngineCoolantTemp_C`)
- **Max 64 characters.** Auto-generated placeholder signals on VDMA frames (`<FrameName>_RawPayload`) can approach this limit; hand-curated signals should be much shorter.
- **Suffix with units only when ambiguous**, e.g. `BoostPressure_kPa` if multiple pressure signals coexist in the same frame
- **Boolean / discrete signals end with state suffix:**
  - `_State` for current state (e.g., `KeySwitchState`)
  - `_Switch` for switch-typed inputs (e.g., `BrakeSwitch`)
  - `_Active` / `_Engaged` for activation status (e.g., `CruiseControlActive`)
- **Counter / cumulative signals end with descriptor:**
  - `Total` (e.g., `EngineTotalRevolutions`)
  - `Trip` (e.g., `EngineTripFuel`)
- **Position / measurement signals:**
  - Position: `<Component>Position` (e.g., `AcceleratorPedalPosition1`)
  - Speed: `<Component>Speed` (e.g., `EngineSpeed`, `WheelBasedVehicleSpeed`)
  - Temperature: `<Component>Temp` or `<Component>Temperature` (consistent within a single DBC)
  - Pressure: `<Component>Pressure`

## Domain prefixes

When in doubt about which prefix to use:

- `Tractor*` / `Implement*` — components clearly belonging to one side of an ISOBUS tractor-implement bus
- `Engine*` — engine-bay sensors (J1939 EEC1/EEC2/ET1/EFLP1)
- `Transmission*` / `TRF*` — transmission system
- `Boom*` — sprayer boom-mounted sensors
- `Header*` — combine header / reel / gathering chains
- `RowUnit*` — planter per-row instrumentation
- `Hub*` / `WheelEnd*` — per-wheel sensors

## Units

Use SI where possible. Common units in ag CAN:

| Quantity | Unit | DBC string |
|---|---|---|
| Temperature | °C | `°C` |
| Pressure | kPa or bar (be consistent per DBC) | `kPa` |
| Speed (vehicle) | km/h or m/s | `km/h` |
| Speed (rotational) | rpm | `rpm` |
| Volume | L | `L` |
| Mass | kg | `kg` |
| Distance | m or km | `m` |
| Time | s, min, h | `s` |
| Percentage | % | `%` |
| Current | A | `A` |
| Voltage | V | `V` |
| Angular velocity (curvature) | 1/km | `1/km` |

Where SAE J1939 documentation gives factors/offsets in mixed units (e.g., kPa for one signal, bar for another in the same PGN), preserve the source convention and cite it in the `CM_` comment.

## Value tables (enum-like signals)

- Labels are **PascalCase** (matching AgIsoStack++ enum conventions): `Off`, `NotOff`, `Forward`, `Reverse`, `Error`, `NotAvailable`
- Standard J1939 4-state signals use: `0 = Disabled / Off / NotReversed`, `1 = Enabled / On / Reversed`, `2 = Error`, `3 = NotAvailable`

## Comments

Every uncertain or community-contributed signal MUST have a `CM_ SG_` comment with source attribution:

```
CM_ SG_ 12345 EngineSpeed "Source: Wikipedia SAE J1939, EEC1 PGN 0xF004";
```

For VDMA-sourced placeholders, the detail-page URL is in the frame-level `CM_ BO_` comment:

```
CM_ BO_ 256 "Source: isobus.net VDMA Data Dictionary (https://www.isobus.net/isobus/pGNAndSPN/38?type=PGN)";
```

## When in doubt

Match the style of an existing similar signal in `iso11783_from_agisostack.dbc` (most carefully-curated DBC in the corpus) or `j1939_ag_subset.dbc` (hand-curated J1939). If still unsure, ask in a discussion / draft PR before completing.

## Note on case convention

CSS Electronics, Vector, and many other commercial DBC ecosystems prefer **snake_case** signal names (`Wheel_Based_Vehicle_Speed`) rather than CamelCase (`WheelBasedVehicleSpeed`). The CamelCase choice here mirrors AgIsoStack++ C++ enum style, which is our primary upstream PGN source. Translation between the two conventions is a mechanical 1-line change — if a downstream consumer needs the snake_case form, opening a PR with a side-by-side `dbc/iso11783_from_agisostack_snakecase.dbc` is welcome.
