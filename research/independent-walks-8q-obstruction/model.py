"""Partitioned independent-walk dual readout at eight queries.

Freestanding priced alphabet under PR1898 (b,a,x)=(38,2,2): two restored walks
with independent dirt and distinct slot lists, total Q = n0 + n1 = 8, dual
even-parity readout. Answers dirty-shadow / onerepeat OQ2 by naming one new
alphabet at Q=8 outside leave-alones and pending transfer-coupled-onerepeat.

Self-contained relative to PR1898 / #2677 / #2779 / #2840. Prepared by Wentao Li
with substantial AI assistance. Apache-2.0.
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
    "partition_26_covering": 3916416,
    "partition_26_min_R": 92,
    "partition_26_histogram": {"92": 1416576, "96": 1249920, "104": 1249920},
    "partition_35_covering": 10416000,
    "partition_35_min_R": 98,
    "partition_35_histogram": {"98": 3124800, "104": 7291200},
    "partition_44_covering": 14165760,
    "partition_44_min_R": 100,
    "partition_44_histogram": {"100": 3610880, "104": 9999360, "112": 555520},
    "partition_min_R": 92,
    "champion_26_walks": ((0, 16), (0, 1, 2, 4, 8, 15)),
    "champion_35_walks": ((0, 1, 2), (0, 4, 8, 13, 16)),
    "champion_44_walks": ((0, 1, 2, 4), (0, 7, 8, 16)),
    "champion_26_path_X": 16,
    "champion_35_path_X": 12,
    "champion_44_path_X": 16,
    "tariff_floor_at_X0": 488,
    "endpoint_tariff_Q6": 436,
    "single_walk_even_min_R_Q8": 74,
    "length1_invalid": True,
}


def tariff_qrx(q, r, x, extra=0):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2), plus optional extras."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch + extra


def even_table(slots):
    """Even-subset per-mask minima on a slot list (INF if unreachable)."""
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


def dual_R_short_long(e_long, sigma):
    """Optimized dual when the short walk is (0, sigma): e_short[0]=0, e_short[sigma]=2."""
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


def path_X(slots):
    """Path XOR cost on the restored closed walk slots + (0,)."""
    closed = slots + (0,)
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        if delta == 0:
            return None
        total += 2 * (delta.bit_count() - 1)
    return total


def valid_restored_walk(slots):
    """A restored walk needs length ≥ 2 (closed return must be a nonzero edge)."""
    if type(slots) is not tuple or not slots or slots[0] != 0:
        return False
    if len(slots) < 2:
        return False
    return path_X(slots) is not None


def sum_even_nonzero(even, span):
    return sum(even[v] for v in span if v != 0)


def structural_26_rank4_outside(sigma, long_slots):
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
    even_sum = sum_even_nonzero(e_long, span)
    need(r == 2 * even_sum + 32, f"rank-4 outside identity failed: {r} vs {2 * even_sum + 32}")
    return {
        "applies": True,
        "rank": 4,
        "sigma_in_span": False,
        "R": r,
        "sum_even": even_sum,
    }


# --- multiprocessing workers (module-level for pickling) ---

_WORKER_TABLES = None


def _init_worker_tables(tables):
    global _WORKER_TABLES
    _WORKER_TABLES = tables


def _work_short_chunk(chunk):
    hist = Counter()
    covering = 0
    witnesses = {}
    for e_long in chunk:
        for sigma in range(1, 32):
            r = dual_R_short_long(e_long, sigma)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            witnesses.setdefault(r, sigma)
    return covering, hist, witnesses


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


def enumerate_partition_26():
    """All distinct-label (2,6) pairs; covering spectrum {92,96,104}."""
    tables = [even_table((0,) + nz) for nz in combinations(range(1, 32), 5)]
    n = _pool_count()
    chunk = max(1, (len(tables) + n * 4 - 1) // (n * 4))
    chunks = [tables[i : i + chunk] for i in range(0, len(tables), chunk)]
    with Pool(n) as pool:
        covering, hist, _ = _merge_results(pool.map(_work_short_chunk, chunks))
    need(covering == EXPECTED["partition_26_covering"], "26 covering count")
    need(min(hist) == EXPECTED["partition_26_min_R"], "26 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_26_histogram"],
        "26 histogram",
    )
    # Rebuild first witnesses with concrete walks for the certificate.
    witnesses = {}
    long_nz = list(combinations(range(1, 32), 5))
    for nz, e_long in zip(long_nz, tables):
        slots = (0,) + nz
        for sigma in range(1, 32):
            r = dual_R_short_long(e_long, sigma)
            if r is None:
                continue
            witnesses.setdefault(r, ((0, sigma), slots))
            if len(witnesses) == len(hist):
                break
        if len(witnesses) == len(hist):
            break
    # Structural check on the R=92 champion (rank-4 outside).
    w0, w1 = EXPECTED["champion_26_walks"]
    struct = structural_26_rank4_outside(w0[1], w1)
    need(struct["applies"] and struct["R"] == 92, "champion 26 structural")
    return {
        "kind": "partition_2_plus_6",
        "Q": 8,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
        "champion_structural_rank4_outside": struct,
    }


def enumerate_partition_35():
    """All distinct-label (3,5) pairs; covering spectrum {98,104}."""
    tables3 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 2)]
    tables5 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 4)]
    n = _pool_count()
    with Pool(n, initializer=_init_worker_tables, initargs=((tables3, tables5),)) as pool:
        covering, hist, wit_idx = _merge_results(
            pool.map(_work_pair_index, range(len(tables3)))
        )
    need(covering == EXPECTED["partition_35_covering"], "35 covering count")
    need(min(hist) == EXPECTED["partition_35_min_R"], "35 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_35_histogram"],
        "35 histogram",
    )
    nz3 = list(combinations(range(1, 32), 2))
    nz5 = list(combinations(range(1, 32), 4))
    witnesses = {}
    for r, (i, j) in wit_idx.items():
        witnesses[r] = ((0,) + nz3[i], (0,) + nz5[j])
    return {
        "kind": "partition_3_plus_5",
        "Q": 8,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
    }


def enumerate_partition_44():
    """All ordered distinct-label (4,4) pairs; covering spectrum {100,104,112}."""
    tables4 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 3)]
    n = _pool_count()
    with Pool(n, initializer=_init_worker_tables, initargs=((tables4, tables4),)) as pool:
        covering, hist, wit_idx = _merge_results(
            pool.map(_work_pair_index, range(len(tables4)))
        )
    need(covering == EXPECTED["partition_44_covering"], "44 covering count")
    need(min(hist) == EXPECTED["partition_44_min_R"], "44 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_44_histogram"],
        "44 histogram",
    )
    nz4 = list(combinations(range(1, 32), 3))
    witnesses = {}
    for r, (i, j) in wit_idx.items():
        witnesses[r] = ((0,) + nz4[i], (0,) + nz4[j])
    return {
        "kind": "partition_4_plus_4",
        "Q": 8,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
    }


def length1_invalid_examples():
    """Length-1 'walks' are not restored: closed return is a zero edge."""
    examples = []
    for slots in ((0,),):
        examples.append(
            {
                "slots": list(slots),
                "valid_restored_walk": valid_restored_walk(slots),
                "path_X": path_X(slots),
                "note": "closed_(0,0)_zero_edge",
            }
        )
    need(all(not ex["valid_restored_walk"] for ex in examples), "length-1 must be invalid")
    need(all(ex["path_X"] is None for ex in examples), "zero return edge")
    return examples


def champion_analysis():
    w26_a, w26_b = EXPECTED["champion_26_walks"]
    w35_a, w35_b = EXPECTED["champion_35_walks"]
    w44_a, w44_b = EXPECTED["champion_44_walks"]
    for w in (w26_a, w26_b, w35_a, w35_b, w44_a, w44_b):
        need(valid_restored_walk(w), f"invalid champion walk {w}")
    r26 = dual_R_short_long(even_table(w26_b), w26_a[1])
    r35 = dual_independent_R(even_table(w35_a), even_table(w35_b))
    r44 = dual_independent_R(even_table(w44_a), even_table(w44_b))
    x26 = path_X(w26_a) + path_X(w26_b)
    x35 = path_X(w35_a) + path_X(w35_b)
    x44 = path_X(w44_a) + path_X(w44_b)
    need(r26 == 92, "champ 26 R")
    need(r35 == 98, "champ 35 R")
    need(r44 == 100, "champ 44 R")
    need(x26 == EXPECTED["champion_26_path_X"], "champ 26 X")
    need(x35 == EXPECTED["champion_35_path_X"], "champ 35 X")
    need(x44 == EXPECTED["champion_44_path_X"], "champ 44 X")
    struct = structural_26_rank4_outside(w26_a[1], w26_b)
    need(struct["applies"] and struct["R"] == 92, "champ structural")
    tariff26 = tariff_qrx(8, r26, x26)
    tariff35 = tariff_qrx(8, r35, x35)
    tariff44 = tariff_qrx(8, r44, x44)
    tariff_floor = tariff_qrx(8, 92, 0)
    need(tariff_floor == EXPECTED["tariff_floor_at_X0"], "floor")
    need(tariff_floor > EXPECTED["endpoint_tariff_Q6"], "no undercut at X0")
    need(tariff26 >= tariff_floor, "champ 26 tariff")
    need(tariff35 >= tariff_floor, "champ 35 tariff")
    need(tariff44 >= tariff_floor, "champ 44 tariff")
    return {
        "champion_26": {
            "walks": [list(w26_a), list(w26_b)],
            "R": r26,
            "path_X": x26,
            "tariff": tariff26,
            "structural_rank4_outside": struct,
        },
        "champion_35": {
            "walks": [list(w35_a), list(w35_b)],
            "R": r35,
            "path_X": x35,
            "tariff": tariff35,
        },
        "champion_44": {
            "walks": [list(w44_a), list(w44_b)],
            "R": r44,
            "path_X": x44,
            "tariff": tariff44,
        },
        "tariff_floor_at_X0": tariff_floor,
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        "single_walk_even_min_R_Q8": EXPECTED["single_walk_even_min_R_Q8"],
        "partition_min_R": EXPECTED["partition_min_R"],
    }
