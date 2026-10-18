"""Shared-dirt partitioned dual readout at eight queries.

Freestanding priced alphabet under PR1898 (b,a,x)=(38,2,2): two restored walks
with distinct slot lists and a **shared dirt coefficient** (joint even live-read
parity across both walks), total Q = n0 + n1 = 8. Names one new dirt-legal
readout alphabet beyond same-walk / dirty-shadow / partitioned dual /
one-repeat / two-repeat.

Answers preferred next18 / tworepeat OQ1–OQ2. Soft-overlap-safe vs deferred
shared-XOR (#2643): this couples the R-side dirt coefficient only; path-X and
non-path XOR schedules are unchanged and not shared.

Self-contained relative to PR1898 / #2851 / iw lineage / tworepeat.
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
    "partition_26_covering": 3916416,
    "partition_26_min_R": 82,
    "partition_26_histogram": {"82": 583296, "88": 2916480, "96": 416640},
    "partition_35_covering": 10416000,
    "partition_35_min_R": 82,
    "partition_35_histogram": {"82": 1458240, "88": 7291200, "96": 1666560},
    "partition_44_covering": 14165760,
    "partition_44_min_R": 82,
    "partition_44_histogram": {"82": 1944320, "88": 9721600, "96": 2499840},
    "partition_min_R": 82,
    "independent_26_min_R": 92,
    "independent_35_min_R": 98,
    "independent_44_min_R": 100,
    "champion_26_walks": ((0, 16), (0, 1, 2, 4, 8, 15)),
    "champion_35_walks": ((0, 1, 2), (0, 4, 8, 15, 16)),
    "champion_44_walks": ((0, 1, 2, 4), (0, 8, 15, 16)),
    "champion_26_path_X": 16,
    "champion_35_path_X": 16,
    "champion_44_path_X": 16,
    "tariff_floor_at_X0": 468,
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


def even_odd_tables(slots):
    """Even- and odd-subset per-mask minima on a slot list (INF if unreachable)."""
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    n = len(slots)
    even = [INF] * 32
    odd = [INF] * 32
    even[0] = 0
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        table = even if size % 2 == 0 else odd
        if size < table[value]:
            table[value] = size
    return even, odd


def even_table(slots):
    even, _odd = even_odd_tables(slots)
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


def dual_shared_dirt_R(e0, o0, e1, o1):
    """Shared dirt: joint even total live-read parity (even+even or odd+odd).

    Cost for mask m is
        min( min_α (e0[α]+e1[α⊕m]),  min_α (o0[α]+o1[α⊕m]) ).
    Independent dirt admits only the even+even branch.
    """
    reach_e0 = [(a, e0[a]) for a in range(32) if e0[a] < INF]
    reach_o0 = [(a, o0[a]) for a in range(32) if o0[a] < INF]
    total = 0
    for m in range(1, 32):
        best = INF
        for a, c0 in reach_e0:
            c1 = e1[a ^ m]
            if c1 < INF:
                cost = c0 + c1
                if cost < best:
                    best = cost
        for a, c0 in reach_o0:
            c1 = o1[a ^ m]
            if c1 < INF:
                cost = c0 + c1
                if cost < best:
                    best = cost
        if best >= INF:
            return None
        total += best
    return total


def dual_shared_short_long(e_long, o_long, sigma):
    """Shared-dirt dual when the short walk is (0, sigma).

    Short tables: e[0]=0, e[sigma]=2, o[0]=1, o[sigma]=1.
    Per mask: min(e_long[m], 2+e_long[m⊕σ], 1+o_long[m], 1+o_long[m⊕σ]).
    """
    total = 0
    for m in range(1, 32):
        best = e_long[m]
        flipped = e_long[m ^ sigma]
        if flipped < INF:
            best = min(best, 2 + flipped)
        odd_m = o_long[m]
        if odd_m < INF:
            best = min(best, 1 + odd_m)
        odd_flip = o_long[m ^ sigma]
        if odd_flip < INF:
            best = min(best, 1 + odd_flip)
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


def short_walk_tables(sigma):
    """Sanity tables for (0, sigma)."""
    e, o = even_odd_tables((0, sigma))
    need(e[0] == 0 and e[sigma] == 2, "short even")
    need(o[0] == 1 and o[sigma] == 1, "short odd")
    return e, o


# --- multiprocessing workers ---

_WORKER_TABLES = None


def _init_worker_tables(tables):
    global _WORKER_TABLES
    _WORKER_TABLES = tables


def _work_short_chunk(chunk):
    hist = Counter()
    covering = 0
    witnesses = {}
    for e_long, o_long in chunk:
        for sigma in range(1, 32):
            r = dual_shared_short_long(e_long, o_long, sigma)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            witnesses.setdefault(r, sigma)
    return covering, hist, witnesses


def _work_pair_index(i):
    e0, o0 = _WORKER_TABLES[0][i]
    hist = Counter()
    covering = 0
    witnesses = {}
    for j, (e1, o1) in enumerate(_WORKER_TABLES[1]):
        r = dual_shared_dirt_R(e0, o0, e1, o1)
        if r is None:
            continue
        covering += 1
        hist[r] += 1
        witnesses.setdefault(r, (i, j))
    return covering, hist, witnesses


def _work_pair_sym(i):
    """Ordered (4,4) via upper triangle: dual_shared is symmetric in the two walks."""
    tables = _WORKER_TABLES[0]
    e0, o0 = tables[i]
    hist = Counter()
    covering = 0
    witnesses = {}
    r = dual_shared_dirt_R(e0, o0, e0, o0)
    if r is not None:
        covering += 1
        hist[r] += 1
        witnesses.setdefault(r, (i, i))
    for j in range(i + 1, len(tables)):
        e1, o1 = tables[j]
        r = dual_shared_dirt_R(e0, o0, e1, o1)
        if r is None:
            continue
        covering += 2
        hist[r] += 2
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
    """All distinct-label (2,6) shared-dirt pairs; covering spectrum {82,88,96}."""
    tables = [even_odd_tables((0,) + nz) for nz in combinations(range(1, 32), 5)]
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
    witnesses = {}
    long_nz = list(combinations(range(1, 32), 5))
    for nz, (e_long, o_long) in zip(long_nz, tables):
        slots = (0,) + nz
        for sigma in range(1, 32):
            r = dual_shared_short_long(e_long, o_long, sigma)
            if r is None:
                continue
            witnesses.setdefault(r, ((0, sigma), slots))
            if len(witnesses) == len(hist):
                break
        if len(witnesses) == len(hist):
            break
    # Short-long identity on the R=82 champion.
    w0, w1 = EXPECTED["champion_26_walks"]
    e1, o1 = even_odd_tables(w1)
    r_fast = dual_shared_short_long(e1, o1, w0[1])
    e0, o0 = even_odd_tables(w0)
    r_full = dual_shared_dirt_R(e0, o0, e1, o1)
    need(r_fast == r_full == 82, "champion 26 short-long identity")
    return {
        "kind": "shared_dirt_partition_2_plus_6",
        "Q": 8,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
        "champion_short_long_identity": True,
    }


def enumerate_partition_35():
    """All distinct-label (3,5) shared-dirt pairs; covering spectrum {82,88,96}."""
    tables3 = [even_odd_tables((0,) + nz) for nz in combinations(range(1, 32), 2)]
    tables5 = [even_odd_tables((0,) + nz) for nz in combinations(range(1, 32), 4)]
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
        "kind": "shared_dirt_partition_3_plus_5",
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
    """All ordered distinct-label (4,4) shared-dirt pairs; spectrum {82,88,96}."""
    tables4 = [even_odd_tables((0,) + nz) for nz in combinations(range(1, 32), 3)]
    n = _pool_count()
    with Pool(n, initializer=_init_worker_tables, initargs=((tables4,),)) as pool:
        covering, hist, wit_idx = _merge_results(
            pool.map(_work_pair_sym, range(len(tables4)))
        )
    need(covering == EXPECTED["partition_44_covering"], "44 covering count")
    need(min(hist) == EXPECTED["partition_44_min_R"], "44 min R")
    need(
        {str(r): hist[r] for r in sorted(hist)} == EXPECTED["partition_44_histogram"],
        "44 histogram",
    )
    # Symmetry sanity: swap of champion walks yields the same R.
    w0, w1 = EXPECTED["champion_44_walks"]
    e0, o0 = even_odd_tables(w0)
    e1, o1 = even_odd_tables(w1)
    need(
        dual_shared_dirt_R(e0, o0, e1, o1) == dual_shared_dirt_R(e1, o1, e0, o0) == 82,
        "44 symmetry",
    )
    nz4 = list(combinations(range(1, 32), 3))
    witnesses = {}
    for r, (i, j) in wit_idx.items():
        witnesses[r] = ((0,) + nz4[i], (0,) + nz4[j])
    return {
        "kind": "shared_dirt_partition_4_plus_4",
        "Q": 8,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist),
        "first_witnesses": {
            str(r): [list(a), list(b)] for r, (a, b) in sorted(witnesses.items())
        },
        "symmetry_checked": True,
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


def beats_independent_on_champions():
    """Shared dirt strictly undercuts independent-dirt floors on each shape's champ."""
    rows = []
    for name, walks, ind_floor in (
        ("26", EXPECTED["champion_26_walks"], EXPECTED["independent_26_min_R"]),
        ("35", EXPECTED["champion_35_walks"], EXPECTED["independent_35_min_R"]),
        ("44", EXPECTED["champion_44_walks"], EXPECTED["independent_44_min_R"]),
    ):
        w0, w1 = walks
        e0, o0 = even_odd_tables(w0)
        e1, o1 = even_odd_tables(w1)
        r_shared = dual_shared_dirt_R(e0, o0, e1, o1)
        r_ind = dual_independent_R(e0, e1)
        need(r_shared is not None and r_ind is not None, f"{name} covering")
        need(r_shared < r_ind, f"{name} shared should beat independent on champ")
        need(r_shared < ind_floor or r_shared == 82, f"{name} vs independent floor")
        rows.append(
            {
                "partition": name,
                "walks": [list(w0), list(w1)],
                "R_shared": r_shared,
                "R_independent": r_ind,
                "independent_floor": ind_floor,
                "beats_independent_floor": r_shared < ind_floor,
            }
        )
    return rows


