"""
Extract PGN definitions from AgIsoStack++ MIT-licensed C++ source.

Reads:
  extractions/agisostack_clone/isobus/include/isobus/isobus/can_general_parameter_group_numbers.hpp
  and selected interface headers for signal enrichment.

Writes:
  extractions/agisostack_pgns.json — structured intermediate
  opendbc_ag/dbc/iso11783_from_agisostack.dbc — DBC file

Scope policy: pure-standard only. PGNs in 0xEF00 or 0xFF00..0xFFFF are rejected.

Usage:
  python -m opendbc_ag.tools.extract_agisostack [--repo-root PATH]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


# Proprietary-range predicate lives in _scope_policy (centralized, DP0+DP1 + name patterns).
from opendbc_ag.tools._scope_policy import is_in_scope, reject_reason


@dataclass
class Signal:
    name: str
    start_bit: int
    length: int
    factor: float = 1.0
    offset: float = 0.0
    unit: str = ""
    comment: str = ""
    value_table: dict[int, str] = field(default_factory=dict)


@dataclass
class Pgn:
    name: str
    pgn: int
    source_file: str
    source_line: int
    comment: str = ""
    signals: list[Signal] = field(default_factory=list)


def parse_pgn_enum(header_path: Path) -> list[Pgn]:
    """Parse can_general_parameter_group_numbers.hpp for the CANLibParameterGroupNumber enum."""
    text = header_path.read_text()
    enum_match = re.search(
        r"enum\s+class\s+CANLibParameterGroupNumber\s*\{(.*?)\};",
        text,
        re.DOTALL,
    )
    if not enum_match:
        raise RuntimeError(f"CANLibParameterGroupNumber enum not found in {header_path}")
    body = enum_match.group(1)

    # Compute the base line number for the enum so we can attribute each entry
    enum_start_offset = enum_match.start(1)
    base_line = text[:enum_start_offset].count("\n") + 1

    pgns: list[Pgn] = []
    for line_idx, line in enumerate(body.splitlines()):
        stripped = line.strip().rstrip(",").rstrip()
        m = re.match(r"^([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(0x[0-9A-Fa-f]+|\d+)\s*(?://.*)?$", stripped)
        if not m:
            continue
        name = m.group(1)
        val_str = m.group(2)
        pgn = int(val_str, 0)
        if name == "Any" and pgn == 0:
            continue  # sentinel
        rel_line = base_line + line_idx
        pgns.append(
            Pgn(
                name=name,
                pgn=pgn,
                source_file=str(header_path.name),
                source_line=rel_line,
                comment=f"Source: AgIsoStack++ {header_path.name}:{rel_line}",
            )
        )
    return pgns


def enrich_speed_distance(pgns_by_name: dict[str, Pgn]) -> None:
    """Add known signal definitions for the speed/distance PGNs per ISO 11783-7 + AgIsoStack++ docs."""
    # Wheel-based Speed and Distance — PGN 0xFE48
    if "WheelBasedSpeedAndDistance" in pgns_by_name:
        p = pgns_by_name["WheelBasedSpeedAndDistance"]
        p.signals.extend([
            Signal(
                name="WheelBasedMachineSpeed",
                start_bit=0, length=16,
                factor=0.001, offset=0, unit="m/s",
                comment="Source: isobus_speed_distance_messages.hpp WheelBasedMachineSpeedData",
            ),
            Signal(
                name="WheelBasedMachineDistance",
                start_bit=16, length=32,
                factor=1, offset=0, unit="m",
                comment="Source: isobus_speed_distance_messages.hpp",
            ),
            Signal(
                name="MaximumTimeOfTractorPowerOk",
                start_bit=48, length=8,
                factor=1, offset=0, unit="minutes",
                comment="Source: isobus_speed_distance_messages.hpp",
            ),
            Signal(
                name="OperatorDirectionReversed",
                start_bit=56, length=2,
                comment="0=NotReversed 1=Reversed 2=Error 3=NotAvailable",
                value_table={0: "NotReversed", 1: "Reversed", 2: "Error", 3: "NotAvailable"},
            ),
            Signal(
                name="StartStopState",
                start_bit=58, length=2,
                comment="0=Stop 1=Start 2=Error 3=NotAvailable",
                value_table={0: "Stop", 1: "Start", 2: "Error", 3: "NotAvailable"},
            ),
            Signal(
                name="KeySwitchState",
                start_bit=60, length=2,
                comment="0=Off 1=NotOff 2=Error 3=NotAvailable",
                value_table={0: "Off", 1: "NotOff", 2: "Error", 3: "NotAvailable"},
            ),
            Signal(
                name="MachineDirection",
                start_bit=62, length=2,
                comment="0=Reverse 1=Forward 2=Error 3=NotAvailable",
                value_table={0: "Reverse", 1: "Forward", 2: "Error", 3: "NotAvailable"},
            ),
        ])

    # Ground-based Speed and Distance — PGN 0xFE49
    if "GroundBasedSpeedAndDistance" in pgns_by_name:
        p = pgns_by_name["GroundBasedSpeedAndDistance"]
        p.signals.extend([
            Signal(
                name="GroundBasedMachineSpeed",
                start_bit=0, length=16,
                factor=0.001, offset=0, unit="m/s",
                comment="Source: isobus_speed_distance_messages.hpp GroundBasedSpeedAndDistance",
            ),
            Signal(
                name="GroundBasedMachineDistance",
                start_bit=16, length=32,
                factor=1, offset=0, unit="m",
                comment="Source: isobus_speed_distance_messages.hpp",
            ),
            Signal(
                name="MachineDirection",
                start_bit=62, length=2,
                comment="0=Reverse 1=Forward 2=Error 3=NotAvailable",
                value_table={0: "Reverse", 1: "Forward", 2: "Error", 3: "NotAvailable"},
            ),
        ])

    # Machine Selected Speed — PGN 0xF022
    if "MachineSelectedSpeed" in pgns_by_name:
        p = pgns_by_name["MachineSelectedSpeed"]
        p.signals.extend([
            Signal(
                name="MachineSelectedSpeed",
                start_bit=0, length=16,
                factor=0.001, offset=0, unit="m/s",
                comment="Source: isobus_speed_distance_messages.hpp MachineSelectedSpeedData",
            ),
            Signal(
                name="MachineSelectedSpeedDistance",
                start_bit=16, length=32,
                factor=1, offset=0, unit="m",
            ),
            Signal(
                name="MachineSelectedSpeedExitReasonCode",
                start_bit=48, length=6,
                comment="Source-of-selected-speed exit reason code per ISO 11783-7",
            ),
            Signal(
                name="MachineSelectedSpeedSource",
                start_bit=54, length=3,
                comment="0=Wheel 1=Ground 2=Navigation 3=Blended 4=Simulated",
                value_table={0: "Wheel", 1: "Ground", 2: "Navigation", 3: "Blended", 4: "Simulated"},
            ),
            Signal(
                name="MachineDirection",
                start_bit=57, length=2,
                value_table={0: "Reverse", 1: "Forward", 2: "Error", 3: "NotAvailable"},
            ),
        ])


def enrich_guidance(pgns_by_name: dict[str, Pgn]) -> None:
    """Guidance PGNs per isobus_guidance_interface.hpp."""
    if "AgriculturalGuidanceMachineInfo" in pgns_by_name:
        p = pgns_by_name["AgriculturalGuidanceMachineInfo"]
        p.signals.extend([
            Signal(
                name="EstimatedCurvature",
                start_bit=0, length=16,
                factor=0.25, offset=-8032,
                unit="1/km",
                comment="Source: isobus_guidance_interface.hpp GuidanceMachineInfo",
            ),
            Signal(
                name="MechanicalSystemLockoutState",
                start_bit=16, length=2,
                value_table={0: "NotActive", 1: "Active", 2: "Error", 3: "NotAvailable"},
            ),
            Signal(
                name="MachineSteeringSystemReadinessState",
                start_bit=18, length=2,
                value_table={0: "NotReady", 1: "Ready", 2: "Error", 3: "NotAvailable"},
            ),
            Signal(
                name="MachineSteeringSystemCommandExitReasonCode",
                start_bit=20, length=6,
                comment="Per ISO 11783-7 exit reason codes",
            ),
            Signal(
                name="GuidanceLimitStatus",
                start_bit=29, length=3,
                value_table={0: "NotLimited", 1: "OperatorLimited", 2: "LimitedHigh", 3: "LimitedLow"},
            ),
            Signal(
                name="GuidanceRequestStatus",
                start_bit=32, length=2,
                value_table={0: "RequiredNoSteer", 1: "Required", 2: "Error", 3: "NotAvailable"},
            ),
        ])

    if "AgriculturalGuidanceSystemCommand" in pgns_by_name:
        p = pgns_by_name["AgriculturalGuidanceSystemCommand"]
        p.signals.extend([
            Signal(
                name="CurvatureCommand",
                start_bit=0, length=16,
                factor=0.25, offset=-8032,
                unit="1/km",
                comment="Source: isobus_guidance_interface.hpp GuidanceSystemCommand",
            ),
            Signal(
                name="CurvatureCommandStatus",
                start_bit=16, length=2,
                value_table={0: "IntendedNotSteering", 1: "IntendedSteering", 2: "Error", 3: "NotAvailable"},
            ),
        ])


def enrich_time_date(pgns_by_name: dict[str, Pgn]) -> None:
    if "TimeDate" in pgns_by_name:
        p = pgns_by_name["TimeDate"]
        p.signals.extend([
            Signal(name="Seconds", start_bit=0, length=8, factor=0.25, offset=0, unit="s"),
            Signal(name="Minutes", start_bit=8, length=8, factor=1, offset=0, unit="min"),
            Signal(name="Hours", start_bit=16, length=8, factor=1, offset=0, unit="h"),
            Signal(name="Month", start_bit=24, length=8, factor=1, offset=0, unit="month"),
            Signal(name="Day", start_bit=32, length=8, factor=0.25, offset=0, unit="day"),
            Signal(name="Year", start_bit=40, length=8, factor=1, offset=1985, unit="year"),
            Signal(name="LocalMinuteOffset", start_bit=48, length=8, factor=1, offset=-125, unit="min"),
            Signal(name="LocalHourOffset", start_bit=56, length=8, factor=1, offset=-125, unit="h"),
        ])


def enrich_language(pgns_by_name: dict[str, Pgn]) -> None:
    if "LanguageCommand" in pgns_by_name:
        p = pgns_by_name["LanguageCommand"]
        p.signals.extend([
            Signal(
                name="LanguageCode_Byte0",
                start_bit=0, length=8,
                comment="ASCII char 1 of ISO 639-1 language code, e.g. 'e' for en",
            ),
            Signal(name="LanguageCode_Byte1", start_bit=8, length=8, comment="ASCII char 2"),
            Signal(name="NumberFormat", start_bit=16, length=2, comment="Decimal separator + grouping convention"),
            Signal(name="DateFormat", start_bit=24, length=8, comment="0=ddmmyyyy 1=ddyyyymm 2=mmyyyydd 3=mmddyyyy 4=yyyymmdd 5=yyyyddmm"),
            Signal(name="TimeFormat", start_bit=32, length=2, comment="0=24h 1=12h"),
            Signal(name="DistanceUnits", start_bit=34, length=2, comment="0=metric 1=imperial-US 2=imperial-UK 3=reserved"),
            Signal(name="AreaUnits", start_bit=36, length=2),
            Signal(name="VolumeUnits", start_bit=38, length=2),
            Signal(name="MassUnits", start_bit=40, length=2),
            Signal(name="TemperatureUnits", start_bit=42, length=2),
            Signal(name="PressureUnits", start_bit=44, length=2),
        ])


def enrich_maintain_power(pgns_by_name: dict[str, Pgn]) -> None:
    if "MaintainPower" in pgns_by_name:
        p = pgns_by_name["MaintainPower"]
        p.signals.extend([
            Signal(
                name="MaintainPower_MaxTimeFromOff",
                start_bit=0, length=2,
                comment="MaintainPower request — maximum time for ECU power-down",
                value_table={0: "DoNotMaintain", 1: "Maintain2Sec", 2: "MaintainExt", 3: "NotAvailable"},
            ),
            Signal(
                name="MaintainPower_KeySwitchState",
                start_bit=6, length=2,
                value_table={0: "Off", 1: "NotOff", 2: "Error", 3: "NotAvailable"},
            ),
            Signal(
                name="MaintainPower_ImplementInWorkState",
                start_bit=8, length=2,
                value_table={0: "NotInWork", 1: "InWork", 2: "Error", 3: "NotAvailable"},
            ),
            Signal(
                name="MaintainPower_ImplementReadyToWorkState",
                start_bit=10, length=2,
                value_table={0: "NotReady", 1: "Ready", 2: "Error", 3: "NotAvailable"},
            ),
        ])


def enrich_heartbeat(pgns_by_name: dict[str, Pgn]) -> None:
    if "HeartbeatMessage" in pgns_by_name:
        p = pgns_by_name["HeartbeatMessage"]
        p.signals.extend([
            Signal(
                name="HeartbeatSequenceCounter",
                start_bit=0, length=8,
                comment="Increments 0..250 then wraps; per isobus_heartbeat.hpp",
            ),
        ])


def build_dbc(pgns: list[Pgn], dbc_out: Path) -> int:
    """Generate a DBC file from extracted PGNs using canmatrix's Python API."""
    from canmatrix import canmatrix as cm
    from canmatrix import formats

    matrix = cm.CanMatrix()
    # Note: global BusType/ProtocolType attributes require global_defines registration;
    # omitted for v0.1.0 — canmatrix --check validates without them and they're advisory.

    for p in pgns:
        # Use the PGN value as the CAN message ID.
        # Mark as extended (29-bit) since J1939 / ISO 11783 use 29-bit identifiers.
        frame_id = cm.ArbitrationId(id=p.pgn, extended=True)
        frame = cm.Frame(
            name=p.name,
            arbitration_id=frame_id,
            size=8,
            comment=p.comment,
        )
        if p.signals:
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
                if s.value_table:
                    for v, label in s.value_table.items():
                        sig.add_values(v, label)
                frame.add_signal(sig)
        else:
            # Placeholder generic 64-bit raw payload for PGNs without enriched signals.
            sig = cm.Signal(
                name=f"{p.name}_RawPayload",
                start_bit=0,
                size=64,
                is_little_endian=True,
                is_signed=False,
                factor=1,
                offset=0,
                comment=(
                    "Generic 8-byte raw payload. Signal-level decoding requires ISO 11783-X spec lookup "
                    "or AgIsoStack++ parser inspection — manual enrichment via PR welcome."
                ),
            )
            frame.add_signal(sig)
        matrix.add_frame(frame)

    formats.dumpp({"": matrix}, str(dbc_out))
    return len(pgns)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="opendbc-ag repo root (default: derived from this file)",
    )
    args = parser.parse_args()
    repo = args.repo_root

    # Commit pin gate: refuse to run without a recorded upstream SHA.
    # Re-running against `main` six months from now silently parses a moved target.
    pin_file = repo / "extractions/AGISOSTACK_PIN.txt"
    if not pin_file.exists():
        print(
            "ERROR: extractions/AGISOSTACK_PIN.txt is missing.\n"
            "Record the upstream AgIsoStack++ commit SHA that this extraction\n"
            "should be reproducible against, then re-run.",
            file=sys.stderr,
        )
        return 1
    pinned_sha = pin_file.read_text().strip().split()[0]
    print(f"AgIsoStack++ pin: {pinned_sha}")

    enum_header = (
        repo
        / "extractions/agisostack_clone/isobus/include/isobus/isobus/can_general_parameter_group_numbers.hpp"
    )
    if not enum_header.exists():
        print(f"ERROR: AgIsoStack++ enum header not found at {enum_header}", file=sys.stderr)
        print(
            f"Run: cd extractions && git clone https://github.com/Open-Agriculture/AgIsoStack-plus-plus.git agisostack_clone && cd agisostack_clone && git checkout {pinned_sha}",
            file=sys.stderr,
        )
        return 1

    # Phase 2a: parse PGN enum
    all_pgns = parse_pgn_enum(enum_header)
    print(f"Parsed {len(all_pgns)} PGN enum entries.")

    # Phase 2b: filter via centralized scope policy (DP0+DP1 ranges + name patterns)
    valid_pgns = [p for p in all_pgns if is_in_scope(p.pgn, p.name)]
    rejected = [p for p in all_pgns if not is_in_scope(p.pgn, p.name)]
    print(f"Rejected {len(rejected)} out-of-scope PGNs:")
    for p in rejected:
        print(f"  - {p.pgn:#X} {p.name!r}: {reject_reason(p.pgn, p.name)}")
    print(f"Retained {len(valid_pgns)} pure-standard PGNs.")

    # Phase 2c: enrich subset with signal-level data
    by_name = {p.name: p for p in valid_pgns}
    enrich_speed_distance(by_name)
    enrich_guidance(by_name)
    enrich_time_date(by_name)
    enrich_language(by_name)
    enrich_maintain_power(by_name)
    enrich_heartbeat(by_name)

    enriched = sum(1 for p in valid_pgns if p.signals)
    print(f"Enriched {enriched}/{len(valid_pgns)} PGNs with signal-level definitions.")

    # Save intermediate JSON
    out_json = repo / "extractions/agisostack_pgns.json"
    from datetime import datetime, timezone
    payload = {
        "source": "Open-Agriculture/AgIsoStack-plus-plus",
        "source_license": "MIT",
        "source_commit_pin": pinned_sha,
        "extraction_date": datetime.now(timezone.utc).date().isoformat(),
        "pgn_count_total": len(all_pgns),
        "pgn_count_rejected_proprietary": len(rejected),
        "pgn_count_valid": len(valid_pgns),
        "pgn_count_enriched_with_signals": enriched,
        "pgns": [
            {
                "name": p.name,
                "pgn": p.pgn,
                "pgn_hex": f"0x{p.pgn:04X}",
                "source_file": p.source_file,
                "source_line": p.source_line,
                "comment": p.comment,
                "signals": [asdict(s) for s in p.signals],
            }
            for p in valid_pgns
        ],
    }
    out_json.write_text(json.dumps(payload, indent=2))
    print(f"Wrote extraction JSON: {out_json}")

    # Generate DBC
    out_dbc = repo / "opendbc_ag/dbc/iso11783_from_agisostack.dbc"
    count = build_dbc(valid_pgns, out_dbc)
    print(f"Wrote DBC: {out_dbc} ({count} frames)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
