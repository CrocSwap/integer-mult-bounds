"""All-subset / dirty-parity repair at eight queries (PR1898 alphabet).

Answers open question 2 of #2715 (`research/cheaper-readout-7q-obstruction`):
does the dirty-parity collapse apply at Q=8 for all-subset versus even-subset
floors? Self-contained relative to PR1898 / #2677 / #2715. Prepared by Wentao Li
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

# Distinct-7 covering census (length-8 slots = {0}+7 distinct nonzero).
EXPECTED = {
    "distinct7_covering": 2430400,
    "all_subset_attainable_R": [61, 64, 68],
    "all_subset_histogram": {"61": 416640, "64": 1180480, "68": 833280},
    "all_subset_min_R": 61,
    "even_subset_attainable_R": [74, 80, 84],
    "even_subset_histogram": {"74": 416640, "80": 1180480, "84": 833280},
    "even_subset_min_R": 74,
    "parity_repair_attainable_R": [74, 80, 84],
    "parity_repair_histogram": {"74": 416640, "80": 1180480, "84": 833280},
    "parity_repair_min_R": 74,
    "repair_equals_even_count": 2430400,
    "one_dup_covering": 4083072,
    "one_dup_all_subset_attainable_R": [66, 72],
    "one_dup_all_subset_histogram": {"66": 680512, "72": 3402560},
    "one_dup_all_subset_min_R": 66,
    "one_dup_parity_repair_attainable_R": [82, 88],
    "one_dup_parity_repair_histogram": {"82": 680512, "88": 3402560},
    "one_dup_parity_repair_min_R": 82,
    "champion_slots": (0, 1, 2, 3, 4, 8, 16, 29),
    "champion_all_R": 61,
    "champion_even_R": 74,
    "champion_repair_R": 74,
    "endpoint_tariff_Q6": 436,
    "hypothetical_all_subset_tariff_X0": 426,
    "parity_repair_tariff_X0": 452,
    "pr2677_even_distinct_floor": 74,
}


def tariff_qrx(q, r, x):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2)."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch


def gf2_rank(vals):
    basis = []
    for v in vals:
        x = v
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    return len(basis)


def spectrum_totals(slots):
    """DP: (all_total, even_total, repair_total) or Nones if not all-covering.

    Repair tracks whether an odd realizing set already used a 0-valued slot
    (drop) or must adjoin one (add), matching the bit-enumeration model of #2715.
    """
    ba = [INF] * 32
    be = [INF] * 32
    boz = [INF] * 32
    bon = [INF] * 32
    ba[0] = 0
    be[0] = 0
    for v in slots:
        is_zero = v == 0
        na = ba[:]
        ne = be[:]
        noz = boz[:]
        non = bon[:]
        for m in range(32):
            a = ba[m]
            if a < INF:
                nm = m ^ v
                c = a + 1
                if c < na[nm]:
                    na[nm] = c
            e = be[m]
            if e < INF:
                nm = m ^ v
                c = e + 1
                if is_zero:
                    if c < noz[nm]:
                        noz[nm] = c
                else:
                    if c < non[nm]:
                        non[nm] = c
            if boz[m] < INF:
                nm = m ^ v
                c = boz[m] + 1
                if c < ne[nm]:
                    ne[nm] = c
            if bon[m] < INF:
                nm = m ^ v
                c = bon[m] + 1
                if c < ne[nm]:
                    ne[nm] = c
        ba, be, boz, bon = na, ne, noz, non
    has_zero = any(s == 0 for s in slots)
    br = be[:]
    if has_zero:
        for m in range(32):
            if boz[m] < INF:
                br[m] = min(br[m], boz[m] - 1)
            if bon[m] < INF:
                br[m] = min(br[m], bon[m] + 1)

    def tot(best):
        if any(best[m] >= INF for m in range(1, 32)):
            return None
        return sum(best[1:])

    return tot(ba), tot(be), tot(br)


def bit_enum_totals(slots):
    """Independent bit-enumeration oracle (used on small witnesses)."""
    n = len(slots)
    ba = [99] * 32
    be = [99] * 32
    br = [99] * 32
    zero_idxs = [i for i in range(n) if slots[i] == 0]
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size < ba[value]:
            ba[value] = size
        if size % 2 == 0:
            if size < be[value]:
                be[value] = size
            if size < br[value]:
                br[value] = size
        elif zero_idxs:
            includes_zero = any(bits >> i & 1 for i in zero_idxs)
            cost = size - 1 if includes_zero else size + 1
            if cost < br[value]:
                br[value] = cost
    if any(ba[m] >= 99 for m in range(1, 32)):
        return None
    return sum(ba[1:]), sum(be[1:]), sum(br[1:])


def min_all_subset_R(slots):
    got = spectrum_totals(slots)
    return None if got[0] is None else got[0]


def min_even_subset_R(slots):
    got = spectrum_totals(slots)
    return None if got[1] is None else got[1]


def min_parity_repair_R(slots):
    got = spectrum_totals(slots)
    return None if got[2] is None else got[2]


def all_subset_reads(slots):
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
        need(found is not None, f"uncovered mask {mask}")
        reads[mask] = found
    return reads


def odd_dirt_masks(reads):
    return [m for m, subset in reads.items() if len(subset) % 2 == 1]


def _distinct7_worker(combos):
    ha, he, hr = Counter(), Counter(), Counter()
    covering = 0
    match = 0
    mins = [999, 999, 999]
    wits = [None, None, None]
    for combo in combos:
        if gf2_rank(combo) < 5:
            continue
        slots = (0,) + combo
        ta, te, tr = spectrum_totals(slots)
        if ta is None:
            continue
        covering += 1
        ha[ta] += 1
        he[te] += 1
        hr[tr] += 1
        if tr == te:
            match += 1
        if ta < mins[0]:
            mins[0] = ta
            wits[0] = slots
        if te < mins[1]:
            mins[1] = te
            wits[1] = slots
        if tr < mins[2]:
            mins[2] = tr
            wits[2] = slots
    return covering, match, ha, he, hr, mins, wits


def enumerate_distinct7_triple_spectrum():
    combos = list(combinations(range(1, 32), 7))
    n = os.cpu_count() or 4
    chunk = (len(combos) + n - 1) // n
    chunks = [combos[i * chunk : (i + 1) * chunk] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_distinct7_worker, chunks)
    covering = match = 0
    ha, he, hr = Counter(), Counter(), Counter()
    mins = [999, 999, 999]
    wits = [None, None, None]
    for c, m, a, e, r, mn, w in parts:
        covering += c
        match += m
        ha.update(a)
        he.update(e)
        hr.update(r)
        for i in range(3):
            if mn[i] < mins[i]:
                mins[i] = mn[i]
                wits[i] = w[i]
    return {
        "covering_sets": covering,
        "repair_equals_even_count": match,
        "all_subset": {
            "attainable_R": sorted(ha),
            "histogram": {str(k): ha[k] for k in sorted(ha)},
            "min_R": mins[0],
            "first_witness": list(wits[0]) if wits[0] is not None else None,
        },
        "even_subset": {
            "attainable_R": sorted(he),
            "histogram": {str(k): he[k] for k in sorted(he)},
            "min_R": mins[1],
            "first_witness": list(wits[1]) if wits[1] is not None else None,
        },
        "parity_repair": {
            "attainable_R": sorted(hr),
            "histogram": {str(k): hr[k] for k in sorted(hr)},
            "min_R": mins[2],
            "first_witness": list(wits[2]) if wits[2] is not None else None,
        },
    }


def _one_dup_worker(items):
    ha, hr = Counter(), Counter()
    covering = 0
    min_a = min_r = 999
    wit_a = wit_r = None
    for six, dup in items:
        if gf2_rank(six) < 5:
            continue
        labels = (0,) + six
        slots = tuple(sorted(labels + (dup,)))
        ta, _te, tr = spectrum_totals(slots)
        if ta is None:
            continue
        covering += 1
        ha[ta] += 1
        hr[tr] += 1
        if ta < min_a:
            min_a = ta
            wit_a = slots
        if tr < min_r:
            min_r = tr
            wit_r = slots
    return covering, ha, hr, min_a, min_r, wit_a, wit_r


def enumerate_one_duplicate_spectrum():
    """Length-8 multisets with exactly seven distinct labels including 0."""
    items = []
    for six in combinations(range(1, 32), 6):
        labels = (0,) + six
        for dup in labels:
            items.append((six, dup))
    n = os.cpu_count() or 4
    chunk = (len(items) + n - 1) // n
    chunks = [items[i * chunk : (i + 1) * chunk] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_one_dup_worker, chunks)
    covering = 0
    ha, hr = Counter(), Counter()
    min_a = min_r = 999
    wit_a = wit_r = None
    for c, a, r, ma, mr, wa, wr in parts:
        covering += c
        ha.update(a)
        hr.update(r)
        if ma < min_a:
            min_a = ma
            wit_a = wa
        if mr < min_r:
            min_r = mr
            wit_r = wr
    return {
        "covering_multisets": covering,
        "all_subset": {
            "attainable_R": sorted(ha),
            "histogram": {str(k): ha[k] for k in sorted(ha)},
            "min_R": min_a,
            "first_witness": list(wit_a) if wit_a is not None else None,
        },
        "parity_repair": {
            "attainable_R": sorted(hr),
            "histogram": {str(k): hr[k] for k in sorted(hr)},
            "min_R": min_r,
            "first_witness": list(wit_r) if wit_r is not None else None,
        },
    }


def champion_analysis():
    slots = EXPECTED["champion_slots"]
    ca, ce, cr = bit_enum_totals(slots)
    need(ca == EXPECTED["champion_all_R"], "champion all")
    need(ce == EXPECTED["champion_even_R"], "champion even")
    need(cr == EXPECTED["champion_repair_R"], "champion repair")
    reads = all_subset_reads(slots)
    odds = odd_dirt_masks(reads)
    need(len(odds) > 0, "champion must show odd dirt")
    hyp = tariff_qrx(8, ca, 0)
    rep = tariff_qrx(8, cr, 0)
    need(hyp == EXPECTED["hypothetical_all_subset_tariff_X0"], "hyp tariff")
    need(rep == EXPECTED["parity_repair_tariff_X0"], "repair tariff")
    return {
        "slots": list(slots),
        "all_subset_R": ca,
        "even_subset_R": ce,
        "parity_repair_R": cr,
        "odd_dirt_mask_count": len(odds),
        "odd_dirt_masks": odds,
        "hypothetical_tariff_X0": hyp,
        "repair_tariff_X0": rep,
    }


def dirt_obstruction_examples():
    slots = EXPECTED["champion_slots"]
    reads = all_subset_reads(slots)
    examples = []
    for mask, subset in reads.items():
        if len(subset) % 2 == 1:
            examples.append(
                {
                    "mask": mask,
                    "subset_idxs": list(subset),
                    "values": [slots[i] for i in subset],
                    "size": len(subset),
                    "live_connector_parity": "odd",
                }
            )
        if len(examples) >= 5:
            break
    need(len(examples) >= 2, "need dirt examples")
    return examples


CHAMPION_8 = EXPECTED["champion_slots"]
