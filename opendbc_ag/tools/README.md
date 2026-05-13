# `opendbc_ag/tools/`

Python utilities for working with the DBC corpus.

- `dbc_inferrer.py` — heuristic DBC signal inference from CAN logs (Phase 9)
- `coverage_report.py` — walks `opendbc_ag/dbc/`, generates `docs/coverage.md`
- `anonymize.py` — PII stripping for `corpus/` submissions (GPS, machine-IDs, timestamps)

All tools use the project venv (`pip install -e .`).
