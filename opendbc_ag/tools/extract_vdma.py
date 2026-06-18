"""
Scrape isobus.net VDMA Data Dictionary PGN index for opendbc-ag.

Polite scrape: 2-second delay between requests, User-Agent identifying the project.
Scope: PGN-level list only (3,200+ entries across 33 pages). Detail-page signal
enrichment is left as community-PR territory.

Reads (live): https://www.isobus.net/isobus/pGNAndSPN/index?type=PGN&PGNAndSPN_page=N
Writes:
  extractions/vdma_pgn_index.json — structured intermediate
  opendbc_ag/dbc/iso11783_from_vdma.dbc — DBC file with PGN-level entries + RawPayload placeholders

Scope policy: pure-standard only. PGNs in 0xEF00 or 0xFF00..0xFFFF are rejected.
Also: PGNs duplicated from the AgIsoStack++ extraction are skipped (no duplicates across
DBC files; the AgIsoStack-sourced version with richer signals wins).

Checkpoint: if scrape fails (rate limit, JS-rendered content, 4xx/5xx), write
RALPH_STATUS.md with state=blocked_phase3 and return non-zero so the loop can
proceed to Phase 4 without erroring out.

Usage:
  python -m opendbc_ag.tools.extract_vdma [--repo-root PATH] [--max-pages N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USER_AGENT = "opendbc-ag-bot/0.1 (+https://github.com/chris-youngblut-solutions/opendbc-ag; pure-standard ISO 11783 DBC corpus)"
REQUEST_DELAY_SEC = 2.0
LIST_URL = "https://www.isobus.net/isobus/pGNAndSPN/index"

from opendbc_ag.tools._scope_policy import is_in_scope, reject_reason


@dataclass
class VdmaPgnEntry:
    pgn: int
    name: str
    detail_url: str


def parse_list_html(html: str) -> tuple[list[VdmaPgnEntry], int | None]:
    """Pure-function: parse one isobus.net list page's HTML into entries + total_pages.

    Pulled out of `scrape_list_page` for unit-testability without HTTP.
    """
    soup = BeautifulSoup(html, "lxml")

    entries: list[VdmaPgnEntry] = []
    for a in soup.find_all("a", href=re.compile(r"/isobus/pGNAndSPN/\d+\?type=PGN")):
        parent_tr = a.find_parent("tr")
        if parent_tr is None:
            continue
        cells = parent_tr.find_all("td")
        if len(cells) < 2:
            continue
        pgn_text = cells[0].get_text(strip=True)
        name_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        try:
            pgn_val = int(pgn_text, 0)
        except ValueError:
            continue
        entries.append(
            VdmaPgnEntry(
                pgn=pgn_val,
                name=name_text,
                detail_url=f"https://www.isobus.net{a['href']}",
            )
        )

    total_pages = None
    pag = soup.find("ul", class_=re.compile(r"pagination"))
    if pag:
        last_link = pag.find("a", string=re.compile(r"^(Last|»»)$"))
        if last_link and last_link.get("href"):
            m = re.search(r"PGNAndSPN_page=(\d+)", last_link["href"])
            if m:
                total_pages = int(m.group(1))
    return entries, total_pages


def scrape_list_page(page_num: int, session: requests.Session) -> tuple[list[VdmaPgnEntry], int | None]:
    """Fetch a single list page; return (entries, total_pages) where total_pages may be None on later calls."""
    url = LIST_URL
    params = {"type": "PGN", "PGNAndSPN_page": page_num}
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return parse_list_html(resp.text)


def sanitize_signal_name(name: str, max_len: int = 32) -> str:
    """Convert a PGN human-readable name into a DBC-safe signal name."""
    s = re.sub(r"[^A-Za-z0-9_]", "_", name)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "Unknown"
    if not re.match(r"^[A-Za-z_]", s):
        s = "_" + s
    return s[:max_len]


def build_dbc(entries: list[VdmaPgnEntry], dbc_out: Path) -> int:
    from canmatrix import canmatrix as cm
    from canmatrix import formats

    matrix = cm.CanMatrix()

    for e in entries:
        # 29-bit extended ID; treat the PGN value itself as the frame ID base
        frame_id = cm.ArbitrationId(id=e.pgn, extended=True)
        safe_name = sanitize_signal_name(e.name) or f"PGN_{e.pgn:X}"
        # Prefix with PGN to ensure name uniqueness
        frame_name = f"VDMA_{e.pgn:X}_{safe_name}"[:64]
        frame = cm.Frame(
            name=frame_name,
            arbitration_id=frame_id,
            size=8,
            comment=f"Source: isobus.net VDMA Data Dictionary ({e.detail_url})",
        )
        sig = cm.Signal(
            name=f"{safe_name}_RawPayload"[:64],
            start_bit=0,
            size=64,
            is_little_endian=True,
            is_signed=False,
            factor=1,
            offset=0,
            comment=(
                f"Generic 8-byte raw payload. Detail page: {e.detail_url}. "
                "Signal-level enrichment via PR welcome — see CONTRIBUTING.md."
            ),
        )
        frame.add_signal(sig)
        matrix.add_frame(frame)

    formats.dumpp(
        {"": matrix},
        str(dbc_out),
        dbcExportEncoding="utf-8",
        dbcExportCommentEncoding="utf-8",
    )
    # Inherit cleanup helpers from extract_j1939_ag (post-process for factor + BS_).
    from opendbc_ag.tools.extract_j1939_ag import _clean_numeric_tokens, _set_baudrate
    _clean_numeric_tokens(dbc_out)
    _set_baudrate(dbc_out, 250000)
    return len(entries)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=33,
        help="Max number of pagination pages to fetch (default 33 = full corpus)",
    )
    args = parser.parse_args()
    repo = args.repo_root

    status_md = repo / "extractions/SCRAPE_STATUS.md"

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    session.headers["Accept"] = "text/html"

    all_entries: list[VdmaPgnEntry] = []
    page = 1
    declared_total = None
    while page <= args.max_pages:
        try:
            print(f"Fetching list page {page}…", flush=True)
            entries, total_pages = scrape_list_page(page, session)
        except requests.RequestException as e:
            msg = f"VDMA scrape blocked at page {page}: {e}"
            print(f"ERROR: {msg}", file=sys.stderr)
            status_md.write_text(
                f"# Ralph status — Phase 3 blocked\n\n{msg}\n\n"
                f"Continuing to Phase 4. Re-run `python -m opendbc_ag.tools.extract_vdma` after resolving.\n"
            )
            return 1

        if not entries:
            print(f"  page {page}: 0 entries → stopping pagination.")
            break

        all_entries.extend(entries)
        print(f"  page {page}: +{len(entries)} entries (running total {len(all_entries)})")

        if declared_total is None and total_pages is not None:
            declared_total = total_pages
            print(f"  pagination reports {declared_total} total pages")

        if declared_total is not None and page >= declared_total:
            break

        page += 1
        time.sleep(REQUEST_DELAY_SEC)

    print(f"\nTotal entries scraped: {len(all_entries)}")

    # Filter via centralized scope policy (DP0+DP1 ranges + name patterns)
    valid = [e for e in all_entries if is_in_scope(e.pgn, e.name)]
    rejected = [e for e in all_entries if not is_in_scope(e.pgn, e.name)]
    print(f"Rejected {len(rejected)} out-of-scope entries.")
    for e in rejected[:10]:
        print(f"  - {e.pgn:#X} {e.name!r}: {reject_reason(e.pgn, e.name)}")
    if len(rejected) > 10:
        print(f"  ... and {len(rejected) - 10} more")

    # De-duplicate against other DBCs that have richer signal-level content
    # (Phase 2 AgIsoStack++ + Phase 4 J1939 ag-subset).
    higher_priority_pgns: set[int] = set()
    for path in (
        repo / "extractions/agisostack_pgns.json",
        repo / "extractions/j1939_ag_pgns.json",
    ):
        if path.exists():
            data = json.loads(path.read_text())
            ids = {p["pgn"] for p in data["pgns"]}
            higher_priority_pgns |= ids
            print(f"Loaded {len(ids)} PGN IDs from {path.name} for de-dup.")
    print(f"Total higher-priority PGN IDs (will be skipped in VDMA DBC): {len(higher_priority_pgns)}")

    unique = [e for e in valid if e.pgn not in higher_priority_pgns]
    deduped = [e for e in valid if e.pgn in higher_priority_pgns]
    print(f"De-duplicated {len(deduped)} entries already covered by signal-level DBCs.")
    print(f"Final unique entries for VDMA DBC: {len(unique)}")

    # Floor-count gate: a successful scrape should yield well over 1500 entries.
    # Below that, isobus.net's HTML structure has likely changed; halt rather than
    # silently overwrite the cached corpus.
    SCRAPE_FLOOR = 1500
    if len(all_entries) < SCRAPE_FLOOR:
        status_md = repo / "extractions/SCRAPE_STATUS.md"
        status_md.write_text(
            f"# VDMA scrape returned {len(all_entries)} entries (< floor {SCRAPE_FLOOR}).\n\n"
            f"Likely cause: isobus.net HTML structure changed. Re-derive the parser\n"
            f"against the current page shape (`opendbc_ag/tests/fixtures/vdma_pgn_sample.html`\n"
            f"can be regenerated by `curl --output -` against a known detail-page URL).\n"
        )
        print(
            f"ERROR: scrape returned only {len(all_entries)} entries (floor: {SCRAPE_FLOOR}). "
            f"Wrote {status_md}; refusing to overwrite the cached JSON/DBC.",
            file=sys.stderr,
        )
        return 1

    # Save intermediate JSON
    from datetime import datetime, timezone
    out_json = repo / "extractions/vdma_pgn_index.json"
    payload = {
        "source": "isobus.net VDMA Data Dictionary (public summaries)",
        "source_url": "https://www.isobus.net/isobus/pGNAndSPN/",
        "extraction_date": datetime.now(timezone.utc).date().isoformat(),
        "scraped_pages": page,
        "total_scraped": len(all_entries),
        "rejected_proprietary": len(rejected),
        "deduplicated_against_agisostack": len(deduped),
        "final_unique": len(unique),
        "entries": [
            {
                "pgn": e.pgn,
                "pgn_hex": f"0x{e.pgn:X}",
                "name": e.name,
                "detail_url": e.detail_url,
            }
            for e in unique
        ],
    }
    out_json.write_text(json.dumps(payload, indent=2))
    print(f"Wrote: {out_json}")

    # Generate DBC
    out_dbc = repo / "opendbc_ag/dbc/iso11783_from_vdma.dbc"
    n = build_dbc(unique, out_dbc)
    print(f"Wrote DBC: {out_dbc} ({n} frames)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
