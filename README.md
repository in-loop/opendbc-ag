# opendbc-ag

> OSS canonical agricultural-CAN DBC repository — ISO 11783 (ISOBUS) + J1939 ag-relevant subset, MIT-licensed.

**Status:** `v0.1.0-private` — under review by author before public release. Not affiliated with comma.ai, opendbc, AgIsoStack, AgOpenGPS, John Deere, CNH, AGCO, Kubota, Kinze, Hagie, Brent, or any OEM.

## What

opendbc-ag is the agricultural analog to commaai's `opendbc` — a community-maintainable, MIT-licensed repository of CAN DBC files for agricultural equipment. Scope is **pure-standard PGNs only**: ISO 11783 (ISOBUS) public summaries and SAE J1939 ag-relevant subset. No reverse-engineered proprietary OEM PGNs.

## Why

As of May 2026, no ag-flavored fork of opendbc exists in the OSS world. The commercial incumbent (CSS Electronics ISOBUS DBC) is closed and non-redistributable. opendbc-ag fills the gap with MIT-licensed coverage anyone can fork, modify, and ship.

## Coverage

See [`docs/coverage.md`](docs/coverage.md) for the live PGN coverage matrix.

## Install

```bash
git clone <repo-url>
cd opendbc-ag
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). PRs accepted for additional public-spec-derived content. **Proprietary OEM PGNs (PGN IDs in 0xEF00 or 0xFF00–0xFFFF ranges) are out of scope and CI-rejected.**

## License

[MIT](LICENSE). See also [`docs/legal-context.md`](docs/legal-context.md) for the policy rationale.

## Acknowledgments

- [AgIsoStack++](https://github.com/Open-Agriculture/AgIsoStack-plus-plus) — MIT-licensed ISOBUS stack; primary PGN source
- [isobus.net VDMA Data Dictionary](https://www.isobus.net/isobus/) — public ISO 11783-7 summary content
- [SAE J1939 community resources](https://en.wikipedia.org/wiki/SAE_J1939) — public J1939 PGN tables
- Tools used: [canmatrix](https://github.com/ebroecker/canmatrix) (BSD-2), [cantools](https://github.com/cantools/cantools) (BSD-2), [python-can](https://github.com/hardbyte/python-can) (LGPL-3.0)

## Not affiliated with

This project is independent. Not affiliated with or endorsed by comma.ai, opendbc, AgIsoStack, AgOpenGPS, AEF (Agricultural Industry Electronics Foundation), CSS Electronics, John Deere, CNH Industrial, AGCO, Kubota, Kinze, Hagie, Brent / Unverferth, Tractor Hacking, Open-Agriculture, or any other organization mentioned in the source documentation.

## Roadmap (post-public-release)

- Partnership cross-links (Open-Agriculture, AgOpenGPS, Tractor Hacking, ISOBlue HD/Purdue)
- Community contribution review queue
- Quarterly release cadence
- Reference CAN trace corpus from real field deployments
