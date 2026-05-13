# Changelog

All notable changes to opendbc-ag are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Added (Phase 6 — README finalization)
- Expanded README with live coverage table (frames/signals/source per DBC)
- Cross-link to auto-regenerated `docs/coverage.md`

## [v0.0.1] — 2026-05-13

### Added
- **Phase 0** — Initial scaffold: `LICENSE` (MIT), `.gitignore`, `README.md`, `CHANGELOG.md`. Private GitHub repo created. Scope policy: pure-standard ISO 11783 + J1939 PGNs only; no proprietary OEM ranges.
- **Phase 1** — Directory structure: `opendbc_ag/{dbc,tools,tests}/`, `docs/`, `.github/{workflows,ISSUE_TEMPLATE}/`, `corpus/`, `extractions/` with per-directory READMEs.
- **Phase 2** — AgIsoStack++ PGN extraction (46 PGNs, 84 signals, 9 signal-enriched). `opendbc_ag/tools/extract_agisostack.py`, `extractions/agisostack_pgns.json`, `opendbc_ag/dbc/iso11783_from_agisostack.dbc`.
- **Phase 3** — isobus.net VDMA scrape (2,892 unique pure-standard PGNs). `opendbc_ag/tools/extract_vdma.py`, `extractions/vdma_pgn_index.json`, `opendbc_ag/dbc/iso11783_from_vdma.dbc`.
- **Phase 4** — J1939 ag-relevant subset (17 PGNs, 69 signals, hand-curated from public summaries). `opendbc_ag/tools/extract_j1939_ag.py`, `extractions/j1939_ag_pgns.json`, `opendbc_ag/dbc/j1939_ag_subset.dbc`.
- **Phase 5** — CI workflows (`ci.yml` + `consistency.yml` + `coverage.yml`), `pyproject.toml`, `opendbc_ag/tools/coverage_report.py`, `opendbc_ag/tests/test_smoke.py` (6 tests), first `docs/coverage.md`. CI enforces: DBC parses + no proprietary-range PGNs + no cross-DBC duplicates + corpus size >= 80.

### Notes
- Copyright holder set to `ctyoungb` (user-confirmed handle, 2026-05-13).
- Ralph-loop autonomous build in progress. See `RALPH_REPORT.md` (Phase 12) for final summary.
