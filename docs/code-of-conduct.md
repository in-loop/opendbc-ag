# Code of conduct

## Adoption

This project adopts the **[Contributor Covenant, version 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)** as its baseline code of conduct.

The canonical text — including the pledge, the standards of conduct, the enforcement responsibilities, and the four-tier enforcement ladder — is hosted upstream and licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). We do not redistribute the text inline; please read it at the link above.

The addendum below records project-specific clarifications. It does **not** replace or weaken the upstream Covenant — it only fills gaps the Covenant intentionally leaves to each project.

---

## Project-specific addendum

### 1. Where this code applies

The Covenant applies whenever someone is acting on behalf of opendbc-ag or interacting in a project space. Project spaces include:

- This GitHub repository — issues, pull requests, discussions, code review comments, commit messages, releases, the wiki.
- Any communication channel the project later adopts (e.g. a chat room or mailing list) when this code is referenced there.
- Public statements made under the project's name (e.g. a maintainer speaking as the project at a conference).

It does **not** govern unrelated personal speech in private spaces, or behavior in other communities, except where that behavior creates a direct, demonstrable risk for participants in this project.

### 2. How to report

To report a concern under the Covenant, email **`ctyoung.agent@gmail.com`**.

You can include as much or as little detail as you choose. Reporters may use a pseudonymous email; reports will be read by the maintainer named below. We will acknowledge receipt within seven days.

**Maintainer responsible for enforcement:** `ctyoungb`

### 3. Conflict of interest (best-effort, single-maintainer project)

This is a single-maintainer project. If a report concerns the maintainer themself, or someone the maintainer has a close personal or professional tie to, the maintainer will recuse from the decision and ask an external reviewer to handle the report. A standing external reviewer-of-record has not yet been named; if a conflict situation arises before one is, the maintainer will publicly name a reviewer at decision time and document the choice. This is an acknowledged gap of the current single-maintainer phase — expect this section to tighten as the project grows.

### 4. Appeals

A person subject to an enforcement action may request reconsideration once, in writing, within 30 days. The appeal will be reviewed by someone who was not the original decision-maker where that is possible (see §3 on the single-maintainer constraint); otherwise the original decision-maker will reconsider with reasons documented. Appeals do not pause the action while under review.

### 5. Reporter privacy

We retain only what is needed to act on a report and handle appeals, and purge it when no longer needed. We do not share reporter identity with the reported party without the reporter's explicit consent, except where required by law. Concretely: report email + thread is stored in the maintainer's personal mail archive (outside this repository); no retention SOP beyond that is published. If the project's report volume ever justifies a formal retention schedule, this section will be replaced with one.

### 6. AI-assisted contributions

You may use AI tools (LLM coding assistants, transcript tools, etc.) to help prepare contributions. Two expectations:

- **You are responsible for what you submit.** Review the output; do not paste in suggestions you have not read.
- **Disclose substantive AI assistance** in the pull request description — one line is enough. The PR template includes a checkbox for this. The disclosure protects reviewers' time and helps us catch hallucinated PGN/signal definitions, which is a real failure mode in this domain.

The load-bearing safeguard against hallucinated content is the source-citation requirement in `CONTRIBUTING.md` and the PR template, not this section. Treat the AI-disclosure rule as a norm-setting expectation; the citation check is what gates merge.

Bulk AI-generated drive-by PRs (no human review, no source citation, low-context) will be closed without merge.

### 7. Safety-relevant signal documentation

Some ag-CAN signals are safety-critical (brake, steering, hydraulic, PTO engagement, three-point hitch). When discussing or documenting these:

- Cite a public source. If your understanding of a safety-critical signal comes from observation of a specific machine rather than public spec, label it as observational and identify the machine class — do not present it as a general-purpose definition.
- If you believe a published signal definition in this repository is wrong in a way that could cause harm if followed, please **open an issue tagged `safety` and email the conduct contact** rather than only opening a PR. We want a record of the disclosure.

This is not a vulnerability-disclosure program — opendbc-ag does not produce binaries — but the same instinct applies: tell us about safety-relevant errors loudly and early.

### 8. Project scope versus legal scope

opendbc-ag exists to document **publicly-summarized** ag-CAN content. The project does not, and will not, host:

- Transcriptions of paywalled spec text (ISO, SAE).
- Reverse-engineered OEM proprietary CAN content (anything in the PGN ranges `0xEF00` / `0x1EF00` / `0xFF00..0xFFFF` / `0x1FF00..0x1FFFF`, or anything named `Proprietary*` / `Reserved*`).
- Material whose primary purpose is to circumvent a technological protection measure.

Contributors are responsible for the legality of their own actions on their own equipment under their own jurisdiction. This code of conduct does not grant any legal advice, indemnity, or §1201 exemption — see [`docs/legal-context.md`](legal-context.md) for the broader legal landscape.

Discussions of right-to-repair policy, OEM service practices, and the legal landscape (FTC v Deere, Iowa HF 2763, FARM Act, the §1201 repair exemption) are welcome in issues and discussions — they are part of why this project exists. Personal attacks on companies, employees, regulators, or contributors are not.

### 9. Off-topic content

The project's scope is technical. Off-topic posts (general politics, unrelated ideological argument, recruiting, promotion) will be redirected or closed. This is not a values statement; it is throughput management.

---

## License of this document

The upstream Contributor Covenant 2.1 is licensed under CC BY 4.0 by the Contributor Covenant project. This **project-specific addendum** is licensed under the same terms (CC BY 4.0) for ease of reuse.

## Changes

| Date | Change |
|---|---|
| 2026-05-13 | Initial adoption (v0.1.0-private). |
