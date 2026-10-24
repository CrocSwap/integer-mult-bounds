#!/usr/bin/env python3
"""Product of 6 * 2^{-256} with the printed E envelope.

The layout is the #4174 equality case p=1, ell=2, r_max=2, G=256.
The comparison is one rational. No census is run, and no new kappa is
claimed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-reservoir-envelope-product"
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


def ratio(modulus: int, guard_log: int, factor: int) -> tuple[int, int]:
    """factor * ((p+2) / 2^{log})^{64} as an unreduced integer pair."""
    base = modulus + 2
    return factor * base ** 64, 1 << (64 * guard_log)


def equality_case(allocator) -> None:
    layout = allocator.Layout(1, 2, (1,) * 65536)
    need(layout.p == 1 and layout.ell == 2 and layout.G == 256, "equality parameters")
    need(layout.r_max == 2 and layout.L == 65536, "equality batch and length")
    logarithm = (layout.p + 1).bit_length()
    need(logarithm == 2 and layout.G == 64 * (layout.ell + logarithm), "guard matches the formula")
    factor = 3 * layout.r_max
    need(factor == 6, "prefactor is 6")
    numerator, denominator = ratio(layout.p, logarithm, factor)
    need(numerator == 6 * 3 ** 64 and denominator == 1 << 128, "raw ratio")
    need(numerator // 2 == 3 ** 65 and denominator // 2 == 1 << 127, "reduced ratio 3^{65}/2^{127}")
    # 6 * 3^{16} / 2^{248} = 3^{17} / 2^{247}.
    need(6 * 3 ** 16 == 2 * 3 ** 17 and (1 << 248) == 2 * (1 << 247), "product is 3^{17}/2^{247}")
    room_den = (1 << (60 * layout.ell)) * 3 ** 48
    need(room_den == (1 << 120) * 3 ** 48, "room denominator")
    need(3 ** 17 * room_den < (1 << 247), "product is strictly below the room")
    need(1 << 103 <= 3 ** 65 < 1 << 104, "ratio lies between 2^{-24} and 2^{-23}")
    need(6400 * 3 ** 65 < 1 << 127, "ratio is strictly below 1/6400")
    quotient, remainder = divmod(1 << 127, 6400 * 3 ** 65)
    need(quotient == 2580 and remainder > 0, "room allowance over the product")


def power_of_two_control(allocator) -> None:
    """p+2 = 4 is a power of two, so the envelope slack is 1 and the factor 6 remains."""
    layout = allocator.Layout(2, 2, (1,) * 65536)
    need(layout.p == 2 and layout.ell == 2 and layout.G == 256 and layout.r_max == 2, "control layout")
    logarithm = (layout.p + 1).bit_length()
    need(logarithm == 2 and (1 << logarithm) == layout.p + 2, "no envelope slack")
    numerator, denominator = ratio(layout.p, logarithm, 3 * layout.r_max)
    need(numerator == 6 * denominator, "ratio equals 6")
    need(numerator > denominator, "product exceeds the room")


def main() -> None:
    pins_and_phrases()
    allocator = load_allocator()
    equality_case(allocator)
    power_of_two_control(allocator)
    print(
        "PASS_CRT_RESERVOIR_ENVELOPE_PRODUCT "
        "ratio=3^65/2^127 below_room=1 below_6400=1 control_ratio=6"
    )


if __name__ == "__main__":
    main()
