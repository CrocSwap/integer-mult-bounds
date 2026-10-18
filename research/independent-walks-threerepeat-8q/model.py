"""Three-repeat partitioned independent-walk duals at Q=8.

Names one freestanding priced readout alphabet under PR1898
(b,a,x)=(38,2,2) beyond same-walk / dirty-shadow / partitioned dual /
one-repeat / two-repeat / shared-dirt: the three-repeat (excess-3)
companion of partitioned independent duals on shapes (2,6), (3,5), and
(4,4).

Answers preferred next19 / shared-dirt OQ1 without editing leave-alones
through #2861/#2860/#2858/#2851 or pending shared-dirt tip.

Self-contained relative to PR1898 / #2779 / iw8q / excess-repeat lineage.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations


def need(ok, message):
    if not ok:
        raise ValueError(message)


INF = 99

EXPECTED = {
    "Q": 8,
    "distinct_26_min_R": 92,
    "distinct_35_min_R": 98,
    "distinct_44_min_R": 100,
    "one_repeat_26_min_R": 112,
    "one_repeat_35_min_R": 112,
    "one_repeat_44_min_R": 112,
    "two_repeat_26_covering": 0,
    "two_repeat_35_covering": 0,
    "two_repeat_44_covering": 0,
    "shared_dirt_partition_min_R": 82,
    "partition_26_covering": 0,
    "partition_26_valid_walks": 930,
    "partition_26_shape_32": 930,
    "partition_26_shape_41": 0,
    "partition_35_covering": 0,
    "partition_35_valid_multisets": 0,
    "partition_35_shape_4_never_restores": 0,
    "partition_35_short_tables": 465,
    "partition_44_covering": 0,
    "partition_44_valid_walks": 0,
    "length4_three_repeat_valid": 0,
    "tariff_floor_at_X0": None,
    "endpoint_tariff_Q6": 436,
    "undercuts_436": False,
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


def excess_nonzero(slots):
    """Σ (count−1) over nonzero labels; three-repeat has excess 3."""
    need(type(slots) is tuple and slots and slots[0] == 0, "slots form")
    return sum(c - 1 for c in Counter(slots[1:]).values())


def is_three_repeat_nonzero(slots):
    return excess_nonzero(slots) == 3


def find_restoring(multiset_nz):
    for perm in set(permutations(multiset_nz)):
        walk = (0,) + perm
        if path_X(walk) is not None:
            return walk
    return None


def slots_from_multiset(ms):
    nz = []
    for lab, cnt in sorted(Counter(ms).items()):
        nz.extend([lab] * cnt)
    return (0,) + tuple(nz)


def three_repeat_l6_walks():
    """Restoring three-repeat length-6 walks: only shape {3,2} restores.

    Excess 3 on five nonzero slots forces exactly two distinct labels.
    Shapes: {d:3,e:2} (restores) and {d:4,o} (never restores: adjacent d→d).
    """
    walks_32 = []
    for d, e in combinations(range(1, 32), 2):
        for triple, pair in ((d, e), (e, d)):
            walk = find_restoring((triple, triple, triple, pair, pair))
            need(walk is not None, "{3,2} should restore")
            need(is_three_repeat_nonzero(walk), "excess 3")
            walks_32.append(walk)
    # Shape {4,1} never restores.
    never_41 = 0
    for d in range(1, 32):
        for o in range(1, 32):
            if o == d:
                continue
            need(find_restoring((d, d, d, d, o)) is None, "{4,1} never restores")
            never_41 += 1
    need(never_41 == 930, "{4,1} enumeration")
    need(len(walks_32) == EXPECTED["partition_26_shape_32"], "32 count")
    need(EXPECTED["partition_26_shape_41"] == 0, "41 valid is 0")
    need(len(walks_32) == EXPECTED["partition_26_valid_walks"], "L6 total")
    return walks_32


def three_repeat_l5_never_restores():
    """Three-repeat length-5 is shape {d:4}; closed walk always has a zero edge."""
    valid = 0
    for d in range(1, 32):
        if find_restoring((d, d, d, d)) is not None:
            valid += 1
    need(valid == EXPECTED["partition_35_shape_4_never_restores"], "L5 {4}")
    return valid


def length4_three_repeat_count():
    """Length-4 cannot host excess 3 (3 nonzero slots ⇒ max excess 2)."""
    # Exhaustive: every 3-slot multiset with excess 3 is impossible, so 0.
    # Max excess shapes on L4: {d:3} has excess 2 (two-repeat).
    valid = 0
    for d in range(1, 32):
        # No multiset of size 3 has excess 3; check vacuously that no
        # restoring walk of length 4 has excess 3.
        for e in range(1, 32):
            for f in range(1, 32):
                walk = (0, d, e, f)
                if path_X(walk) is not None and excess_nonzero(walk) == 3:
                    valid += 1
    need(valid == EXPECTED["length4_three_repeat_valid"], "L4 three-repeat")
    return valid


def structural_rank_bound_l6(walk):
    """Three-repeat L6 has exactly 2 distinct nonzero labels ⇒ rank ≤2 ⇒ |span|≤4."""
    labels = set(walk[1:])
    need(len(labels) == 2, "three-repeat L6 exactly 2 labels")
    span, rank = gf2_span(walk)
    need(rank <= 2, "rank ≤2")
    need(len(span) <= 4, "|span|≤4")
    return span, rank


def census_three_repeat_26():
    """Short (0,σ) × three-repeat length-6; covering count 0 by span lemma + census."""
    walks_32 = three_repeat_l6_walks()
    for walk in walks_32:
        structural_rank_bound_l6(walk)
    covering = 0
    hist = Counter()
    for walk in walks_32:
        e1 = even_table(slots_from_multiset(walk[1:]))
        span, _rank = gf2_span(walk)
        need(len(span) <= 4, "span bound")
        for sigma in range(1, 32):
            e0 = even_table((0, sigma))
            # Coset bound: reachable masks ⊆ span ∪ (span ⊕ σ).
            union = span | {v ^ sigma for v in span}
            need(len(union) <= 8, "coset union ≤8")
            r = dual_independent_R(e0, e1)
            if r is not None:
                covering += 1
                hist[r] += 1
    need(covering == EXPECTED["partition_26_covering"], "26 covering")
    need(len(hist) == 0, "26 empty spectrum")
    return {
        "kind": "three_repeat_partition_2_plus_6",
        "Q": 8,
        "valid_walks": len(walks_32),
        "shape_32": len(walks_32),
        "shape_41": 0,
        "covering_pairs": covering,
        "attainable_R": [],
        "histogram": {},
        "min_R": None,
        "structural_max_span": 4,
        "structural_max_coset_union": 8,
        "first_witnesses": {},
    }


def census_three_repeat_35():
    """Distinct length-3 × three-repeat length-5 {4}; covering count 0 (never restores)."""
    tables3 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 2)]
    need(len(tables3) == EXPECTED["partition_35_short_tables"], "L3 count")
    valid5 = three_repeat_l5_never_restores()
    need(valid5 == EXPECTED["partition_35_valid_multisets"], "35 valid")
    covering = 0
    # Vacuous dual: no three-repeat L5 restoring multiset exists.
    need(covering == EXPECTED["partition_35_covering"], "35 covering")
    return {
        "kind": "three_repeat_partition_3_plus_5",
        "Q": 8,
        "short_tables": len(tables3),
        "long_multisets": valid5,
        "covering_pairs": covering,
        "attainable_R": [],
        "histogram": {},
        "min_R": None,
        "note": "shape_{d:4}_never_restores",
        "structural_max_label_count_long": 1,
        "first_witnesses": {},
    }


def census_three_repeat_44():
    """Three-repeat length-4 is impossible; covering count 0 vacuously."""
    valid = length4_three_repeat_count()
    need(valid == EXPECTED["partition_44_valid_walks"], "44 valid")
    return {
        "kind": "three_repeat_partition_4_plus_4",
        "Q": 8,
        "valid_three_repeat_l4_walks": valid,
        "covering_pairs": 0,
        "attainable_R": [],
        "histogram": {},
        "min_R": None,
        "note": "excess_3_impossible_on_length4_max_excess_2",
        "first_witnesses": {},
    }


def champion_analysis():
    """No covering champion; record tariff consequence and comparison floors."""
    need(EXPECTED["partition_26_covering"] == 0, "26 cover")
    need(EXPECTED["partition_35_covering"] == 0, "35 cover")
    need(EXPECTED["partition_44_covering"] == 0, "44 cover")
    need(EXPECTED["undercuts_436"] is False, "no undercut")
    endpoint = EXPECTED["endpoint_tariff_Q6"]
    need(endpoint == 436, "endpoint")
    need(tariff_qrx(8, 92, 0) == 488, "distinct 26 floor sanity")
    need(tariff_qrx(8, 112, 0) == 528, "one-repeat floor sanity")
    need(tariff_qrx(8, 82, 0) == 468, "shared-dirt floor sanity")
    return {
        "covering_any_partition": False,
        "tariff_floor_at_X0": None,
        "endpoint_Q6": endpoint,
        "undercuts_436_after_complete_bill": False,
        "distinct_26_min_R": EXPECTED["distinct_26_min_R"],
        "distinct_35_min_R": EXPECTED["distinct_35_min_R"],
        "distinct_44_min_R": EXPECTED["distinct_44_min_R"],
        "one_repeat_26_min_R": EXPECTED["one_repeat_26_min_R"],
        "one_repeat_35_min_R": EXPECTED["one_repeat_35_min_R"],
        "one_repeat_44_min_R": EXPECTED["one_repeat_44_min_R"],
        "two_repeat_26_covering": EXPECTED["two_repeat_26_covering"],
        "shared_dirt_partition_min_R": EXPECTED["shared_dirt_partition_min_R"],
        "three_repeat_covering_min_R": None,
        "comparison_tariffs": {
            "distinct_26_at_R92_X0": tariff_qrx(8, 92, 0),
            "one_repeat_at_R112_X0": tariff_qrx(8, 112, 0),
            "shared_dirt_at_R82_X0": tariff_qrx(8, 82, 0),
            "endpoint_Q6": endpoint,
        },
    }
