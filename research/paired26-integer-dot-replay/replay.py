#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the frozen paired26 primary replay with exact integer dot products.

Produced by Nick Petalas. The loaded verifier and its result retain Andrey
Mas's and the predecessor authors' credit. Only ``dot`` is replaced.
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from fractions import Fraction
from math import lcm
from pathlib import Path
from types import ModuleType
from typing import Callable, Sequence

SOURCE_DIRECTORY = Path("research/complex-paired26-completion")
SOURCE_HASHES = {
    "verify.py": "34f20844f5184a66f2217b481c0cc82ed6a9eb85e97d3ec53eec36b641d2b07d",
    "certificate.json": "18103be5548d9558dfc49cc90bc9308aab13e48e7f99d30a45fd90cec7c2776d",
}
MAX_INPUT_BYTES = 1 << 20
MAX_CACHE_ROWS = 1024
Scalar = int | Fraction


@dataclass(frozen=True)
class IntegerRow:
    owner: Sequence[Scalar]
    snapshot: tuple[Scalar, ...]
    numerators: tuple[int, ...]
    denominator: int
    fractional: bool


class IntegerDot:
    """Cache immutable scalar identities, never a dot-product result."""

    def __init__(self, original: Callable):
        self.original = original
        self.rows: dict[int, IntegerRow] = {}
        self.calls = 0
        self.hits = 0
        self.misses = 0
        self.clears = 0
        self.fallbacks = 0

    def row(self, values: Sequence[Scalar]) -> IntegerRow | None:
        saved = self.rows.get(id(values))
        if (saved is not None and saved.owner is values
                and all(x is y for x, y in zip(values, saved.snapshot))):
            self.hits += 1
            return saved
        if any(type(x) not in (int, Fraction) for x in values):
            return None
        denominator = lcm(*(x.denominator for x in values))
        numerators = tuple(x.numerator * (denominator // x.denominator)
                           for x in values)
        saved = IntegerRow(values, tuple(values), numerators, denominator,
                           any(type(x) is Fraction for x in values))
        if len(self.rows) == MAX_CACHE_ROWS:
            self.rows.clear()
            self.clears += 1
        self.rows[id(values)] = saved
        self.misses += 1
        return saved

    def __call__(self, a: Sequence[Scalar], b: Sequence[Scalar]) -> Scalar:
        self.calls += 1
        if len(a) != 8 or len(b) != 8:
            self.fallbacks += 1
            return self.original(a, b)
        left, right = self.row(a), self.row(b)
        if left is None or right is None:
            self.fallbacks += 1
            return self.original(a, b)
        numerator = sum(x * y for x, y in zip(left.numerators, right.numerators))
        if left.fractional or right.fractional:
            return Fraction(numerator, left.denominator * right.denominator)
        return numerator


def checked_bytes(directory: Path, filename: str, expected: str) -> bytes:
    path = directory / filename
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("source size limit: " + filename)
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("source hash mismatch: " + filename)
    return raw


def load_source(directory: Path | None = None) -> ModuleType:
    if directory is None:
        directory = Path(__file__).resolve().parents[2] / SOURCE_DIRECTORY
    raw = {name: checked_bytes(directory, name, digest)
           for name, digest in SOURCE_HASHES.items()}
    module = ModuleType("paired26_frozen_primary")
    module.__file__ = str(directory / "verify.py")
    # Execute the bytes just authenticated, without importing any cached pyc.
    exec(compile(raw["verify.py"], module.__file__, "exec"), module.__dict__)
    return module


def main() -> int:
    if len(sys.argv) != 1:
        raise ValueError("accelerated replay accepts no arguments")
    module = load_source()
    module.dot = IntegerDot(module.dot)
    return module.main([])


if __name__ == "__main__":
    raise SystemExit(main())
