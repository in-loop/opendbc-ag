# `opendbc_ag/tests/`

Test suite — run with `pytest` from the project root.

- `test_dbc_syntax.py` — parametrized canmatrix validation across all DBC files
- `test_consistency.py` — cross-DBC duplicate PGN detection + proprietary-range PGN rejection
- `test_signal_naming.py` — signal-name convention compliance
- `test_dbc_inferrer.py` — inferrer correctness on synthetic CAN logs
- `test_coverage_report.py` — coverage matrix generation smoke test
- `test_anonymize.py` — PII stripping correctness
- `fixtures/` — synthetic test CAN logs with seeded signals
