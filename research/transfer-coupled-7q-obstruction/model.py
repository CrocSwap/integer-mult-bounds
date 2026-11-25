"""Transfer-coupled dual readout at seven queries, shape (5,1,1).

Answers the transfer-coupled open question left by partitioned independent
walks (#2715 / multi-connector lineage / independent-walks-7q): shared prefix,
priced transfer C≥1, divergent length-1 suffixes, total Q=p+a+b=7, dual
even-parity dirt-legal readout with fair shared-prefix XOR billing.

Scoped to the maximal-sharing fork (p,a,b)=(5,1,1) (walks of length 6+6).
Self-contained relative to PR1898 / #2643 / #2686 / #2715 / #2761 / #2764 /
independent-walks. Prepared by Wentao Li with substantial AI assistance.
Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations
from multiprocessing import Pool

INF = 99

EXPECTED = {
    "shape": (5, 1, 1),
    "Q": 7,
    "covering_pairs": 8749440,
    "attainable_R": [84, 88, 90],
    "histogram": {"84": 1458240, "88": 2083200, "90": 5208000},
    "min_R": 84,
    "n_R84": 1458240,
    "min_fair_X_at_R84": 9,
    "champion_prefix": (0, 1, 3, 6, 12),
    "champion_tips": (8, 16),
    "champion_R": 84,
    "champion_fair_X": 9,
    "champion_tariff": 452,
    "tariff_floor": 452,
    "endpoint_tariff_Q6": 436,
    "transfer_C_min": 1,
    "partitioned_min_R": 112,
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tariff_qrx(q, r, x, extra=0):
    """Abstract complete-call tariff at (b,a,x)=(38,2,2), plus optional extras."""
    leaves = 28 * q + r
    nodes = 9 * q
    dispatch = q + r + x
    return leaves + nodes + x + dispatch + extra


def edge_cost(a, b):
    delta = a ^ b
    if delta == 0:
        return None
    return 2 * (delta.bit_count() - 1)


def even_table_nz5(nz5):
    """Even-subset table on slots (0,) + five nonzero labels (order-irrelevant)."""
    slots = (0,) + tuple(nz5)
    even = [INF] * 32
    even[0] = 0
    for bits in range(1, 64):
        size = bits.bit_count()
        if size % 2:
            continue
        value = 0
        for i in range(6):
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


def fair_X(prefix, tip_a, tip_b, C=1):
    """Fair shared-prefix XOR bill: prefix edges once + transfer C + both tip chains.

    Each tip chain is (prefix_end → tip → 0). Prefix must start at 0.
    """
    need(type(prefix) is tuple and prefix and prefix[0] == 0, "prefix starts at 0")
    need(C >= 1, "priced transfer C>=1")
    x = 0
    prev = prefix[0]
    for v in prefix[1:]:
        c = edge_cost(prev, v)
        if c is None:
            return None
        x += c
        prev = v
    x += C
    pend = prefix[-1]
    for tip in (tip_a, tip_b):
        c = edge_cost(pend, tip)
        if c is None:
            return None
        x += c
        c = edge_cost(tip, 0)
        if c is None:
            return None
        x += c
    return x


def min_path_costs_to_ends(nonzero_prefix):
    """Min Hamiltonian path cost from 0 through all nonzero prefix labels, by end."""
    best = {p: INF for p in nonzero_prefix}
    for pref in permutations(nonzero_prefix):
        cost = 0
        prev = 0
        ok = True
        for v in pref:
            c = edge_cost(prev, v)
            if c is None:
                ok = False
                break
            cost += c
            prev = v
        if not ok:
            continue
        pend = pref[-1]
        if cost < best[pend]:
            best[pend] = cost
    return best


def fair_X_lower_bound(nonzero_prefix, tip_a, tip_b, path_to, C=1):
    """Exact min over prefix orders of fair_X, via end-point decomposition."""
    close = 2 * (tip_a.bit_count() - 1) + 2 * (tip_b.bit_count() - 1)
    best = INF
    for pend in nonzero_prefix:
        ca = edge_cost(pend, tip_a)
        cb = edge_cost(pend, tip_b)
        if ca is None or cb is None:
            continue
        pc = path_to[pend]
        if pc >= INF:
            continue
        lb = pc + C + ca + cb + close
        if lb < best:
            best = lb
    return None if best >= INF else best


def min_fair_X_over_orders(nonzero_prefix, tip_a, tip_b, C=1):
    best = None
    for pref in permutations(nonzero_prefix):
        prefix = (0,) + pref
        x = fair_X(prefix, tip_a, tip_b, C)
        if x is None:
            continue
        if best is None or x < best[0]:
            best = (x, prefix)
    return best


def _process_prefix_set(P):
    """Worker: census tip pairs for one 4-set prefix; track R=84 X bounds."""
    P = tuple(P)
    rem = [x for x in range(1, 32) if x not in P]
    tables = {t: even_table_nz5(P + (t,)) for t in rem}
    path_to = min_path_costs_to_ends(P)
    local = Counter()
    covering = 0
    n84 = 0
    min_x = INF
    witness = None
    for i, a in enumerate(rem):
        ea = tables[a]
        reach0 = [(x, ea[x]) for x in range(32) if ea[x] < INF]
        for b in rem[i + 1 :]:
            e1 = tables[b]
            total = 0
            ok = True
            for m in range(1, 32):
                best = INF
                for x, c0 in reach0:
                    c1 = e1[x ^ m]
                    if c1 < INF:
                        cost = c0 + c1
                        if cost < best:
                            best = cost
                if best >= INF:
                    ok = False
                    break
                total += best
            if not ok:
                continue
            covering += 1
            local[total] += 1
            if total != 84:
                continue
            n84 += 1
            lb = fair_X_lower_bound(P, a, b, path_to, C=1)
            if lb is None:
                continue
            if lb <= 9:
                exact = min_fair_X_over_orders(P, a, b, C=1)
                if exact is None:
                    continue
                x, prefix = exact
                need(x >= lb, "fair X below decomposed lower bound")
                if x < min_x:
                    min_x = x
                    witness = (prefix, a, b, x)
    return covering, dict(local), n84, min_x, witness


def enumerate_511(workers=None):
    """Full distinct-label (5,1,1) dual census with fair-X floor on R=84."""
    prefix_sets = list(combinations(range(1, 32), 4))
    hist = Counter()
    covering = 0
    n84 = 0
    min_x = INF
    witness = None
    with Pool(processes=workers) as pool:
        for c, local, n, mx, w in pool.imap_unordered(
            _process_prefix_set, prefix_sets, chunksize=32
        ):
            covering += c
            hist.update(local)
            n84 += n
            if mx < min_x:
                min_x = mx
                witness = w
    need(covering > 0, "expected covering pairs")
    need(min_x < INF and witness is not None, "expected R=84 witness")
    attainable = sorted(hist)
    return {
        "kind": "transfer_coupled_5_1_1",
        "Q": 7,
        "shape": [5, 1, 1],
        "covering_pairs": covering,
        "n_R84": n84,
        "attainable_R": attainable,
        "histogram": {str(r): hist[r] for r in attainable},
        "min_R": min(attainable),
        "min_fair_X_at_R84": min_x,
        "champion": {
            "prefix": list(witness[0]),
            "tips": [witness[1], witness[2]],
            "R": 84,
            "fair_X": witness[3],
            "tariff": tariff_qrx(7, 84, witness[3]),
            "transfer_C": 1,
        },
        "tariff_floor": tariff_qrx(7, 84, min_x),
        "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
    }


def champion_recompute():
    """Recompute dual R and fair X on the pinned champion (not copied)."""
    prefix = EXPECTED["champion_prefix"]
    a, b = EXPECTED["champion_tips"]
    nz0 = prefix[1:] + (a,)
    nz1 = prefix[1:] + (b,)
    r = dual_independent_R(even_table_nz5(nz0), even_table_nz5(nz1))
    x = fair_X(prefix, a, b, C=1)
    need(r == EXPECTED["champion_R"], f"champion R {r}")
    need(x == EXPECTED["champion_fair_X"], f"champion X {x}")
    t = tariff_qrx(7, r, x)
    need(t == EXPECTED["champion_tariff"], f"champion tariff {t}")
    need(t > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    return {
        "prefix": list(prefix),
        "tips": [a, b],
        "walks": [list(prefix + (a,)), list(prefix + (b,))],
        "R": r,
        "fair_X": x,
        "transfer_C": 1,
        "tariff": t,
    }


def r_undercut_threshold():
    """At Q=7, undercutting 436 requires R+X < 85 (with C folded into X)."""
    # 38*7 + 2(R+X) < 436 ⇒ R+X < 85
    return 85


def other_shape_samples():
    """Spot samples: shapes with observed min R≥86 cannot undercut (R+X≥86>85)."""
    from random import Random

    rng = Random(0)

    def sample_shape(p_nz, a_len, b_len, trials=4000):
        min_r = INF
        covering = 0
        best = None
        labels = list(range(1, 32))
        for _ in range(trials):
            if p_nz:
                P = tuple(sorted(rng.sample(labels, p_nz)))
            else:
                P = ()
            rem = [x for x in labels if x not in P]
            A = tuple(sorted(rng.sample(rem, a_len)))
            rem2 = [x for x in rem if x not in A]
            B = tuple(sorted(rng.sample(rem2, b_len)))
            slots0 = (0,) + P + A
            slots1 = (0,) + P + B

            def even_slots(slots):
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

            r = dual_independent_R(even_slots(slots0), even_slots(slots1))
            if r is None:
                continue
            covering += 1
            if r < min_r:
                min_r = r
                best = {"P": list(P), "A": list(A), "B": list(B), "R": r}
        return {
            "covering_samples": covering,
            "min_R_observed": None if min_r >= INF else min_r,
            "best": best,
            "cannot_undercut_if_R_ge_86": (min_r >= 86) if min_r < INF else None,
        }

    return {
        "threshold_R_plus_X": r_undercut_threshold(),
        "shape_4_1_2": sample_shape(3, 1, 2),
        "shape_3_2_2": sample_shape(2, 2, 2),
        "shape_3_1_3": sample_shape(2, 1, 3),
        "note": (
            "Samples only; not a full other-shape census. Observed minima ≥86 "
            "already forbid undercutting at Q=7 because R+X≥86>85."
        ),
    }


def transfer_C_controls():
    """C=0 is outside the priced-transfer interface; C≥1 is required."""
    prefix = EXPECTED["champion_prefix"]
    a, b = EXPECTED["champion_tips"]
    try:
        fair_X(prefix, a, b, C=0)
        c0_rejected = False
    except ValueError:
        c0_rejected = True
    x1 = fair_X(prefix, a, b, C=1)
    return {
        "C0_rejected_by_need": c0_rejected,
        "C1_fair_X": x1,
        "transfer_C_min": 1,
    }
