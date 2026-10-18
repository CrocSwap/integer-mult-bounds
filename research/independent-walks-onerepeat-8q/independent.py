#!/usr/bin/env python3
"""Independent one-repeat (2,6) dual census at Q=8.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from itertools import combinations, permutations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
INF = 99


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_table(slots):
    n = len(slots)
    even = [INF] * 32
    even[0] = 0
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        if size % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size < even[value]:
            even[value] = size
    return even


def dual_short(e_long, sigma):
    total = 0
    for m in range(1, 32):
        best = INF
        if e_long[m] < INF:
            best = e_long[m]
        if e_long[m ^ sigma] < INF:
            best = min(best, 2 + e_long[m ^ sigma])
        if best >= INF:
            return None
        total += best
    return total


def path_X(slots):
    closed = slots + (0,)
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        if delta == 0:
            return None
        total += 2 * (delta.bit_count() - 1)
    return total


def gf2_span(vals):
    basis = []
    for v in vals:
        x = v
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    span = {0}
    for b in basis:
        span |= {s ^ b for s in span}
    return frozenset(span), len(basis)


def gf2_rank(vals):
    return gf2_span(vals)[1]


def tariff(q, r, x):
    return 38 * q + 2 * r + 2 * x


def _work(dbls):
    valid = 0
    rank4 = 0
    rank_lt4 = 0
    covering = 0
    covering_rank_lt4 = 0
    hist = Counter()
    for dbl in dbls:
        for others in combinations([x for x in range(1, 32) if x != dbl], 3):
            labels = (dbl,) + others
            rank_labels = gf2_rank(labels)
            for perm in set(permutations((dbl, dbl) + others)):
                slots = (0,) + perm
                if path_X(slots) is None:
                    continue
                valid += 1
                if rank_labels != 4:
                    rank_lt4 += 1
                    e = even_table(slots)
                    for sigma in range(1, 32):
                        if dual_short(e, sigma) is not None:
                            covering_rank_lt4 += 1
                    continue
                rank4 += 1
                e = even_table(slots)
                span, rank = gf2_span(slots)
                if rank != 4:
                    fail("rank mismatch")
                even_sum = sum(e[v] for v in span if v)
                if even_sum != 40:
                    fail(f"Σe={even_sum}")
                for sigma in range(1, 32):
                    r = dual_short(e, sigma)
                    if sigma in span:
                        if r is not None:
                            fail("inside span covered")
                        continue
                    if r != 112:
                        fail(f"outside R={r}")
                    covering += 1
                    hist[112] += 1
    return valid, rank4, rank_lt4, covering, covering_rank_lt4, hist


def census():
    n = max(1, os.cpu_count() or 2)
    chunks = [list(range(1, 32))[i::n] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_work, chunks)
    valid = rank4 = rank_lt4 = covering = covering_rank_lt4 = 0
    hist = Counter()
    for v, r4, rlt, c, c_lt, h in parts:
        valid += v
        rank4 += r4
        rank_lt4 += rlt
        covering += c
        covering_rank_lt4 += c_lt
        hist.update(h)
    return valid, rank4, rank_lt4, covering, covering_rank_lt4, hist


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]

    valid, rank4, rank_lt4, covering, covering_rank_lt4, hist = census()
    if valid != claim["valid_one_repeat_walks"]:
        fail(f"valid {valid}")
    if rank4 != claim["rank4_one_repeat_walks"]:
        fail(f"rank4 {rank4}")
    expected_lt4 = claim.get("valid_rank_lt4_walks", 781200)
    if rank_lt4 != expected_lt4:
        fail(f"rank_lt4 {rank_lt4}")
    if valid != rank4 + rank_lt4:
        fail("valid != rank4+rank_lt4")
    if covering_rank_lt4 != 0:
        fail(f"rank<4 covered {covering_rank_lt4}")
    if covering != claim["one_repeat_covering"]:
        fail(f"covering {covering}")
    if min(hist) != 112 or set(hist) != {112} or hist[112] != covering:
        fail(f"hist {dict(hist)}")
    if rank4 * 16 != covering:
        fail("16 outside σ identity")

    w_short, w_long = (0, 16), (0, 4, 1, 8, 2, 1)
    if Counter(w_long[1:]).most_common(1)[0][1] != 2:
        fail("champ not one-repeat")
    r = dual_short(even_table(w_long), 16)
    if r != 112:
        fail(f"champ R {r}")
    x = path_X(w_short) + path_X(w_long)
    if x != 8:
        fail(f"champ X {x}")
    if path_X((0,)) is not None:
        fail("length-1 should be invalid")

    floor = tariff(8, 112, 0)
    if floor != 528 or floor <= 436:
        fail(f"tariff floor {floor}")
    if tariff(8, 112, x) < floor:
        fail("champion tariff below floor")
    if claim["one_repeat_min_R"] <= claim["distinct_partition_26_min_R"]:
        fail("should not beat distinct 92")

    print(
        "PASS_INDEPENDENT_WALKS_ONEREPEAT_8Q",
        f"covering={covering}",
        f"valid={valid}",
        f"rank4={rank4}",
        f"rank_lt4={rank_lt4}",
        "covering_rank_lt4=0",
        "one_repeat_min_R=112",
        f"tariff_floor={floor}",
        "distinct_26_min_R=92",
        "answers_independent_walks_8q_oq1_onerepeat",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
