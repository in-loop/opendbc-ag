# Security policy

## Scope

opendbc-ag ships data (DBC files) and Python tooling. It does not produce binaries, install on equipment, or interact with running CAN buses. The traditional CVE / binary-vulnerability model does not apply.

What we **do** treat as security-relevant:

- **Incorrect signal definitions that could cause harm if followed** — particularly for safety-critical signal classes (brake, steering, hydraulic, PTO engagement, three-point hitch). A misread brake-status bit position is, functionally, a vulnerability in the documentation.

## Reporting

If you believe a published signal definition in this repository is wrong in a way that could cause harm if followed:

1. Open a GitHub issue tagged `safety`.
2. **Also** email `ctyoungb.agent@gmail.com` (a dedicated, monitored disclosure inbox) so the disclosure has an out-of-band record.

We aim to acknowledge receipt within seven days. The longer disclosure framing — including responsibility expectations and project-vs-legal scope — lives in [`docs/code-of-conduct.md`](docs/code-of-conduct.md) §7.

## What is not in scope here

- Reports about OEM proprietary CAN content. opendbc-ag explicitly does not document those signals; see [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/code-of-conduct.md`](docs/code-of-conduct.md) §8.
- Reports about field equipment safety in general (not signal definitions in this repo). Those belong with the equipment manufacturer.
