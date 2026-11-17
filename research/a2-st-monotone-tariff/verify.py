#!/usr/bin/env python3
"""Exact finite corroboration of the new monotone two-letter tariff."""

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement, permutations, product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def optimum(demand, prices):
    need(type(demand) is int and 0 <= demand <= 32, "demand bound")
    need(2 <= len(prices) <= 33, "price capacity")
    need(prices[0] == 0, "zero price")
    need(all(isinstance(x, (int, Fraction)) for x in prices), "exact prices")
    need(all(a <= b for a, b in zip(prices, prices[1:])), "monotone price")
    costs = [Fraction(0)] * (demand + 1)
    words = [()] * (demand + 1)
    cap = len(prices) - 1
    for total in range(1, demand + 1):
        candidates = [(prices[k] + costs[total-k], (k,) + words[total-k])
                      for k in range(1, min(cap, total) + 1)]
        costs[total], words[total] = min(candidates)
    need(sum(words[demand]) == demand, "partition mass")
    return costs[demand], words[demand]


def partitions(demand, cap):
    """Independent count-vector oracle; no optimizer recurrence."""
    need(0 <= demand <= 8 and 1 <= cap <= 5, "oracle capacity")
    result = []
    ranges = [range(demand // k + 1) for k in range(1, cap + 1)]
    for counts in product(*ranges):
        if sum(k*c for k, c in enumerate(counts, 1)) == demand:
            result.append(tuple(k for k, c in enumerate(counts, 1)
                                for _ in range(c)))
    need(bool(result), "oracle has a partition")
    return result


def check_optimizer():
    cases = nonconcave = 0
    for cap in range(1, 6):
        for tail in combinations_with_replacement(range(4), cap):
            prices = (0,) + tail
            slopes = tuple(b-a for a, b in zip(prices, prices[1:]))
            for demand in range(9):
                value, _ = optimum(demand, prices)
                expected = min(sum(prices[k] for k in parts)
                               for parts in partitions(demand, cap))
                need(value == expected, "partition oracle disagreement")
                cases += 1
                nonconcave += int(any(a < b for a, b in zip(slopes, slopes[1:])))
    return {"partition_optima": cases, "nonconcave_optima": nonconcave}


def check_truncation():
    cases = 0
    for cap in range(1, 5):
        for count in range(1, 6):
            for ranks in combinations_with_replacement(range(1, cap+1), count):
                for demand in range(1, min(8, sum(ranks)) + 1):
                    remaining = demand
                    clipped = []
                    for rank in ranks:
                        kept = min(rank, remaining)
                        clipped.append(kept)
                        remaining -= kept
                    need(remaining == 0, "unfilled truncation")
                    need(sum(clipped) == demand, "wrong truncation mass")
                    for tail in combinations_with_replacement(range(3), cap):
                        prices = (0,) + tail
                        original = sum(prices[k] for k in ranks)
                        reduced = sum(prices[k] for k in clipped)
                        best, _ = optimum(demand, prices)
                        need(original >= reduced >= best, "truncation tariff")
                        cases += 1
    return cases


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def add(a, b, p, sign=1):
    rows = tuple(tuple(x + sign*y for x, y in zip(ar, br))
                 for ar, br in zip(a, b))
    return tuple(tuple(x % p if p else x for x in row) for row in rows)


def mm(a, b, p):
    n = len(a)
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(n)) % p
                       if p else sum(a[i][k]*b[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def rank(a, p):
    m = [[Fraction(x) if not p else x % p for x in row] for row in a]
    n = len(m)
    pivot = 0
    for col in range(n):
        choices = [i for i in range(pivot, n) if m[i][col]]
        if not choices:
            continue
        row = choices[0]
        m[pivot], m[row] = m[row], m[pivot]
        scale = pow(m[pivot][col], -1, p) if p else 1/m[pivot][col]
        m[pivot] = [(x*scale) % p if p else x*scale for x in m[pivot]]
        for i in range(pivot+1, n):
            scale = m[i][col]
            m[i] = [(x-scale*y) % p if p else x-scale*y
                    for x, y in zip(m[i], m[pivot])]
        pivot += 1
    return pivot


IDENTITY = (0, 1, 2)
S = (1, 0, 2)
T = (0, 2, 1)
GROUP = tuple(permutations(range(3)))


def compose(a, b):
    return tuple(a[b[i]] for i in range(3))


def formal_multiply(a, b, p):
    n = len(next(iter(a.values())))
    zero = tuple((0,) * n for _ in range(n))
    result = {}
    for g, x in a.items():
        for h, y in b.items():
            label = compose(g, h)
            result[label] = add(result.get(label, zero), mm(x, y, p), p)
    return {g: x for g, x in result.items() if x != zero}


def factor(label, coupling, p):
    return {IDENTITY: add(eye(len(coupling)), coupling, p, -1), label: coupling}


def construction(demand, left, right, p):
    need(1 <= demand <= 8, "formal fixture capacity")
    need(sum(left) == sum(right) == demand, "construction mass")
    n = demand + 1
    factors = []
    ranks = []
    for label, parts in ((S, left), (T, right)):
        start = 0
        for size in parts:
            coupling = tuple(tuple(int(i == j and start <= i < start+size)
                                   for j in range(n)) for i in range(n))
            factors.append(factor(label, coupling, p))
            ranks.append(size)
            start += size
    expected = {IDENTITY: tuple(tuple(int(i == j == demand) for j in range(n))
                                for i in range(n)),
                compose(S, T): tuple(tuple(int(i == j and i < demand)
                                          for j in range(n)) for i in range(n))}
    return factors, tuple(ranks), expected


def gauges(n, p):
    forward, backward = eye(n), eye(n)
    for i, j in ((0, n-1), (n-1, 0)):
        unit = tuple(tuple(int(r == i and c == j) for c in range(n))
                     for r in range(n))
        forward = mm(forward, add(eye(n), unit, p), p)
        backward = mm(add(eye(n), unit, p, -1), backward, p)
    need(mm(forward, backward, p) == eye(n), "gauge inverse")
    return forward, backward


def regular_apply(formal, vector, p):
    """Faithful action on labelled role vectors, separate from convolution."""
    n = len(vector[0])
    out = [[0]*n for _ in GROUP]
    for h_index, h in enumerate(GROUP):
        for g, matrix in formal.items():
            target = GROUP.index(compose(g, h))
            for i in range(n):
                out[target][i] += sum(matrix[i][j]*vector[h_index][j]
                                      for j in range(n))
    return tuple(tuple(x % p if p else x for x in row) for row in out)


def check_regular(factors, expected, p):
    n = len(next(iter(expected.values())))
    for g in range(6):
        for role in range(n):
            vector = tuple(tuple(int(i == g and j == role) for j in range(n))
                           for i in range(6))
            actual = vector
            for f in reversed(factors):
                actual = regular_apply(f, actual, p)
            need(actual == regular_apply(expected, vector, p), "regular endpoint")
    return 6*n


def check_constructions():
    fixtures = paid = columns = omissions = dirty_coupled = unequal_caps = 0
    missing_boundary_maps = 0
    for demand in range(1, 9):
        cap_pairs = [(cap, cap) for cap in range(1, min(5, demand+2)+1)]
        cap_pairs += [(2, 3), (4, 1)]
        for s_cap, t_cap in cap_pairs:
            s_prices = (0,) + tuple(3+k*k for k in range(1, s_cap+1))
            t_prices = tuple(Fraction(k, k+1) for k in range(t_cap+1))
            _, left = optimum(demand, s_prices)
            _, right = optimum(demand, t_prices)
            for p in (0, 2, 3, 5):
                factors, ranks, expected = construction(demand, left, right, p)
                forward, backward = gauges(demand+1, p)
                changed = [{g: mm(mm(backward, x, p), forward, p)
                            for g, x in f.items()} for f in factors]
                for f, wanted in zip(changed, ranks):
                    label = next(g for g in f if g != IDENTITY)
                    need(rank(f[label], p) == wanted, "conjugated paid rank")
                    dirty_coupled += int(any(f[label][demand]) or
                                         any(row[demand] for row in f[label]))
                full = [{IDENTITY: forward}] + changed + [{IDENTITY: backward}]
                actual = {IDENTITY: eye(demand+1)}
                for f in full:
                    actual = formal_multiply(actual, f, p)
                need(actual == expected, "full formal endpoint")
                missing_map = formal_multiply(actual, {IDENTITY: forward}, p)
                need(missing_map != expected, "missing exit map accepted")
                missing_boundary_maps += 1
                if demand <= 3:
                    columns += check_regular(full, expected, p)
                for skip in range(len(changed)):
                    mutant = {IDENTITY: eye(demand+1)}
                    for j, f in enumerate(full):
                        if j != skip+1:
                            mutant = formal_multiply(mutant, f, p)
                    need(mutant != expected, "omitted call accepted")
                    omissions += 1
                fixtures += 1
                unequal_caps += int(s_cap != t_cap)
                paid += len(changed)
    need(dirty_coupled > 0, "dirty coupling exercised")
    return {"formal_endpoints": fixtures, "paid_calls": paid,
            "regular_basis_columns": columns, "rejected_omissions": omissions,
            "dirty_coupled_calls": dirty_coupled, "unequal_cap_endpoints": unequal_caps,
            "rejected_missing_boundary_maps": missing_boundary_maps}


def check_example():
    s_prices = (0,) + tuple(3+k*k for k in range(1, 5))
    t_prices = tuple(Fraction(k, k+1) for k in range(5))
    s_cost, left = optimum(7, s_prices)
    t_cost, right = optimum(7, t_prices)
    need((s_cost, t_cost) == (25, Fraction(31, 20)), "example optimum")
    need(sorted(left) == [1, 2, 2, 2] and sorted(right) == [3, 4], "example lists")
    packed = s_prices[4]+s_prices[3]+t_prices[4]+t_prices[3]
    need(packed-s_cost-t_cost == 6, "example gain")
    return {"demand": 7, "cap": 4, "s_ranks": list(left), "t_ranks": list(right),
            "s_cost": str(s_cost), "t_cost": str(t_cost),
            "optimum": str(s_cost+t_cost), "packed_comparator": str(packed)}


def check_rejections():
    cases = ((-1, (0, 1)), (33, (0, 1)), (1, (0,)),
             (1, (1, 2)), (1, (0, -1)), (1, (0, 2, 1)), (1, (0, 1.0)))
    for demand, prices in cases:
        rejected = False
        try:
            optimum(demand, prices)
        except ValueError:
            rejected = True
        need(rejected, "invalid input accepted")
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true")
    args = parser.parse_args()
    result = {"status": "PASS_A2_ST_MONOTONE_TARIFF",
              "claim_type": "scoped written proof with finite corroboration",
              "optimizer": check_optimizer(), "truncation_cases": check_truncation(),
              "constructions": check_constructions(), "example": check_example(),
              "input_rejections": check_rejections()}
    package = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["sha256"] = {name: sha256((package/name).read_bytes()).hexdigest()
                        for name in files}
    if args.emit_receipt:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        frozen = json.loads((package/"RESULT.json").read_text())
        need(result == frozen, "receipt disagreement")
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
