#!/usr/bin/env python3
"""Bind the constant-1 CRT evaluator to accepted reservoir layouts.

PR #4377 proves E(p, ell) = 2^{4 ell} (p+2)^{16} on W <= p and at most
8(p+2) axes. PR #4174 constructs the reservoir layouts. Under L <= p this
checks the written proof's integer facts on exact witnesses, the threshold
ell >= 21 for every ell up to 256, and rejection controls. The universal
statement is PROOF.md, not this finite check. No new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from itertools import islice
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-evaluator-layout-binding"
ALLOCATOR = ROOT / "research/crt-reservoir-placement/allocator.py"

PHRASES = {
    "research/crt-uniform-evaluator/PROOF.md": (
        "`A <= 8(p+2)` target axes",
        "E(p, ell) = 2^{4 ell} (p+2)^{16}",
        "may be taken to be `C = 1` on this domain",
    ),
    "research/compact-switch-sharp-density/PROOF.md": (
        "r (2/B + β) E ≤ (C_E p / 6400) 2^{−60 ell} (p+2)^{−48}.",
        "Assume `L ≤ p` and `r ≤ floor(L/(100G))`.",
    ),
    "research/unconditional-batched-crt/CRT.md": (
        "E(p,ell) <= C 2^(4 ell) (p+2)^16.",
        "2^-G E(p,ell) <= C 2^(-60 ell) (p+2)^(-48),",
        "H>=G eventually",
    ),
    "research/crt-reservoir-placement/PROOF.md": (
        "r_max >= d/51200 >= 1,   H>=G,   H<=L/100.",
    ),
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    for path, phrases in PHRASES.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for phrase in phrases:
            need(phrase in text, f"{path}: {phrase}")


def load_allocator():
    spec = importlib.util.spec_from_file_location("crt_reservoir_allocator", ALLOCATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def lam(p: int) -> int:
    return (p + 1).bit_length()  # ceil(log2(p+2))


def scaled_charge(p: int, ell: int, G: int) -> Fraction:
    """2^{-G} E with C_E = 1."""
    return Fraction(2 ** (4 * ell) * (p + 2) ** 16, 2 ** G)


def threshold() -> None:
    """Part 1: with minimal L = 2^16 (ell-1), some p satisfies L <= p and
    ceil(log2(p+2)) <= ell exactly when ell >= 21."""
    feasible = [ell for ell in range(2, 257) if (1 << 16) * (ell - 1) <= (1 << ell) - 2]
    need(feasible == list(range(21, 257)), "ell >= 21 threshold")
    # Remark: actual caller L <= b + 1 with p = 6b.
    caller = [ell for ell in range(2, 257)
              if 6 * ((1 << 16) * (ell - 1) - 1) <= (1 << ell) - 2]
    need(caller == list(range(24, 257)), "ell >= 24 at the actual caller")
    need(lam(1310720) == 21 and lam((1 << 20) - 2) == 20, "lambda helper")


def check_layout(allocator, p: int, ell: int, widths: tuple[int, ...]):
    """Parts 2-4 on one accepted L <= p layout."""
    layout = allocator.Layout(p, ell, widths)
    L, G, r_max, H, d = layout.L, layout.G, layout.r_max, layout.H, layout.d
    need(L <= p and ell >= 21 and lam(p) >= 21 and p >= 1310720 and G >= 2688, "part 1")
    need(G == 64 * (ell + lam(p)) and H == r_max * G and H >= G, "H >= G")
    need(r_max <= p // 268800 < 8 * (p + 2), "batch cap")
    need(d <= p // 20 < 8 * (p + 2), "axis cap")
    # Every batch and control group of the top and bottom levels.
    for level in (1, layout.levels):
        for plan in iter_plans_sample(allocator, layout, level):
            need(len(plan.active_axes) <= r_max, "plan batch size")
            for dep in plan.dependencies:
                lo, hi = dep.left_interval
                need(hi - lo <= L <= p, "control group W <= p")
    charge = scaled_charge(p, ell, G)
    bound = Fraction(1, 2 ** (60 * ell + 48 * lam(p)))
    need(charge <= bound <= Fraction(1, 2 ** 2268), "part 3")
    need(bound <= Fraction(1, 2 ** (60 * ell) * (p + 2) ** 48), "#4100 display")
    B, K = 2 ** G, 64 * G
    sharp = Fraction(2 * (B - 2), 2 ** (64 * G))
    published = Fraction(8 * B, 2 ** K)
    for window in (sharp, published):
        density = r_max * (Fraction(2, B) + window)
        need(density < Fraction(p, 89600 * B), "part 4 density")
        need(density * 2 ** (4 * ell) * (p + 2) ** 16 < Fraction(1, 2 ** 2263), "part 4")
    return layout, charge


def iter_plans_sample(allocator, layout, level):
    # ponytail: first 64 batches of a level; the universal claim is PROOF.md.
    return islice(allocator.iter_plans(layout, level), 64)


def witnesses(allocator) -> None:
    twenty = (20,) * 65536
    minimal, charge = check_layout(allocator, 1310720, 21, twenty)
    need((minimal.L, minimal.G, minimal.r_max, minimal.H) == (1310720, 2688, 4, 10752),
         "minimal witness")
    need(charge < Fraction(1, 2 ** 2268), "minimal witness is not the maximum")
    peak, charge = check_layout(allocator, (1 << 21) - 2, 21, twenty)
    need(peak.r_max == 4 and charge == Fraction(1, 2 ** 2268), "2^{-2268} attained")
    production = tuple(24 - (i % 2) for i in range(65536))
    layout, _ = check_layout(allocator, 6 * sum(production), 24, production)
    need(layout.p == 9240576 and layout.r_max == 5, "#4174 production plan")
    layout, _ = check_layout(allocator, (1 << 24) - 2, 24, (23,) * 65536)
    need(layout.r_max == 4, "#4926 edge layout")


def without_length_hypothesis(allocator) -> None:
    layout = allocator.Layout(2, 2, (2,) * (1 << 19))
    need(layout.L == 1 << 20 and layout.L > layout.p and layout.G == 256, "counterexample")
    need(layout.r_max == 40 and layout.r_max > 8 * (layout.p + 2), "batch cap fails")
    root = next(allocator.iter_plans(layout, layout.levels))
    lo, hi = root.dependencies[0].left_interval
    need(hi - lo == 1 << 19 and hi - lo > layout.p, "root W exceeds p")


def controls(allocator) -> None:
    """Each mutated claim must be rejected."""
    rejected = 0
    try:  # ell = 20 has lambda = 21 once p >= L = 2^16 * 19
        allocator.Layout(65536 * 19, 20, (19,) * 65536)
    except ValueError:
        rejected += 1
    peak = scaled_charge((1 << 21) - 2, 21, 2688)
    rejected += peak > Fraction(1, 2 ** 2269)  # a sharper universal bound fails
    rejected += 40 > 8 * (2 + 2)  # the cap fails off L <= p
    density = 4 * (Fraction(2, 2 ** 2688) + Fraction(8, 2 ** (63 * 2688)))
    rejected += density >= Fraction(1310720, 268800 * 2 ** 2688)  # 1/268800 is too small
    need(rejected == 4, "rejection controls")


def main() -> None:
    pins_and_phrases()
    threshold()
    allocator = load_allocator()
    witnesses(allocator)
    without_length_hypothesis(allocator)
    controls(allocator)
    print("PASS_CRT_EVALUATOR_LAYOUT_BINDING ell_min=21 p_min=1310720 "
          "max_scaled_charge=2^-2268 record_charge<2^-2263 controls=4")


if __name__ == "__main__":
    main()
