# Legal context

This document summarizes the legal and regulatory landscape that motivates opendbc-ag's existence and shapes its scope policy. It is **for context only**: it is not legal advice, it does not grant any indemnity or exemption, and it does not authorize any specific action against any specific manufacturer or piece of equipment. Decisions about what to do with your own equipment under your own jurisdiction are yours alone.

If you need legal advice for a specific situation, talk to an attorney.

---

## Why this project exists in this form

Three things are simultaneously true in ag equipment as of 2026:

1. **Public standards exist** for ag-CAN communication — primarily ISO 11783 (ISOBUS) and SAE J1939. The actual standard documents are paywalled, but their PGN ranges, frame structures, and many signal definitions are publicly summarized in vendor documentation, open-source projects (AgIsoStack++, AgOpenGPS, CMU ISOBlue), academic papers, vendor advertising, and ISO/SAE summary pages.
2. **OEM proprietary use of CAN** sits on top of those public standards. Equipment manufacturers use the proprietary PGN ranges (`0xEF00` peer-to-peer and `0xFF00..0xFFFF` proprietary B) for vendor-defined signals — diagnostic codes, telemetry, parameter settings, software-version handshakes. The exact contents are vendor business secrets and are generally not documented publicly.
3. **A repair-rights legal movement is in progress** — at the federal level (FTC actions, FARM Act bills), state level (Iowa HF 2763 and analogues), and international (EU Right to Repair Directive). These efforts vary widely in scope and enforcement; the legal status of independent CAN-bus reverse-engineering on owned equipment is jurisdiction-dependent and still evolving.

opendbc-ag's response is to be very strict about what it documents: **standard PGNs from public sources only.** This keeps the project clearly on the legitimate side of every plausible legal regime, regardless of how the repair-rights debate resolves.

---

## Selected reference points

The items below are public-record landmarks contributors might want to know about. Inclusion here is descriptive, not endorsement of any party's position.

### FTC v. Deere & Co. (Federal Trade Commission)

In January 2025, the U.S. Federal Trade Commission and the attorneys general of Illinois and Minnesota filed suit against Deere alleging anti-competitive conduct around repair tools and parts. Case status is publicly trackable on the FTC's case-record portal.

What it means for this project: a federal regulator is actively examining the dealer-network/repair model that motivates much of the right-to-repair conversation. We are not party to the case.

### FARM Act (federal, S.3068 / introduced 2023; reintroduced)

The **Fair Repair of Agricultural Equipment Act** is a federal bill that would require manufacturers of ag equipment to provide independent service providers and equipment owners with diagnostic and repair information on fair, reasonable, and non-discriminatory terms. Versions have been introduced in multiple Congresses; status varies by session.

What it means for this project: the FARM Act, if enacted, would alter the practical environment for repair-information access — but the bill addresses *manufacturer disclosure obligations*, not the legal status of independent reverse engineering. opendbc-ag's scope (public standards only) is unaffected either way.

### Iowa HF 2763 (state)

Iowa House File 2763, introduced in 2024, is a state-level right-to-repair bill targeting agricultural equipment specifically (relevant given Iowa's role as a major ag-equipment market). Status has shifted between sessions; consult Iowa's legislative tracker for current status.

What it means for this project: state laws can create local protections for repair-related activity but do not preempt federal law (e.g. §1201 of the DMCA — see below).

### DMCA §1201 and the Librarian of Congress's exemption process

17 U.S.C. §1201 prohibits circumvention of "technological protection measures" that control access to copyrighted works. Every three years, the U.S. Copyright Office runs an exemption rulemaking; the **2021 cycle** granted a tractor-software exemption for "diagnosis, maintenance, or repair of agricultural vehicles." The exemption was renewed in the **2024 cycle** and expanded in some respects. It does **not** authorize copyright infringement or circumvention for purposes other than repair, and it is rule-bound (lawful access to the device, no derivative works, etc.).

What it means for this project: opendbc-ag does not produce circumvention tools, does not ship binaries, and documents only public-standard content. Discussion of §1201 in this project is informational. Operators capturing CAN traffic on their own machines for documenting **standard** PGNs are operating in a different legal posture than operators reverse-engineering encrypted firmware — we only address the former here.

### Tractor Hacking (the community)

[tractorhacking.github.io](https://tractorhacking.github.io/) is a long-running community wiki documenting independent work on ag-equipment CAN systems. It includes substantive discussion of §1201, EULAs, and the legal landscape from the practitioner's side. opendbc-ag is not affiliated with the Tractor Hacking project; we cite it as a reference point.

---

## Why opendbc-ag is pure-standard only

Given the above, the project's content policy is:

- **In scope:** PGNs in standard ISO 11783 / J1939 ranges, sourced from publicly-available summaries.
- **Out of scope (CI-enforced):** PGNs in the proprietary ranges `0xEF00` (peer-to-peer) and `0xFF00..0xFFFF` (proprietary B).
- **Out of scope (policy):** transcribed paywalled-spec text, reverse-engineered OEM proprietary frame definitions, material whose primary purpose is circumvention.

This policy is not a moral statement about other projects' choices. It is a scope-management decision: a clean, narrow, defensible scope is easier to maintain, easier to attract contributors to, easier to recommend to other projects as a dependency, and easier for the maintainer to keep running over years rather than abandoning when the legal risk math changes.

---

## Disclaimer of legal advice

The content above is summary information for orientation. It is not legal advice and creates no attorney-client relationship. Statutes, regulations, and case law change. Conditions vary by jurisdiction. If you are planning to do something whose legality is unclear to you, talk to a lawyer who knows your jurisdiction and your specific facts.

---

## Changes

| Date | Change |
|---|---|
| 2026-05-13 | Initial draft (v0.1.0-private). |
