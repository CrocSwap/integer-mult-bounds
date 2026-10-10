#!/usr/bin/env python3
"""Exact necessary-cost screens for a conditional exponent saving of 1/100.

These are upper bounds for explicitly specified interfaces, not achieved
suppliers or a lower bound for integer multiplication. Standard library only.
Prepared for huxint with OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
GRID = 10**24
TARGET = Q(1, 100)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def down(x):
    return Q(x.numerator * GRID // x.denominator, GRID)


def atanh_log(x, terms=40):
    """Rational enclosure, with an explicit geometric tail, for 1<=x<=2."""
    need(Q(1) <= x <= Q(2), "Log series outside its range")
    z = (x - 1) / (x + 1)
    power = z
    total = Q(0)
    for j in range(terms):
        total += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return total, total + tail


@lru_cache(None)
def log_interval(x):
    x = Q(x)
    need(x >= 1, "Only positive-rank child ratios at least one are supported")
    power = 0
    while x >= 2:
        x /= 2
        power += 1
    lo2, hi2 = atanh_log(Q(2))
    lo, hi = atanh_log(x)
    lo += power * lo2
    hi += power * hi2
    return down(lo), Q(-((-hi.numerator * GRID) // hi.denominator), GRID)


def cost_floor(m, histogram):
    need(all(0 < int(r) < m and int(n) > 0 for r, n in histogram.items()),
         "Data children must have positive multiplicities and widths below m")
    return sum((Q(int(n) * int(r)) * log_interval(Q(m, int(r)))[0]
                for r, n in histogram.items()), Q(0))


def uplift_floor(m, histogram, saving):
    """Lower bound on sum n*r*((m/r)^saving-1), using 12 positive terms."""
    result = Q(0)
    for r, n in histogram.items():
        x = saving * log_interval(Q(m, int(r)))[0]
        term = Q(1)
        uplift = Q(0)
        for j in range(1, 13):
            term = term * x / j
            uplift += term
        result += int(n) * int(r) * uplift
    return down(result)


def data_histogram(source, target, v):
    result = Counter()
    for hist in (source, target):
        for r, n in hist.items():
            if int(r) and int(n):
                result[int(r)] += 3 * int(n)
    result[2] += 2 * v
    return result


def checkpoint(name):
    x = json.loads((HERE / "inputs" / (name + ".json")).read_text())
    p = x["profile"]
    m, h, v = p["m"], p["h"], p["v"]
    delta, loss = p["deficit"], p["loss"]
    children = {int(r): n for r, n in p["child_histogram"].items() if int(r)}
    need(m == 3 * h, "Pinned three-block architecture")
    need(delta == 2 * v - 3 * loss, "Pinned deficit identity")
    need(sum(r * n for r, n in children.items()) == p["rank"], "Full rank recount")
    need(m * p["W"] - p["rank"] == delta, "Full stock/deficit recount")
    for key in ("source_data_histogram", "target_data_histogram"):
        need(sum(int(r) * n for r, n in p[key].items()) == v * (h - 1),
             "Complete local data itinerary")
    data = data_histogram(p["source_data_histogram"], p["target_data_histogram"], v)
    need(all(children.get(r, 0) >= n for r, n in data.items()), "Data is an actual submultiset")
    lower = cost_floor(m, data)
    full_cost = cost_floor(m, children)
    paid_at_target = uplift_floor(m, data, TARGET)
    # kappa < a/(1+a) for the retained balanced assembly, so this slightly
    # stronger saving is necessary even with its strict backoffs removed.
    assembly_required_saving = TARGET / (1 - TARGET)
    paid_at_assembly_target = uplift_floor(m, data, assembly_required_saving)
    need(Q(2 * v) / lower < Q(9, 1000), "Even free centers stay below 0.009")
    need(paid_at_target > 2 * v, "The fixed data alone rejects a=0.01")
    return {
        "name": name, "provenance": x["provenance"], "h": h, "m": m, "v": v,
        "retained_loss": loss, "retained_deficit": delta,
        "data_histogram": dict(sorted(data.items())),
        "data_entropy_floor": str(lower), "data_entropy_floor_per_port": str(lower / v),
        "full_entropy_floor": str(full_cost),
        "retained_loss_a_ceiling": str(Q(delta) / lower),
        "free_center_a_ceiling": str(Q(2 * v) / lower),
        "fixed_data_required_deficit_at_a_001_lower": str(paid_at_target),
        "fixed_data_required_deficit_per_port_at_a_001_lower": str(paid_at_target / v),
        "assembly_required_saving": str(assembly_required_saving),
        "fixed_data_required_deficit_at_assembly_target_lower": str(paid_at_assembly_target),
        "available_deficit_even_with_free_centers": 2 * v,
        "scope": "The pinned data itinerary and deficit identity; all auxiliary entropy is discarded. Free-center relaxation assumes only D<=2v.",
    }


def odd_cube_ledger(p, degree):
    need(degree >= 3 and degree % 2 == 1 and p >= degree + 1, "Odd-cube family domain")
    t = (degree - 1) // 2
    h, m = 2 * p, 6 * p
    v = 2**degree * comb(p, degree)
    loss = 2**t * comb(p, t) * (h - 2 * t)
    delta = 2 * v - 3 * loss
    # Histograms normalized per port. Repeated widths must accumulate.
    source = Counter([degree - 1, h - degree - 1, 1])
    target = Counter([h - degree - 1] + [1] * degree)
    data = data_histogram(source, target, 1)
    need(sum(r * n for r, n in data.items()) == 6 * (h - 1) + 4, "Data rank identity")
    need(max(data) < h, "All data child logarithms exceed log(3)")
    lower = cost_floor(m, data)
    relaxed = cost_floor(m, {h - 1: 6, 2: 2})
    return {"p": p, "degree": degree, "h": h, "m": m, "v": v,
            "loss": loss, "deficit": delta, "data_histogram_per_port": dict(sorted(data.items())),
            "data_entropy_floor_per_port": str(lower),
            "a_ceiling": str(Q(delta, v) / lower) if delta > 0 else None,
            "arbitrary_local_chains_entropy_floor_per_port": str(relaxed),
            "arbitrary_local_chains_a_ceiling": str(Q(delta, v) / relaxed) if delta > 0 else None}


def binary_rank(vectors):
    pivots = {}
    for x in vectors:
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    return len(pivots)


def b_value(intersection, degree):
    result = Q(1)
    for j in range(1, (degree - 1) // 2 + 1):
        result *= Q(intersection - (2 * j - 1), degree - (2 * j - 1))
    return result


def local_identity(degree):
    """Independent integer checks of the cube kernel, not a global circuit."""
    size = 1 << degree
    denominator = size // 2
    first = []
    for mask in range(size):
        value = b_value(degree - mask.bit_count(), degree) * denominator
        need(value.denominator == 1, "Local kernel is dyadic")
        first.append(int(value))
    eigenvalues = []
    for character in range(size):
        eig = sum((-1 if (character & x).bit_count() % 2 else 1) * first[x]
                  for x in range(size))
        expected = 2 * denominator if character.bit_count() <= (degree - 1) // 2 else 0
        need(eig == expected, "Walsh projector identity")
        eigenvalues.append(eig)
    k = [-b for b in first]
    k[0] += denominator
    for shift in range(size):
        need(sum(k[x] * k[x ^ shift] for x in range(size)) ==
             (denominator**2 if shift == 0 else 0), "Exact K squared")
        need(not k[shift] or shift.bit_count() % 2 == 1, "K only joins opposite parities")
    addresses = [sum(1 << (2 * j + ((mask >> j) & 1)) for j in range(degree))
                 for mask in range(size)]
    parity_classes = [[addresses[x] for x in range(size) if x.bit_count() % 2 == p]
                      for p in (0, 1)]
    need(all(binary_rank(xs) == degree for xs in parity_classes), "Parity source frame")
    need(all((a & b).bit_count() % 2 == 0 for a in parity_classes[0] for b in parity_classes[1]),
         "Source/target orthogonality")
    return {"degree": degree, "ports_per_cube": size, "B_rank": size // 2,
            "K_squared_identity": True, "opposite_parity_source_rank": degree,
            "denominator": denominator, "kernel_numerators": first}


def star_check(p, degree):
    t = (degree - 1) // 2
    fixed = tuple(2 * i for i in range(t))
    vectors = []
    for pairs in combinations(range(t, p), degree - t):
        for bits in product((0, 1), repeat=degree - t):
            vectors.append(sum(1 << i for i in fixed) +
                           sum(1 << (2 * i + b) for i, b in zip(pairs, bits)))
    observed = binary_rank(vectors)
    need(observed == 2 * p - 2 * t, "Copied t-star span")
    return {"p": p, "degree": degree, "fixed_coordinates": list(fixed),
            "source_count": len(vectors), "rank": observed}


def family_screen():
    rows = [odd_cube_ledger(p, d) for p in range(4, 30) for d in range(3, p, 2)]
    positive = [r for r in rows if r["a_ceiling"] is not None]
    best = max(positive, key=lambda r: Q(r["a_ceiling"]))
    best_relaxed = max(positive, key=lambda r: Q(r["arbitrary_local_chains_a_ceiling"]))
    claimed_ceiling = Q(5164, 10**6)
    relaxed_ceiling = Q(8094, 10**6)
    need(Q(best["a_ceiling"]) < claimed_ceiling, "Finite family ceiling")
    need(Q(best_relaxed["arbitrary_local_chains_a_ceiling"]) < relaxed_ceiling,
         "Arbitrary local data chain ceiling")
    # For p>=30, D/v<=2 and each r<m/3 imply
    # C_data/v > (12p-2)*ln(3). This bound decreases with p.
    tail = Q(2) / ((12 * 30 - 2) * log_interval(Q(3))[0])
    need(tail < Q(best["a_ceiling"]), "Infinite tail below finite maximum")
    return {"finite_cases": len(rows), "positive_deficit_cases": len(positive),
            "finite_scan_sha256": sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
            "best_optimistic_case": best,
            "best_arbitrary_local_chains_case": best_relaxed,
            "tail_from_p": 30, "all_degrees_tail_a_ceiling": str(tail),
            "strict_global_a_ceiling": str(claimed_ceiling),
            "strict_arbitrary_local_chains_a_ceiling": str(relaxed_ceiling),
            "scope": "Odd d>=3, p>=d+1; copied t-star centers and m=6p. The 0.005164 bound keeps the destructive-parity source/target flag. The 0.008094 bound permits any local source/target chains of endpoint distance h-1 with each jump at most h. Both discard all auxiliary entropy. No global side circuit is claimed.",
            "local_identity_checks": [local_identity(d) for d in (3, 5, 7)],
            "star_span_checks": [star_check(p, d) for p, d in ((4, 3), (7, 3), (6, 5), (9, 5), (8, 7))]}


def small_network_budget():
    result = []
    log3_lo, log3_hi = log_interval(Q(3))
    for stock in (30, 31):
        lo, hi = log_interval(Q(3 * stock, 3 * stock - 1))
        lower, upper = lo / log3_hi, hi / log3_lo
        if stock == 30:
            need(lower > Q(1, 99), "Thirty-role one-deficit budget")
        else:
            need(upper < Q(1, 99), "Thirty-one-role adverse budget control")
        result.append({"m": 3, "W": stock, "rank_deficit": 1,
                       "uniform_bit_saving_lower": str(lower),
                       "uniform_bit_saving_upper": str(upper),
                       "exceeds_assembly_requirement": stock == 30})
    return {"necessary_ordinary_saving_for_kappa_001": "1/99", "cases": result,
            "scope": "Conditional search budget for the raw uniform bit recurrence, assuming a complete all-role rational-frame certificate exists. No such circuit or complex companion is supplied."}


def certificate():
    need(not sys.flags.optimize, "Run the exact audit without -O")
    return {"status": "SCOPED ARCHITECTURE CEILINGS; NO NEW KAPPA", "target_kappa": str(TARGET),
            "checkpoints": [checkpoint("complex-pr193"), checkpoint("bit-pr187")],
            "odd_cube_extension": family_screen(),
            "small_network_target": small_network_budget()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = certificate()
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    frozen = HERE / "ceiling-certificate.json"
    if args.write:
        frozen.write_text(output)
    else:
        need(frozen.read_text() == output, "Exact ceiling certificate changed")
    for row in result["checkpoints"]:
        print(f"PASS {row['name']}: even free centers a < {float(Q(row['free_center_a_ceiling'])):.12f}")
    print("PASS the specified odd-cube family: a < 0.005164; target 0.01 excluded within this family")
    print("PASS even arbitrary local data chains: a < 0.008094 with the same copied centers and three-block architecture")


if __name__ == "__main__":
    main()
