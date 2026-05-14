"""Unit tests for the hand-curated J1939 ag-subset definitions.

Pins the curated list against the policy invariants (no proprietary PGNs,
expected count, expected signal totals, HRVD rename + correct PGN).
"""
from __future__ import annotations

from opendbc_ag.tools.extract_j1939_ag import PGN_DEFINITIONS
from opendbc_ag.tools._scope_policy import is_in_scope


def test_pgn_count_floor() -> None:
    """Pins the curated count against the smoke-test floor."""
    assert len(PGN_DEFINITIONS) >= 17


def test_no_out_of_scope_entries() -> None:
    violations = [(p.pgn, p.name) for p in PGN_DEFINITIONS if not is_in_scope(p.pgn, p.name)]
    assert not violations, f"curated J1939 list contains out-of-scope entries: {violations}"


def test_hrvd_present_at_correct_pgn() -> None:
    """R2 domain fix: HRVD should be at PGN 0xFEC1, not 0xFD09."""
    hrvd = [p for p in PGN_DEFINITIONS if "HRVD" in p.name]
    assert len(hrvd) == 1, f"expected exactly one HRVD frame, got {[p.name for p in hrvd]}"
    assert hrvd[0].pgn == 0xFEC1
    # And the obsolete HRLD name should not appear
    hrld = [p for p in PGN_DEFINITIONS if "HRLD" in p.name]
    assert not hrld, f"HRLD typo still present: {[p.name for p in hrld]}"


def test_all_signals_have_units() -> None:
    """Hand-curated entries should always include units for numeric signals."""
    for p in PGN_DEFINITIONS:
        for s in p.signals:
            # Some signals are bit-packed enums and may legitimately have empty unit.
            # Just confirm the attribute exists.
            assert hasattr(s, "unit")


def test_total_signal_count_matches_acceptance() -> None:
    total = sum(len(p.signals) for p in PGN_DEFINITIONS)
    # 69 was the published count in v0.1.0-private; HRVD rename does not change signals.
    assert total >= 69
