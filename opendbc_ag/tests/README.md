# `opendbc_ag/tests/`

Test suite — run with `pytest` from the project root.

- `test_smoke.py` — DBC parses, scope-policy invariants (no out-of-scope frames), no cross-DBC duplicate PGN IDs, corpus-size floor
- `test_scope_policy.py` — pins the centralized scope predicate against boundary cases (DP0+DP1 proprietary ranges, name patterns)
- `test_signal_naming.py` — frame/signal name conventions (DBC identifier syntax, length, prefix rules)
- `test_extract_agisostack.py` — AgIsoStack++ C++ enum parser + scope-filter cross-check
- `test_extract_vdma.py` — VDMA HTML parser (against `fixtures/vdma_pgn_sample.html`) + signal-name sanitizer
- `test_extract_j1939_ag.py` — hand-curated J1939 PGN list invariants (count, no proprietary, HRVD-at-correct-PGN)
- `test_dbc_inferrer.py` — heuristic inferrer correctness on the synthetic CAN fixture + DBC emission test + xfail-marked edge-case limitations
- `test_coverage_report.py` — coverage-matrix generator smoke test
- `test_anonymize.py` — PII-stripping primitive correctness
- `fixtures/` — synthetic CAN log + VDMA HTML fixture for the parser tests

Current totals: 76 passing + 2 xfailed (documented inferrer limitations, tracked for v0.1.1).

Run a subset:

```sh
pytest opendbc_ag/tests/test_smoke.py -v
pytest opendbc_ag/tests/ -k "scope_policy or smoke"
pytest --collect-only -q
```
