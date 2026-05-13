# `opendbc_ag/dbc/`

DBC files for agricultural CAN — ISO 11783 (ISOBUS) and SAE J1939 ag-relevant subset.

## Files

- `iso11783_from_agisostack.dbc` — extracted from [AgIsoStack++](https://github.com/Open-Agriculture/AgIsoStack-plus-plus) MIT-licensed C++ source (Phase 2)
- `iso11783_from_vdma.dbc` — extracted from [isobus.net VDMA Data Dictionary](https://www.isobus.net/isobus/) public summaries (Phase 3, best-effort)
- `j1939_ag_subset.dbc` — aggregated from public J1939 community sources for ag-relevant PGNs (Phase 4)

## Scope

**Pure-standard PGNs only.** CI rejects any PGN ID in the proprietary ranges (`0xEF00`, `0xFF00–0xFFFF`).

## Source attribution

Every signal carries a `CM_ SG_` comment citing its source (file + line for code-extracted, URL for web-extracted). See `docs/coverage.md` for the live coverage matrix.
