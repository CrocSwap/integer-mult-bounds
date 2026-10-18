"""One-repeat partitioned independent-walk duals on (3,5) and (4,4) at Q=8.

Answers open question 1 of pending independent-walks-onerepeat-8q: do
one-repeat layers on partitions (3,5) or (4,4) improve on distinct-label
floors R=98 / R=100?

Self-contained relative to PR1898 / #2779 / iw8q / iwor8q lineage.
Leave-alones through #2851 and pending onerepeat-(2,6) are not edited.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from multiprocessing import Pool
import os


def need(ok, message):
    if not ok:
        raise ValueError(message)


INF = 99

EXPECTED = {
    "Q": 8,
    "distinct_35_min_R": 98,
    "distinct_44_min_R": 100,
    "partition_35_covering": 2499840,
    "partition_35_min_R": 112,
    "partition_35_histogram": {"112": 2499840},
    "partition_35_short_tables": 465,
    "partition_35_long_tables": 13485,
    "partition_44_covering": 1666560,
    "partition_44_min_R": 112,
    "partition_44_histogram": {"112": 1666560},
    "partition_44_or_tables": 930,
    "partition_44_distinct_tables": 4495,
    "partition_44_both_or_covering": 0,
    "sum_even_rank3_full_reach": 16,
    "champion_35_walks": ((0, 1, 2), (0, 8, 4, 16, 4)),
    "champion_44_walks": ((0, 1, 2, 1), (0, 4, 8, 16)),
    "champion_35_path_X": 8,
    "champion_44_path_X": 8,
    "tariff_floor_at_X0": 528,
    "endpoint_tariff_Q6": 436,
    "length3_one_repeat_valid": 0,
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


def dual_independent_R(e0, e1):
    """Σ_m min_a (e0[a] + e1[a⊕m]) with independent even-parity ports."""
    reach0 = [(a, e0[a]) for a in range(32) if e0[a] < INF]
    total = 0
    for m in range(1, 32):
        best = INF
        for a, c0 in reach0:
            c1 = e1[a ^ m]
            if c1 < INF:
                cost = c0 + c1
                if cost < best:
                    best = cost
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


def is_one_repeat_nonzero(slots):
    """Nonzero multiset has exactly one repeated label (and at least one singleton)."""
    need(type(slots) is tuple and slots and slots[0] == 0, "slots form")
    counts = sorted(Counter(slots[1:]).values())
    return len(counts) >= 2 and counts[-1] == 2 and all(c == 1 for c in counts[:-1])


def length3_one_repeat_count():
    """Length-3 one-repeat candidates are (0,d,d); closed walk has a zero edge."""
    valid = 0
    for d in range(1, 32):
        if path_X((0, d, d)) is not None:
            valid += 1
    need(valid == EXPECTED["length3_one_repeat_valid"], "length-3 one-repeat")
    return valid


def one_repeat_l5_tables():
    """Even tables for one-repeat length-5 multisets {0,d,d,o1,o2}."""
    tables = []
    reps = []
    meta = []
    for d in range(1, 32):
        others = [x for x in range(1, 32) if x != d]
        for o1, o2 in combinations(others, 2):
            # Separating the repeated label avoids a zero edge on the closed walk.
            rep = (0, d, o1, d, o2)
            need(path_X(rep) is not None, "one-repeat L5 should restore")
            slots_ms = (0, d, d, o1, o2)
            e = even_table(slots_ms)
            span, rank = gf2_span(slots_ms)
            tables.append(e)
            reps.append(rep)
            meta.append({"span": span, "rank": rank, "sum_even": sum(e[v] for v in span if v)})
    need(len(tables) == EXPECTED["partition_35_long_tables"], "L5 table count")
    return tables, reps, meta


def one_repeat_l4_tables():
    """Even tables for one-repeat length-4 walks; only (0,d,o,d) restores."""
    tables = []
    reps = []
    meta = []
    for d in range(1, 32):
        for o in range(1, 32):
            if o == d:
                continue
            rep = (0, d, o, d)
            need(path_X(rep) is not None, "L4 one-repeat form")
            need(path_X((0, d, d, o)) is None, "adjacent repeat invalid")
            slots_ms = (0, d, d, o)
            e = even_table(slots_ms)
            span, rank = gf2_span(slots_ms)
            need(rank == 2, "one-repeat L4 rank")
            need(len(span) == 4, "one-repeat L4 span")
            tables.append(e)
            reps.append(rep)
            meta.append({"span": span, "rank": rank, "sum_even": sum(e[v] for v in span if v)})
    need(len(tables) == EXPECTED["partition_44_or_tables"], "L4 table count")
    return tables, reps, meta


_WORKER_TABLES = None


def _init_worker_tables(tables):
    global _WORKER_TABLES
    _WORKER_TABLES = tables


def _work_pair_index(i):
    e0 = _WORKER_TABLES[0][i]
    hist = Counter()
    covering = 0
    witnesses = {}
    for j, e1 in enumerate(_WORKER_TABLES[1]):
        r = dual_independent_R(e0, e1)
        if r is None:
            continue
        covering += 1
        hist[r] += 1
        witnesses.setdefault(r, (i, j))
    return covering, hist, witnesses


def _merge_results(results):
    hist = Counter()
    covering = 0
    witnesses = {}
    for c, h, w in results:
        covering += c
        hist.update(h)
        for r, wit in w.items():
            witnesses.setdefault(r, wit)
    return covering, hist, witnesses


def _pool_count():
    return max(1, os.cpu_count() or 2)


def census_one_repeat_35():
    """Distinct length-3 × one-repeat length-5; covering spectrum {112}."""
    length3_one_repeat_count()
    tables3 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 2)]
    need(len(tables3) == EXPECTED["partition_35_short_tables"], "L3 count")
    tables5, reps5, meta5 = one_repeat_l5_tables()
    n = _pool_count()
    with Pool(n, initializer=_init_worker_tables, initargs=((tables3, tables5),)) as pool:
        covering, hist, wit_idx = _merge_results(
            pool.map(_work_pair_index, range(len(tables3)))
        )
    need(covering == EXPECTED["partition_35_covering"], "35 covering")
    need(min(hist) == EXPECTED["partition_35_min_R"], "35 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_35_histogram"],
        "35 histogram",
    )
    # Structural: every covering long is rank-3 full-reach with Σe=16.
    sum_e_bad = 0
    for i, j in wit_idx.values():
        meta = meta5[j]
        if meta["rank"] != 3 or meta["sum_even"] != EXPECTED["sum_even_rank3_full_reach"]:
            sum_e_bad += 1
    need(sum_e_bad == 0, "covering longs have Σe=16 at rank 3")
    nz3 = list(combinations(range(1, 32), 2))
    witnesses = {}
    for r, (i, j) in wit_idx.items():
        witnesses[r] = ((0,) + nz3[i], reps5[j])
    return {
        "kind": "one_repeat_partition_3_plus_5",
        "Q": 8,
        "short_tables": len(tables3),
        "long_tables": len(tables5),
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "sum_even_rank3_full_reach": EXPECTED["sum_even_rank3_full_reach"],
        "length3_one_repeat_valid": EXPECTED["length3_one_repeat_valid"],
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
    }


def census_one_repeat_44():
    """One-repeat length-4 × distinct length-4; covering spectrum {112}."""
    tables_or, reps_or, meta_or = one_repeat_l4_tables()
    tables4 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 3)]
    need(len(tables4) == EXPECTED["partition_44_distinct_tables"], "L4 distinct")
    n = _pool_count()
    with Pool(n, initializer=_init_worker_tables, initargs=((tables_or, tables4),)) as pool:
        covering, hist, wit_idx = _merge_results(
            pool.map(_work_pair_index, range(len(tables_or)))
        )
    need(covering == EXPECTED["partition_44_covering"], "44 covering")
    need(min(hist) == EXPECTED["partition_44_min_R"], "44 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_44_histogram"],
        "44 histogram",
    )
    nz4 = list(combinations(range(1, 32), 3))
    witnesses = {}
    for r, (i, j) in wit_idx.items():
        witnesses[r] = (reps_or[i], (0,) + nz4[j])
    # Both sides one-repeat never covers.
    with Pool(n, initializer=_init_worker_tables, initargs=((tables_or, tables_or),)) as pool:
        both_cover, both_hist, _ = _merge_results(
            pool.map(_work_pair_index, range(len(tables_or)))
        )
    need(both_cover == EXPECTED["partition_44_both_or_covering"], "both-or covering")
    need(len(both_hist) == 0, "both-or empty spectrum")
    return {
        "kind": "one_repeat_partition_4_plus_4",
        "Q": 8,
        "one_repeat_tables": len(tables_or),
        "distinct_tables": len(tables4),
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "both_one_repeat_covering": both_cover,
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
    }


def champion_analysis():
    w35_a, w35_b = EXPECTED["champion_35_walks"]
    w44_a, w44_b = EXPECTED["champion_44_walks"]
    for w in (w35_a, w35_b, w44_a, w44_b):
        need(valid_restored_walk(w), f"invalid champion {w}")
    need(is_one_repeat_nonzero(w35_b), "35 long one-repeat")
    need(is_one_repeat_nonzero(w44_a), "44 short one-repeat")
    need(len(set(w35_a[1:])) == len(w35_a) - 1, "35 short distinct")
    need(len(set(w44_b[1:])) == len(w44_b) - 1, "44 long distinct")
    r35 = dual_independent_R(even_table(w35_a), even_table(w35_b))
    r44 = dual_independent_R(even_table(w44_a), even_table(w44_b))
    need(r35 == EXPECTED["partition_35_min_R"], "champ 35 R")
    need(r44 == EXPECTED["partition_44_min_R"], "champ 44 R")
    x35 = path_X(w35_a) + path_X(w35_b)
    x44 = path_X(w44_a) + path_X(w44_b)
    need(x35 == EXPECTED["champion_35_path_X"], "champ 35 X")
    need(x44 == EXPECTED["champion_44_path_X"], "champ 44 X")
    # Structural Σe on one-repeat sides.
    span35, rank35 = gf2_span(w35_b)
    e35 = even_table(w35_b)
    sum_e35 = sum(e35[v] for v in span35 if v)
    need(rank35 == 3, "champ 35 rank")
    need(sum_e35 == EXPECTED["sum_even_rank3_full_reach"], "champ 35 Σe")
    span44, rank44 = gf2_span(w44_a)
    need(rank44 == 2, "champ 44 one-repeat rank")
    tariff_floor = tariff_qrx(8, EXPECTED["partition_35_min_R"], 0)
    need(tariff_floor == EXPECTED["tariff_floor_at_X0"], "floor")
    need(tariff_floor > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(EXPECTED["partition_35_min_R"] > EXPECTED["distinct_35_min_R"], "worsens 35")
    need(EXPECTED["partition_44_min_R"] > EXPECTED["distinct_44_min_R"], "worsens 44")
    return {
        "champion_35": {
            "walks": [list(w35_a), list(w35_b)],
            "R": r35,
            "path_X": x35,
            "tariff": tariff_qrx(8, r35, x35),
            "one_repeat_long": True,
            "long_rank": rank35,
            "long_sum_even": sum_e35,
        },
        "champion_44": {
            "walks": [list(w44_a), list(w44_b)],
            "R": r44,
            "path_X": x44,
            "tariff": tariff_qrx(8, r44, x44),
            "one_repeat_short": True,
            "short_rank": rank44,
        },
        "tariff_floor_at_X0": tariff_floor,
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        "distinct_35_min_R": EXPECTED["distinct_35_min_R"],
        "distinct_44_min_R": EXPECTED["distinct_44_min_R"],
        "one_repeat_35_min_R": EXPECTED["partition_35_min_R"],
        "one_repeat_44_min_R": EXPECTED["partition_44_min_R"],
    }
