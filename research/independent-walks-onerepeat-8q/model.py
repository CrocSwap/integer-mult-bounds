"""One-repeat partitioned independent-walk dual at eight queries.

Answers open question 1 of pending independent-walks-8q: do non-distinct
(one-repeat) label layers inside a partitioned Q=8 walk improve on distinct-
label R=92 at (2,6)?

Self-contained relative to PR1898 / #2779 / iw8q lineage. Leave-alones through
#2846 and pending iw8q are not edited. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations
from multiprocessing import Pool
import os


def need(ok, message):
    if not ok:
        raise ValueError(message)


INF = 99

EXPECTED = {
    "Q": 8,
    "partition": (2, 6),
    "distinct_min_R": 92,
    "valid_one_repeat_walks": 4530960,
    "rank4_one_repeat_walks": 3749760,
    "valid_rank_lt4_walks": 781200,
    "covering_pairs": 59996160,
    "min_R": 112,
    "histogram": {"112": 59996160},
    "sum_even_rank4": 40,
    "sigmas_outside_rank4": 16,
    "champion_walks": ((0, 16), (0, 4, 1, 8, 2, 1)),
    "champion_path_X": 8,
    "champion_rank": 4,
    "tariff_floor_at_X0": 528,
    "endpoint_tariff_Q6": 436,
}


def tariff_qrx(q, r, x, extra=0):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2), plus optional extras."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch + extra


def even_table(slots):
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
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


def dual_R_short_long(e_long, sigma):
    """Optimized dual when the short walk is (0, sigma)."""
    total = 0
    for m in range(1, 32):
        best = INF
        if e_long[m] < INF:
            best = e_long[m]
        flipped = e_long[m ^ sigma]
        if flipped < INF:
            best = min(best, 2 + flipped)
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


def valid_restored_walk(slots):
    if type(slots) is not tuple or not slots or slots[0] != 0:
        return False
    if len(slots) < 2:
        return False
    return path_X(slots) is not None


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


def is_one_repeat_long(slots):
    """Length-6 walk whose five nonzero slots have exactly one repeated label."""
    need(type(slots) is tuple and len(slots) == 6 and slots[0] == 0, "long form")
    counts = sorted(Counter(slots[1:]).values())
    return counts == [1, 1, 1, 2]


def structural_rank4_outside(sigma, long_slots):
    """When long span has rank 4 and sigma is outside, R = 2·Σe + 32."""
    e_long = even_table(long_slots)
    span, rank = gf2_span(long_slots)
    r = dual_R_short_long(e_long, sigma)
    if r is None or rank != 4 or sigma in span:
        return {
            "applies": False,
            "rank": rank,
            "sigma_in_span": sigma in span,
            "R": r,
            "sum_even": None,
        }
    even_sum = sum(e_long[v] for v in span if v != 0)
    need(
        r == 2 * even_sum + 32,
        f"rank-4 outside identity failed: {r} vs {2 * even_sum + 32}",
    )
    return {
        "applies": True,
        "rank": 4,
        "sigma_in_span": False,
        "R": r,
        "sum_even": even_sum,
    }


def _pool_count():
    return max(1, os.cpu_count() or 2)


def _work_dbls(dbls):
    """Census one-repeat (2,6) duals for a chunk of doubled labels."""
    valid = 0
    rank4 = 0
    rank_lt4 = 0
    covering = 0
    covering_rank_lt4 = 0
    hist = Counter()
    sum_e_bad = 0
    inside_cover = 0
    champ = None
    for dbl in dbls:
        others_pool = [x for x in range(1, 32) if x != dbl]
        for others in combinations(others_pool, 3):
            labels = (dbl,) + others
            rank_labels = gf2_rank(labels)
            for perm in set(permutations((dbl, dbl) + others)):
                slots = (0,) + perm
                if path_X(slots) is None:
                    continue
                valid += 1
                if rank_labels != 4:
                    # Admit rank<4 lemma: dual never covers for any σ.
                    rank_lt4 += 1
                    e = even_table(slots)
                    for sigma in range(1, 32):
                        if dual_R_short_long(e, sigma) is not None:
                            covering_rank_lt4 += 1
                    continue
                rank4 += 1
                e = even_table(slots)
                span, rank = gf2_span(slots)
                need(rank == 4, "label rank 4 implies walk span rank 4")
                even_sum = sum(e[v] for v in span if v != 0)
                if even_sum != EXPECTED["sum_even_rank4"]:
                    sum_e_bad += 1
                for sigma in range(1, 32):
                    r = dual_R_short_long(e, sigma)
                    if sigma in span:
                        if r is not None:
                            inside_cover += 1
                            hist[r] += 1
                            covering += 1
                        continue
                    need(r == 112, f"outside rank-4 must be R=112, got {r}")
                    covering += 1
                    hist[112] += 1
                    if champ is None:
                        champ = ((0, sigma), slots)
    return (
        valid,
        rank4,
        rank_lt4,
        covering,
        covering_rank_lt4,
        hist,
        sum_e_bad,
        inside_cover,
        champ,
    )


def census_one_repeat_26(workers=None):
    """All valid one-repeat length-6 longs × short (0,σ); covering spectrum {112}."""
    n = workers or _pool_count()
    chunks = [list(range(1, 32))[i::n] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_work_dbls, chunks)
    valid = rank4 = rank_lt4 = covering = covering_rank_lt4 = 0
    sum_e_bad = inside_cover = 0
    hist = Counter()
    champ = None
    for v, r4, rlt, c, c_lt, h, bad, inside, ch in parts:
        valid += v
        rank4 += r4
        rank_lt4 += rlt
        covering += c
        covering_rank_lt4 += c_lt
        sum_e_bad += bad
        inside_cover += inside
        hist.update(h)
        if champ is None and ch is not None:
            champ = ch
    need(valid == EXPECTED["valid_one_repeat_walks"], "valid walk count")
    need(rank4 == EXPECTED["rank4_one_repeat_walks"], "rank4 walk count")
    need(rank_lt4 == EXPECTED["valid_rank_lt4_walks"], "rank<4 walk count")
    need(valid == rank4 + rank_lt4, "valid partition rank4+rank<4")
    need(covering_rank_lt4 == 0, "rank<4 never covers")
    need(covering == EXPECTED["covering_pairs"], "covering count")
    need(sum_e_bad == 0, "every rank-4 one-repeat has Σe=40")
    need(inside_cover == 0, "sigma in span never covers")
    need(min(hist) == EXPECTED["min_R"], "min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["histogram"],
        "histogram",
    )
    need(rank4 * EXPECTED["sigmas_outside_rank4"] == covering, "16 outside σ")
    need(champ is not None, "champion exists")
    return {
        "kind": "one_repeat_partition_2_plus_6",
        "Q": 8,
        "valid_one_repeat_walks": valid,
        "rank4_one_repeat_walks": rank4,
        "valid_rank_lt4_walks": rank_lt4,
        "covering_rank_lt4": covering_rank_lt4,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "sum_even_rank4": EXPECTED["sum_even_rank4"],
        "sigmas_outside_rank4": EXPECTED["sigmas_outside_rank4"],
        "first_witness": {
            "112": [list(champ[0]), list(champ[1])],
        },
    }


def champion_analysis():
    w_short, w_long = EXPECTED["champion_walks"]
    need(valid_restored_walk(w_short), "short champion")
    need(valid_restored_walk(w_long), "long champion")
    need(is_one_repeat_long(w_long), "long is one-repeat")
    need(len(set(w_short[1:])) == len(w_short) - 1, "short has distinct nonzero")
    r = dual_R_short_long(even_table(w_long), w_short[1])
    need(r == EXPECTED["min_R"], "champion R")
    x = path_X(w_short) + path_X(w_long)
    need(x == EXPECTED["champion_path_X"], "champion X")
    struct = structural_rank4_outside(w_short[1], w_long)
    need(struct["applies"] and struct["R"] == 112, "champion structural")
    need(struct["sum_even"] == EXPECTED["sum_even_rank4"], "champion Σe")
    need(struct["rank"] == EXPECTED["champion_rank"], "champion rank")
    tariff_floor = tariff_qrx(8, EXPECTED["min_R"], 0)
    need(tariff_floor == EXPECTED["tariff_floor_at_X0"], "floor")
    need(tariff_floor > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(EXPECTED["min_R"] > EXPECTED["distinct_min_R"], "worsens distinct")
    champ_tariff = tariff_qrx(8, r, x)
    need(champ_tariff >= tariff_floor, "champ tariff")
    return {
        "champion": {
            "walks": [list(w_short), list(w_long)],
            "R": r,
            "path_X": x,
            "tariff": champ_tariff,
            "structural_rank4_outside": struct,
            "one_repeat_long": True,
        },
        "tariff_floor_at_X0": tariff_floor,
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        "distinct_partition_26_min_R": EXPECTED["distinct_min_R"],
        "one_repeat_min_R": EXPECTED["min_R"],
    }
