#!/usr/bin/env python3
"""Uniform constant for every layout the #4174 constructor accepts.

C = 3 r_max / p is enough for the factored window term once G >= 256.
The constructor forces that floor. No layout census is run, and no new
kappa is claimed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-reservoir-uniform-constant"
ALLOCATOR = ROOT / "research/crt-reservoir-placement/allocator.py"

ABSORPTION = "r (2/B + β) < r (2 + 2^{1−62G}) 2^{−G} ≤ p 2^{−G} / 6400."
GUARD_LINE = "guard_digit_bits = 64 * (ell + logarithm)"


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
    allocator = ALLOCATOR.read_text(encoding="utf-8")
    need(ABSORPTION in proof, "printed 1/6400 absorption")
    need(GUARD_LINE in allocator, "constructor guard formula")
    need('ell >= logarithm' in allocator, "constructor logarithm floor")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def load_allocator():
    spec = importlib.util.spec_from_file_location("crt_reservoir_allocator", ALLOCATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def logarithm_floor(allocator) -> None:
    """Every integer p >= 1 has ceil(log2(p+2)) >= 2."""
    need((1).bit_length() == 1 and (2).bit_length() == 2, "bit length of 1 and 2")
    # If m >= 4 and m//2 <= 1, then m = 2*(m//2) + (m%2) <= 3.
    need(2 * 1 + 1 < 4, "no integer m >= 4 has m//2 <= 1")
    need(allocator.ceil_log2(3) == 2, "ceil(log2(3)) is 2")
    # p >= 1 ⇒ p+2 >= 3 ⇒ (p+1) >= 2. Descent reaches 2 or 3, both of bit length 2.
    need((3).bit_length() == 2, "bit length of 3")


def guard_floor() -> None:
    """ell >= log >= 2, so G = 64*(ell+log) >= 256."""
    log_min = 2
    ell_min = log_min
    need(64 * (ell_min + log_min) == 256, "minimum guard is 256")
    need(62 * 256 >= 2, "62G is at least 2 at the floor")
    # Exponent 1-62G <= -1, and 3-62G <= -1, so each tiny term is at most 1/2.
    need(1 - 62 * 256 <= -1 and 3 - 62 * 256 <= -1, "both window corrections are at most 1/2")


def sharp_unit(guard: int) -> int:
    return (1 << (1 + 63 * guard)) + (1 << (1 + guard)) - 4


def published_unit(guard: int) -> int:
    return (1 << (1 + 63 * guard)) + (1 << (3 + guard))


def fits(numerator: int, constant_num: int, constant_den: int, modulus: int, scale: int) -> bool:
    return numerator * constant_den <= constant_num * modulus * scale


def equality_witness(allocator) -> None:
    layout = allocator.Layout(1, 2, (1,) * 65536)
    need(layout.G == 256 and layout.r_max == 2 and layout.p == 1, "equality-case parameters")
    need(layout.L == 65536 and layout.L > layout.p, "equality-case address is longer than p")
    scale = 1 << (63 * layout.G)
    sharp = layout.r_max * sharp_unit(layout.G)
    published = layout.r_max * published_unit(layout.G)
    # C = 3 r_max / p = 6.
    need(3 * layout.r_max == 6 * layout.p, "equality-case constant is 6")
    need(fits(sharp, 6, 1, layout.p, scale), "C=6 holds on the sharp term")
    need(fits(published, 6, 1, layout.p, scale), "C=6 holds on the published term")
    need(not fits(sharp, 1, 1, layout.p, scale), "C=1 fails on the equality case")
    need(not fits(sharp, 1, 6400, layout.p, scale), "1/6400 fails on the equality case")


def old_constant_survives_when_address_is_short() -> None:
    """L <= p and G >= 256 give 3 r_max / p <= 3/25600 < 1/6400."""
    need(3 * 6400 < 25600, "3/25600 is strictly below 1/6400")
    need(3 * 5 * 25600 <= 9240576, "production plan still fits the tighter majorant")


def rejected(allocator) -> None:
    try:
        allocator.Layout(1, 1, (1,) * 65536)
    except ValueError:
        return
    raise SystemExit("FAIL: ell=1 was accepted")


def main() -> None:
    pins_and_phrases()
    allocator = load_allocator()
    logarithm_floor(allocator)
    guard_floor()
    equality_witness(allocator)
    old_constant_survives_when_address_is_short()
    rejected(allocator)
    print(
        "PASS_CRT_RESERVOIR_UNIFORM_CONSTANT "
        "G_min=256 equality_p=1 equality_r=2 integer_factor=3"
    )


if __name__ == "__main__":
    main()
