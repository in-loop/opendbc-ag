"""Unit tests for the VDMA scraper's HTML parser + signal-name sanitizer.

Uses the static HTML fixture in `fixtures/vdma_pgn_sample.html` so no network
access is required.
"""
from __future__ import annotations

from pathlib import Path

from opendbc_ag.tools.extract_vdma import (
    VdmaPgnEntry,
    parse_list_html,
    sanitize_signal_name,
)

FIXTURE_HTML = (Path(__file__).parent / "fixtures" / "vdma_pgn_sample.html").read_text()


def test_parse_list_html_extracts_valid_rows() -> None:
    entries, total_pages = parse_list_html(FIXTURE_HTML)
    pgns = {e.pgn for e in entries}
    # Decimal 256 + hex 0xFE48 + decimal 65217 (the 3 valid rows)
    assert pgns == {256, 0xFE48, 65217}


def test_parse_list_html_skips_garbage_row() -> None:
    entries, _ = parse_list_html(FIXTURE_HTML)
    names = {e.name for e in entries}
    assert "Garbage row that should be skipped" not in names


def test_parse_list_html_detail_urls_are_absolute() -> None:
    entries, _ = parse_list_html(FIXTURE_HTML)
    for e in entries:
        assert e.detail_url.startswith("https://www.isobus.net/isobus/pGNAndSPN/")


def test_parse_list_html_reads_pagination_total() -> None:
    _, total_pages = parse_list_html(FIXTURE_HTML)
    assert total_pages == 33


def test_sanitize_signal_name_handles_spaces_and_specials() -> None:
    assert sanitize_signal_name("Wheel-based Speed and Distance") == "Wheel_based_Speed_and_Distance"
    assert sanitize_signal_name("Engine Coolant Temp °C") == "Engine_Coolant_Temp_C"
    # Empty input
    assert sanitize_signal_name("") == "Unknown"


def test_sanitize_signal_name_truncates() -> None:
    long = "A" * 100
    assert len(sanitize_signal_name(long)) <= 32


def test_sanitize_signal_name_safe_dbc_identifier() -> None:
    import re
    sanitized = sanitize_signal_name("123 Numbers First")
    assert re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", sanitized)


def test_scope_policy_filters_fixture_entries() -> None:
    """Confirm the scope predicate works against the fixture entries."""
    from opendbc_ag.tools._scope_policy import is_in_scope

    entries, _ = parse_list_html(FIXTURE_HTML)
    in_scope = [e for e in entries if is_in_scope(e.pgn, e.name)]
    # All 3 fixture entries should pass (none are in proprietary ranges or named Proprietary/Reserved)
    assert len(in_scope) == len(entries) == 3
