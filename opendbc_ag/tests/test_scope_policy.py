"""Pin the scope-policy predicate against the boundaries.

If this test changes, the project's published scope claim changes — review
README / CoC §8 / legal-context.md / CONTRIBUTING.md scope sections together.
"""
from __future__ import annotations

import pytest

from opendbc_ag.tools._scope_policy import (
    is_in_scope,
    is_nonstandard_name,
    is_proprietary_pgn,
)


@pytest.mark.parametrize(
    "pgn,expected",
    [
        # In-scope: standard ranges
        (0x0000, False),
        (0xEEFF, False),
        (0xEF01, False),
        (0xFE48, False),  # WheelBasedSpeedAndDistance
        (0xFEFF, False),
        # DP0 proprietary
        (0xEF00, True),  # Proprietary A
        (0xFF00, True),  # Proprietary B low boundary
        (0xFF80, True),
        (0xFFFF, True),  # Proprietary B high boundary
        # DP1 proprietary
        (0x1EF00, True),  # Proprietary A2
        (0x1FF00, True),  # Proprietary B Page 1 low boundary
        (0x1FFFF, True),  # Proprietary B Page 1 high boundary
        # DP1 standard (just below DP1 proprietary range)
        (0x1FEFF, False),
    ],
)
def test_is_proprietary_pgn(pgn: int, expected: bool) -> None:
    assert is_proprietary_pgn(pgn) is expected


@pytest.mark.parametrize(
    "name,expected",
    [
        # Out-of-scope name patterns
        ("Proprietary_Method_Identification", True),
        ("Proprietary Method Identification", True),  # space-separated
        ("ProprietaryB", True),
        ("Reserved_for_ISO_15765", True),
        ("Reserved for ISO 15765-2", True),  # space-separated (real isobus.net form)
        ("Reserved_for_Diagnostic", True),
        ("Reserved for Diagnostic Message", True),
        ("Reserved for FMS Telltale status", True),
        ("Reserved", True),
        ("RESERVED FOR FMS", True),  # case-insensitive
        # In-scope names
        ("WheelBasedSpeedAndDistance", False),
        ("EngineCoolantTemp", False),
        ("AgriculturalGuidanceMachineInfo", False),
        ("", False),  # empty name is in scope by name; PGN check still applies
    ],
)
def test_is_nonstandard_name(name: str, expected: bool) -> None:
    assert is_nonstandard_name(name) is expected


def test_in_scope_combined_predicate() -> None:
    # In-scope: standard PGN + standard name
    assert is_in_scope(0xFE48, "WheelBasedSpeedAndDistance")
    # Out-of-scope by PGN range
    assert not is_in_scope(0xFF00, "EvenLooksLegit")
    # Out-of-scope by name pattern (PGN itself standard)
    assert not is_in_scope(0x9B00, "Proprietary_Method_Identification")
    # Out-of-scope by DP1
    assert not is_in_scope(0x1FF00, "Anything")
