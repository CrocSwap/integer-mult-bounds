"""Odd-cardinality / all-subset readout vs dirty-parity repair at seven queries.

Answers open question 1 of the seven-query R-floor package (#2686): whether a
readout alphabet strictly cheaper than even-subset connector-state combinations
can reach R<=78 at Q=7 with X=6. Self-contained relative to PR1898 / #2643 /
#2686. Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations


def need(ok, message):
    if not ok:
        raise ValueError(message)


# Expected spectra (single-pass distinct-6 census; one-repeat GL basis).
EXPECTED = {
    "distinct6_covering": 583296,
    "all_subset_attainable_R": [66, 72],
    "all_subset_histogram": {"66": 97216, "72": 486080},
    "all_subset_min_R": 66,
    "even_subset_attainable_R": [82, 88],
    "even_subset_histogram": {"82": 97216, "88": 486080},
    "even_subset_min_R": 82,
    "parity_repair_attainable_R": [82, 88],
    "parity_repair_histogram": {"82": 97216, "88": 486080},
    "parity_repair_min_R": 82,
    "one_repeat_all_subset_R": 80,
    "one_repeat_all_subset_covering": 1680,
    "one_repeat_parity_repair_R": 96,
    "one_repeat_parity_repair_covering": 1680,
    "champion_slots": (0, 1, 2, 6, 12, 24, 16),
    "champion_all_R": 66,
    "champion_even_R": 82,
    "champion_repair_R": 82,
    "endpoint_tariff_Q6": 436,
    "hypothetical_all_subset_tariff_X6": 410,
    "parity_repair_tariff_X6": 442,
}


def tariff_qrx(q, r, x):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2)."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch


def mask_best_sizes(slots):
    """Per-mask min sizes: all-subset, even-subset, and zero-slot parity repair."""
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    n = len(slots)
    best_all = [99] * 32
    best_even = [99] * 32
    best_repair = [99] * 32
    zero_idxs = [i for i in range(n) if slots[i] == 0]
    for bits in range(1 << n):
        size = bits.bit_count()
        if size == 0:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size < best_all[value]:
            best_all[value] = size
        if size % 2 == 0:
            if size < best_even[value]:
                best_even[value] = size
            if size < best_repair[value]:
                best_repair[value] = size
        elif zero_idxs:
            # Odd live-connector parity: repair at a 0-valued slot (adjoin or drop).
            includes_zero = any(bits >> i & 1 for i in zero_idxs)
            cost = size - 1 if includes_zero else size + 1
            if cost < best_repair[value]:
                best_repair[value] = cost
    return {
        "all": best_all,
        "even": best_even,
        "repair": best_repair,
        "zero_idxs": zero_idxs,
    }


def total_from_best(best):
    if any(best[mask] >= 99 for mask in range(1, 32)):
        return None
    return sum(best[1:])


def min_all_subset_R(slots):
    return total_from_best(mask_best_sizes(slots)["all"])


def min_even_subset_R(slots):
    return total_from_best(mask_best_sizes(slots)["even"])


def min_parity_repair_R(slots):
    """Minimum dirty-canceling cost with odd sets repaired at a 0-valued slot.

    An odd realizing set S either contains a 0-valued slot index (drop one:
    cost |S|-1, same XOR) or adjoins one 0-valued slot readout (cost |S|+1).
    Both repairs restore even live-connector parity for arbitrary connector dirt.
    """
    return total_from_best(mask_best_sizes(slots)["repair"])


def all_subset_reads(slots):
    """Minimum-cardinality (any parity) realizing subsets for each nonzero mask."""
    n = len(slots)
    reads = {}
    for mask in range(1, 32):
        found = None
        for size in range(1, n + 1):
            for subset in combinations(range(n), size):
                value = 0
                for i in subset:
                    value ^= slots[i]
                if value == mask:
                    found = subset
                    break
            if found is not None:
                break
        need(found is not None, f"mask {mask} uncovered under all-subset")
        reads[mask] = found
    return reads


def dirt_parity_by_mask(reads):
    """Live-connector dirt parity contributed to each output by a readout schedule."""
    return {mask: len(subset) % 2 for mask, subset in reads.items()}


def odd_dirt_masks(reads):
    return sorted(mask for mask, parity in dirt_parity_by_mask(reads).items() if parity)


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


def enumerate_distinct6_triple_spectrum():
    """One pass: all-subset, even-subset, and parity-repair R on distinct-6 covers."""
    hist_all = Counter()
    hist_even = Counter()
    hist_repair = Counter()
    covering = 0
    witnesses = {"all": {}, "even": {}, "repair": {}}
    repair_matches_even = 0
    for nonzero in combinations(range(1, 32), 6):
        slots = (0,) + nonzero
        info = mask_best_sizes(slots)
        if any(info["even"][m] >= 99 for m in range(1, 32)):
            continue
        all_r = sum(info["all"][1:])
        even_r = sum(info["even"][1:])
        repair_r = sum(info["repair"][1:])
        covering += 1
        hist_all[all_r] += 1
        hist_even[even_r] += 1
        hist_repair[repair_r] += 1
        if repair_r == even_r:
            repair_matches_even += 1
        witnesses["all"].setdefault(all_r, slots)
        witnesses["even"].setdefault(even_r, slots)
        witnesses["repair"].setdefault(repair_r, slots)
    return {
        "covering_sets": covering,
        "all_subset": {
            "attainable_R": sorted(hist_all),
            "histogram": {str(r): hist_all[r] for r in sorted(hist_all)},
            "min_R": min(hist_all) if hist_all else None,
            "first_witnesses": {str(r): list(slots) for r, slots in witnesses["all"].items()},
        },
        "even_subset": {
            "attainable_R": sorted(hist_even),
            "histogram": {str(r): hist_even[r] for r in sorted(hist_even)},
            "min_R": min(hist_even) if hist_even else None,
            "first_witnesses": {str(r): list(slots) for r, slots in witnesses["even"].items()},
        },
        "parity_repair": {
            "attainable_R": sorted(hist_repair),
            "histogram": {str(r): hist_repair[r] for r in sorted(hist_repair)},
            "min_R": min(hist_repair) if hist_repair else None,
            "first_witnesses": {
                str(r): list(slots) for r, slots in witnesses["repair"].items()
            },
            "matches_even_on_covering": repair_matches_even,
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


def champion_analysis():
    slots = EXPECTED["champion_slots"]
    closed = slots + (0,)
    reads = all_subset_reads(slots)
    odd_masks = odd_dirt_masks(reads)
    return {
        "slots": list(slots),
        "path_X": path_X(closed),
        "all_subset_R": min_all_subset_R(slots),
        "even_subset_R": min_even_subset_R(slots),
        "parity_repair_R": min_parity_repair_R(slots),
        "all_subset_odd_dirt_masks": odd_masks,
        "all_subset_odd_dirt_count": len(odd_masks),
        "hypothetical_tariff_all_X6": tariff_qrx(7, min_all_subset_R(slots), 6),
        "tariff_repair_X6": tariff_qrx(7, min_parity_repair_R(slots), 6),
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
    }


def dirt_obstruction_examples():
    """Finite checks: odd live-connector R_m parity leaves connector dirt on y_m."""
    examples = []
    # Abstract F2 dirt: each live R_m flips output dirt; legal iff even.
    for slots, note in (
        (EXPECTED["champion_slots"], "champion_all_subset"),
        ((0, 1, 2, 4, 8, 15, 16), "first_all_subset_66_witness"),
    ):
        reads = all_subset_reads(slots)
        odds = odd_dirt_masks(reads)
        examples.append(
            {
                "note": note,
                "slots": list(slots),
                "odd_dirt_masks": odds,
                "odd_dirt_count": len(odds),
                "legal_under_dirty_cancellation": len(odds) == 0,
                "all_R": min_all_subset_R(slots),
                "repair_R": min_parity_repair_R(slots),
            }
        )
    need(all(ex["odd_dirt_count"] > 0 for ex in examples), "expected odd dirt")
    need(all(not ex["legal_under_dirty_cancellation"] for ex in examples), "illegal")
    return examples


# Credited path-lowered champion from the 789q / #2643 / #2686 lineage.
CHAMPION_7 = (0, 1, 2, 6, 12, 24, 16, 0)
