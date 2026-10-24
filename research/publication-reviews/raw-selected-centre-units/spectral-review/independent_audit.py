#!/usr/bin/env python3
"""Check the spectral margins and controls without a source checker import."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path


def need(condition, label):
    if not condition:
        raise ValueError(label)


def log_interval(value):
    x = Q(value)
    need(x >= 1, "The review only uses logarithms at least one")
    exponent = 0
    while x > 2:
        x /= 2
        exponent += 1
    z = (x-1)/(x+1)
    low = sum((2*z**n/n for n in range(1, 192, 2)), Q(0))
    high = low + 2*z**193/(193*(1-z*z))
    if exponent:
        a, b = log_interval(2)
        low, high = low+exponent*a, high+exponent*b
    return low, high


def bounds(v, edges):
    trace, moment = 4*v, 16*v+8*edges
    discriminant = 7*(8*moment-trace*trace)
    root_floor = isqrt(discriminant*256**2)
    root_up = root_floor + int(root_floor**2 < discriminant*256**2)
    cap = min(Q(2*v+2), Q(16+7*v, 4), Q(trace, 8)+Q(root_up, 2048))
    need(0 < cap < 44, "Positive-definite range")
    a = int(trace//cap)
    b = trace-a*cap
    crude = (44-cap)**a*(44-b)*44**(7-a)
    upper = (Q(44)-Q(v, 2))**8
    lo44, hi44 = log_interval(44)
    lo_ratio, hi_ratio = log_interval(44/(44-cap))
    low = 8*lo44-Q(trace, 44)-Q(moment)/cap**2*(hi_ratio-cap/44)
    high = 8*hi44-Q(trace, 44)-Q(moment)/cap**2*(lo_ratio-cap/44)
    return cap, crude, upper, low, high, discriminant, root_floor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--annex", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    need(not args.out.exists(), "Output file must be new")
    lanes = args.annex / "frozen/work/centre-encoding-campaign-20261014/lanes"
    raw = (lanes/"circuit-interface/INTERFACE.json").read_bytes()
    need(sha256(raw).hexdigest() == "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3", "Interface pin")
    r = [[int(row.get(str(j), 0)) for j in range(112)] for row in json.loads(raw)["R"]]
    columns = list(zip(*r))
    need(all(sum(x*x for x in col) == 4 for col in columns), "Every actual column norm")
    dots = Counter(sum(x*y for x, y in zip(a, b))
                   for i, a in enumerate(columns) for b in columns[:i])
    need(dots == {0: 3304, 2: 1960, -2: 952}, "All actual root pairs")
    receipt = json.loads((lanes/"schur-selection/SPECTRAL-BOUND.json").read_bytes())
    lo2, hi2 = log_interval(2)
    profiles = []
    critical_margin = None
    for row in receipt["rows"]:
        v = row["selected_size"]-16
        edges = min(v*(v-1)//2, 7*v*v//16)
        if v >= 15:
            edges = min(edges, 93*v*(v-1)//210)
        cap, crude, upper, lower, _, discriminant, root_floor = bounds(v, edges)
        lower_power = max(e for e in range(60) if lower > e*hi2 or crude > 2**e)
        upper_power = min(e for e in range(60) if upper < 2**e)
        possible = list(range(lower_power+1, upper_power))
        need(str(cap) == row["largest_eigenvalue_bound"], "Rational eigenvalue cap")
        need(possible == row["remaining_power_exponents"], "Exponent profile")
        need([lower_power, upper_power] == [row["strict_lower_power"], row["strict_upper_power"]], "Strict bounds")
        profiles.append({"size": v+16, "strict_powers": [lower_power, upper_power], "possible": possible})
        if v == 15:
            critical_margin = lower-41*hi2
            need(critical_margin > Q(1, 1250), "Exact size-31 margin")
            need(root_floor**2 < discriminant*256**2, "Rounding the critical square root down is invalid")
    need(len(profiles) == 16, "All saved size profiles")
    need([row["size"] for row in profiles if not row["possible"]] == [24, 25, 26, 28, 29, 30, 31], "Exact exclusion set")
    need(profiles[3]["size"] == 27 and profiles[3]["possible"] == [42], "Size 27 is not excluded")

    # The weaker clique bound cannot certify the critical logarithmic gap.
    weak_edges = 7*15*15//16
    _, _, _, _, weak_high, _, _ = bounds(15, weak_edges)
    weak_margin_upper = weak_high-41*lo2
    need(weak_edges == 98 and weak_margin_upper < 0, "The 93-edge lemma is needed for this certificate")

    # The residual case h=2,z=2 permits seven possible omitted-index edges.
    epsilon = [1, 1, 0, 0, 0, 0, 0]
    possible_edges = sum(bool({1-2*x-1, 1-2*x+1} & {-2, 2}) for x in epsilon)
    t, h = 6, 2
    need(possible_edges == 7 and h+min(t, possible_edges) > 7,
         "A constant-seven degree bound is invalid for the permitted residual case")
    need(h+min(t, possible_edges) <= max(7, t+2), "The stated degree bound covers the case")
    result = {
        "status": "PASS_INDEPENDENT_FIXED_BASELINE_SPECTRAL_AUDIT",
        "method": "Direct 96-term rational logarithm intervals and actual matrix products; no source checker imports",
        "interface_sha256": sha256(raw).hexdigest(),
        "root_pairs": sum(dots.values()),
        "pair_products": dict(sorted(dots.items())),
        "profiles": profiles,
        "critical_size31_margin_strictly_above": "1/1250",
        "critical_size31_margin_lower": str(critical_margin),
        "weak_98_edge_margin_upper": str(weak_margin_upper),
        "negative_controls": ["The permitted h=2,z=2 residual case defeats a constant-seven degree bound",
                              "The weaker 98-edge bound fails the size-31 logarithmic certificate",
                              "Downward square-root rounding is invalid at the critical size",
                              "Size27 still permits determinant exponent42"],
        "scope": "Fixed A,T and retained selected source baselines; necessary determinant conditions only",
        "not_claimed": ["Existence at size27", "A global selected-set minimum", "Native cost or kappa improvement"],
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(result["status"])


if __name__ == "__main__":
    main()
