# Legal context

This document summarizes the legal and regulatory landscape relevant to opendbc-ag's scope policy. It is **for context only**: it is not legal advice, it does not grant any indemnity or exemption, and it does not authorize any specific action against any specific manufacturer or piece of equipment. Decisions about what to do with your own equipment under your own jurisdiction are yours alone.

If you need legal advice for a specific situation, talk to an attorney.

---

## Standards, proprietary use, and the repair-rights landscape

Three things are simultaneously true in ag equipment as of 2026:

1. **Public standards exist** for ag-CAN communication — primarily ISO 11783 (ISOBUS) and SAE J1939. The actual standard documents are paywalled, but their PGN ranges, frame structures, and many signal definitions are publicly summarized in vendor documentation, open-source projects (AgIsoStack++, AgOpenGPS, CMU ISOBlue), academic papers, vendor advertising, and ISO/SAE summary pages.
2. **OEM proprietary use of CAN** sits on top of those public standards. Equipment manufacturers use the proprietary PGN ranges (`0xEF00` peer-to-peer and `0xFF00..0xFFFF` proprietary B) for vendor-defined signals — diagnostic codes, telemetry, parameter settings, software-version handshakes. The exact contents are vendor business secrets and are generally not documented publicly.
3. **A repair-rights legal movement is in progress** — at the federal level (FTC actions, FARM Act bills), state level (Iowa HF 2763 and analogues), and international (EU Right to Repair Directive). These efforts vary widely in scope and enforcement; the legal status of independent CAN-bus reverse-engineering on owned equipment is jurisdiction-dependent and still evolving.

opendbc-ag documents **standard PGNs from public sources only.**

---

## Selected reference points

The items below are public-record landmarks contributors might want to know about. Inclusion here is descriptive, not endorsement of any party's position.

### FTC v. Deere & Co. (Federal Trade Commission)

In January 2025, the U.S. Federal Trade Commission and the attorneys general of Illinois and Minnesota filed suit against Deere alleging anti-competitive conduct around repair tools and parts. Case status is publicly trackable on the FTC's case-record portal.

Relevance to scope: opendbc-ag is not a party to the case; its public-standards scope is unaffected by the outcome.

### FARM Act (federal, S.3068 / introduced 2023; reintroduced)

The **Fair Repair of Agricultural Equipment Act** is a federal bill that would require manufacturers of ag equipment to provide independent service providers and equipment owners with diagnostic and repair information on fair, reasonable, and non-discriminatory terms. Versions have been introduced in multiple Congresses; status varies by session.

Relevance to scope: the FARM Act addresses *manufacturer disclosure obligations*, not the legal status of independent reverse engineering. opendbc-ag's scope (public standards only) is unaffected either way.

### Iowa HF 2763 (state)

Iowa House File 2763, introduced in 2024, is a state-level right-to-repair bill targeting agricultural equipment specifically (relevant given Iowa's role as a major ag-equipment market). Status has shifted between sessions; consult Iowa's legislative tracker for current status.

Relevance to scope: state laws can create local protections for repair-related activity but do not preempt federal law (e.g. §1201 of the DMCA — see below).

### DMCA §1201 and the Librarian of Congress's exemption process

17 U.S.C. §1201 prohibits circumvention of "technological protection measures" that control access to copyrighted works. Every three years, the U.S. Copyright Office runs an exemption rulemaking; the **2021 cycle** granted a tractor-software exemption for "diagnosis, maintenance, or repair of agricultural vehicles." The exemption was renewed in the **2024 cycle** and expanded in some respects. It does **not** authorize copyright infringement or circumvention for purposes other than repair, and it is rule-bound (lawful access to the device, no derivative works, etc.).

Relevance to scope: opendbc-ag does not produce circumvention tools, does not ship binaries, and documents only public-standard content. Discussion of §1201 here is informational. Capturing CAN traffic on owned equipment to document **standard** PGNs is a different legal posture than reverse-engineering encrypted firmware; opendbc-ag addresses only the former.

### Tractor Hacking (the community)

[tractorhacking.github.io](https://tractorhacking.github.io/) is a long-running community wiki documenting independent work on ag-equipment CAN systems. It includes substantive discussion of §1201, EULAs, and the legal landscape from the practitioner's side. opendbc-ag is not affiliated with the Tractor Hacking project; it is listed here as a reference point.

---

## Scope policy

The project's content policy:

- **In scope:** PGNs in standard ISO 11783 / J1939 ranges, sourced from publicly-available summaries.
- **Out of scope (CI-enforced):** PGNs in the proprietary ranges `0xEF00` (peer-to-peer) and `0xFF00..0xFFFF` (proprietary B).
- **Out of scope (policy):** transcribed paywalled-spec text, reverse-engineered OEM proprietary frame definitions, material whose primary purpose is circumvention.

---

## Disclaimer of legal advice

The content above is summary information for orientation. It is not legal advice and creates no attorney-client relationship. Statutes, regulations, and case law change. Conditions vary by jurisdiction. If you are planning to do something whose legality is unclear to you, talk to a lawyer who knows your jurisdiction and your specific facts.

---

## Changes

| Date | Change |
|---|---|
| 2026-05-13 | Initial draft (v0.1.0-private). |
| 2026-06-16 | Neutralized register (justification → reference); legal facts and disclaimers unchanged. |
| 2026-06-18 | Removed residual defensive/justification lines (scope unambiguity claim, policy-rationale paragraph); legal facts and disclaimers unchanged. |
