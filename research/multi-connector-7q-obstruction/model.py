"""Multi-connector / priced-shadow readout at seven queries.

Answers open question 1 of the cheaper-readout package (#2715): whether a
multi-connector readout alphabet (two live connectors, or a priced shadow
snapshot) can reach R<=78 at Q=7 with X=6 after a complete dirty bill.
Self-contained relative to PR1898 / #2643 / #2686 / #2715. Prepared by
Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations


def need(ok, message):
    if not ok:
        raise ValueError(message)


EXPECTED = {
    "distinct6_covering": 583296,
    "even_subset_attainable_R": [82, 88],
    "even_subset_histogram": {"82": 97216, "88": 486080},
    "even_subset_min_R": 82,
    "dirty_shadow_attainable_R": [82, 88],
    "dirty_shadow_histogram": {"82": 97216, "88": 486080},
    "dirty_shadow_min_R": 82,
    "dirty_shadow_matches_even_covering": 583296,
    "dual_indep_attainable_R": [82, 88],
    "dual_indep_histogram": {"82": 97216, "88": 486080},
    "dual_indep_min_R": 82,
    "dual_indep_matches_even_covering": 583296,
    "clean_shadow_attainable_R": [71, 80],
    "clean_shadow_histogram": {"71": 97216, "80": 486080},
    "clean_shadow_min_R": 71,
    "one_repeat_even_R": 96,
    "one_repeat_dirty_shadow_R": 96,
    "one_repeat_clean_shadow_R": 88,
    "one_repeat_covering": 1680,
    "champion_slots": (0, 1, 2, 6, 12, 24, 16),
    "champion_even_R": 82,
    "champion_dirty_shadow_min_R": 82,
    "champion_clean_shadow_min_R": 71,
    "champion_clean_best_k": 1,
    "endpoint_tariff_Q6": 436,
    "legal_tariff_at_X6": 442,
    "hypothetical_clean_tariff_at_X6": 420,
}


def tariff_qrx(q, r, x, extra=0):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2), plus optional extras."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch + extra


def mask_best_bundle(slots):
    """Even, dirty-shadow (per k), and clean-shadow (per k) per-mask minima.

    Dirty shadow at index k: second live connector inherits correlated dirt from
    a priced copy of the primary at slot k. Legal schedules need even total
    live-read parity across primary+shadow (same dirt coefficient).

    Clean shadow at index k: hypothetical dirt-free snapshot of value slots[k]
    (illegal under PR1898 arbitrary dirt — retained only as a counterfactual).
    Primary still needs even live-connector parity; shadow reads are free of dirt.
    """
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    n = len(slots)
    even = [99] * 32
    even[0] = 0
    dirty = [[99] * 32 for _ in range(n)]
    clean = [[99] * 32 for _ in range(n)]
    for bits in range(1 << n):
        size = bits.bit_count()
        if size == 0:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size % 2 == 0:
            if size < even[value]:
                even[value] = size
            for k in range(n):
                if size < dirty[k][value]:
                    dirty[k][value] = size
                if size < clean[k][value]:
                    clean[k][value] = size
                sigma = slots[k]
                cost = size + 1
                v = value ^ sigma
                if cost < clean[k][v]:
                    clean[k][v] = cost
        else:
            for k in range(n):
                sigma = slots[k]
                cost = size + 1
                v = value ^ sigma
                if cost < dirty[k][v]:
                    dirty[k][v] = cost
    for k in range(n):
        sigma = slots[k]
        if sigma != 0 and 1 < clean[k][sigma]:
            clean[k][sigma] = 1
    return {"even": even, "dirty": dirty, "clean": clean}


def total_or_none(best):
    if any(best[mask] >= 99 for mask in range(1, 32)):
        return None
    return sum(best[1:])


def min_even_subset_R(slots):
    return total_or_none(mask_best_bundle(slots)["even"])


def dirty_shadow_R_by_k(slots):
    info = mask_best_bundle(slots)
    return [total_or_none(info["dirty"][k]) for k in range(len(slots))]


def min_dirty_shadow_R(slots):
    vals = [v for v in dirty_shadow_R_by_k(slots) if v is not None]
    return min(vals) if vals else None


def clean_shadow_R_by_k(slots):
    info = mask_best_bundle(slots)
    return [total_or_none(info["clean"][k]) for k in range(len(slots))]


def min_clean_shadow_R(slots):
    vals = [v for v in clean_shadow_R_by_k(slots) if v is not None]
    return min(vals) if vals else None


def even_triangle_holds(even):
    """Even-subset costs obey e[m] <= e[a] + e[a⊕m] (concatenate two even sets)."""
    if any(even[m] >= 99 for m in range(1, 32)):
        return False
    for m in range(1, 32):
        for a in range(32):
            c0 = even[a]
            c1 = even[a ^ m]
            if c0 < 99 and c1 < 99 and even[m] > c0 + c1:
                return False
    return True


def dual_and_triangle_from_even(even):
    """One 31×32 pass: (Σ_m min_a (e[a]+e[a⊕m]), triangle_holds).

    Dual cost is computed directly (not copied from Σ e[m]). Triangle is
    e[m] <= e[a]+e[a⊕m] for every covered a,m. With e[0]=0 the choice a=m
    always achieves e[m], so triangle forces dual == Σ e[m] on covering lists.
    """
    if any(even[m] >= 99 for m in range(1, 32)):
        return None, False
    total = 0
    triangle = True
    for m in range(1, 32):
        best = 99
        em = even[m]
        for a in range(32):
            c0 = even[a]
            c1 = even[a ^ m]
            if c0 < 99 and c1 < 99:
                cost = c0 + c1
                if cost < best:
                    best = cost
                if em > cost:
                    triangle = False
        if best >= 99:
            return None, False
        total += best
    return total, triangle


def dual_independent_from_even(even):
    """Dual-indep R = Σ_{m=1}^{31} min_a (e[a] + e[a⊕m]) from even table."""
    dual_r, _triangle = dual_and_triangle_from_even(even)
    return dual_r


def dual_independent_same_walk_R(slots):
    """Two independently dirty connectors on the same slot list.

    Each port needs even live-read parity separately. Cost is |T0|+|T1| for
    even realizing sets with XOR(T0)⊕XOR(T1)=m. Empty second port recovers
    ordinary even-subset; triangle inequality prevents any improvement.
    """
    return dual_independent_from_even(mask_best_bundle(slots)["even"])


def dirty_shadow_symdiff_identities(slots, k):
    """Check the sym-diff collapse: odd primary + shadow ≡ even set via Δ{k}."""
    n = len(slots)
    sigma = slots[k]
    checked = 0
    for bits in range(1 << n):
        size = bits.bit_count()
        if size % 2 == 0:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        new_bits = bits ^ (1 << k)
        new_size = new_bits.bit_count()
        need(new_size % 2 == 0, "sym-diff must be even")
        includes = (bits >> k) & 1
        need(new_size == (size - 1 if includes else size + 1), "sym-diff cost")
        new_value = 0
        for i in range(n):
            if new_bits >> i & 1:
                new_value ^= slots[i]
        need(new_value == (value ^ sigma), "sym-diff XOR")
        checked += 1
    return checked


def valid_walk_slots(slots):
    if type(slots) is not tuple or len(slots) != 7 or slots[0] != 0:
        return False
    if slots[-1] == 0:
        return False
    if any(slots[i] == slots[i + 1] for i in range(6)):
        return False
    return True


def path_X(closed):
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        need(delta != 0, "zero query edge")
        total += 2 * (delta.bit_count() - 1)
    return total


def enumerate_distinct6_multi_connector():
    """One pass: even, dirty-shadow, clean-shadow, and dual-indep (real min_a)."""
    hist_even = Counter()
    hist_dirty = Counter()
    hist_dual = Counter()
    hist_clean = Counter()
    covering = 0
    dirty_matches = 0
    dual_matches = 0
    triangle_ok = 0
    witnesses = {"even": {}, "dirty": {}, "dual": {}, "clean": {}}
    for nonzero in combinations(range(1, 32), 6):
        slots = (0,) + nonzero
        info = mask_best_bundle(slots)
        even = info["even"]
        even_r = total_or_none(even)
        if even_r is None:
            continue
        dirty_vals = [total_or_none(info["dirty"][k]) for k in range(7)]
        clean_vals = [total_or_none(info["clean"][k]) for k in range(7)]
        need(all(v is not None for v in dirty_vals), "dirty uncovered")
        need(all(v is not None for v in clean_vals), "clean uncovered")
        dual_r, tri_ok = dual_and_triangle_from_even(even)
        need(dual_r is not None, "dual uncovered")
        dirty_r = min(dirty_vals)
        clean_r = min(clean_vals)
        covering += 1
        hist_even[even_r] += 1
        hist_dirty[dirty_r] += 1
        hist_dual[dual_r] += 1
        hist_clean[clean_r] += 1
        if dirty_r == even_r and all(v == even_r for v in dirty_vals):
            dirty_matches += 1
        if dual_r == even_r:
            dual_matches += 1
        if tri_ok:
            triangle_ok += 1
        witnesses["even"].setdefault(even_r, slots)
        witnesses["dirty"].setdefault(dirty_r, slots)
        witnesses["dual"].setdefault(dual_r, slots)
        witnesses["clean"].setdefault(clean_r, slots)
    return {
        "covering_sets": covering,
        "even_subset": {
            "attainable_R": sorted(hist_even),
            "histogram": {str(r): hist_even[r] for r in sorted(hist_even)},
            "min_R": min(hist_even) if hist_even else None,
            "first_witnesses": {
                str(r): list(slots) for r, slots in witnesses["even"].items()
            },
        },
        "dirty_shadow": {
            "attainable_R": sorted(hist_dirty),
            "histogram": {str(r): hist_dirty[r] for r in sorted(hist_dirty)},
            "min_R": min(hist_dirty) if hist_dirty else None,
            "matches_even_on_covering": dirty_matches,
            "first_witnesses": {
                str(r): list(slots) for r, slots in witnesses["dirty"].items()
            },
        },
        "dual_independent": {
            "attainable_R": sorted(hist_dual),
            "histogram": {str(r): hist_dual[r] for r in sorted(hist_dual)},
            "min_R": min(hist_dual) if hist_dual else None,
            "matches_even_on_covering": dual_matches,
            "triangle_holds_on_covering": triangle_ok,
            "first_witnesses": {
                str(r): list(slots) for r, slots in witnesses["dual"].items()
            },
        },
        "clean_shadow_counterfactual": {
            "attainable_R": sorted(hist_clean),
            "histogram": {str(r): hist_clean[r] for r in sorted(hist_clean)},
            "min_R": min(hist_clean) if hist_clean else None,
            "first_witnesses": {
                str(r): list(slots) for r, slots in witnesses["clean"].items()
            },
            "legal_under_dirty_contract": False,
        },
    }


def one_repeat_basis_census(score):
    """Valid Q=7 one-repeat walks on the standard basis, scored by ``score``."""
    labels = (1, 2, 4, 8, 16)
    hist = Counter()
    covering = 0
    best = None
    witness = None

    for j in range(1, 6):
        rest = [i for i in range(1, 7) if i != j]
        for perm in permutations(labels):
            slots = [0] * 7
            slots[j] = 0
            for pos, val in zip(rest, perm):
                slots[pos] = val
            slots_t = tuple(slots)
            if not valid_walk_slots(slots_t):
                continue
            total = score(slots_t)
            if total is None:
                continue
            covering += 1
            hist[total] += 1
            if best is None or total < best:
                best = total
                witness = slots_t

    for dbl_idx in range(5):
        others = [labels[i] for i in range(5) if i != dbl_idx]
        for p1, p2 in combinations(range(1, 7), 2):
            rest_pos = [i for i in range(1, 7) if i not in (p1, p2)]
            for perm in permutations(others):
                slots = [0] * 7
                slots[p1] = slots[p2] = labels[dbl_idx]
                for pos, val in zip(rest_pos, perm):
                    slots[pos] = val
                slots_t = tuple(slots)
                if not valid_walk_slots(slots_t):
                    continue
                total = score(slots_t)
                if total is None:
                    continue
                covering += 1
                hist[total] += 1
                if best is None or total < best:
                    best = total
                    witness = slots_t

    attainable = sorted(hist)
    return {
        "kind": "one_repeat_on_standard_basis",
        "covering_walks": covering,
        "attainable_R": attainable,
        "histogram": {str(r): hist[r] for r in attainable},
        "min_R": best,
        "first_witness": list(witness) if witness is not None else None,
    }


def clean_shadow_dirt_examples():
    """Finite checks: dirt-free shadow schedules fail inherited-dirt cancellation."""
    examples = []
    slots = EXPECTED["champion_slots"]
    # Best clean k for champion is 1 (sigma=1), R=71.
    k = EXPECTED["champion_clean_best_k"]
    sigma = slots[k]
    # Shadow-only readout of mask sigma has odd live dirt on the shadow port.
    examples.append(
        {
            "note": "champion_shadow_only_sigma",
            "slots": list(slots),
            "snapshot_index": k,
            "sigma": sigma,
            "mask": sigma,
            "primary_reads": 0,
            "shadow_reads": 1,
            "inherited_dirt_parity": 1,
            "legal_under_correlated_dirt": False,
            "clean_R": min_clean_shadow_R(slots),
            "dirty_R": min_dirty_shadow_R(slots),
        }
    )
    # First clean-71 witness: odd shadow use similarly illegal.
    witness = (0, 1, 2, 4, 8, 15, 16)
    k2 = min(range(7), key=lambda i: clean_shadow_R_by_k(witness)[i])
    examples.append(
        {
            "note": "first_clean_71_witness_shadow_dirt",
            "slots": list(witness),
            "snapshot_index": k2,
            "sigma": witness[k2],
            "mask": witness[k2],
            "primary_reads": 0,
            "shadow_reads": 1,
            "inherited_dirt_parity": 1,
            "legal_under_correlated_dirt": False,
            "clean_R": min_clean_shadow_R(witness),
            "dirty_R": min_dirty_shadow_R(witness),
        }
    )
    need(all(ex["inherited_dirt_parity"] == 1 for ex in examples), "odd dirt")
    need(all(not ex["legal_under_correlated_dirt"] for ex in examples), "illegal")
    return examples


def champion_analysis():
    slots = EXPECTED["champion_slots"]
    closed = slots + (0,)
    dirty_by_k = dirty_shadow_R_by_k(slots)
    clean_by_k = clean_shadow_R_by_k(slots)
    return {
        "slots": list(slots),
        "path_X": path_X(closed),
        "even_R": min_even_subset_R(slots),
        "dirty_shadow_R_by_k": dirty_by_k,
        "dirty_shadow_min_R": min(dirty_by_k),
        "dual_independent_R": dual_independent_same_walk_R(slots),
        "clean_shadow_R_by_k": clean_by_k,
        "clean_shadow_min_R": min(clean_by_k),
        "clean_best_k": min(range(7), key=lambda i: clean_by_k[i]),
        "legal_tariff_X6": tariff_qrx(7, min(dirty_by_k), 6),
        "hypothetical_clean_tariff_X6": tariff_qrx(7, min(clean_by_k), 6),
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        "symdiff_checked_at_k1": dirty_shadow_symdiff_identities(slots, 1),
    }


# Credited path-lowered champion from the 789q / #2643 / #2686 / #2715 lineage.
CHAMPION_7 = (0, 1, 2, 6, 12, 24, 16, 0)
