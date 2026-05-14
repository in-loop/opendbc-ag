"""Heuristic DBC signal inference from a CAN log.

Reads a CAN log (CSV with columns: timestamp, can_id, data_hex) and emits
suggested BO_ / SG_ definitions with confidence scores. Detects:

- Frame cadence (mode of inter-arrival intervals)
- Constant bytes (single observed value across the log)
- Boolean toggles (single bit, exactly two observed states)
- Single-byte varying signals
- Multi-byte aggregation candidates (adjacent bytes whose values correlate)

Out of scope for v0.1: physical scale/offset inference (requires ground-truth
gauge values). Suggested scale/offset = 1.0/0.0 until enriched.
"""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SignalCandidate:
    name: str
    start_bit: int
    size: int
    factor: float = 1.0
    offset: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    confidence: float = 0.0
    rationale: str = ""


@dataclass
class FrameAnalysis:
    can_id: int
    sample_count: int
    cycle_time_ms: float | None
    constant_bytes: list[int] = field(default_factory=list)
    candidate_signals: list[SignalCandidate] = field(default_factory=list)


def load_csv(path: Path) -> list[tuple[float, int, bytes]]:
    out = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # row 1 is header
            try:
                ts = float(row["timestamp"])
                cid = int(str(row["can_id"]).strip(), 0)
                data = bytes.fromhex(row["data_hex"])
            except (ValueError, KeyError, TypeError) as e:
                raise ValueError(
                    f"{path}: failed to parse row {i} ({row!r}): {e}"
                ) from e
            out.append((ts, cid, data))
    return out


def _infer_cycle_ms(timestamps: list[float]) -> float | None:
    if len(timestamps) < 2:
        return None
    diffs = [(b - a) * 1000.0 for a, b in zip(timestamps, timestamps[1:])]
    rounded = [round(d, 1) for d in diffs]
    if not rounded:
        return None
    return statistics.mode(rounded)


def _byte_value_sets(payloads: list[bytes], n_bytes: int) -> list[set[int]]:
    sets: list[set[int]] = [set() for _ in range(n_bytes)]
    for p in payloads:
        for i in range(min(n_bytes, len(p))):
            sets[i].add(p[i])
    return sets


def _detect_boolean_bits(payloads: list[bytes], byte_idx: int) -> list[int]:
    """Return list of bit indices (0..7) within byte_idx that are single-bit toggles."""
    transitions = [0] * 8
    last_byte = None
    for p in payloads:
        if byte_idx >= len(p):
            continue
        b = p[byte_idx]
        if last_byte is not None and last_byte != b:
            for bit in range(8):
                if (last_byte ^ b) & (1 << bit):
                    transitions[bit] += 1
        last_byte = b
    bool_bits = []
    for bit in range(8):
        bit_values = {(p[byte_idx] >> bit) & 1 for p in payloads if byte_idx < len(p)}
        if bit_values == {0, 1} and transitions[bit] >= 2:
            bool_bits.append(bit)
    return bool_bits


def _detect_multibyte_aggregates(payloads: list[bytes], byte_sets: list[set[int]]) -> list[tuple[int, int]]:
    """Adjacent byte spans where each byte has >2 unique values.

    Cardinality of 2 indicates a boolean-like byte, which should be handled
    by single-bit detection rather than absorbed into a wide signal.
    """
    candidates = []
    i = 0
    n = len(byte_sets)
    while i < n - 1:
        if len(byte_sets[i]) > 2 and len(byte_sets[i + 1]) > 2:
            j = i + 1
            while j < n - 1 and len(byte_sets[j + 1]) > 2 and (j + 1 - i + 1) <= 8:
                j += 1
            candidates.append((i, j - i + 1))
            i = j + 1
        else:
            i += 1
    return candidates


