# Changelog

All notable changes to opendbc-ag are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/).

## [Unreleased]

(no unreleased changes — next development happens after the v0.1.0-private review)

## [v0.1.0-private] — 2026-05-13

### Added
- **Phase 6** — README finalization with live coverage table + cross-link to `docs/coverage.md`.
- **Phase 7** — Community workflow scaffolding: `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, three `ISSUE_TEMPLATE/*.yml` forms (bug, feature, new-pgn), `docs/signal-naming-guide.md`, `docs/code-of-conduct.md` (adopts Contributor Covenant 2.1 by link + project-specific addendum: scope, reporting contact, conflict-of-interest, appeals, AI-content disclosure, safety-signal disclosure, legal-scope clarification).
- **Phase 8** — `docs/cabana-for-ag-setup.md`: generic tooling, dongles, ISOBUS pinout (public sources), capture workflow, signal-discovery method, DBC export flow, fleet-specific pinouts flagged `<TODO>`.
- **Phase 9** — `opendbc_ag/tools/dbc_inferrer.py` (heuristic signal inference), `opendbc_ag/tools/anonymize.py` (log scrubber), deterministic synthetic fixture (`opendbc_ag/tests/fixtures/`), 17 new tests across `test_dbc_inferrer.py`, `test_coverage_report.py`, `test_anonymize.py`.
- **Phase 10** — `opendbc_ag/tests/test_signal_naming.py` (6 tests: DBC-identifier syntax, length limits, prefix conventions). Naming guide signal-length cap lifted 32 → 64 chars.
- **Phase 11** — `docs/legal-context.md` (FTC v Deere, FARM Act, Iowa HF 2763, §1201 / repair exemption, Tractor Hacking), `docs/faq.md`, `docs/architecture.md`. README documentation-link section added.
- **Phase 12** — `RALPH_REPORT.md` (autonomous-build summary + user-TODO punch list); `v0.1.0-private` tag + GitHub pre-release.

### Acceptance criteria (PRD)
- Repo visibility = PRIVATE — ✅
- `pytest opendbc_ag/tests/` passes — ✅ (76 passed, 2 xfailed; was 29/29 at v0.0.1, grown by the R-series remediation)
- `canmatrix --check opendbc_ag/dbc/*.dbc` returns 0 errors — ✅
- Corpus ≥ 80 PGNs — ✅ (2,690 unique PGNs / 2,780 signals, after Phase R1 proprietary-range filtering)
- CI workflows green on `main` — ✅
- `RALPH_REPORT.md` enumerates user TODOs — ✅
- No PGN in proprietary range — ✅ (CI-enforced)
- `docs/cabana-for-ag-setup.md` `<TODO>` placeholders tagged — ✅ (5 fleet-class TODOs flagged in §7 + 2 introductory `<TODO>` markers)

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
