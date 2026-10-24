#!/usr/bin/env python3
"""Width threshold of the ordinary interchange's recursive branch.

BIT.md section 4 runs the elementary digit-swap algorithm whenever
2k >= e or the body width is below 64. This verifier computes that test
exactly, finds the q-ary and binary width thresholds, and compares them
with the #4174 reservoir width H = r_max G. No new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-interchange-width-threshold"
BIT = ROOT / "research/unconditional-batched-crt/BIT.md"
CRT = ROOT / "research/unconditional-batched-crt/CRT.md"
ALLOCATOR = ROOT / "research/crt-reservoir-placement/allocator.py"

Q = (1 << 89) - 1
C = Fraction(8667, 5000000)
A2 = C * (1 - C * C)
LAST_ELEMENTARY = 311308
BINARY_THRESHOLD = 27706412

BIT_PHRASES = (
    "q=2^89-1,",
    "c=8667/5000000,",
    "K(w)=269241600 N q^(4096(w-1)),",
    "D(n)=0 (n<64),  D(n)=1+D(42 floor(n/64)) (n>=64).",
    "At a root choose w=ceil(e^c), and retain that w at every descendant.",
    "On original radix width e compute stock=K(w)^D(e) and the least k with",
    "q^k>=stock before removing borrowed digits. If 2k>=e or the body width is",
    "failures occur at only finitely many widths. Otherwise write e=k+nw+ell",
    "Finally embed each 2^e binary field into q^E, E=ceil(log_q(2^e)); each",
)
CRT_PHRASES = (
    "G=64(ell+ceil(log2(p+2))),  B=2^G,  K=64G,",
    "r_max=floor(L/(100G)),  H=r_max G.",
    "One color uses O(1) ordinary H-bit interchanges plus linear scans and paid",
    "repair. It costs O(V H^(1-a)+V). With K colors and H<=L=O(p), one switch",
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    bit = BIT.read_text(encoding="utf-8")
    for phrase in BIT_PHRASES:
        need(phrase in bit, "BIT.md phrase: " + phrase)
    crt = CRT.read_text(encoding="utf-8")
    for phrase in CRT_PHRASES:
        need(phrase in crt, "CRT.md phrase: " + phrase)
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def depth(n: int) -> int:
    count = 0
    while n >= 64:
        n = 42 * (n // 64)
        count += 1
    return count


def block_starts(limit: int) -> list[int]:
    """m[D] is the least n with depth(n) = D, for every block starting below limit."""
    starts = [0, 64]
    while starts[-1] < limit:
        starts.append(64 * -(-starts[-1] // 42))
    return starts


def stock_digits(max_depth: int) -> list[int]:
    """j[D] is the least j with q^j >= (269241600 N)^D, so k = 4096 D + j[D] at w=2."""
    group_order = 1
    for i in range(64):
        group_order *= Q**64 - Q**i
    base = 269241600 * group_order
    need(Q**4096 < base < Q**4097, "269241600 N lies strictly between q^4096 and q^4097")
    digits = []
    power = 1
    for d in range(max_depth + 1):
        guess = 4096 * d + (31475 * d + 99999) // 100000
        while Q ** (guess - 1) >= power:
            guess -= 1
        while Q**guess < power:
            guess += 1
        need(Q ** (guess - 1) < power <= Q**guess, f"exact stock digits at D={d}")
        digits.append(guess)
        power *= base
    for d in range(1, max_depth + 1):
        need(0 <= digits[d] - digits[d - 1] - 4096 <= 1, f"stock increment at D={d}")
    return digits


def elementary(width: int, digits: list[int]) -> bool:
    """BIT.md section 4 test at w = 2, valid for 2 <= width <= 2^576."""
    k = 4096 * depth(width) + digits[depth(width)]
    return 2 * k >= width or (width - k) // 2 < 64


def threshold(digits: list[int]) -> None:
    # w = ceil(E^c) = 2 exactly when 2 <= E <= 2^(1/c); 1/c > 576.
    need(Fraction(1) / C > 576, "w = 2 on 2 <= E <= 2^576")
    starts = block_starts(1 << 20)
    for d in range(1, len(starts) - 1):
        need(depth(starts[d]) == d and depth(starts[d] - 1) == d - 1, f"block {d} start")
    need(starts[19] <= LAST_ELEMENTARY < starts[20], "the boundary lies in the D=19 block")
    k19 = 4096 * 19 + digits[19]
    need(k19 == 155654 and 2 * k19 == LAST_ELEMENTARY, "2 k = 311308 at D = 19")
    # Exhaustive check below the boundary block's end, and the boundary itself.
    for width in range(2, starts[20]):
        need(elementary(width, digits) == (width <= LAST_ELEMENTARY), f"width {width}")
    # Larger blocks with w = 2. Since 269241600 N < q^4097, j[D] <= 4097 D and k <= 8193 D.
    starts = block_starts(1 << 577)
    for d in range(20, len(starts)):
        if starts[d] > 1 << 576:
            break
        bound = 8193 * d
        need(2 * bound < starts[d] and (starts[d] - bound) // 2 >= 64, f"block {d}")
    # The w >= 3 range E > 2^576: 2k < 2^(17 + c x + log2 x) < 2^(x-1) at x = 576.
    need(17 + C * 576 + 10 < 575, "w >= 3 range")


def binary_threshold() -> None:
    power = Q**LAST_ELEMENTARY
    need(power.bit_length() == BINARY_THRESHOLD, "binary width threshold")
    need(BINARY_THRESHOLD - 1 < 89 * LAST_ELEMENTARY, "consistent with log2 q < 89")


def q_width(bits: int) -> int:
    width = 0
    power = 1
    while power < 1 << bits:
        power *= Q
        width += 1
    return width


def load_allocator():
    spec = importlib.util.spec_from_file_location("crt_reservoir_allocator", ALLOCATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def layouts(allocator, digits: list[int]) -> None:
    production = allocator.Layout(9240576, 24, (24, 23) * 32768)
    need(production.L == 1540096 and production.r_max == 5, "production layout")
    need(production.H == 15360 and q_width(production.H) == 173, "production H")
    need(elementary(173, digits), "production interchange is elementary")
    floor = allocator.Layout(1310720, 21, (20,) * 65536)
    need(floor.L == 1310720 and floor.r_max == 4, "smallest L <= p layout")
    need(floor.H == 10752 and q_width(floor.H) == 121, "smallest L <= p H")
    need(elementary(121, digits), "smallest-layout interchange is elementary")
    # r_max = floor(L/(100G)) gives H <= L/100, so a recursive call needs L >= 100 e*.
    need(100 * production.H <= production.L and 100 * floor.H <= floor.L, "H <= L/100")
    need(100 * BINARY_THRESHOLD == 2770641200, "length needed for a recursive call")
    need(2770641200 // production.L == 1799, "ratio to the production length")


def absorption() -> None:
    # E < 2^19 on every elementary width, so E^a2 < 2^(19 a2) < 2^0.033.
    need(LAST_ELEMENTARY < 1 << 19, "elementary widths are below 2^19")
    need(19 * A2 < Fraction(33, 1000), "19 a2 < 0.033")


def main() -> None:
    pins_and_phrases()
    digits = stock_digits(20)
    threshold(digits)
    binary_threshold()
    layouts(load_allocator(), digits)
    absorption()
    print(
        "PASS_CRT_INTERCHANGE_WIDTH_THRESHOLD "
        f"last_elementary_q_width={LAST_ELEMENTARY} binary_threshold={BINARY_THRESHOLD} "
        "production_q_width=173"
    )


if __name__ == "__main__":
    main()