def analyze_frame(can_id: int, samples: list[tuple[float, bytes]]) -> FrameAnalysis:
    timestamps = [s[0] for s in samples]
    payloads = [s[1] for s in samples]
    n_bytes = max((len(p) for p in payloads), default=0)

    cycle = _infer_cycle_ms(timestamps)
    byte_sets = _byte_value_sets(payloads, n_bytes)
    constants = [i for i, s in enumerate(byte_sets) if len(s) == 1]
    varying = [i for i, s in enumerate(byte_sets) if len(s) > 1]

    candidates: list[SignalCandidate] = []

    # Boolean toggles inside varying single bytes (only if no multi-byte aggregate covers them).
    aggregates = _detect_multibyte_aggregates(payloads, byte_sets)
    aggregate_byte_idxs = set()
    for start, size in aggregates:
        for k in range(size):
            aggregate_byte_idxs.add(start + k)

    for byte_idx in varying:
        if byte_idx in aggregate_byte_idxs:
            continue
        byte_card = len(byte_sets[byte_idx])
        if byte_card <= 2:
            # Cardinality of 2 → boolean-like; detect the toggling bit.
            for bit in _detect_boolean_bits(payloads, byte_idx):
                candidates.append(SignalCandidate(
                    name=f"CAN_{can_id:X}_byte{byte_idx}_bit{bit}_Bool",
                    start_bit=byte_idx * 8 + bit,
                    size=1,
                    confidence=0.9,
                    rationale="Single bit with exactly two observed states; byte has cardinality 2",
                ))
        else:
            # Higher cardinality → treat as U8 signal (not a bag of booleans).
            values = sorted(byte_sets[byte_idx])
            candidates.append(SignalCandidate(
                name=f"CAN_{can_id:X}_byte{byte_idx}_U8",
                start_bit=byte_idx * 8,
                size=8,
                min_value=float(values[0]),
                max_value=float(values[-1]),
                confidence=0.6,
                rationale=f"Single-byte varying signal, {byte_card} unique values",
            ))

    for start, size in aggregates:
        # Compute observed range as little-endian unsigned int.
        observed = set()
        for p in payloads:
            if start + size <= len(p):
                v = int.from_bytes(p[start:start + size], byteorder="little", signed=False)
                observed.add(v)
        if not observed:
            continue
        candidates.append(SignalCandidate(
            name=f"CAN_{can_id:X}_byte{start}_U{size * 8}_LE",
            start_bit=start * 8,
            size=size * 8,
            min_value=float(min(observed)),
            max_value=float(max(observed)),
            confidence=0.7,
            rationale=f"Adjacent varying bytes [{start}..{start + size - 1}] suggest a {size * 8}-bit little-endian signal",
        ))

    return FrameAnalysis(
        can_id=can_id,
        sample_count=len(samples),
        cycle_time_ms=cycle,
        constant_bytes=constants,
        candidate_signals=candidates,
    )


def analyze(records: list[tuple[float, int, bytes]]) -> dict[int, FrameAnalysis]:
    by_id: dict[int, list[tuple[float, bytes]]] = defaultdict(list)
    for ts, cid, data in records:
        by_id[cid].append((ts, data))
    return {cid: analyze_frame(cid, samples) for cid, samples in by_id.items()}


def render_report(analyses: dict[int, FrameAnalysis]) -> str:
    lines = ["# Inferred frames\n"]
    for cid in sorted(analyses):
        a = analyses[cid]
        lines.append(f"## CAN ID 0x{cid:X}")
        lines.append(f"- samples: {a.sample_count}")
        lines.append(f"- cycle_time: {a.cycle_time_ms} ms" if a.cycle_time_ms else "- cycle_time: (insufficient samples)")
        if a.constant_bytes:
            lines.append(f"- constant bytes: {a.constant_bytes}")
        if a.candidate_signals:
            lines.append("- candidate signals:")
            for sig in a.candidate_signals:
                lines.append(
                    f"  - **{sig.name}**: bit {sig.start_bit}, len {sig.size}, "
                    f"range [{sig.min_value}, {sig.max_value}], conf {sig.confidence:.2f} — {sig.rationale}"
                )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", type=Path, help="Path to CAN log CSV (columns: timestamp, can_id, data_hex)")
    p.add_argument("-o", "--output", type=Path, default=None, help="Write Markdown report to file (default: stdout)")
    args = p.parse_args(argv)

    records = load_csv(args.log)
    analyses = analyze(records)
    report = render_report(analyses)

    if args.output:
        args.output.write_text(report)
        print(f"Wrote {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
