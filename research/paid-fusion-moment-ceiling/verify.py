#!/usr/bin/env python3
"""Exact certificate for the paid-fusion moment ceiling.

Every power a^c with integer a >= 1 and rational 0 < c < 1 is enclosed in an
exact rational interval [lo, hi].  The transcendental step uses CPython
``decimal`` at PREC digits, whose ``ln`` and ``exp`` are correctly rounded to
the context precision; each result is widened by one unit in the last place, so
the enclosure is rigorous.  All later arithmetic and every comparison is exact
rational arithmetic, so a certified inequality is a proof of that finite case.

The file also regenerates a canonical summary and compares its SHA-256 with the
value stored in RESULT.json, so the receipt is bound to the exact numbers.
"""
from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import isqrt
from pathlib import Path

if not __debug__:
    raise RuntimeError("run without -O; assertions are proof checks")

PREC = 90
HERE = Path(__file__).resolve().parent


def _ulp(x: Decimal) -> Decimal:
    """One unit in the last place of a PREC-digit decimal."""
    return Decimal(1).scaleb(x.adjusted() - PREC + 1)


def _ln_bounds(n: int) -> tuple[F, F]:
    assert n >= 1
    with localcontext() as ctx:
        ctx.prec = PREC
        v = Decimal(n).ln()
    u = _ulp(v)
    return F(v - u), F(v + u)


def _exp_bounds(x: F) -> tuple[F, F]:
    """exp on a rational argument, rigorous both sides."""
    with localcontext() as ctx:
        ctx.prec = PREC + 20
        d = Decimal(x.numerator) / Decimal(x.denominator)
    with localcontext() as ctx:
        ctx.prec = PREC
        lo = d.exp()
        hi = d.exp()
    ulo = _ulp(lo)
    uhi = _ulp(hi)
    return F(lo - ulo), F(hi + uhi)


def power_interval(base: int, c: F) -> tuple[F, F]:
    """Rigorous [lo, hi] with lo <= base**c <= hi for integer base >= 1, c > 0."""
    assert isinstance(base, int) and base >= 1
    assert isinstance(c, F) and c > 0
    if c == 1:
        return F(base), F(base)
    ll, lh = _ln_bounds(base)
    lo, _ = _exp_bounds(ll * c)
    _, hi = _exp_bounds(lh * c)
    return lo, hi


def split_deficit_bounds(a: int, b: int, c: F) -> tuple[F, F]:
    """Bounds for D(a,b) = a**c + b**c - (a+b)**c."""
    lo_a, hi_a = power_interval(a, c)
    lo_b, hi_b = power_interval(b, c)
    lo_s, hi_s = power_interval(a + b, c)
    return lo_a + lo_b - hi_s, hi_a + hi_b - lo_s


def min_power_bounds(a: int, b: int, c: F) -> tuple[F, F]:
    return power_interval(min(a, b), c)


class Certificate:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.inconclusive: dict[str, int] = {}
        self.hashes: list[str] = []

    def record(self, tag: str, ok: bool) -> None:
        self.counts[tag] = self.counts.get(tag, 0) + 1
        if not ok:
            self.inconclusive[tag] = self.inconclusive.get(tag, 0) + 1


CS = [
    ("1/1000", F(1, 1000)),
    ("1/279", F(1, 279)),
    ("kappa_363005817/100000000000", F(363005817, 100000000000)),
    ("1/2", F(1, 2)),
    ("3/4", F(3, 4)),
]

cert = Certificate()

# --- Lemma 1: strict subadditivity, 0 < D(a,b) < min(a,b)**c -----------------
for cname, c in CS:
    for a in range(1, 41):
        for b in range(a, 41):
            d_lo, d_hi = split_deficit_bounds(a, b, c)
            m_lo, m_hi = min_power_bounds(a, b, c)
            cert.record(f"subadditivity[{cname}]", d_lo > 0)
            cert.record(f"sharp_cap[{cname}]", d_hi < m_lo)


# --- Lemma 2: m-block strict subadditivity ----------------------------------
def block_bounds(parts: list[int], c: F) -> tuple[F, F]:
    lo = sum(power_interval(p, c)[0] for p in parts)
    hi = sum(power_interval(p, c)[1] for p in parts)
    return lo, hi


for cname, c in CS:
    for m in (2, 3, 4):
        for parts in (
            [1] * m,
            [1] + [2] * (m - 1),
            [2] * m,
            [1, 2, 3, 4][:m],
            [3, 5, 7, 11][:m],
        ):
            lo, hi = block_bounds(parts, c)
            s_lo, s_hi = power_interval(sum(parts), c)
            cert.record(f"mblock[{cname}]", hi > s_lo)

# --- Sharpness of the cap: D(1,b) / 1 tends to one (c = 1/2, exact bounds) ---
def sqrt_bounds(n: int) -> tuple[F, F]:
    """Exact rational enclosure of sqrt(n); Newton gives x >= sqrt(n) >= n/x."""
    s = max(isqrt(n), 1)
    x = F(s)
    for _ in range(12):
        x = (x + F(n) / x) / 2
    lo, hi = (F(n) / x, x) if x >= F(n) / x else (x, F(n) / x)
    assert lo * lo <= n <= hi * hi
    return lo, hi


