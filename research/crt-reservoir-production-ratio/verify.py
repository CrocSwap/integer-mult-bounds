#!/usr/bin/env python3
"""Production-plan envelope ratio against 1/6400.

The plan is the #4174 census layout. The comparison is one integer.
No schedule is replayed, and no new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-reservoir-production-ratio"
ALLOCATOR = ROOT / "research/crt-reservoir-placement/allocator.py"

ENVELOPE = "E(p, ell) ≤ C_E 2^{4 ell} (p+2)^{16}"
ROOM = "≤ 2^{−60 ell} (p+2)^{−48}"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    proof = (ROOT / "research/compact-switch-sharp-density/PROOF.md").read_text(encoding="utf-8")
    need(ENVELOPE in proof, "printed E envelope")
    need(ROOM in proof, "printed room line")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def load_allocator():
    spec = importlib.util.spec_from_file_location("crt_reservoir_allocator", ALLOCATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def production(allocator) -> None:
    widths = tuple(24 - (i % 2) for i in range(65536))
    length = sum(widths)
    layout = allocator.Layout(6 * length, 24, widths)
    need(layout.p == 9240576 and layout.L == 1540096 and layout.ell == 24, "production parameters")
    need(layout.G == 3072 and layout.r_max == 5 and layout.L <= layout.p, "production guard")
    logarithm = (layout.p + 1).bit_length()
    need(logarithm == 24, "ceil(log2(9240578)) is 24")
    need((1 << 23) < layout.p + 2 < (1 << 24), "p+2 lies strictly between 2^23 and 2^24")
    need(layout.G == 64 * (layout.ell + logarithm), "guard formula")
    base = layout.p + 2
    power = base ** 64
    denominator = 1 << (64 * logarithm)
    numerator = 15 * power
    need((1 << 1484) <= numerator < (1 << 1485), "ratio lies in [2^{-52}, 2^{-51})")
    need(numerator * 6400 < denominator, "ratio is strictly below 1/6400")
    allowance, remainder = divmod(denominator, numerator * 6400)
    need(allowance == 393602022308 and remainder > 0, "allowance over the ratio")
    room, room_remainder = divmod(denominator, numerator)
    need(room == 2519052942774845 and room_remainder > 0, "bare room over the ratio")


def power_edge(allocator) -> None:
    """Same ell, L <= p, and p+2 a power of two. The ratio keeps the factor 3 r_max."""
    modulus = (1 << 24) - 2
    layout = allocator.Layout(modulus, 24, (23,) * 65536)
    need(layout.p == 16777214 and layout.ell == 24 and layout.G == 3072, "edge parameters")
    need(layout.r_max == 4 and layout.L == 1507328 and layout.L <= layout.p, "edge length")
    need(layout.p + 2 == 1 << 24, "no envelope slack")
    need(3 * layout.r_max == 12, "edge ratio equals 12")
    need(12 * 6400 > 1, "edge ratio exceeds 1/6400")


def main() -> None:
    pins_and_phrases()
    allocator = load_allocator()
    production(allocator)
    power_edge(allocator)
    print(
        "PASS_CRT_RESERVOIR_PRODUCTION_RATIO "
        "log=24 ratio_bits=52 below_6400=1 edge_ratio=12"
    )


if __name__ == "__main__":
    main()
