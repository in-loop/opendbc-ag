# `corpus/`

Reference CAN trace corpus for DBC validation and contributor testing.

**Status (v0.1.0-private):** Empty placeholder. Captures from real field deployments are deferred to the manual phase — they require Stub R hardware deployment + actual planting/spraying/harvest passes (see priority shortlist item #1).

## Contribution guidelines (when active)

All `corpus/` submissions MUST be processed through `opendbc_ag/tools/anonymize.py` before PR:

- GPS coordinates rounded to ±1 km
- Machine IDs (JDLink VIN, serial numbers) stripped
- Timestamps rounded to date-only

CI rejects raw / non-anonymized captures.

## Format

- `*.mf4` — preferred (canedge-native, dense binary)
- `*.parquet` — analysis-friendly
- `*.log` — cabana-compatible CSV