def champion_analysis():
    w26_a, w26_b = EXPECTED["champion_26_walks"]
    w35_a, w35_b = EXPECTED["champion_35_walks"]
    w44_a, w44_b = EXPECTED["champion_44_walks"]
    for w in (w26_a, w26_b, w35_a, w35_b, w44_a, w44_b):
        need(valid_restored_walk(w), f"invalid champion walk {w}")
    e26a, o26a = even_odd_tables(w26_a)
    e26b, o26b = even_odd_tables(w26_b)
    e35a, o35a = even_odd_tables(w35_a)
    e35b, o35b = even_odd_tables(w35_b)
    e44a, o44a = even_odd_tables(w44_a)
    e44b, o44b = even_odd_tables(w44_b)
    r26 = dual_shared_dirt_R(e26a, o26a, e26b, o26b)
    r35 = dual_shared_dirt_R(e35a, o35a, e35b, o35b)
    r44 = dual_shared_dirt_R(e44a, o44a, e44b, o44b)
    x26 = path_X(w26_a) + path_X(w26_b)
    x35 = path_X(w35_a) + path_X(w35_b)
    x44 = path_X(w44_a) + path_X(w44_b)
    need(r26 == 82, "champ 26 R")
    need(r35 == 82, "champ 35 R")
    need(r44 == 82, "champ 44 R")
    need(x26 == EXPECTED["champion_26_path_X"], "champ 26 X")
    need(x35 == EXPECTED["champion_35_path_X"], "champ 35 X")
    need(x44 == EXPECTED["champion_44_path_X"], "champ 44 X")
    # Shared ≤ independent on every champion.
    need(dual_independent_R(e26a, e26b) == 92, "26 ind on shared champ")
    need(r26 < 92, "26 shared beats ind")
    need(r35 < dual_independent_R(e35a, e35b), "35 shared beats ind")
    need(r44 < dual_independent_R(e44a, e44b), "44 shared beats ind")
    tariff26 = tariff_qrx(8, r26, x26)
    tariff35 = tariff_qrx(8, r35, x35)
    tariff44 = tariff_qrx(8, r44, x44)
    tariff_floor = tariff_qrx(8, 82, 0)
    need(tariff_floor == EXPECTED["tariff_floor_at_X0"], "floor")
    need(tariff_floor > EXPECTED["endpoint_tariff_Q6"], "no undercut at X0")
    need(tariff26 >= tariff_floor, "champ 26 tariff")
    need(tariff35 >= tariff_floor, "champ 35 tariff")
    need(tariff44 >= tariff_floor, "champ 44 tariff")
    return {
        "champion_26": {
            "walks": [list(w26_a), list(w26_b)],
            "R_shared": r26,
            "R_independent": 92,
            "path_X": x26,
            "tariff": tariff26,
        },
        "champion_35": {
            "walks": [list(w35_a), list(w35_b)],
            "R_shared": r35,
            "R_independent": dual_independent_R(e35a, e35b),
            "path_X": x35,
            "tariff": tariff35,
        },
        "champion_44": {
            "walks": [list(w44_a), list(w44_b)],
            "R_shared": r44,
            "R_independent": dual_independent_R(e44a, e44b),
            "path_X": x44,
            "tariff": tariff44,
        },
        "tariff_floor_at_X0": tariff_floor,
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        "single_walk_even_min_R_Q8": EXPECTED["single_walk_even_min_R_Q8"],
        "partition_min_R": EXPECTED["partition_min_R"],
        "beats_independent_floors": True,
        "undercuts_436_after_complete_bill": False,
        "soft_overlap_shared_xor": "safe_R_side_dirt_coupling_only",
    }
