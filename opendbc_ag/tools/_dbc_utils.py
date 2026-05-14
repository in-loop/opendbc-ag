"""Shared DBC-loading helpers.

Centralizes the `list(formats.loadp(...).values())[0]` idiom (which appears
in 5+ places). canmatrix can return a multi-bus dict; for our single-bus
DBCs we want explicit-fail semantics instead of silently grabbing the first
bus, which would hide a real corpus problem.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from canmatrix.canmatrix import CanMatrix


def first_matrix(path: str | Path) -> "CanMatrix":
    """Load `path` and return its sole CanMatrix.

    Raises ValueError if the file resolves to zero or more than one bus —
    those are real corpus problems we don't want to paper over.
    """
    from canmatrix import formats

    matrices = formats.loadp(str(path))
    if not matrices:
        raise ValueError(f"{path}: canmatrix returned no matrices")
    if len(matrices) > 1:
        raise ValueError(
            f"{path}: expected single bus, got {len(matrices)} ({list(matrices)!r})"
        )
    return next(iter(matrices.values()))
