# `extractions/`

Intermediate extraction artifacts from Ralph-loop phases. Kept in-repo (per user preference) so the work isn't lost if the loop re-runs.

- `agisostack_pgns.json` — Phase 2 output: parsed PGN/SPN definitions from AgIsoStack++ C++ source
- `vdma_pgns.json` — Phase 3 output: scraped PGN definitions from isobus.net VDMA Data Dictionary (best-effort)
- `j1939_ag_pgns.json` — Phase 4 output: aggregated public J1939 ag-relevant PGN definitions

These are the structured intermediates between source-of-truth (upstream code/specs) and DBC files. Re-running the extraction is deterministic from these JSON artifacts.

`extractions/agisostack_clone/` (gitignored): ephemeral clone of `Open-Agriculture/AgIsoStack-plus-plus` used during Phase 2 extraction. Auto-cleaned.
