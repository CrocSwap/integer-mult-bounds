"""Partitioned independent-walk dual readout at seven queries.

Answers the independent-walks open question left by multi-connector / #2715
lineage (partitioned case): two restored walks with independent dirt and
distinct slot lists, total Q = n0 + n1 = 7, dual even-parity readout.

Self-contained relative to PR1898 / #2643 / #2686 / #2715 / pending mc7q
same-walk. Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations


def need(ok, message):
    if not ok:
        raise ValueError(message)


INF = 99

EXPECTED = {
    "partition_25_covering": 416640,
    "partition_25_min_R": 112,
    "partition_25_histogram": {"112": 416640},
    "partition_34_covering": 833280,
    "partition_34_min_R": 112,
    "partition_34_histogram": {"112": 833280},
    "partition_R": 112,
    "champion_25_walks": ((0, 1), (0, 2, 4, 8, 16)),
    "champion_34_walks": ((0, 1, 2), (0, 4, 8, 16)),
    "champion_25_path_X": 6,
    "champion_34_path_X": 6,
    "tariff_floor_at_X0": 490,
    "endpoint_tariff_Q6": 436,
    "single_walk_even_min_R": 82,
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
    total = 0
    for m in range(1, 32):
        best = INF
        for a in range(32):
            c0 = e0[a]
            c1 = e1[a ^ m]
            if c0 < INF and c1 < INF:
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


def structural_25_identity(sigma, long_slots):
    """Lemma check: covering (2,5) forces rank-4 long span, sigma outside, R=112."""
    e_long = even_table(long_slots)
    span, rank = gf2_span(long_slots)
    r = dual_R_short_long(e_long, sigma)
    if r is None:
        return {
            "covering": False,
            "rank": rank,
            "sigma_in_span": sigma in span,
            "R": None,
            "sum_even": None,
        }
    need(rank == 4, "covering (2,5) long walk must have rank 4")
    need(sigma not in span, "covering (2,5) sigma must lie outside long span")
    even_sum = sum_even_nonzero(e_long, span)
    need(even_sum == 40, f"even sum on F2^4 basis+0 must be 40, got {even_sum}")
    need(r == 2 * even_sum + 32 == 112, f"structural R identity failed: {r}")
    return {
        "covering": True,
        "rank": rank,
        "sigma_in_span": False,
        "R": r,
        "sum_even": even_sum,
    }


def enumerate_partition_25():
    """All distinct-label (2,5) pairs; covering ones have R=112 exactly."""
    hist = Counter()
    covering = 0
    structural_ok = 0
    witnesses = {}
    long_tables = {}
    for nz in combinations(range(1, 32), 4):
        slots = (0,) + nz
        long_tables[nz] = (slots, even_table(slots))
    for sigma in range(1, 32):
        for nz, (slots, e_long) in long_tables.items():
            r = dual_R_short_long(e_long, sigma)
            if r is None:
                continue
            info = structural_25_identity(sigma, slots)
            need(info["covering"], "dual cover without structural cover")
            need(info["R"] == 112, "structural R")
            covering += 1
            structural_ok += 1
            hist[r] += 1
            witnesses.setdefault(r, ((0, sigma), slots))
    return {
        "kind": "partition_2_plus_5",
        "Q": 7,
        "covering_pairs": covering,
        "structural_ok": structural_ok,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist) if hist else None,
        "first_witnesses": {
            str(r): [list(w0), list(w1)] for r, (w0, w1) in witnesses.items()
        },
    }


def enumerate_partition_34():
    """All distinct-label (3,4) pairs; covering ones have R=112 exactly."""
    hist = Counter()
    covering = 0
    witnesses = {}
    tables3 = {
        nz: ((0,) + nz, even_table((0,) + nz)) for nz in combinations(range(1, 32), 2)
    }
    tables4 = {
        nz: ((0,) + nz, even_table((0,) + nz)) for nz in combinations(range(1, 32), 3)
    }
    for _a, (s0, e0) in tables3.items():
        for _b, (s1, e1) in tables4.items():
            r = dual_independent_R(e0, e1)
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            witnesses.setdefault(r, (s0, s1))
            need(r == 112, f"(3,4) covering R must be 112, got {r}")
    return {
        "kind": "partition_3_plus_4",
        "Q": 7,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(r): hist[r] for r in sorted(hist)},
        "min_R": min(hist) if hist else None,
        "first_witnesses": {
            str(r): [list(w0), list(w1)] for r, (w0, w1) in witnesses.items()
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
    w25_a, w25_b = EXPECTED["champion_25_walks"]
    w34_a, w34_b = EXPECTED["champion_34_walks"]
    need(valid_restored_walk(w25_a) and valid_restored_walk(w25_b), "champ 25 valid")
    need(valid_restored_walk(w34_a) and valid_restored_walk(w34_b), "champ 34 valid")
    e25b = even_table(w25_b)
    r25 = dual_R_short_long(e25b, w25_a[1])
    r34 = dual_independent_R(even_table(w34_a), even_table(w34_b))
    x25 = path_X(w25_a) + path_X(w25_b)
    x34 = path_X(w34_a) + path_X(w34_b)
    need(r25 == 112 and r34 == 112, "champion R")
    need(x25 == EXPECTED["champion_25_path_X"], "champ 25 X")
    need(x34 == EXPECTED["champion_34_path_X"], "champ 34 X")
    struct = structural_25_identity(w25_a[1], w25_b)
    need(struct["covering"] and struct["R"] == 112, "champ structural")
    tariff25 = tariff_qrx(7, r25, x25)
    tariff34 = tariff_qrx(7, r34, x34)
    tariff_floor = tariff_qrx(7, 112, 0)
    need(tariff_floor == EXPECTED["tariff_floor_at_X0"], "floor")
    need(tariff_floor > EXPECTED["endpoint_tariff_Q6"], "no undercut at X0")
    need(tariff25 >= tariff_floor and tariff34 >= tariff_floor, "champ tariffs")
    return {
        "champion_25": {
            "walks": [list(w25_a), list(w25_b)],
            "R": r25,
            "path_X": x25,
            "tariff": tariff25,
            "structural": struct,
        },
        "champion_34": {
            "walks": [list(w34_a), list(w34_b)],
            "R": r34,
            "path_X": x34,
            "tariff": tariff34,
        },
        "tariff_floor_at_X0": tariff_floor,
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        "single_walk_even_min_R": EXPECTED["single_walk_even_min_R"],
    }


def even_sum_standard_F2_4():
    """Σ_{v≠0} least_even_geq(wt(v)) over F2^4 = 40."""
    total = 0
    for v in range(1, 16):
        wt = v.bit_count()
        total += wt + (wt % 2)  # least even integer ≥ wt, using free 0-slot
    return total
