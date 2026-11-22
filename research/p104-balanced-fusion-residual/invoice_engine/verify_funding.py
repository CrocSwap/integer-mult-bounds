"""Reprice the two sufficient P104 invoices at the paper's exact target.

Run with CPython 3.12: python3.12 -IB verify_funding.py
The independent moment bounds below use rational log and exponential series.
The pinned reference encloses powers by successive integer square roots.
"""
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import importlib.util
import json


ROOT = Path(__file__).resolve().parent
PIN = ROOT / "pinned"
GRID = 1 << 160


def load_reference():
    path = PIN / "price_audit.py"
    expected = "ca650d573f605bf51a8806a772903b6775cd036dfbfe7f043eccd3e51bc9977b"
    assert sha256(path.read_bytes()).hexdigest() == expected
    spec = importlib.util.spec_from_file_location("p104_reference_price", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def down(x):
    return Q((x * GRID).__floor__(), GRID)


def up(x):
    return Q((x * GRID).__ceil__(), GRID)


@lru_cache(None)
def log_series(u):
    # log(u) = 2 atanh(z), with the omitted denominators at least 2N+1.
    z = (u - 1) / (u + 1)
    assert 0 <= z <= Q(1, 3)
    n = 64
    part = 2 * sum(z ** (2*j+1) / (2*j+1) for j in range(n))
    tail = 2 * z ** (2*n+1) / ((2*n+1) * (1-z*z))
    return down(part), up(part+tail)


def exp_series(u):
    # Terms after degree n have successive ratio at most u/(n+2).
    assert 0 <= u <= Q(1, 2)
    n = 42
    term = total = Q(1)
    for j in range(1, n+1):
        term *= u/j
        total += term
    tail = term*u/(n+1)/(1-u/(n+2))
    return down(total), up(total+tail)


@lru_cache(None)
def power(r, exponent):
    assert r >= 1 and exponent >= 0
    if r == 1 or exponent == 0:
        return Q(1), Q(1)
    h = r.bit_length()-1
    l2, u2 = log_series(Q(2))
    lm, um = log_series(Q(r, 1 << h))
    lo = down((h*l2+lm)*exponent/16)
    hi = up((h*u2+um)*exponent/16)
    elo, _ = exp_series(lo)
    _, ehi = exp_series(hi)
    return down(elo**16), up(ehi**16)


def moment(hist, exponent):
    lo = hi = Q(0)
    for r, count in hist.items():
        a, b = power(r, exponent)
        lo += count*a
        hi += count*b
    return lo, hi


def surplus(target, paid, c, v, z, w, weight, keep):
    t = 1-c
    tl, th = moment(target, t)
    pl, ph = moment(paid, t)
    gl, gh = moment(paid, t+z)
    ol, oh = moment(target, t-w)
    cl, ch = power(12, z)
    kl, kh = power(keep, w)
    lo = 1-(ph/tl)**v-weight*(gh/(tl*cl))**v-(oh*kh/tl)**v
    hi = 1-(pl/th)**v-weight*(gl/(th*ch))**v-(ol*kl/th)**v
    return lo, hi


def difference(target, paid, k):
    tl, th = moment(target, 1-k)
    pl, ph = moment(paid, 1-k)
    return tl-ph, th-pl


def agree(interval, reference):
    assert max(interval[0], reference[0]) <= min(interval[1], reference[1])


def main():
    ref = load_reference()
    k, c, g = Q(194523, 50000000), Q(70084296829703, 2**54), Q(1, 10**17)
    assert k == ref.K and g == ref.G
    target, base = ref.load_inputs()
    cases = {"baseline": (0, 0), "24 fusions": (24, 0), "25 fusions": (25, 0),
             "one net rank-one deletion": (0, 1), "36 net rank-one deletions": (0, 36)}
    report = {}
    for label, (fusions, deletions) in cases.items():
        paid = base.copy()
        paid[1] -= 2*fusions+deletions
        paid[2] += fusions
        assert min(paid.values()) > 0
        assert sum(paid.values()) == 104904-fusions-deletions
        first_moment = sum(r*n for r, n in paid.items())
        assert first_moment == 285600-deletions
        raw = difference(target, paid, k)
        split = surplus(target, paid, c, 268, ref.Z, ref.W, ref.WEIGHT, 15)
        agree(raw, ref.raw_difference(target, paid, k))
        agree(split, ref.powered_surplus(target, paid, c, 268, ref.Z, ref.W, ref.WEIGHT, 15))
        if deletions or fusions == 25:
            assert raw[0] > 0 and split[0] > Q(2, 2**50)
            ref.power_and_enumeration_checks(268, 2**50, c, sum(paid.values()))
        else:
            assert raw[1] < 0 and split[1] < 0
        report[label] = {"paid_count": sum(paid.values()), "paid_rank_sum": first_moment,
                         "raw": ref.enclosing_text(*raw, 18),
                         "split_268": ref.enclosing_text(*split, 18)}
    shortenings = {}
    for r in sorted(base):
        if r == 1:
            continue
        paid = base.copy()
        paid[r] -= 1
        paid[r-1] += 1
        assert sum(paid.values()) == 104904 and sum(q*n for q,n in paid.items()) == 285599
        raw = difference(target, paid, k)
        split = surplus(target, paid, c, 268, ref.Z, ref.W, ref.WEIGHT, 15)
        agree(raw, ref.raw_difference(target, paid, k))
        agree(split, ref.powered_surplus(target, paid, c, 268, ref.Z, ref.W, ref.WEIGHT, 15))
        assert raw[0] > Q(84,100) and split[0] > Q(79,100000)
        shortenings[str(r)] = {"raw": ref.enclosing_text(*raw,18),
                               "split_268": ref.enclosing_text(*split,18)}
    ref.power_and_enumeration_checks(268, 2**50, c, 104904)
    assert len(shortenings) == 13
    report["single rank shortenings"] = shortenings
    pos = surplus(ref.POS_TARGET, ref.POS_PAID, ref.POS_C, 128, Q(19,64), Q(23,64), Q(2), 16)
    agree(pos, ref.powered_surplus(ref.POS_TARGET, ref.POS_PAID, ref.POS_C, 128,
                                   Q(19,64), Q(23,64), Q(2), 16))
    assert pos[0] > Q(2, 2**15)
    assert ref.bit_debit(268, 2**50, c) == 21 and ref.positive_debit() == 10
    levels = ref.stage_prices(c, 21)
    cap = ref.POS_C-Q(10, 1600000)
    strict, functional, positive_gap = ref.signed_margins(k, g, ref.ORDINARY, cap)
    assert len(strict) == 54 and len(functional) == 4
    assert min(*strict, *functional, positive_gap) == Q(1, 10**18)
    assert min(ref.signed_margins(k, 0, ref.ORDINARY, cap)[0]) == 0
    assert min(ref.signed_margins(k, g, k+4*g, cap)[0]) == 0
    assert ref.signed_margins(k, g, ref.ORDINARY, k+5*g)[2] == 0
    report["shared application"] = {
        "positive_split_128": ref.enclosing_text(*pos, 18), "positive_cap": str(cap),
        "ordinary_gate_margin": str(ref.ORDINARY-k-4*g), "positive_gate_margin": str(positive_gap),
        "last_stage_headroom": str(levels[-1][2]-ref.ORDINARY),
        "stage_rates": [str(level[3]) for level in levels],
        "minimum_signed_gate_margin": str(min(*strict,*functional,positive_gap)),
        "strict_gates": len(strict), "functional_gates": len(functional),
        "kappa_target": str(k), "status": "conditional prices; physical word required"}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
