"""Run all DBC corpus invariants — used by CI and reproducible locally.

Exits non-zero if any violation is found. Used by `.github/workflows/consistency.yml`
so the CI logic stays unit-testable (vs heredoc-embedded Python in YAML).

Local equivalent:
    python scripts/check_dbc_policy.py
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from canmatrix import formats

from opendbc_ag.tools._scope_policy import is_in_scope, reject_reason


def check_scope(dbc_dir: Path) -> list[str]:
    """Out-of-scope frame detection (DP0+DP1 proprietary + name patterns)."""
    violations = []
    for dbc in sorted(dbc_dir.glob("*.dbc")):
        m = formats.loadp(str(dbc))
        mat = list(m.values())[0]
        for frame in mat.frames:
            pgn = frame.arbitration_id.id
            if not is_in_scope(pgn, frame.name):
                violations.append(
                    f"{dbc.name}: {frame.name} (PGN 0x{pgn:X}) — {reject_reason(pgn, frame.name)}"
                )
    return violations


def check_no_duplicates(dbc_dir: Path) -> list[str]:
    """Cross-DBC duplicate PGN ID detection."""
    seen: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for dbc in sorted(dbc_dir.glob("*.dbc")):
        m = formats.loadp(str(dbc))
        mat = list(m.values())[0]
        for frame in mat.frames:
            seen[frame.arbitration_id.id].append((dbc.name, frame.name))
    return [
        f"PGN 0x{pgn:X}: {locs}"
        for pgn, locs in sorted(seen.items())
        if len(locs) > 1
    ]


def check_source_citations(dbc_dir: Path) -> list[str]:
    """Every frame's CM_ comment should cite a public source (URL or 'Source:').

    Soft-warning checker (informational) — escalate to hard-fail if PR drift
    becomes a problem.
    """
    missing = []
    for dbc in sorted(dbc_dir.glob("*.dbc")):
        m = formats.loadp(str(dbc))
        mat = list(m.values())[0]
        for frame in mat.frames:
            c = (frame.comment or "").lower()
            if "source:" not in c and "http" not in c and "isobus.net" not in c:
                missing.append(f"{dbc.name}: {frame.name} (no source citation in CM_ comment)")
    return missing


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    dbc_dir = repo_root / "opendbc_ag" / "dbc"
    if not dbc_dir.exists():
        print(f"FAIL: dbc dir not found at {dbc_dir}", file=sys.stderr)
        return 1

    scope_violations = check_scope(dbc_dir)
    dupe_violations = check_no_duplicates(dbc_dir)
    citation_warnings = check_source_citations(dbc_dir)

    failed = False

    if scope_violations:
        print(f"FAIL: {len(scope_violations)} out-of-scope frames")
        for v in scope_violations[:30]:
            print(f"  {v}")
        if len(scope_violations) > 30:
            print(f"  ... and {len(scope_violations) - 30} more")
        failed = True
    else:
        print("OK: no out-of-scope frames")

    if dupe_violations:
        print(f"FAIL: {len(dupe_violations)} cross-DBC duplicate PGN(s)")
        for v in dupe_violations[:20]:
            print(f"  {v}")
        failed = True
    else:
        print("OK: no cross-DBC duplicates")

    if citation_warnings:
        # Informational only — don't fail CI on this for now.
        print(f"WARN: {len(citation_warnings)} frame(s) with no public-source citation")
        for w in citation_warnings[:10]:
            print(f"  {w}")
        if len(citation_warnings) > 10:
            print(f"  ... and {len(citation_warnings) - 10} more")
    else:
        print("OK: all frames carry a source citation")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
