"""One-repeat transfer-coupled (5,1,1) dual obstruction at seven queries.

Answers open question 1 of #2836 (transfer-coupled-all-shapes): do non-distinct
(repeat-label) layers improve on distinct-label R=84 at shape (5,1,1)?

Self-contained relative to PR1898 / #2836 / #2817 lineage. Leave-alones are not
edited. Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from multiprocessing import Pool

from dual_lib import INF, dual_sum


def need(ok, message):
    if not ok:
        raise ValueError(message)


EXPECTED = {
    "shape": (5, 1, 1),
    "Q": 7,
    "distinct_min_R": 84,
    "prefix_dup_covering": 2499840,
    "prefix_dup_min_R": 98,
    "prefix_dup_histogram": {"98": 2499840},
    "prefix_dup_champion": {
        "prefix": [0, 1, 1, 2, 7],
        "suf_a": [8],
        "suf_b": [16],
        "R": 98,
    },
    "suffix_hit_covering": 1666560,
    "suffix_hit_min_R": 96,
    "suffix_hit_histogram": {"96": 1666560},
    "suffix_hit_champion": {
        "prefix": [0, 1, 2, 4, 9],
        "suf_a": [1],
        "suf_b": [16],
        "R": 96,
    },
    "combined_covering": 4166400,
    "combined_min_R": 96,
    "transfer_C": 1,
    "endpoint_tariff_Q6": 436,
    "tariff_floor": 459,
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


def dual_R_from_walks(w0, w1):
    return dual_sum(even_table(w0), even_table(w1))


def nz_multiset(prefix, sa, sb):
    return Counter(list(prefix[1:]) + [sa, sb])


def is_one_repeat(prefix, sa, sb):
    """Exactly one nonzero label appears twice among the six nonzero slots."""
    need(sa != sb, "divergent suffixes")
    counts = sorted(nz_multiset(prefix, sa, sb).values())
    return counts == [1, 1, 1, 1, 2]


def _prefix_dup_chunk(threes):
    from collections import Counter as _Counter
    from dual_lib import dual_sum as _dual
    from itertools import combinations as _comb

    def _even(slots):
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

    hist = _Counter()
    covering = 0
    min_r = None
    champ = None
    for three in threes:
        for dbl in three:
            others = tuple(x for x in three if x != dbl)
            pref = (0,) + tuple(sorted((dbl, dbl) + others))
            rem = [x for x in range(1, 32) if x not in three]
            for sa, sb in _comb(rem, 2):
                r = _dual(_even(pref + (sa,)), _even(pref + (sb,)))
                if r is None:
                    continue
                covering += 1
                hist[r] += 1
                if min_r is None or r < min_r:
                    min_r = r
                    champ = (pref, (sa,), (sb,), r)
    return covering, hist, min_r, champ


def _suffix_hit_chunk(fours):
    from collections import Counter as _Counter
    from dual_lib import dual_sum as _dual

    def _even(slots):
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

    hist = _Counter()
    covering = 0
    min_r = None
    champ = None
    for four in fours:
        pref = (0,) + four
        for c in four:
            for f in range(1, 32):
                if f in four:
                    continue
                sa, sb = (c, f) if c < f else (f, c)
                r = _dual(_even(pref + (sa,)), _even(pref + (sb,)))
                if r is None:
                    continue
                covering += 1
                hist[r] += 1
                if min_r is None or r < min_r:
                    min_r = r
                    champ = (pref, (sa,), (sb,), r)
    return covering, hist, min_r, champ


def _merge(parts):
    hist = Counter()
    covering = 0
    min_r = None
    champ = None
    for cov, h, mr, ch in parts:
        covering += cov
        hist.update(h)
        if mr is not None and (min_r is None or mr < min_r):
            min_r = mr
            champ = ch
    need(covering > 0 and min_r is not None, "empty one-repeat covering")
    pref, sa, sb, r = champ
    return {
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(k): hist[k] for k in sorted(hist)},
        "min_R": min_r,
        "champion": {
            "prefix": list(pref),
            "suf_a": list(sa),
            "suf_b": list(sb),
            "R": r,
            "walks": [list(pref) + list(sa), list(pref) + list(sb)],
        },
    }


def census_prefix_dup(workers=4):
    """Prefix-internal double: multiset {dbl:2,o1,o2} + fresh divergent suffixes."""
    threes = list(combinations(range(1, 32), 3))
    chunks = [threes[i::workers] for i in range(workers)]
    with Pool(workers) as pool:
        parts = pool.map(_prefix_dup_chunk, chunks)
    return _merge(parts)


def census_suffix_hit(workers=4):
    """One suffix collides with a distinct 4-label prefix; the other is fresh."""
    fours = list(combinations(range(1, 32), 4))
    chunks = [fours[i::workers] for i in range(workers)]
    with Pool(workers) as pool:
        parts = pool.map(_suffix_hit_chunk, chunks)
    return _merge(parts)


def champion_checks():
    rows = []
    for kind, key in (
        ("prefix_dup", "prefix_dup_champion"),
        ("suffix_hit", "suffix_hit_champion"),
    ):
        ch = EXPECTED[key]
        pref = tuple(ch["prefix"])
        sa = tuple(ch["suf_a"])
        sb = tuple(ch["suf_b"])
        need(is_one_repeat(pref, sa[0], sb[0]), f"{kind} one-repeat")
        r = dual_R_from_walks(pref + sa, pref + sb)
        need(r == ch["R"], f"{kind} champion R")
        rows.append({"kind": kind, "R": r, "prefix": list(pref), "suf_a": list(sa), "suf_b": list(sb)})
    floor = tariff_qrx(7, EXPECTED["combined_min_R"], 0, EXPECTED["transfer_C"])
    need(floor == EXPECTED["tariff_floor"], "tariff floor")
    need(floor > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(EXPECTED["combined_min_R"] > EXPECTED["distinct_min_R"], "worsens distinct")
    return {"champions": rows, "tariff_floor": floor}


def full_census(workers=4):
    prefix = census_prefix_dup(workers=workers)
    suffix = census_suffix_hit(workers=workers)
    need(prefix["covering_pairs"] == EXPECTED["prefix_dup_covering"], "P covering")
    need(prefix["min_R"] == EXPECTED["prefix_dup_min_R"], "P min R")
    need(prefix["histogram"] == EXPECTED["prefix_dup_histogram"], "P hist")
    need(suffix["covering_pairs"] == EXPECTED["suffix_hit_covering"], "S covering")
    need(suffix["min_R"] == EXPECTED["suffix_hit_min_R"], "S min R")
    need(suffix["histogram"] == EXPECTED["suffix_hit_histogram"], "S hist")
    combined = prefix["covering_pairs"] + suffix["covering_pairs"]
    need(combined == EXPECTED["combined_covering"], "combined covering")
    need(min(prefix["min_R"], suffix["min_R"]) == EXPECTED["combined_min_R"], "combined min")
    return {"prefix_dup": prefix, "suffix_hit": suffix, "combined_covering": combined}
