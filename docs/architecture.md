# Architecture

A short tour of what lives where in the repository, the data flow that produces the DBC corpus, and the CI gates that keep it consistent.

---

## Directory tour

```
opendbc-ag/
├── opendbc_ag/                          # Python package
│   ├── dbc/                             # The DBC corpus (the actual product)
│   │   ├── iso11783_from_agisostack.dbc
│   │   ├── iso11783_from_vdma.dbc
│   │   └── j1939_ag_subset.dbc
│   ├── tools/                           # Extractors, inferrer, anonymizer
│   │   ├── extract_agisostack.py        # AgIsoStack++ C++ → DBC
│   │   ├── extract_vdma.py              # isobus.net VDMA HTML → DBC
│   │   ├── extract_j1939_ag.py          # Hand-curated J1939 → DBC
│   │   ├── dbc_inferrer.py              # Heuristic signal inference from CAN logs
│   │   ├── anonymize.py                 # Log scrubber (GPS, timestamps, SA)
│   │   └── coverage_report.py           # Generates docs/coverage.md
│   └── tests/
│       ├── test_smoke.py                # Parse + scope + duplicate + size invariants
│       ├── test_signal_naming.py        # DBC identifier / length / prefix rules
│       ├── test_dbc_inferrer.py         # Inferrer against deterministic fixture
│       ├── test_coverage_report.py      # Smoke test for report generation
│       ├── test_anonymize.py            # Scrubber primitive correctness
│       └── fixtures/
│           ├── generate_synthetic_can.py
│           └── synthetic_can.csv
├── extractions/                         # Intermediate JSON from each extractor
│   ├── agisostack_pgns.json
│   ├── vdma_pgn_index.json
│   └── j1939_ag_pgns.json
├── corpus/                              # Reference CAN trace corpus (future)
├── docs/
│   ├── coverage.md                      # Auto-generated
│   ├── signal-naming-guide.md
│   ├── cabana-for-ag-setup.md
│   ├── code-of-conduct.md
│   ├── legal-context.md
│   ├── faq.md
│   └── architecture.md                  # this file
└── .github/
    ├── workflows/
    │   ├── ci.yml                       # Install + DBC parse check + pytest
    │   ├── consistency.yml              # Proprietary range + cross-DBC dup check
    │   └── coverage.yml                 # Auto-regenerate docs/coverage.md
    ├── ISSUE_TEMPLATE/{bug,feature,new-pgn}.yml
    └── PULL_REQUEST_TEMPLATE.md
```

---

## Data flow: how the DBC corpus is built

Each DBC file in `opendbc_ag/dbc/` is produced by a dedicated extractor that lives in `opendbc_ag/tools/`. The extractor writes an intermediate JSON to `extractions/` first, then converts that JSON to DBC via `canmatrix`. This two-stage pipeline keeps the DBC generation reproducible and the intermediate auditable.

```
Public source                Intermediate                   Final DBC
─────────────                ────────────                   ─────────

AgIsoStack++ C++       →   agisostack_pgns.json       →   iso11783_from_agisostack.dbc
(MIT, cloned local)        (Sig/Pgn dataclasses)          (canmatrix dumpp)

isobus.net VDMA HTML    →   vdma_pgn_index.json        →   iso11783_from_vdma.dbc
(scraped 2s-delay)         (deduped vs above + J1939)     (placeholder _RawPayload)

Hand-curated J1939      →   j1939_ag_pgns.json         →   j1939_ag_subset.dbc
(Wikipedia, CSS Elec.)     (PGN_DEFINITIONS literal)      (signal-level definitions)
```

Each signal in the resulting DBC carries a `CM_ SG_` comment naming its public source, so provenance is traceable from the final artifact back to the original published page or line of code.

---

## CI gates

Three workflows run on push and PR:

| Workflow | What it checks | Failure mode |
|---|---|---|
| `ci.yml` | Python 3.11 + 3.12 matrix. Installs the package, parses every DBC via canmatrix, runs the full pytest suite (currently 29 tests). | Hard fail; cannot merge. |
| `consistency.yml` | No PGN ID in `0xEF00` or `0xFF00..0xFFFF`. No PGN ID appearing in more than one DBC file. | Hard fail; cannot merge. |
| `coverage.yml` | On push to `main`, regenerates `docs/coverage.md` and commits the diff under the `github-actions[bot]` identity if anything changed. | Best-effort; informational. |

The CI design follows two principles:

1. **Scope policy is enforced by code, not by review.** Anyone can open a PR; CI rejects scope violations without requiring a maintainer to read every line.
2. **Duplicate detection is enforced by code.** Cross-DBC duplicate PGN IDs are easy to introduce by accident when three extractors target overlapping ranges. The consistency workflow makes this a build-time error rather than a runtime correctness bug.

---

## Test layout

29 tests as of v0.1.0-private:

| File | Count | Scope |
|---|---|---|
| `test_smoke.py` | 6 | DBC parses; no proprietary PGNs; no cross-DBC dupes; corpus ≥ 80 PGNs |
| `test_signal_naming.py` | 6 | Identifier syntax, length limits, prefix conventions |
| `test_dbc_inferrer.py` | 10 | Inferrer correctness against the synthetic fixture |
| `test_coverage_report.py` | 1 | Coverage generator runs and writes expected sections |
| `test_anonymize.py` | 6 | Scrubber primitives |

The synthetic fixture (`fixtures/synthetic_can.csv`) is regenerated by a deterministic script — running the generator produces byte-identical output. The fixture seeds known signal patterns (constant bytes, boolean toggle, 16-bit ramp, sinusoidal u8) so the inferrer's heuristics can be tested against ground truth.

---

## Dependencies

| Dependency | Purpose | License |
|---|---|---|
| `canmatrix` | DBC parser / writer, used by extractors and CI checks | BSD-2-Clause |
| `cantools` | Alternate DBC parser, available for downstream user convenience | BSD-2-Clause |
| `python-can` | CAN frame model, used in tooling | LGPL-3.0-or-later (link-only) |
| `numpy` | Numeric ops in the inferrer | BSD-3-Clause |
| `requests` + `beautifulsoup4` + `lxml` | HTML scrape for VDMA extractor | Apache-2.0 / MIT |
| `pytest` (dev) | Test runner | MIT |

All dependencies are pinned at floor versions in `pyproject.toml`. No GPL/AGPL runtime dependencies.

---

## What's not here

- **Reference CAN trace corpus** in `corpus/` is currently a placeholder directory. Trace capture requires hardware deployment and field operations — it lives outside the scope of the initial build and will be populated as captures accumulate.
- **Field-specific pinouts** (JD 9R, Kinze 3700, Hagie STS, Brent V-Series TRAX, JD S/X combine) are flagged `<TODO>` in `docs/cabana-for-ag-setup.md` §7 — to be filled in after first-hand capture.
- **Partnership cross-links** (AgOpenGPS, Open-Agriculture, Tractor Hacking, ISOBlue HD) happen at public release time, not before.

---

## Changes

| Date | Change |
|---|---|
| 2026-05-13 | Initial draft (v0.1.0-private). |
