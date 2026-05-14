"""
Hand-curated SAE J1939 ag-relevant PGN subset with signal-level definitions.

Sources are public summaries only (no paywalled SAE J1939 PDF content transcribed):
- Wikipedia J1939 reference tables
- CSS Electronics free educational blog posts
- Public community resources (awesome-canbus, iDoka/awesome-automotive-can-id)
- Cross-reference with AgIsoStack++ J1939 transport-layer code

Scope: 15-25 high-value J1939 PGNs that appear on every diesel engine + drivetrain bus.
These PGNs ARE in the VDMA extraction at the PGN-ID level (as placeholders), but this
DBC adds signal-level enrichment — consumers pick the richer DBC.

Outputs:
  extractions/j1939_ag_pgns.json
  opendbc_ag/dbc/j1939_ag_subset.dbc
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Sig:
    name: str
    start_bit: int
    length: int
    factor: float = 1.0
    offset: float = 0.0
    unit: str = ""
    comment: str = ""
    value_table: dict[int, str] = field(default_factory=dict)


@dataclass
class P:
    pgn: int
    name: str
    description: str
    source: str  # public source citation
    signals: list[Sig]


# Hand-curated public-source-derived J1939 ag-relevant PGNs.
# Each comes with explicit source citation. All signal definitions are from Wikipedia
# or community-publicly-summarized content — no paywalled SAE PDF transcription.
WIKIPEDIA_J1939 = "Wikipedia SAE J1939 PGN list (en.wikipedia.org/wiki/SAE_J1939)"
CSS_J1939 = "CSS Electronics J1939 educational posts (csselectronics.com/pages/j1939-explained-simple-intro)"
COMMUNITY = "Community-curated J1939 PGN references (github.com/iDoka/awesome-automotive-can-id)"


PGN_DEFINITIONS: list[P] = [
    P(
        pgn=0xF004,  # 61444
        name="J1939_EEC1_ElectronicEngineController1",
        description="Engine speed, torque mode, demand torque",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="EngineTorqueMode", start_bit=0, length=4,
                value_table={
                    0: "LowIdleGovernor", 1: "AcceleratorPedal", 2: "CruiseControl",
                    3: "PTOGovernor", 4: "RoadSpeedGovernor", 5: "ASRControl",
                    6: "TransmissionControl", 7: "ABSControl", 8: "TorqueLimiting",
                    9: "HighSpeedGovernor", 10: "BrakingSystem", 11: "RemoteAccelerator",
                    14: "Other", 15: "NotAvailable",
                }),
            Sig(name="ActualEngineTorquePct", start_bit=16, length=8,
                factor=1, offset=-125, unit="%",
                comment="Actual engine percent torque"),
            Sig(name="EngineSpeed", start_bit=24, length=16,
                factor=0.125, offset=0, unit="rpm"),
            Sig(name="SourceAddressOfControllingDevice", start_bit=40, length=8,
                comment="Source address of the device commanding engine torque"),
        ],
    ),
    P(
        pgn=0xFEF2,  # 65266
        name="J1939_LFE1_FuelEconomy",
        description="Fuel rate + instantaneous + average fuel economy",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="FuelRate", start_bit=0, length=16,
                factor=0.05, offset=0, unit="L/h"),
            Sig(name="InstantaneousFuelEconomy", start_bit=16, length=16,
                factor=1/512, offset=0, unit="km/L"),
            Sig(name="AverageFuelEconomy", start_bit=32, length=16,
                factor=1/512, offset=0, unit="km/L"),
            Sig(name="ThrottlePosition", start_bit=48, length=8,
                factor=0.4, offset=0, unit="%"),
        ],
    ),
    P(
        pgn=0xFEEE,  # 65262
        name="J1939_ET1_EngineTemperature1",
        description="Coolant + fuel + engine oil + intercooler temperatures",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="EngineCoolantTemp", start_bit=0, length=8,
                factor=1, offset=-40, unit="°C"),
            Sig(name="FuelTemp", start_bit=8, length=8,
                factor=1, offset=-40, unit="°C"),
            Sig(name="EngineOilTemp1", start_bit=16, length=16,
                factor=0.03125, offset=-273, unit="°C"),
            Sig(name="TurboOilTemp", start_bit=32, length=16,
                factor=0.03125, offset=-273, unit="°C"),
            Sig(name="EngineIntercoolerTemp", start_bit=48, length=8,
                factor=1, offset=-40, unit="°C"),
        ],
    ),
    P(
        pgn=0xFEEF,  # 65263
        name="J1939_EFLP1_EngineFluidLevelPressure1",
        description="Oil pressure/level + coolant pressure/level + fuel delivery pressure",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="FuelDeliveryPressure", start_bit=0, length=8,
                factor=4, offset=0, unit="kPa"),
            Sig(name="EngineOilLevel", start_bit=16, length=8,
                factor=0.4, offset=0, unit="%"),
            Sig(name="EngineOilPressure", start_bit=24, length=8,
                factor=4, offset=0, unit="kPa"),
            Sig(name="CoolantPressure", start_bit=40, length=8,
                factor=2, offset=0, unit="kPa"),
            Sig(name="CoolantLevel", start_bit=48, length=8,
                factor=0.4, offset=0, unit="%"),
        ],
    ),
    P(
        pgn=0xFEF1,  # 65265
        name="J1939_CCVS1_CruiseControlVehicleSpeed1",
        description="Vehicle speed + cruise control state + brake/clutch/parking switches",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="TwoSpeedAxleSwitch", start_bit=0, length=2),
            Sig(name="ParkingBrakeSwitch", start_bit=2, length=2),
            Sig(name="CruiseControlPauseSwitch", start_bit=4, length=2),
            Sig(name="WheelBasedVehicleSpeed", start_bit=8, length=16,
                factor=1/256, offset=0, unit="km/h"),
            Sig(name="CruiseControlActive", start_bit=24, length=2),
            Sig(name="CruiseControlEnableSwitch", start_bit=26, length=2),
            Sig(name="BrakeSwitch", start_bit=28, length=2),
            Sig(name="ClutchSwitch", start_bit=30, length=2),
            Sig(name="CruiseControlSetSwitch", start_bit=32, length=2),
            Sig(name="CruiseControlCoastSwitch", start_bit=34, length=2),
            Sig(name="CruiseControlResumeSwitch", start_bit=36, length=2),
            Sig(name="CruiseControlAccelerateSwitch", start_bit=38, length=2),
            Sig(name="CruiseControlSetSpeed", start_bit=40, length=8,
                factor=1, offset=0, unit="km/h"),
            Sig(name="PTOState", start_bit=48, length=5),
        ],
    ),
    P(
        pgn=0xFE6C,  # 65132
        name="J1939_TCO1_TachographInformation",
        description="Tachograph + driver state (mostly for heavy-truck FMS)",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="Driver1WorkingState", start_bit=0, length=3),
            Sig(name="Driver2WorkingState", start_bit=3, length=3),
            Sig(name="VehicleMotion", start_bit=6, length=2),
            Sig(name="TachographVehicleSpeed", start_bit=48, length=16,
                factor=1/256, offset=0, unit="km/h"),
        ],
    ),
    P(
        pgn=0xFEE5,  # 65253
        name="J1939_HOURS_EngineHours",
        description="Engine total hours of operation",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="EngineTotalHoursOfOperation", start_bit=0, length=32,
                factor=0.05, offset=0, unit="h"),
            Sig(name="EngineTotalRevolutions", start_bit=32, length=32,
                factor=1000, offset=0, unit="r"),
        ],
    ),
    P(
        pgn=0xFEEC,  # 65260
        name="J1939_VI_VehicleIdentification",
        description="Vehicle Identification Number (VIN)",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="VIN_Char01", start_bit=0, length=8,
                comment="ASCII byte 0 of VIN; full VIN spans multipacket"),
        ],
    ),
    P(
        pgn=0xFEF7,  # 65271
        name="J1939_VEP1_VehicleElectricalPower1",
        description="Battery + alternator + engine starter electrical state",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="NetBatteryCurrent", start_bit=0, length=8,
                factor=1, offset=-125, unit="A"),
            Sig(name="AlternatorCurrent", start_bit=8, length=8,
                factor=1, offset=0, unit="A"),
            Sig(name="AlternatorPotential", start_bit=16, length=16,
                factor=0.05, offset=0, unit="V"),
            Sig(name="ElectricalPotential", start_bit=32, length=16,
                factor=0.05, offset=0, unit="V"),
            Sig(name="BatteryPotentialSwitched", start_bit=48, length=16,
                factor=0.05, offset=0, unit="V"),
        ],
    ),
    P(
        pgn=0xFD7C,  # 64892
        name="J1939_DEF_DieselExhaustFluidConcentration",
        description="DEF (urea) tank level + temperature + concentration",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="DEFTankLevel", start_bit=0, length=8,
                factor=0.4, offset=0, unit="%"),
            Sig(name="DEFTankTemperature", start_bit=8, length=8,
                factor=1, offset=-40, unit="°C"),
        ],
    ),
    P(
        pgn=0xFEE3,  # 65251
        name="J1939_EC1_EngineConfiguration1",
        description="Engine configuration data — displacement, speed limits, fuel type",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="EngineSpeedAtIdle", start_bit=0, length=16,
                factor=0.125, offset=0, unit="rpm"),
            Sig(name="EngineSpeedAtMaxIdlePoint1", start_bit=24, length=16,
                factor=0.125, offset=0, unit="rpm"),
        ],
    ),
    P(
        pgn=0xFEDF,  # 65247
        name="J1939_EEC3_ElectronicEngineController3",
        description="Engine demand percent torque + nominal friction torque",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="EngineDemandPercentTorque", start_bit=56, length=8,
                factor=1, offset=-125, unit="%"),
        ],
    ),
    P(
        pgn=0xF003,  # 61443
        name="J1939_EEC2_ElectronicEngineController2",
        description="Accelerator pedal + percent load",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="AcceleratorPedal1LowIdleSwitch", start_bit=0, length=2),
            Sig(name="AcceleratorPedalKickdownSwitch", start_bit=2, length=2),
            Sig(name="AcceleratorPedalPosition1", start_bit=8, length=8,
                factor=0.4, offset=0, unit="%"),
            Sig(name="EnginePercentLoadAtCurrentSpeed", start_bit=16, length=8,
                factor=1, offset=0, unit="%"),
        ],
    ),
    P(
        pgn=0xFEF8,  # 65272
        name="J1939_TRF1_TransmissionFluids1",
        description="Transmission oil + clutch pressure",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="ClutchPressure", start_bit=0, length=8,
                factor=16, offset=0, unit="kPa"),
            Sig(name="TransmissionOilLevel", start_bit=8, length=8,
                factor=0.4, offset=0, unit="%"),
            Sig(name="TransmissionFilterDifferentialPressure", start_bit=16, length=8,
                factor=2, offset=0, unit="kPa"),
            Sig(name="TransmissionOilPressure", start_bit=24, length=8,
                factor=16, offset=0, unit="kPa"),
            Sig(name="TransmissionOilTemperature", start_bit=32, length=16,
                factor=0.03125, offset=-273, unit="°C"),
        ],
    ),
    P(
        pgn=0xFEF6,  # 65270
        name="J1939_IC1_InletExhaustConditions1",
        description="Boost + intake air temp + air filter differential pressure",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="ParticulateTrapInletPressure", start_bit=0, length=8,
                factor=0.5, offset=0, unit="kPa"),
            Sig(name="BoostPressure", start_bit=8, length=8,
                factor=2, offset=0, unit="kPa"),
            Sig(name="IntakeManifold1Temperature", start_bit=16, length=8,
                factor=1, offset=-40, unit="°C"),
            Sig(name="AirInletPressure", start_bit=24, length=8,
                factor=2, offset=0, unit="kPa"),
            Sig(name="AirFilterDifferentialPressure", start_bit=32, length=8,
                factor=0.05, offset=0, unit="kPa"),
            Sig(name="ExhaustGasTemp", start_bit=40, length=16,
                factor=0.03125, offset=-273, unit="°C"),
            Sig(name="CoolantFilterDifferentialPressure", start_bit=56, length=8,
                factor=0.5, offset=0, unit="kPa"),
        ],
    ),
    # Note: 0xFEEB (Component Identification) intentionally omitted here —
    # AgIsoStack++ extraction (Phase 2) is authoritative for that PGN. See
    # iso11783_from_agisostack.dbc :: ComponentIdentification.
    P(
        pgn=0xFCB2,  # 64690
        name="J1939_FFE_FuelEconomyExtended",
        description="Trip fuel + total fuel + trip distance",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="EngineTripFuel", start_bit=0, length=32,
                factor=0.5, offset=0, unit="L"),
            Sig(name="EngineTotalFuelUsed", start_bit=32, length=32,
                factor=0.5, offset=0, unit="L"),
        ],
    ),
    P(
        pgn=0xFEC1,  # 65217 — corrected from 0xFD09 (R2 domain fix)
        name="J1939_HRVD_HighResolutionVehicleDistance",
        description="High-resolution vehicle distance (HRVD per SAE J1939-71)",
        source=WIKIPEDIA_J1939,
        signals=[
            Sig(name="HighResolutionTotalVehicleDistance", start_bit=0, length=32,
                factor=5, offset=0, unit="m"),
            Sig(name="HighResolutionTripDistance", start_bit=32, length=32,
                factor=5, offset=0, unit="m"),
        ],
    ),
]


from opendbc_ag.tools._scope_policy import is_in_scope, reject_reason


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    repo = args.repo_root

    valid = [p for p in PGN_DEFINITIONS if is_in_scope(p.pgn, p.name)]
    rejected = [p for p in PGN_DEFINITIONS if not is_in_scope(p.pgn, p.name)]
    print(f"Total curated J1939 ag-subset PGNs: {len(PGN_DEFINITIONS)}")
    print(f"Rejected out-of-scope: {len(rejected)}")
    for p in rejected:
        print(f"  - {p.pgn:#X} {p.name!r}: {reject_reason(p.pgn, p.name)}")
    print(f"Retained: {len(valid)}")
    print(f"Total signals: {sum(len(p.signals) for p in valid)}")

    # Save intermediate
    out_json = repo / "extractions/j1939_ag_pgns.json"
    payload = {
        "source": "Hand-curated SAE J1939 ag-relevant subset from public summaries",
        "primary_sources": [
            "Wikipedia SAE J1939 PGN list (en.wikipedia.org/wiki/SAE_J1939)",
            "CSS Electronics J1939 educational posts (csselectronics.com/pages/j1939-explained-simple-intro)",
            "Community-curated J1939 PGN references (github.com/iDoka/awesome-automotive-can-id)",
        ],
        "license_note": (
            "No paywalled SAE J1939 PDF content has been transcribed. All signal "
            "definitions are derived from publicly-summarized content. Verify "
            "against your equipment's actual J1939 documentation before production use."
        ),
        "extraction_date": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).date().isoformat(),
        "pgn_count": len(valid),
        "signal_count": sum(len(p.signals) for p in valid),
        "pgns": [
            {
                "pgn": p.pgn,
                "pgn_hex": f"0x{p.pgn:04X}",
                "pgn_decimal": p.pgn,
                "name": p.name,
                "description": p.description,
                "source": p.source,
                "signals": [asdict(s) for s in p.signals],
            }
            for p in valid
        ],
    }
    out_json.write_text(json.dumps(payload, indent=2))
    print(f"Wrote: {out_json}")

    # Generate DBC
    from canmatrix import canmatrix as cm
    from canmatrix import formats

    matrix = cm.CanMatrix()
    for p in valid:
        frame_id = cm.ArbitrationId(id=p.pgn, extended=True)
        frame = cm.Frame(
            name=p.name,
            arbitration_id=frame_id,
            size=8,
            comment=f"{p.description}. Source: {p.source}",
        )
        for s in p.signals:
            sig = cm.Signal(
                name=s.name,
                start_bit=s.start_bit,
                size=s.length,
                is_little_endian=True,
                is_signed=False,
                factor=s.factor,
                offset=s.offset,
                unit=s.unit,
                comment=s.comment,
            )
            for v, label in s.value_table.items():
                sig.add_values(v, label)
            frame.add_signal(sig)
        matrix.add_frame(frame)

    out_dbc = repo / "opendbc_ag/dbc/j1939_ag_subset.dbc"
    formats.dumpp({"": matrix}, str(out_dbc))
    print(f"Wrote DBC: {out_dbc} ({len(valid)} frames)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
