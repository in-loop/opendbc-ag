# `extractions/`

Intermediate extraction artifacts from the three extractors. Kept in-repo so the DBC corpus is reproducible from these JSON intermediates, not just from the upstream sources (which may move).

- `agisostack_pgns.json` — parsed PGN/SPN definitions from AgIsoStack++ C++ source. Carries the pinned upstream SHA (see `AGISOSTACK_PIN.txt`).
- `vdma_pgn_index.json` — scraped PGN definitions from isobus.net VDMA Data Dictionary (best-effort, filtered through the scope policy).
- `j1939_ag_pgns.json` — aggregated public J1939 ag-relevant PGN definitions (hand-curated).
- `AGISOSTACK_PIN.txt` — pin file recording the AgIsoStack++ commit SHA the extraction was derived from. Required by `extract_agisostack.py`; the script refuses to run without it.
- `SCRAPE_STATUS.md` — written by `extract_vdma.py` if the scrape falls below the floor count (signal that isobus.net HTML changed).

`extractions/agisostack_clone/` (gitignored): ephemeral clone of `Open-Agriculture/AgIsoStack-plus-plus` used during the AgIsoStack extraction. Checkout matches the SHA in `AGISOSTACK_PIN.txt`.
