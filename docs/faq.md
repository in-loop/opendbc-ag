# FAQ

## What is opendbc-ag?

A repository of DBC files describing agricultural CAN bus traffic — primarily ISOBUS (ISO 11783) and the ag-relevant subset of SAE J1939 — sourced from publicly-available documentation and open-source projects. The DBCs are usable directly with [cantools](https://github.com/cantools/cantools), [canmatrix](https://github.com/ebroecker/canmatrix), [SavvyCAN](https://github.com/collin80/SavvyCAN), and the openpilot tools ecosystem.

## Why does this project exist?

There is no widely-shared canonical DBC corpus for ag-CAN content the way [opendbc](https://github.com/commaai/opendbc) is for automotive. Individual researchers, fleet integrators, AgOpenGPS contributors, and academic projects (ISOBlue at Purdue) each maintain partial sets. This project is an attempt at a shared, MIT-licensed, open baseline that anyone can build on. See `docs/legal-context.md` for the scope-policy rationale.

## Is this affiliated with comma.ai, opendbc, AgIsoStack, AgOpenGPS, or any OEM?

No. opendbc-ag is independent. Where we use content from other projects (notably AgIsoStack++ for PGN definitions), the source is cited per signal in the DBC comments and the upstream license is honored.

## Why MIT?

To match opendbc (the automotive project) and AgIsoStack++ (the primary upstream PGN source), and to maximize compatibility with downstream tooling — both commercial and OSS. MIT also avoids the practical complications GPL/AGPL would introduce for users who want to embed these DBCs in proprietary diagnostic or monitoring products.

## Can I add my OEM's proprietary signals?

Not to this repository. opendbc-ag's scope is **pure-standard PGNs only** — anything in the `0xEF00` or `0xFF00..0xFFFF` ranges is rejected by CI. Proprietary signal definitions are interesting and valuable, but they belong in a project whose scope welcomes them. See `docs/legal-context.md` and `docs/code-of-conduct.md` §8 for the reasoning.

## Can I add a PGN I sniffed from my own equipment?

Yes, if (a) the PGN is in the standard range, (b) you can cite a public summary (isobus.net, AgIsoStack++, J1939 Wikipedia, a vendor application note, etc.) for what the signals mean, and (c) your contribution does not transcribe paywalled spec text. See `CONTRIBUTING.md` and the new-PGN issue template.

## What if I see a wrong signal definition?

Open an issue with the `bug` template, or a PR with the fix. If you believe the wrong definition could be **dangerous if followed** (brake, steering, hydraulic, PTO), additionally email the conduct contact in `docs/code-of-conduct.md` so we keep a record of the disclosure.

## What if I can capture a real bus but can't program?

Start with `docs/cabana-for-ag-setup.md`. Capture a log against a known stimulus (drive at known speed, engage PTO, lift the three-point, etc.). Open an issue with the new-PGN template and attach an anonymized log — a maintainer or community contributor can help interpret it.

## Why are the VDMA-sourced frames just placeholders with one big signal?

The isobus.net VDMA Data Dictionary is a list-page-level scrape. We have the PGN ID and name, but most pages do not have signal-level definitions in a clean machine-parseable form. The placeholder `_RawPayload` signal preserves the PGN's existence so it shows up in the corpus, with a `CM_` comment pointing to the detail page for follow-on enrichment by community PR.

## Is this useful with classic CAN dongles?

Yes, for the ISOBUS implement bus (250 kbps classic CAN) and most J1939 chassis buses (500 kbps classic CAN). Newer Hagie, some JD post-2022 systems, and parts of the Raven control bus use CAN-FD — you need a CAN-FD-capable dongle for those. See `docs/cabana-for-ag-setup.md` §2.

## Will there be a public release?

opendbc-ag is publicly available; this repository is the canonical source. Partnerships and announcements happen from the maintainer's account.

## How do I cite this project?

For now: cite the GitHub URL and the commit hash you used. A formal Zenodo DOI / citation file will be added with the first public release tag.

## Where do I report a security issue?

opendbc-ag does not ship binaries, so the traditional CVE/binary-vulnerability model does not apply. For **incorrect signal definitions that could cause harm if followed** (safety-relevant signals — brake, steering, hydraulic, PTO), open an issue with the `safety` label **and** email the conduct contact in `docs/code-of-conduct.md`.

## Changes

| Date | Change |
|---|---|
| 2026-05-13 | Initial draft (v0.1.0-private). |