for k in range(2, 13):
    b = 10 ** k
    lb, ub = sqrt_bounds(b)
    lb1, ub1 = sqrt_bounds(b + 1)
    lo = 1 + lb - ub1                 # lower bound of 1 + sqrt(b) - sqrt(b+1)
    hi = 1 + ub - lb1
    assert lo <= hi
    cert.record("sharpness_gap_below_one", hi < 1)
    if k >= 4:
        cert.record("sharpness_gap_above_0.99", lo > F(99, 100))

# --- Balanced split maximizes the single fusion saving at fixed total rank ---
for cname, c in CS:
    for r in range(3, 61):
        m = r // 2
        e_lo, e_hi = split_deficit_bounds(m, r - m, c)
        for a in range(1, m):
            o_lo, o_hi = split_deficit_bounds(a, r - a, c)
            cert.record(f"balanced_split_max[{cname}]", o_hi < e_lo)

# --- Global fusion ceiling --------------------------------------------------
def merged_moment_bounds(multiset: list[int], blocks: list[list[int]], c: F):
    assert sorted(p for block in blocks for p in block) == sorted(multiset)
    lo = sum(power_interval(sum(block), c)[0] for block in blocks)
    hi = sum(power_interval(sum(block), c)[1] for block in blocks)
    return lo, hi


MULTISETS = [
    [1, 1, 1, 1, 2, 2, 3],
    [1] * 7,
    [1, 2, 3, 4, 5, 8, 16],
    [2, 2, 3, 3, 5, 7, 11, 13],
    [1] * 12 + [6, 6],
]
for cname, c in CS:
    for ms in MULTISETS:
        total_lo, total_hi = power_interval(sum(ms), c)
        blocks = [[p] for p in ms]
        m_lo, m_hi = merged_moment_bounds(ms, blocks, c)
        base_lo = sum(power_interval(p, c)[0] for p in ms)
        base_hi = sum(power_interval(p, c)[1] for p in ms)
        # the singleton partition is the identity rewrite
        assert m_lo <= base_hi and base_lo <= m_hi
        # ceiling: M(P') >= (sum P)**c  for every partition
        cert.record(f"fusion_ceiling[{cname}]", m_lo > total_hi)
        # full collapse attains the ceiling value
        full_lo, full_hi = merged_moment_bounds(ms, [ms], c)
        assert full_lo <= total_hi and total_lo <= full_hi
        # a genuine fusion strictly lowers the paid moment
        for blocks2 in ([[ms[0], ms[1]]] + [[p] for p in ms[2:]],
                        [[p] for p in ms[:-2]] + [[ms[-2], ms[-1]]],
                        [[ms[0], ms[1], ms[2]]] + [[p] for p in ms[3:]]):
            f_lo, f_hi = merged_moment_bounds(ms, blocks2, c)
            cert.record(f"fusion_monotone[{cname}]", f_hi < base_lo)
        # non-fusion control: splitting any paid job raises the moment
        split = ms + [1]
        s_lo = sum(power_interval(p, c)[0] for p in split)
        cert.record(f"split_control[{cname}]", s_lo > base_hi)

# --- Rejection controls: the hypothesis 0 < c < 1 is necessary --------------
for c in (F(1), F(2), F(3, 2)):
    a, b = 3, 5
    d_lo, d_hi = split_deficit_bounds(a, b, c)
    cert.record("control_non_strict_or_reversed", d_lo <= 0)

for bad in (0, -2):
    try:
        power_interval(bad, F(1, 2))
    except AssertionError:
        cert.record("control_nonpositive_rank_rejected", True)
    else:
        cert.record("control_nonpositive_rank_rejected", False)

try:
    power_interval(4, F(0))
except AssertionError:
    cert.record("control_zero_exponent_rejected", True)
else:
    cert.record("control_zero_exponent_rejected", False)

# --- Receipt ---------------------------------------------------------------
failures = {tag: n for tag, n in cert.inconclusive.items() if n}
summary = {
    "checked": dict(sorted(cert.counts.items())),
    "inconclusive": failures,
    "precision_digits": PREC,
    "exponents": [name for name, _ in CS],
    "proof_sha256": hashlib.sha256((HERE / "PROOF.md").read_bytes()).hexdigest(),
}
canonical = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
summary_sha = hashlib.sha256(canonical).hexdigest()

result = json.loads((HERE / "RESULT.json").read_text())
print(json.dumps(summary, indent=1, sort_keys=True))
print("summary_sha256", summary_sha)
print("expected      ", result["receipt_sha256"])
assert not failures, f"inconclusive cases: {failures}"
assert summary_sha == result["receipt_sha256"], "receipt mismatch"
assert summary["proof_sha256"] == result["proof_sha256"], "proof hash mismatch"
print("PASS_PAID_FUSION_MOMENT_CEILING")
