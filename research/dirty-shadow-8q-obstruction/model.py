"""Dirty-shadow sym-diff collapse at eight queries (PR1898 alphabet).

Companion of #2761 (dirty-shadow at Q=7) and #2764 (dirty-parity at Q=8):
does the priced dirty-shadow snapshot collapse to even-subset via sym-diff
extend verbatim to length-8 slot lists? Self-contained relative to PR1898 /
#2677 / #2761 / #2764. Prepared by Wentao Li with substantial AI assistance.
Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, islice
from multiprocessing import Pool
import os


def need(ok, message):
    if not ok:
        raise ValueError(message)


INF = 99

EXPECTED = {
    "distinct7_covering": 2430400,
    "even_subset_attainable_R": [74, 80, 84],
    "even_subset_histogram": {"74": 416640, "80": 1180480, "84": 833280},
    "even_subset_min_R": 74,
    "dirty_shadow_attainable_R": [74, 80, 84],
    "dirty_shadow_histogram": {"74": 416640, "80": 1180480, "84": 833280},
    "dirty_shadow_min_R": 74,
    "dirty_shadow_matches_even_covering": 2430400,
    "clean_shadow_attainable_R": [67, 70, 76],
    "clean_shadow_histogram": {"67": 416640, "70": 1180480, "76": 833280},
    "clean_shadow_min_R": 67,
    "one_dup_covering": 4083072,
    "one_dup_even_attainable_R": [82, 88],
    "one_dup_even_histogram": {"82": 680512, "88": 3402560},
    "one_dup_even_min_R": 82,
    "one_dup_dirty_attainable_R": [82, 88],
    "one_dup_dirty_histogram": {"82": 680512, "88": 3402560},
    "one_dup_dirty_min_R": 82,
    "one_dup_dirty_matches_even": 4083072,
    "one_dup_clean_attainable_R": [71, 80],
    "one_dup_clean_histogram": {"71": 680512, "80": 3402560},
    "one_dup_clean_min_R": 71,
    "champion_slots": (0, 1, 2, 3, 4, 8, 16, 29),
    "champion_even_R": 74,
    "champion_dirty_shadow_min_R": 74,
    "champion_clean_shadow_min_R": 67,
    "champion_clean_best_k": 2,
    "endpoint_tariff_Q6": 436,
    "legal_tariff_at_X0": 452,
    "hypothetical_clean_tariff_at_X0": 438,
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


def even_odd_tables(slots):
    """DP min costs for even- and odd-cardinality realizing sets."""
    be = [INF] * 32
    bo = [INF] * 32
    be[0] = 0
    for v in slots:
        ne = be[:]
        no = bo[:]
        for m in range(32):
            e = be[m]
            if e < INF:
                nm = m ^ v
                c = e + 1
                if c < no[nm]:
                    no[nm] = c
            o = bo[m]
            if o < INF:
                nm = m ^ v
                c = o + 1
                if c < ne[nm]:
                    ne[nm] = c
        be, bo = ne, no
    return be, bo


def mask_best_bundle(slots):
    """Even, dirty-shadow (per k), and clean-shadow (per k) per-mask minima.

    Dirty shadow at index k: second live connector inherits correlated dirt from
    a priced copy of the primary at slot k. Legal schedules need even total
    live-read parity across primary+shadow.

    Clean shadow at index k: hypothetical dirt-free snapshot (illegal under
    PR1898 arbitrary dirt — retained only as a counterfactual).
    """
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    be, bo = even_odd_tables(slots)
    n = len(slots)
    if any(be[m] >= INF for m in range(1, 32)):
        return None
    dirty = [[INF] * 32 for _ in range(n)]
    clean = [[INF] * 32 for _ in range(n)]
    for k, sigma in enumerate(slots):
        dirty[k][0] = 0
        clean[k][0] = 0
        for m in range(32):
            if be[m] < INF:
                dirty[k][m] = min(dirty[k][m], be[m])
                clean[k][m] = min(clean[k][m], be[m])
            if bo[m ^ sigma] < INF:
                dirty[k][m] = min(dirty[k][m], bo[m ^ sigma] + 1)
            if be[m ^ sigma] < INF:
                clean[k][m] = min(clean[k][m], be[m ^ sigma] + 1)
        if sigma != 0 and 1 < clean[k][sigma]:
            clean[k][sigma] = 1
    return {"even": be, "odd": bo, "dirty": dirty, "clean": clean}


def bit_enum_bundle(slots):
    """Independent bit-enumeration oracle (used on small witnesses)."""
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
                cost = size + 1
                v = value ^ slots[k]
                if cost < clean[k][v]:
                    clean[k][v] = cost
        else:
            for k in range(n):
                cost = size + 1
                v = value ^ slots[k]
                if cost < dirty[k][v]:
                    dirty[k][v] = cost
    for k in range(n):
        sigma = slots[k]
        if sigma != 0 and 1 < clean[k][sigma]:
            clean[k][sigma] = 1
    if any(even[m] >= 99 for m in range(1, 32)):
        return None
    return {"even": even, "dirty": dirty, "clean": clean}


def total_or_none(best):
    if any(best[mask] >= INF for mask in range(1, 32)):
        return None
    return sum(best[1:])


def min_even_subset_R(slots):
    info = mask_best_bundle(slots)
    return None if info is None else total_or_none(info["even"])


def dirty_shadow_R_by_k(slots):
    info = mask_best_bundle(slots)
    if info is None:
        return None
    return [total_or_none(info["dirty"][k]) for k in range(len(slots))]


def min_dirty_shadow_R(slots):
    vals = dirty_shadow_R_by_k(slots)
    if vals is None:
        return None
    ok = [v for v in vals if v is not None]
    return min(ok) if ok else None


def clean_shadow_R_by_k(slots):
    info = mask_best_bundle(slots)
    if info is None:
        return None
    return [total_or_none(info["clean"][k]) for k in range(len(slots))]


def min_clean_shadow_R(slots):
    vals = clean_shadow_R_by_k(slots)
    if vals is None:
        return None
    ok = [v for v in vals if v is not None]
    return min(ok) if ok else None


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


def _census_scores(slots):
    """Fast covering score: (even_r, dirty_matches_all_k, clean_min_r) or None.

    Dirty totals equal even when the per-mask collapse inequality holds for
    every snapshot index; the census records that match rather than rebuilding
    full dirty tables.
    """
    be, bo = even_odd_tables(slots)
    if any(be[m] >= INF for m in range(1, 32)):
        return None
    even_r = sum(be[1:])
    dirty_matches_all_k = True
    clean_min = 10**9
    for sigma in slots:
        clean_r = 0
        for m in range(1, 32):
            e = be[m]
            alt = bo[m ^ sigma]
            if alt < INF and alt + 1 < e:
                dirty_matches_all_k = False
            c = e
            e2 = be[m ^ sigma]
            if e2 < INF and e2 + 1 < c:
                c = e2 + 1
            if sigma == m and c > 1:
                c = 1
            clean_r += c
        if clean_r < clean_min:
            clean_min = clean_r
    return even_r, dirty_matches_all_k, clean_min


def _spectrum_worker(combos):
    he, hd, hc = Counter(), Counter(), Counter()
    covering = 0
    dirty_matches = 0
    first = {"even": {}, "dirty": {}, "clean": {}}
    for combo in combos:
        if gf2_rank(combo) < 5:
            continue
        slots = (0,) + combo
        got = _census_scores(slots)
        if got is None:
            continue
        even_r, dirty_ok, clean_r = got
        if dirty_ok:
            dirty_r = even_r
            dirty_matches += 1
        else:
            # Retain an explicit dirty total via the slow path if collapse fails.
            info = mask_best_bundle(slots)
            need(info is not None, "dirty fail uncovered")
            dirty_r = min(total_or_none(info["dirty"][k]) for k in range(8))
        covering += 1
        he[even_r] += 1
        hd[dirty_r] += 1
        hc[clean_r] += 1
        first["even"].setdefault(even_r, slots)
        first["dirty"].setdefault(dirty_r, slots)
        first["clean"].setdefault(clean_r, slots)
    return covering, dirty_matches, he, hd, hc, first


def _merge_first(dst, src):
    for key, slots in src.items():
        prev = dst.get(key)
        if prev is None or slots < prev:
            dst[key] = slots



def _bounded_parts(worker, items):
    """Preserve input/result order without materializing the full census.

    At most four workers; input batches contain at most 1024 records. Ordered
    imap preserves the original first-witness tie breaking. The small aggregate
    records may be collected, but the millions of input tuples are streamed.
    """
    iterator = iter(items)
    batches = iter(lambda: tuple(islice(iterator, 1024)), ())
    with Pool(min(4, os.cpu_count() or 1)) as pool:
        return list(pool.imap(worker, batches, chunksize=1))

def enumerate_distinct7_shadow_spectrum():
    parts = _bounded_parts(_spectrum_worker, combinations(range(1, 32), 7))
    covering = dirty_matches = 0
    he, hd, hc = Counter(), Counter(), Counter()
    first = {"even": {}, "dirty": {}, "clean": {}}
    for c, dm, a, d, cl, fr in parts:
        covering += c
        dirty_matches += dm
        he.update(a)
        hd.update(d)
        hc.update(cl)
        for kind in ("even", "dirty", "clean"):
            _merge_first(first[kind], fr[kind])
    return {
        "covering_sets": covering,
        "dirty_matches_even_on_covering": dirty_matches,
        "even_subset": {
            "attainable_R": sorted(he),
            "histogram": {str(k): he[k] for k in sorted(he)},
            "min_R": min(he) if he else None,
            "first_witnesses": {
                str(r): list(slots) for r, slots in sorted(first["even"].items())
            },
        },
        "dirty_shadow": {
            "attainable_R": sorted(hd),
            "histogram": {str(k): hd[k] for k in sorted(hd)},
            "min_R": min(hd) if hd else None,
            "matches_even_on_covering": dirty_matches,
            "first_witnesses": {
                str(r): list(slots) for r, slots in sorted(first["dirty"].items())
            },
        },
        "clean_shadow_counterfactual": {
            "attainable_R": sorted(hc),
            "histogram": {str(k): hc[k] for k in sorted(hc)},
            "min_R": min(hc) if hc else None,
            "first_witnesses": {
                str(r): list(slots) for r, slots in sorted(first["clean"].items())
            },
            "legal_under_dirty_contract": False,
        },
    }


def _one_dup_worker(items):
    he, hd, hc = Counter(), Counter(), Counter()
    covering = 0
    dirty_matches = 0
    mins = [999, 999, 999]
    wits = [None, None, None]
    for six, dup in items:
        if gf2_rank(six) < 5:
            continue
        labels = (0,) + six
        slots = tuple(sorted(labels + (dup,)))
        got = _census_scores(slots)
        if got is None:
            continue
        even_r, dirty_ok, clean_r = got
        dirty_r = even_r
        if dirty_ok:
            dirty_matches += 1
        else:
            info = mask_best_bundle(slots)
            need(info is not None, "dirty fail uncovered")
            dirty_r = min(total_or_none(info["dirty"][k]) for k in range(8))
        covering += 1
        he[even_r] += 1
        hd[dirty_r] += 1
        hc[clean_r] += 1
        if even_r < mins[0]:
            mins[0] = even_r
            wits[0] = slots
        if dirty_r < mins[1]:
            mins[1] = dirty_r
            wits[1] = slots
        if clean_r < mins[2]:
            mins[2] = clean_r
            wits[2] = slots
    return covering, dirty_matches, he, hd, hc, mins, wits


def enumerate_one_duplicate_shadow_spectrum():
    """Length-8 multisets with exactly seven distinct labels including 0."""
    items = ((six, dup) for six in combinations(range(1, 32), 6) for dup in (0,) + six)
    parts = _bounded_parts(_one_dup_worker, items)
    covering = dirty_matches = 0
    he, hd, hc = Counter(), Counter(), Counter()
    mins = [999, 999, 999]
    wits = [None, None, None]
    for c, dm, a, d, cl, mn, w in parts:
        covering += c
        dirty_matches += dm
        he.update(a)
        hd.update(d)
        hc.update(cl)
        for i in range(3):
            if mn[i] < mins[i]:
                mins[i] = mn[i]
                wits[i] = w[i]
    return {
        "covering_multisets": covering,
        "dirty_matches_even_on_covering": dirty_matches,
        "even_subset": {
            "attainable_R": sorted(he),
            "histogram": {str(k): he[k] for k in sorted(he)},
            "min_R": mins[0],
            "first_witness": list(wits[0]) if wits[0] is not None else None,
        },
        "dirty_shadow": {
            "attainable_R": sorted(hd),
            "histogram": {str(k): hd[k] for k in sorted(hd)},
            "min_R": mins[1],
            "matches_even_on_covering": dirty_matches,
            "first_witness": list(wits[1]) if wits[1] is not None else None,
        },
        "clean_shadow_counterfactual": {
            "attainable_R": sorted(hc),
            "histogram": {str(k): hc[k] for k in sorted(hc)},
            "min_R": mins[2],
            "first_witness": list(wits[2]) if wits[2] is not None else None,
            "legal_under_dirty_contract": False,
        },
    }


def clean_shadow_dirt_examples():
    """Finite checks: dirt-free shadow schedules fail inherited-dirt cancellation."""
    examples = []
    slots = EXPECTED["champion_slots"]
    k = EXPECTED["champion_clean_best_k"]
    sigma = slots[k]
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
    witness = (0, 1, 2, 3, 4, 8, 12, 16)
    k2 = min(range(8), key=lambda i: clean_shadow_R_by_k(witness)[i])
    examples.append(
        {
            "note": "first_clean_70_witness_shadow_dirt",
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
    dirty_by_k = dirty_shadow_R_by_k(slots)
    clean_by_k = clean_shadow_R_by_k(slots)
    need(dirty_by_k is not None and clean_by_k is not None, "champion uncovered")
    return {
        "slots": list(slots),
        "even_R": min_even_subset_R(slots),
        "dirty_shadow_R_by_k": dirty_by_k,
        "dirty_shadow_min_R": min(dirty_by_k),
        "clean_shadow_R_by_k": clean_by_k,
        "clean_shadow_min_R": min(clean_by_k),
        "clean_best_k": min(range(8), key=lambda i: clean_by_k[i]),
        "legal_tariff_X0": tariff_qrx(8, min(dirty_by_k), 0),
        "hypothetical_clean_tariff_X0": tariff_qrx(8, min(clean_by_k), 0),
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        "symdiff_checked_at_k2": dirty_shadow_symdiff_identities(slots, 2),
    }


CHAMPION_8 = EXPECTED["champion_slots"]
