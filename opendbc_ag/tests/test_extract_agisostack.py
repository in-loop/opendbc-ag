"""Unit tests for the AgIsoStack++ PGN-enum parser.

Doesn't require the AgIsoStack++ clone — uses an inline-fixture C++ header.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from opendbc_ag.tools.extract_agisostack import parse_pgn_enum

FIXTURE_HEADER = """\
// AgIsoStack-style header fragment for unit testing
#pragma once

namespace isobus
{
\tenum class CANLibParameterGroupNumber {
\t\tAny = 0,
\t\tWheelBasedSpeedAndDistance = 0xFE48,
\t\tGroundBasedSpeedAndDistance = 0xFE49,
\t\tProprietaryA = 0xEF00,
\t\tProprietaryB_Lo = 0xFF00,
\t\tProprietaryB_Hi = 0xFFFF,
\t\tProprietaryA2 = 0x1EF00,
\t\tStandardPGN_DP1 = 0x1FEFF,
\t\tAddressClaim = 0xEE00,
\t};
}
"""


@pytest.fixture
def header(tmp_path: Path) -> Path:
    h = tmp_path / "can_general_parameter_group_numbers.hpp"
    h.write_text(FIXTURE_HEADER)
    return h


def test_parse_pgn_enum_extracts_entries(header: Path) -> None:
    pgns = parse_pgn_enum(header)
    names = {p.name for p in pgns}
    # `Any = 0` sentinel must be filtered by the parser
    assert "Any" not in names
    # All other entries present
    assert names >= {
        "WheelBasedSpeedAndDistance",
        "GroundBasedSpeedAndDistance",
        "ProprietaryA",
        "ProprietaryB_Lo",
        "ProprietaryB_Hi",
        "ProprietaryA2",
        "StandardPGN_DP1",
        "AddressClaim",
    }


def test_parse_pgn_enum_hex_values_correct(header: Path) -> None:
    pgns = {p.name: p.pgn for p in parse_pgn_enum(header)}
    assert pgns["WheelBasedSpeedAndDistance"] == 0xFE48
    assert pgns["ProprietaryA2"] == 0x1EF00
    assert pgns["StandardPGN_DP1"] == 0x1FEFF
    assert pgns["AddressClaim"] == 0xEE00


def test_parse_pgn_enum_attaches_source_attribution(header: Path) -> None:
    pgns = parse_pgn_enum(header)
    for p in pgns:
        assert p.comment.startswith("Source: AgIsoStack++ ")
        assert p.source_file == header.name


def test_scope_policy_rejects_proprietary_subset(header: Path) -> None:
    """Cross-check: parse + apply scope policy + verify expected rejections."""
    from opendbc_ag.tools._scope_policy import is_in_scope

    pgns = parse_pgn_enum(header)
    kept = [p for p in pgns if is_in_scope(p.pgn, p.name)]
    rejected = [p for p in pgns if not is_in_scope(p.pgn, p.name)]
    rejected_names = {p.name for p in rejected}
    kept_names = {p.name for p in kept}

    assert rejected_names == {
        "ProprietaryA",
        "ProprietaryB_Lo",
        "ProprietaryB_Hi",
        "ProprietaryA2",
    }
    assert kept_names == {
        "WheelBasedSpeedAndDistance",
        "GroundBasedSpeedAndDistance",
        "StandardPGN_DP1",
        "AddressClaim",
    }
