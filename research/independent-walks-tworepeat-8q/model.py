"""Two-repeat partitioned independent-walk duals at Q=8.

Names one freestanding priced readout alphabet under PR1898
(b,a,x)=(38,2,2) beyond same-walk / dirty-shadow / partitioned dual /
one-repeat: the two-repeat (excess-2) companion of partitioned independent
duals on shapes (2,6), (3,5), and (4,4).

Answers preferred next17 / independent-walks-onerepeat-35-44 OQ1–OQ2 without
editing leave-alones through #2851 or pending onerepeat tips.

Self-contained relative to PR1898 / #2779 / iw8q / iwor lineage.
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
    "partition_26_covering": 0,
    "partition_26_valid_walks": 26970,
    "partition_26_shape_221": 13485,
    "partition_26_shape_311": 13485,
    "partition_35_covering": 0,
    "partition_35_valid_multisets": 465,
    "partition_35_short_tables": 465,
    "partition_44_covering": 0,
    "partition_44_valid_walks": 0,
    "length4_two_repeat_valid": 0,
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
    """Σ (count−1) over nonzero labels; one-repeat has excess 1, two-repeat 2."""
    need(type(slots) is tuple and slots and slots[0] == 0, "slots form")
    return sum(c - 1 for c in Counter(slots[1:]).values())


def is_two_repeat_nonzero(slots):
    return excess_nonzero(slots) == 2


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


def two_repeat_l6_walks():
    """Restoring two-repeat length-6 walks: shapes {2,2,1} and {3,1,1}."""
    walks_221 = []
    walks_311 = []
    for d, e in combinations(range(1, 32), 2):
        others = [x for x in range(1, 32) if x != d and x != e]
        for o in others:
            walk = find_restoring((d, d, e, e, o))
            need(walk is not None, "{2,2,1} should restore")
            need(is_two_repeat_nonzero(walk), "excess 2")
            walks_221.append(walk)
    for d in range(1, 32):
        others = [x for x in range(1, 32) if x != d]
        for o1, o2 in combinations(others, 2):
            walk = find_restoring((d, d, d, o1, o2))
            need(walk is not None, "{3,1,1} should restore")
            need(is_two_repeat_nonzero(walk), "excess 2")
            walks_311.append(walk)
    need(len(walks_221) == EXPECTED["partition_26_shape_221"], "221 count")
    need(len(walks_311) == EXPECTED["partition_26_shape_311"], "311 count")
    need(
        len(walks_221) + len(walks_311) == EXPECTED["partition_26_valid_walks"],
        "L6 total",
    )
    return walks_221, walks_311


def two_repeat_l5_multisets():
    """Unique two-repeat length-5 multisets; only shape {2,2} restores."""
    tables = []
    reps = []
    for d, e in combinations(range(1, 32), 2):
        walk = find_restoring((d, d, e, e))
        need(walk is not None, "{2,2} should restore")
        slots = slots_from_multiset((d, d, e, e))
        need(is_two_repeat_nonzero(slots), "excess 2")
        tables.append(even_table(slots))
        reps.append(walk)
    # Shape {3,1} never restores.
    for d in range(1, 32):
        for o in range(1, 32):
            if o == d:
                continue
            need(find_restoring((d, d, d, o)) is None, "{3,1} never restores")
    for d in range(1, 32):
        need(find_restoring((d, d, d, d)) is None, "{4} never restores")
    need(len(tables) == EXPECTED["partition_35_valid_multisets"], "L5 count")
    return tables, reps


def length4_two_repeat_count():
    """Length-4 two-repeat is shape {d:3}; closed walk always has a zero edge."""
    valid = 0
    for d in range(1, 32):
        if find_restoring((d, d, d)) is not None:
            valid += 1
    need(valid == EXPECTED["length4_two_repeat_valid"], "L4 two-repeat")
    return valid


def structural_rank_bound_l6(walk):
    """Two-repeat L6 has ≤3 distinct nonzero labels ⇒ rank ≤3 ⇒ |span|≤8."""
    labels = set(walk[1:])
    need(len(labels) <= 3, "two-repeat L6 ≤3 labels")
    span, rank = gf2_span(walk)
    need(rank <= 3, "rank ≤3")
    need(len(span) <= 8, "|span|≤8")
    return span, rank


def census_two_repeat_26():
    """Short (0,σ) × two-repeat length-6; covering count 0 by span lemma + census."""
    walks_221, walks_311 = two_repeat_l6_walks()
    all_walks = walks_221 + walks_311
    # Structural: every long has |span|≤8, so with short coset at most 16 masks.
    for walk in all_walks:
        structural_rank_bound_l6(walk)
    covering = 0
    hist = Counter()
    for walk in all_walks:
        e1 = even_table(slots_from_multiset(walk[1:]))
        span, _rank = gf2_span(walk)
        need(len(span) <= 8, "span bound")
        for sigma in range(1, 32):
            e0 = even_table((0, sigma))
            # Coset bound: reachable masks ⊆ span ∪ (span ⊕ σ).
            union = span | {v ^ sigma for v in span}
            need(len(union) <= 16, "coset union ≤16")
            r = dual_independent_R(e0, e1)
            if r is not None:
                covering += 1
                hist[r] += 1
    need(covering == EXPECTED["partition_26_covering"], "26 covering")
    need(len(hist) == 0, "26 empty spectrum")
    return {
        "kind": "two_repeat_partition_2_plus_6",
        "Q": 8,
        "valid_walks": len(all_walks),
        "shape_221": len(walks_221),
        "shape_311": len(walks_311),
        "covering_pairs": covering,
        "attainable_R": [],
        "histogram": {},
        "min_R": None,
        "structural_max_span": 8,
        "structural_max_coset_union": 16,
        "first_witnesses": {},
    }


def census_two_repeat_35():
    """Distinct length-3 × two-repeat length-5 {2,2}; covering count 0."""
    tables3 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 2)]
    need(len(tables3) == EXPECTED["partition_35_short_tables"], "L3 count")
    tables5, reps5 = two_repeat_l5_multisets()
    covering = 0
    hist = Counter()
    nz3 = list(combinations(range(1, 32), 2))
    for i, e0 in enumerate(tables3):
        span0, rank0 = gf2_span((0,) + nz3[i])
        need(rank0 <= 2 and len(span0) <= 4, "L3 span")
        for j, e1 in enumerate(tables5):
            span1, rank1 = gf2_span(reps5[j])
            need(rank1 <= 2 and len(span1) <= 4, "L5 {2,2} span")
            # Sumset of two affine reaches of size ≤4 has size ≤16 < 32.
            sumset = {a ^ b for a in span0 for b in span1}
            need(len(sumset) <= 16, "sumset ≤16")
            r = dual_independent_R(e0, e1)
            if r is not None:
                covering += 1
                hist[r] += 1
    need(covering == EXPECTED["partition_35_covering"], "35 covering")
    need(len(hist) == 0, "35 empty spectrum")
    return {
        "kind": "two_repeat_partition_3_plus_5",
        "Q": 8,
        "short_tables": len(tables3),
        "long_multisets": len(tables5),
        "covering_pairs": covering,
        "attainable_R": [],
        "histogram": {},
        "min_R": None,
        "structural_max_label_count_long": 2,
        "structural_max_sumset": 16,
        "first_witnesses": {},
    }


def census_two_repeat_44():
    """Two-repeat length-4 never restores; covering count 0 vacuously."""
    valid = length4_two_repeat_count()
    need(valid == EXPECTED["partition_44_valid_walks"], "44 valid")
    return {
        "kind": "two_repeat_partition_4_plus_4",
        "Q": 8,
        "valid_two_repeat_l4_walks": valid,
        "covering_pairs": 0,
        "attainable_R": [],
        "histogram": {},
        "min_R": None,
        "note": "shape_{d:3}_never_restores",
        "first_witnesses": {},
    }


def champion_analysis():
    """No covering champion; record tariff consequence and comparison floors."""
    need(EXPECTED["partition_26_covering"] == 0, "26 cover")
    need(EXPECTED["partition_35_covering"] == 0, "35 cover")
    need(EXPECTED["partition_44_covering"] == 0, "44 cover")
    need(EXPECTED["undercuts_436"] is False, "no undercut")
    # Abstract floor is undefined (no covering R); compare endpoint only.
    endpoint = EXPECTED["endpoint_tariff_Q6"]
    need(endpoint == 436, "endpoint")
    need(tariff_qrx(8, 92, 0) == 488, "distinct 26 floor sanity")
    need(tariff_qrx(8, 112, 0) == 528, "one-repeat floor sanity")
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
        "two_repeat_covering_min_R": None,
        "comparison_tariffs": {
            "distinct_26_at_R92_X0": tariff_qrx(8, 92, 0),
            "one_repeat_at_R112_X0": tariff_qrx(8, 112, 0),
            "endpoint_Q6": endpoint,
        },
    }
