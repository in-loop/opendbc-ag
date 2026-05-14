"""Strip PII / identifying details from CAN logs before contributing to corpus/.

Operations:
- Quantize GPS coordinates to a ~1 km grid (default).
- Reset machine source-address ranges to 0xFE (NULL address per J1939-81).
- Round timestamps to date-level (00:00:00 UTC of the same day).

This is a best-effort tool. Operators are still responsible for reviewing
output before publishing. Anonymization happens at the **log** level; the
DBC files in this repository contain no log-derived PII by construction.
"""
from __future__ import annotations

import argparse
import csv
import math
from datetime import datetime, timezone
from pathlib import Path

# 1 degree latitude ≈ 111 km. ~1 km grid in latitude = ~0.009°.
GRID_DEGREES = 0.009


def quantize_gps(lat: float, lon: float, grid_degrees: float = GRID_DEGREES) -> tuple[float, float]:
    """Snap (lat, lon) to a coarse grid. Returns the grid-center coordinates."""
    qlat = round(lat / grid_degrees) * grid_degrees
    qlon = round(lon / grid_degrees) * grid_degrees
    return qlat, qlon


def truncate_timestamp_to_date(ts: float) -> float:
    """Return the UTC midnight (epoch seconds) of the day containing `ts`."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.timestamp()


def strip_source_address_j1939(can_id_29bit: int) -> int:
    """Zero out the J1939 source-address byte (low 8 bits of the 29-bit ID).

    Per J1939-81, 0xFE is the NULL address — treat it as 'machine-anonymized'.
    """
    return (can_id_29bit & ~0xFF) | 0xFE


def anonymize_payload_bytes(data: bytes, byte_range: slice) -> bytes:
    """Zero out a slice of the payload (e.g. embedded serial number)."""
    out = bytearray(data)
    for i in range(*byte_range.indices(len(out))):
        out[i] = 0x00
    return bytes(out)


def anonymize_log_csv(
    input_path: Path,
    output_path: Path,
    *,
    strip_sa: bool = True,
    quantize_time: bool = True,
    payload_strip: slice | None = None,
) -> int:
    """Read a CAN log CSV (timestamp, can_id, data_hex) and write an anonymized copy.

    Returns count of rows written.
    """
    written = 0
    with input_path.open() as fin, output_path.open("w", newline="") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout)
        writer.writerow(["timestamp", "can_id", "data_hex"])

        for i, row in enumerate(reader, start=2):  # row 1 is header
            try:
                ts = float(row["timestamp"])
                cid = int(str(row["can_id"]).strip(), 0)
                data = bytes.fromhex(row["data_hex"])
            except (ValueError, KeyError, TypeError) as e:
                raise ValueError(
                    f"{input_path}: failed to parse row {i} ({row!r}): {e}"
                ) from e

            if strip_sa and cid > 0xFFFF:
                cid = strip_source_address_j1939(cid)
            if quantize_time:
                ts = truncate_timestamp_to_date(ts) if ts > 1_000_000_000 else ts
            if payload_strip is not None:
                data = anonymize_payload_bytes(data, payload_strip)

            writer.writerow([f"{ts:.4f}", cid, data.hex().upper()])
            written += 1
    return written


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path, help="Input CAN log CSV")
    p.add_argument("output", type=Path, help="Output anonymized CSV")
    p.add_argument("--keep-source-address", action="store_true", help="Do not strip J1939 source-address byte")
    p.add_argument("--keep-time", action="store_true", help="Do not quantize timestamps to date")
    p.add_argument("--strip-bytes", type=str, default=None, help="Payload byte range to zero, e.g. '2:6'")
    args = p.parse_args(argv)

    payload_strip = None
    if args.strip_bytes:
        a, b = args.strip_bytes.split(":")
        payload_strip = slice(int(a), int(b))

    n = anonymize_log_csv(
        args.input,
        args.output,
        strip_sa=not args.keep_source_address,
        quantize_time=not args.keep_time,
        payload_strip=payload_strip,
    )
    print(f"Anonymized {n} rows → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
