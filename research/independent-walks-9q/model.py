"""Partitioned independent-walk dual readout at nine queries.

Freestanding priced alphabet under PR1898 (b,a,x)=(38,2,2): two restored walks
with independent dirt and distinct slot lists, total Q = n0 + n1 = 9, dual
even-parity readout. Answers preferred next20 / threerepeat OQ2 by naming the
Q=9 partitioned independent dual companion outside leave-alones and pending
three-repeat.

Self-contained relative to PR1898 / #2677 / #2851 / pending threerepeat.
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
    "partition_27_covering": 20512576,
    "partition_27_min_R": 80,
    "partition_27_histogram": {
        "80": 972160,
        "82": 2041536,
        "86": 6319040,
        "88": 8749440,
        "92": 972160,
        "100": 1458240,
    },
    "partition_36_covering": 69370560,
    "partition_36_min_R": 88,
    "partition_36_histogram": {
        "88": 3749760,
        "90": 20623680,
        "92": 11249280,
        "94": 5624640,
        "96": 21873600,
        "100": 5624640,
        "104": 624960,
    },
    "partition_45_covering": 122561600,
    "partition_45_min_R": 92,
    "partition_45_histogram": {
        "92": 4166400,
        "94": 37497600,
        "96": 43747200,
        "98": 3472000,
        "100": 31248000,
        "104": 2430400,
    },
    "partition_min_R": 80,
    "champion_27_walks": ((0, 19), (0, 1, 2, 4, 8, 15, 16)),
    "champion_36_walks": ((0, 1, 2), (0, 4, 8, 13, 16, 22)),
    "champion_45_walks": ((0, 1, 2, 4), (0, 7, 8, 16, 25)),
    "champion_27_path_X": 26,
    "champion_36_path_X": 18,
    "champion_45_path_X": 22,
    "tariff_floor_at_X0": 502,
    "endpoint_tariff_Q6": 436,
    "same_walk_q9_floor": 466,
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


def enumerate_partition_27():
    """All distinct-label (2,7) pairs; covering spectrum includes min R=80."""
    tables = [even_table((0,) + nz) for nz in combinations(range(1, 32), 6)]
    n = _pool_count()
    chunk = max(1, (len(tables) + n * 4 - 1) // (n * 4))
    chunks = [tables[i : i + chunk] for i in range(0, len(tables), chunk)]
    with Pool(n) as pool:
        covering, hist, _ = _merge_results(pool.map(_work_short_chunk, chunks))
    need(covering == EXPECTED["partition_27_covering"], "27 covering count")
    need(min(hist) == EXPECTED["partition_27_min_R"], "27 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_27_histogram"],
        "27 histogram",
    )
    witnesses = {}
    long_nz = list(combinations(range(1, 32), 6))
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
    return {
        "kind": "partition_2_plus_7",
        "Q": 9,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
    }


def enumerate_partition_36():
    """All distinct-label (3,6) pairs; covering spectrum includes min R=88."""
    tables3 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 2)]
    tables6 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 5)]
    n = _pool_count()
    with Pool(n, initializer=_init_worker_tables, initargs=((tables3, tables6),)) as pool:
        covering, hist, wit_idx = _merge_results(
            pool.map(_work_pair_index, range(len(tables3)))
        )
    need(covering == EXPECTED["partition_36_covering"], "36 covering count")
    need(min(hist) == EXPECTED["partition_36_min_R"], "36 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_36_histogram"],
        "36 histogram",
    )
    nz3 = list(combinations(range(1, 32), 2))
    nz6 = list(combinations(range(1, 32), 5))
    witnesses = {}
    for r, (i, j) in wit_idx.items():
        witnesses[r] = ((0,) + nz3[i], (0,) + nz6[j])
    return {
        "kind": "partition_3_plus_6",
        "Q": 9,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
    }


def enumerate_partition_45():
    """All ordered distinct-label (4,5) pairs; covering spectrum includes min R=92."""
    tables4 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 3)]
    tables5 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 4)]
    n = _pool_count()
    with Pool(n, initializer=_init_worker_tables, initargs=((tables4, tables5),)) as pool:
        covering, hist, wit_idx = _merge_results(
            pool.map(_work_pair_index, range(len(tables4)))
        )
    need(covering == EXPECTED["partition_45_covering"], "45 covering count")
    need(min(hist) == EXPECTED["partition_45_min_R"], "45 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_45_histogram"],
        "45 histogram",
    )
    nz4 = list(combinations(range(1, 32), 3))
    nz5 = list(combinations(range(1, 32), 4))
    witnesses = {}
    for r, (i, j) in wit_idx.items():
        witnesses[r] = ((0,) + nz4[i], (0,) + nz5[j])
    return {
        "kind": "partition_4_plus_5",
        "Q": 9,
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
    w27_a, w27_b = EXPECTED["champion_27_walks"]
    w36_a, w36_b = EXPECTED["champion_36_walks"]
    w45_a, w45_b = EXPECTED["champion_45_walks"]
    for w in (w27_a, w27_b, w36_a, w36_b, w45_a, w45_b):
        need(valid_restored_walk(w), f"invalid champion walk {w}")
    r27 = dual_R_short_long(even_table(w27_b), w27_a[1])
    r36 = dual_independent_R(even_table(w36_a), even_table(w36_b))
    r45 = dual_independent_R(even_table(w45_a), even_table(w45_b))
    x27 = path_X(w27_a) + path_X(w27_b)
    x36 = path_X(w36_a) + path_X(w36_b)
    x45 = path_X(w45_a) + path_X(w45_b)
    need(r27 == 80, "champ 27 R")
    need(r36 == 88, "champ 36 R")
    need(r45 == 92, "champ 45 R")
    need(x27 == EXPECTED["champion_27_path_X"], "champ 27 X")
    need(x36 == EXPECTED["champion_36_path_X"], "champ 36 X")
    need(x45 == EXPECTED["champion_45_path_X"], "champ 45 X")
    tariff27 = tariff_qrx(9, r27, x27)
    tariff36 = tariff_qrx(9, r36, x36)
    tariff45 = tariff_qrx(9, r45, x45)
    tariff_floor = tariff_qrx(9, 80, 0)
    need(tariff_floor == EXPECTED["tariff_floor_at_X0"], "floor")
    need(tariff_floor > EXPECTED["endpoint_tariff_Q6"], "no undercut at X0")
    need(tariff_floor > EXPECTED["same_walk_q9_floor"], "above same-walk Q9 floor")
    need(tariff27 >= tariff_floor, "champ 27 tariff")
    need(tariff36 >= tariff_floor, "champ 36 tariff")
    need(tariff45 >= tariff_floor, "champ 45 tariff")
    return {
        "champion_27": {
            "walks": [list(w27_a), list(w27_b)],
            "R": r27,
            "path_X": x27,
            "tariff": tariff27,
        },
        "champion_36": {
            "walks": [list(w36_a), list(w36_b)],
            "R": r36,
            "path_X": x36,
            "tariff": tariff36,
        },
        "champion_45": {
            "walks": [list(w45_a), list(w45_b)],
            "R": r45,
            "path_X": x45,
            "tariff": tariff45,
        },
        "tariff_floor_at_X0": tariff_floor,
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        "same_walk_q9_floor": EXPECTED["same_walk_q9_floor"],
        "partition_min_R": EXPECTED["partition_min_R"],
    }


def quick_checks():
    """Champion / tariff / length-1 controls without full census."""
    length1 = length1_invalid_examples()
    champ = champion_analysis()
    need(not valid_restored_walk((0,)), "length-1 invalid")
    need(champ["partition_min_R"] == 80, "quick min R constant")
    need(champ["tariff_floor_at_X0"] == 502, "quick floor")
    need(champ["tariff_floor_at_X0"] > 436, "quick no undercut")
    return {"length1_invalid_examples": length1, "champion": champ}
