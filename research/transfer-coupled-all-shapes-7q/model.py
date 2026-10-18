"""Transfer-coupled dual readout at seven queries.

Answers open question 1 of #2779 (partitioned independent-walks package): can a
transfer-coupled dual (shared prefix, priced transfer C>=1, divergent suffixes)
undercut tariff 436 after charging walks+transfers+dirt at total Q=7?

Self-contained relative to PR1898 / #2643 / #2686 / #2715 / #2761 / #2779.
Leave-alones are not edited. Prepared by Wentao Li with substantial AI
assistance. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from multiprocessing import Pool

from dual_lib import INF, dual_sum


def need(ok, message):
    if not ok:
        raise ValueError(message)


# Unordered shapes (p,a,b) with p+a+b=7, p,a,b>=1, a<=b.
SHAPES = (
    (1, 1, 5),
    (1, 2, 4),
    (1, 3, 3),
    (2, 1, 4),
    (2, 2, 3),
    (3, 1, 3),
    (3, 2, 2),
    (4, 1, 2),
    (5, 1, 1),
)

EXPECTED = {
    "shapes": {
        "1_1_5": {
            "covering": 3499776,
            "min_R": 92,
            "histogram": {"92": 1416576, "96": 833280, "104": 1249920},
            "champion": {"prefix": [0], "suf_a": [1], "suf_b": [2, 4, 7, 8, 16], "R": 92},
        },
        "1_2_4": {
            "covering": 8749440,
            "min_R": 98,
            "histogram": {"98": 3124800, "104": 5624640},
            "champion": {"prefix": [0], "suf_a": [1, 2], "suf_b": [4, 8, 13, 16], "R": 98},
        },
        "1_3_3": {
            "covering": 5832960,
            "min_R": 100,
            "histogram": {"100": 1805440, "104": 3749760, "112": 277760},
            "champion": {"prefix": [0], "suf_a": [1, 2, 4], "suf_b": [7, 8, 16], "R": 100},
        },
        "2_1_4": {
            "covering": 17498880,
            "min_R": 90,
            "histogram": {"90": 4583040, "92": 4999680, "96": 5416320, "100": 2499840},
            "champion": {"prefix": [0, 1], "suf_a": [2], "suf_b": [4, 8, 14, 16], "R": 90},
        },
        "2_2_3": {
            "covering": 34997760,
            "min_R": 94,
            "histogram": {"94": 7499520, "96": 17498880, "100": 9166080, "104": 833280},
            "champion": {"prefix": [0, 1], "suf_a": [2, 4], "suf_b": [8, 15, 16], "R": 94},
        },
        "3_1_3": {
            "covering": 34997760,
            "min_R": 88,
            "histogram": {"88": 6666240, "90": 7499520, "92": 7499520, "94": 9999360, "96": 3333120},
            "champion": {"prefix": [0, 1, 2], "suf_a": [4], "suf_b": [8, 15, 16], "R": 88},
        },
        "3_2_2": {
            "covering": 26248320,
            "min_R": 90,
            "histogram": {"90": 4374720, "92": 8124480, "94": 7499520, "96": 6249600},
            "champion": {"prefix": [0, 1, 2], "suf_a": [4, 8], "suf_b": [15, 16], "R": 90},
        },
        "4_1_2": {
            "covering": 34997760,
            "min_R": 86,
            "histogram": {"86": 5832960, "88": 3333120, "90": 9999360, "92": 15832320},
            "champion": {"prefix": [0, 1, 2, 7], "suf_a": [8], "suf_b": [12, 16], "R": 86},
        },
        "5_1_1": {
            "covering": 8749440,
            "min_R": 84,
            "histogram": {"84": 1458240, "88": 2083200, "90": 5208000},
            "champion": {"prefix": [0, 4, 8, 15, 18], "suf_a": [1], "suf_b": [2], "R": 84},
        },
    },
    "global_min_R": 84,
    "global_min_shape": (5, 1, 1),
    "second_min_R": 86,
    "second_min_shape": (4, 1, 2),
    "x0_covering_511": 0,
    "min_even_path_X_for_covering": 2,
    "transfer_C": 1,
    "endpoint_tariff_Q6": 436,
    "tariff_floor_critical": 439,
    "partitioned_min_R": 112,
    "same_walk_even_min_R": 82,
}


def shape_key(p, a, b):
    return f"{p}_{a}_{b}"


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


def path_edge_cost(a, b):
    delta = a ^ b
    if delta == 0:
        return None
    return 2 * (delta.bit_count() - 1)


def fair_path_X(prefix, suf_a, suf_b):
    """Fair shared-prefix XOR: prefix internals once; both forks+suffixes+returns."""
    need(prefix and prefix[0] == 0, "prefix starts at 0")
    need(suf_a and suf_b, "divergent suffixes nonempty")
    total = 0
    for u, v in zip(prefix, prefix[1:]):
        cost = path_edge_cost(u, v)
        if cost is None:
            return None
        total += cost
    for suf in (suf_a, suf_b):
        seq = (prefix[-1],) + tuple(suf) + (0,)
        for u, v in zip(seq, seq[1:]):
            cost = path_edge_cost(u, v)
            if cost is None:
                return None
            total += cost
    return total


def walk_slots(prefix, suf):
    return tuple(prefix) + tuple(suf)


def dual_R_from_walks(w0, w1):
    return dual_sum(even_table(w0), even_table(w1))


def _census_chunk(args):
    """Worker: census one chunk of prefix nonzero tuples for shape (p,a,b)."""
    p, a, b, pref_nz_chunk = args
    # Local imports for spawn contexts.
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
    for pn in pref_nz_chunk:
        used = set(pn)
        rem = [x for x in range(1, 32) if x not in used]
        pref = (0,) + tuple(pn)
        Asets = list(_comb(rem, a))
        Atables = {A: _even(pref + A) for A in Asets}
        if a == b:
            for i, A in enumerate(Asets):
                sa = set(A)
                ea = Atables[A]
                for B in Asets[i + 1 :]:
                    if sa & set(B):
                        continue
                    r = _dual(ea, Atables[B])
                    if r is None:
                        continue
                    covering += 1
                    hist[r] += 1
                    if min_r is None or r < min_r:
                        min_r = r
                        champ = (pref, A, B, r)
        else:
            Bsets = list(_comb(rem, b))
            Btables = {B: _even(pref + B) for B in Bsets}
            for A, ea in Atables.items():
                sa = set(A)
                for B, eb in Btables.items():
                    if sa & set(B):
                        continue
                    r = _dual(ea, eb)
                    if r is None:
                        continue
                    covering += 1
                    hist[r] += 1
                    if min_r is None or r < min_r:
                        min_r = r
                        champ = (pref, A, B, r)
    return covering, hist, min_r, champ


def _census_511_chunk(chunk):
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
    for six in chunk:
        for priv in _comb(six, 2):
            shared = tuple(sorted(set(six) - set(priv)))
            sa, sb = priv
            pref = (0,) + shared
            r = _dual(_even(pref + (sa,)), _even(pref + (sb,)))
            if r is None:
                continue
            covering += 1
            hist[r] += 1
            if min_r is None or r < min_r:
                min_r = r
                champ = (pref, (sa,), (sb,), r)
    return covering, hist, min_r, champ


def census_shape(p, a, b, workers=4):
    """Distinct-label transfer-coupled census for shape (p,a,b)."""
    need(p + a + b == 7 and min(p, a, b) >= 1, "shape must partition 7")
    need(a <= b, "normalize a<=b")
    if (p, a, b) == (5, 1, 1):
        sixes = list(combinations(range(1, 32), 6))
        chunks = [sixes[i::workers] for i in range(workers)]
        with Pool(workers) as pool:
            parts = pool.map(_census_511_chunk, chunks)
    else:
        prefs = list(combinations(range(1, 32), p - 1))
        chunks = [prefs[i::workers] for i in range(workers)]
        args = [(p, a, b, ch) for ch in chunks if ch]
        with Pool(workers) as pool:
            parts = pool.map(_census_chunk, args)
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
    need(covering > 0 and min_r is not None, f"no covering for {(p,a,b)}")
    pref, sa, sb, r = champ
    return {
        "shape": (p, a, b),
        "Q": 7,
        "covering_pairs": covering,
        "attainable_R": sorted(hist),
        "histogram": {str(k): hist[k] for k in sorted(hist)},
        "min_R": min_r,
        "champion": {
            "prefix": list(pref),
            "suf_a": list(sa),
            "suf_b": list(sb),
            "R": r,
            "walks": [list(walk_slots(pref, sa)), list(walk_slots(pref, sb))],
        },
    }


def nbrs5(v):
    return [v ^ (1 << i) for i in range(5)]


def x0_covering_count_511():
    """Exhaustive Gray (wt-1 edges) covering count for shape (5,1,1).

    X=0 forces every fair-path edge to have Hamming weight 1. Returns to 0 then
    force suffix labels in {1,2,4,8,16}. Enumerating all distinct wt-1 prefix
    paths of length 4 from 0 and all admissible suffix pairs yields zero
    covering duals.
    """
    paths = [(0,)]
    for _ in range(4):
        paths = [p + (w,) for p in paths for w in nbrs5(p[-1]) if w not in p]
    covering = 0
    for pref in paths:
        end = pref[-1]
        used = set(pref)
        cands = [
            sa
            for sa in (1, 2, 4, 8, 16)
            if sa not in used and (end ^ sa).bit_count() == 1
        ]
        for i, sa in enumerate(cands):
            for sb in cands[i + 1 :]:
                r = dual_R_from_walks(pref + (sa,), pref + (sb,))
                if r is None:
                    continue
                covering += 1
                # Fair X is 0 by construction of the Gray edges.
                need(fair_path_X(pref, (sa,), (sb,)) == 0, "Gray path must have X=0")
    return {"prefix_paths": len(paths), "covering": covering}


def champion_checks():
    """Recompute dual R on every pinned champion; check tariff floors."""
    rows = []
    global_min = None
    for p, a, b in SHAPES:
        key = shape_key(p, a, b)
        exp = EXPECTED["shapes"][key]
        ch = exp["champion"]
        pref = tuple(ch["prefix"])
        sa = tuple(ch["suf_a"])
        sb = tuple(ch["suf_b"])
        need(len(pref) == p and len(sa) == a and len(sb) == b, "champion shape")
        need(pref[0] == 0, "champion prefix")
        need(set(sa).isdisjoint(pref) and set(sb).isdisjoint(pref), "disjoint")
        need(set(sa).isdisjoint(sb), "divergent private labels")
        r = dual_R_from_walks(walk_slots(pref, sa), walk_slots(pref, sb))
        need(r == ch["R"] == exp["min_R"], f"champion R mismatch {key}")
        x = fair_path_X(pref, sa, sb)
        need(x is not None and x % 2 == 0, "fair X even")
        t0 = tariff_qrx(7, r, 0, EXPECTED["transfer_C"])
        t_floor = tariff_qrx(7, r, 0 if r >= 86 else 2, EXPECTED["transfer_C"])
        rows.append(
            {
                "shape": [p, a, b],
                "R": r,
                "fair_X_sample": x,
                "tariff_at_X0_C1": t0,
                "obstruction_tariff_floor": t_floor,
            }
        )
        if global_min is None or r < global_min[0]:
            global_min = (r, (p, a, b))
    need(global_min[0] == EXPECTED["global_min_R"], "global min R")
    need(global_min[1] == EXPECTED["global_min_shape"], "global min shape")
    # Critical: R=84 needs X>=2; R>=86 already safe at X=0.
    crit = tariff_qrx(7, 84, 2, 1)
    safe86 = tariff_qrx(7, 86, 0, 1)
    need(crit == EXPECTED["tariff_floor_critical"], "critical floor")
    need(safe86 == EXPECTED["tariff_floor_critical"], "86 floor")
    need(crit > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(safe86 > EXPECTED["endpoint_tariff_Q6"], "no undercut at 86")
    # Hypothetical illegal X=0 at R=84 would undercut — excluded by X lemma.
    hypo = tariff_qrx(7, 84, 0, 1)
    need(hypo == 435, "hypo arithmetic")
    need(hypo < EXPECTED["endpoint_tariff_Q6"], "hypo would undercut if X=0 legal")
    return {
        "champions": rows,
        "global_min_R": global_min[0],
        "global_min_shape": list(global_min[1]),
        "tariff_floor_critical": crit,
        "hypothetical_R84_X0_C1": hypo,
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
    }


def census_all_shapes(workers=4, shapes=None):
    shapes = list(shapes) if shapes is not None else list(SHAPES)
    out = {}
    for p, a, b in shapes:
        key = shape_key(p, a, b)
        result = census_shape(p, a, b, workers=workers)
        exp = EXPECTED["shapes"][key]
        need(result["covering_pairs"] == exp["covering"], f"{key} covering")
        need(result["min_R"] == exp["min_R"], f"{key} min R")
        need(result["histogram"] == exp["histogram"], f"{key} hist")
        out[key] = result
    return out
