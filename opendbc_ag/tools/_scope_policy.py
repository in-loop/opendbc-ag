"""Centralized scope-policy predicate for the opendbc-ag corpus.

This module is the single source of truth for which PGNs and frame names are
in scope. All extractors (`extract_*.py`), the CI smoke tests, and the CI
consistency workflow use the functions here.

Why centralized: the original v0.1.0-private build duplicated the predicate
across three extractors and the test suite. Only Data Page 0 ranges were
checked. Data Page 1 proprietary ranges (`0x1EF00`, `0x1FF00..0x1FFFF`) and
"Proprietary"/"Reserved_for_*" name patterns leaked through, producing 810
out-of-scope frames in the published DBC. Single-predicate enforcement
prevents that class of drift from recurring.

References (public sources):
- SAE J1939-21: protocol layer, PDU1/PDU2 distinction, Data Page bit
- SAE J1939-71: vehicle application layer, proprietary range definitions
- AgIsoStack++ source comments documenting the ranges
"""
from __future__ import annotations

import re

# Data Page 0 (DP=0) proprietary ranges
PROPRIETARY_A_DP0 = 0xEF00
PROPRIETARY_B_DP0_LO = 0xFF00
PROPRIETARY_B_DP0_HI = 0xFFFF

# Data Page 1 (DP=1) proprietary ranges. The DP1 bit shifts the PGN range by 0x10000.
PROPRIETARY_A_DP1 = 0x1EF00
PROPRIETARY_B_DP1_LO = 0x1FF00
PROPRIETARY_B_DP1_HI = 0x1FFFF

# Name patterns that indicate out-of-scope content even when the PGN ID itself
# is in a nominally-standard range. isobus.net's VDMA index includes a number
# of "Reserved for ..." / "Reserved_for_..." / "Proprietary ..." placeholder entries
# that are not standard ag content. Source names may be either spaces or
# underscores, so use a word-boundary match.
_NONSTANDARD_NAME_PATTERN = re.compile(
    r"^(Proprietary|Reserved)",
    re.IGNORECASE,
)


def is_proprietary_pgn(pgn: int) -> bool:
    """Return True if `pgn` falls in any J1939/ISO 11783 proprietary range.

    Covers DP0 and DP1 ranges:
    - 0xEF00       (Proprietary A,  DP0)
    - 0x1EF00      (Proprietary A2, DP1)
    - 0xFF00..0xFFFF   (Proprietary B,  DP0)
    - 0x1FF00..0x1FFFF (Proprietary B,  DP1)
    """
    if pgn == PROPRIETARY_A_DP0 or pgn == PROPRIETARY_A_DP1:
        return True
    if PROPRIETARY_B_DP0_LO <= pgn <= PROPRIETARY_B_DP0_HI:
        return True
    if PROPRIETARY_B_DP1_LO <= pgn <= PROPRIETARY_B_DP1_HI:
        return True
    return False


def is_nonstandard_name(name: str) -> bool:
    """Return True if the PGN's name marks it as non-standard placeholder content.

    Matches `Proprietary*`, `Reserved_for_*`, and bare `Reserved`. Case-insensitive.
    Use in addition to `is_proprietary_pgn` — both must pass for the entry to be in scope.
    """
    if not name:
        return False
    return bool(_NONSTANDARD_NAME_PATTERN.match(name))


def is_in_scope(pgn: int, name: str = "") -> bool:
    """Combined predicate. True if the entry is in scope for this corpus."""
    return not is_proprietary_pgn(pgn) and not is_nonstandard_name(name)


def reject_reason(pgn: int, name: str = "") -> str | None:
    """Return a one-line reason for rejection, or None if in scope.

    Useful for logging during extraction.
    """
    if is_proprietary_pgn(pgn):
        return f"proprietary PGN range (0x{pgn:X})"
    if is_nonstandard_name(name):
        return f"non-standard name pattern ({name!r})"
    return None
