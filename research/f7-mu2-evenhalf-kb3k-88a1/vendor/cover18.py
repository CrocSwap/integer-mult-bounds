"""KB3e engine: the 18-point cover question for F2^7.

Object.  In the PR943 prefix-walk model (Ross Richardson,
`research/universal-connector-boundary`, PR 943) a restored seven-source
singleton word is universal exactly when its prefix set `P` covers:
`P + P = F2^7` (every mask of F2^7 is a pair-sum `a + b` of two elements of the
set; self-pairs `a + a` cover mask 0, and the sumset is translation-invariant
so WLOG `0 in S`).  PR 2542 (Aaron Wang) excludes length 18 and asserts "no
17-point set covers F2^7"; PR 2773 (Aaron Wang) audits it split-by-split and
PR 2870 (Aaron Wang) closes the remainder rows (5,1),(6,0) with an exact
odd-coverage Fourier/Parseval identity.  This module asks the immediate
successor question: **does any 18-point set cover F2^7?**

Parity splits.  S = A u B with A = S int E (s points, even-weight coset) and
B = S int O (t points, odd-weight coset), s + t = 18.  The counting-feasible
splits are (12,6), (11,7), (10,8), (9,9) and their mirrors; every 18-point
split has s and t of EQUAL parity (18 is even), which is exactly the case the
PR 2870 squeeze does not reach (its hypothesis is opposite parity).

Three layers of evidence are computed here, all exact integer arithmetic:

1. `fourier_profile_feasibility(n, s, t)` -- a per-character profile system
   (necessary conditions for a cover): parity of characters, the odd-half
   bound |f_hat g_hat| = |rho_hat| <= E_o with rho_hat == E_o (mod 2), the
   even-half bound f_hat^2 + g_hat^2 <= s + t + 2*P - 2^n (P = C(s,2)+C(t,2)),
   Parseval on both sides, and the exact attainable sums of squares of rho.
   Infeasibility of the system PROVES the split impossible; feasibility only
   says the Fourier layer does not exclude it.  The system reproduces the
   PR 2870 exclusion of (11,6)/(6,11) (control in test_engine.py).
2. `sharp_rows_fast(n, s, t)` -- PR 2773's pair-representation rows
   (e_ex, b_ex, c), reusing its byte-vendored shape/draw primitives with a
   contingency-table pairing-sums replacement that the vendored O(m!) pairing
   loop cannot run at the 18-point row sizes.  Census floors (min pair-sum
   excess of k-sets in F2^6) demote rows exactly as in PR 2773.
3. `search_split(...)` / `search_direct(...)` -- a bounded, seeded local
   search for a covering pair (A, D) resp. an 18-point set.  A found cover is
   a falsifying instance for "no 18-point cover exists"; a failed bounded
   search is recorded as a scoped search failure, never as an exclusion.

Reduction lemma (checked exhaustively at n = 3 in test_engine.py).  Fix an
odd mask p and set D = p + B (a subset of E).  Then S = A u B covers F2^n iff
(i) A + D = E and (ii) (A + A) u (D + D) = E.  So every split (s, t) is a
two-set covering problem in the even group E =~ F2^6.

All arithmetic is exact Python integers; no floats are used.
"""

import random
import time
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))

import agent64_cover17 as c17  # noqa: E402

# Byte pins of the vendored PR 2773 engine (credit: Aaron Wang, PR 2773,
# head 6739c799799621878a9249c93e2b12cc799c1482; extracted with
# agent_tools.py pr-tree-extract from PR 2870's hash-pinned vendor/).
VENDOR_PIN_COVER17 = (
    "082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654"
)
VENDOR_PIN_SEARCH17 = (
    "9eb1bf79ffb99b0efcdaf57916c493bc781abd4a0096d584dc6bc6ca294bf674"
)


# ------------------------------------------------------------- coverage


def dot(s, x):
    return (s & x).bit_count() & 1


def coverage_mask(pts):
    """Bitmask of {a ^ b : a, b in pts} (self-pairs give mask 0)."""
    mask = 1
    for i in range(len(pts)):
        pi = pts[i]
        for j in range(i):
            mask |= 1 << (pi ^ pts[j])
    return mask


def covers(pts, n=7):
    return coverage_mask(pts) == (1 << (1 << n)) - 1


def split_of(pts):
    e = sum(1 for p in pts if not dot(127, p))
    return (e, len(pts) - e)


def even_masks(n=7):
    return [x for x in range(1 << n) if not dot((1 << n) - 1, x)]


def odd_masks(n=7):
    return [x for x in range(1 << n) if dot((1 << n) - 1, x)]


def _pair_mask(pts):
    """Bitmask over the 128 masks of {a ^ b : a, b in pts} (0 via a = b)."""
    return coverage_mask(pts)


def _covers_all(mask, universe):
    return (mask & universe) == universe


def reduction_conditions(A, B, n=7):
    """(odd_ok, even_ok) of the (A, D) reduction.  D = p + B for an odd p;
    A u B covers F2^n iff odd_ok and even_ok both hold."""
    p = 1
    D = [p ^ b for b in B]
    ev = even_masks(n)
    universe = 0
    for x in ev:
        universe |= 1 << x
    cross = 0
    for a in A:
        for d in D:
            cross |= 1 << (a ^ d)
    selfs = _pair_mask(A) | _pair_mask(D)
    return _covers_all(cross, universe), _covers_all(selfs, universe)


# ------------------------------------------------------- rho bookkeeping


def _partitions(total):
    if total == 0:
        yield ()
        return
    for part in range(total, 0, -1):
        for rest in _partitions(total - part):
            if not rest or rest[0] <= part:
                yield (part,) + rest


@lru_cache(maxsize=None)
def rho_square_values(excess):
    """Attainable sums of squares sum rho_x^2 over integer rho >= 0 with
    sum rho_x = excess (partition square sums).  Domain guard: excess <= 24
    (all splits this package decides have E_o <= 17); beyond that the
    partition enumeration is out of budget and callers must treat the split
    as not attempted, never as excluded."""
    if excess > 24:
        raise ValueError("rho_square_values: excess %d out of budget" % excess)
    return sorted({sum(j * j for j in parts) for parts in _partitions(excess)})


# ------------------------------------------------- Fourier profile system


def even_half_max(n, s, t):
    """Max of f_hat^2 + g_hat^2 off the all-ones hyperplane, from the even
    half of the covering condition: s + t + 2*P - 2^n, P = C(s,2)+C(t,2)."""
    P = s * (s - 1) // 2 + t * (t - 1) // 2
    return s + t + 2 * P - (1 << n)


def shapes_fourier(n, s, t, nonzero_both=False):
    """Admissible per-character shapes (f2, g2, p2) = (f_hat^2, g_hat^2,
    (f_hat*g_hat)^2) off {0, 1}: character parities, |rho_hat| <= E_o with
    rho_hat == E_o (mod 2), and the even-half bound.  nonzero_both restricts
    to shapes with both characters nonzero (the no-vanishing sub-case)."""
    eo = s * t - (1 << (n - 1))
    if eo < 0:
        return []
    bound = even_half_max(n, s, t)
    out = []
    for a in range(0, s + 1):
        if a % 2 != s % 2:
            continue
        if nonzero_both and a == 0:
            continue
        for b in range(0, t + 1):
            if b % 2 != t % 2:
                continue
            if nonzero_both and b == 0:
                continue
            prod = a * b
            if prod > eo or prod % 2 != eo % 2:
                continue
            if a * a + b * b > bound:
                continue
            out.append((a * a, b * b, prod * prod))
    return out


def _solve_counts(shapes, U, RF, RG, RP, cap=4000000):
    """First nonneg integer solution of sum n_i = U, sum n_i f2_i = RF,
    sum n_i g2_i = RG, sum n_i p2_i = RP, or None.  Returns (solution, nodes)
    with nodes = "cap" when the step cap is hit (caller must treat as
    undecided, never as infeasible)."""
    m = len(shapes)
    if m == 0:
        if U == 0 and RF == 0 and RG == 0 and RP == 0:
            return ([], 0)
        return (None, 0)
    order = sorted(range(m), key=lambda i: -shapes[i][0])
    shp = [shapes[i] for i in order]
    sol = [0] * m
    nodes = [0]

    # suffix min/max of each coefficient for bound pruning
    smin_f = [0] * (m + 1)
    smax_f = [0] * (m + 1)
    smin_g = [0] * (m + 1)
    smax_g = [0] * (m + 1)
    smin_p = [0] * (m + 1)
    smax_p = [0] * (m + 1)
    for i in range(m - 1, -1, -1):
        f2, g2, p2 = shp[i]
        smin_f[i] = min(f2, smin_f[i + 1])
        smax_f[i] = max(f2, smax_f[i + 1])
        smin_g[i] = min(g2, smin_g[i + 1])
        smax_g[i] = max(g2, smax_g[i + 1])
        smin_p[i] = min(p2, smin_p[i + 1])
        smax_p[i] = max(p2, smax_p[i + 1])

    def rec(i, u_rem, rf, rg, rp):
        nodes[0] += 1
        if nodes[0] > cap:
            return "cap"
        if i == m - 1:
            f2, g2, p2 = shp[i]
            if u_rem >= 0 and rf == u_rem * f2 and rg == u_rem * g2 and rp == u_rem * p2:
                sol[i] = u_rem
                return True
            return False
        f2, g2, p2 = shp[i]
        hi = u_rem
        if f2:
            hi = min(hi, rf // f2)
        if g2:
            hi = min(hi, rg // g2)
        if p2:
            hi = min(hi, rp // p2)
        for k in range(hi, -1, -1):
            ru, rff, rgg, rpp = u_rem - k, rf - k * f2, rg - k * g2, rp - k * p2
            if ru < 0 or rff < 0 or rgg < 0 or rpp < 0:
                continue
            if rff > ru * smax_f[i + 1] or rff < ru * smin_f[i + 1]:
                continue
            if rgg > ru * smax_g[i + 1] or rgg < ru * smin_g[i + 1]:
                continue
            if rpp > ru * smax_p[i + 1] or rpp < ru * smin_p[i + 1]:
                continue
            sol[i] = k
            got = rec(i + 1, ru, rff, rgg, rpp)
            if got == "cap":
                return "cap"
            if got:
                return True
        sol[i] = 0
        return False

    got = rec(0, U, RF, RG, RP)
    if got == "cap":
        return (None, "cap")
    if got:
        out = [0] * m
        for slot, orig in enumerate(order):
            out[orig] = sol[slot]
        return (out, nodes[0])
    return (None, nodes[0])


def fourier_profile_feasibility(n, s, t, nonzero_both=False):
    """Necessary-condition system for an (s,t) split at F2^n.  `feasible`
    False PROVES the odd half (hence the cover) impossible; `feasible` True
    means only that this Fourier layer does not exclude the split.  With
    nonzero_both=True the system is restricted to per-characters with both
    sides nonzero: infeasibility then PROVES every cover of this split must
    have at least one vanishing character off {0, 1}."""
    eo = s * t - (1 << (n - 1))
    res = {
        "n": n,
        "split": (s, t),
        "odd_excess": eo,
        "nonzero_both": nonzero_both,
        "even_half_max": even_half_max(n, s, t),
    }
    if eo < 0:
        res["feasible"] = False
        res["reason"] = "counting: fewer cross pairs than odd masks"
        res["feasible_S"] = []
        return res
    if eo > 24:
        res["feasible"] = None
        res["reason"] = "E_o out of the rho-square enumeration budget: not attempted"
        res["feasible_S"] = []
        return res
    shapes = shapes_fourier(n, s, t, nonzero_both=nonzero_both)
    res["shapes"] = shapes
    U = (1 << n) - 2
    RF = (1 << n) * s - 2 * s * s
    RG = (1 << n) * t - 2 * t * t
    res["parseval_remainders"] = (RF, RG)
    feasible_S = []
    example = None
    capped = False
    for S in rho_square_values(eo):
        RP = (1 << n) * S - 2 * eo * eo
        sol, nodes = _solve_counts(shapes, U, RF, RG, RP)
        if nodes == "cap":
            capped = True
            continue
        if sol is not None:
            feasible_S.append(S)
            if example is None:
                example = {"S": S, "counts": sol}
    res["feasible_S"] = feasible_S
    res["example"] = example
    res["capped"] = capped
    if capped:
        res["feasible"] = True
        res["reason"] = (
            "step cap hit for some S values: undecided for those (never a "
            "proof of impossibility); S values listed are the feasible ones"
        )
    elif feasible_S:
        res["feasible"] = True
        res["reason"] = (
            "profile system consistent for S in %s; no Fourier contradiction"
            % sorted(feasible_S)
        )
    else:
        res["feasible"] = False
        res["reason"] = (
            "profile system infeasible for every attainable rho square sum: "
            "no integer character profile satisfies parity, |rho_hat| <= E_o, "
            "the even-half bound and Parseval simultaneously"
        )
    return res


def witness_constraints_ok(A, B, n=7):
    """Direct validation of every profile-system constraint on an actual
    covering pair (A, B).  Used as the soundness control: a real cover can
    never violate a constraint the system uses."""
    N = 1 << n
    half = 1 << (n - 1)
    eo = len(A) * len(B) - half
    if eo < 0:
        return False
    s, t = len(A), len(B)
    # odd half: r = 1_A * 1_B >= 1 on O
    r = [0] * N
    for a in A:
        for b in B:
            r[a ^ b] += 1
    odds = [x for x in range(N) if dot(N - 1, x)]
    if any(r[x] < 1 for x in odds):
        return False
    rho = {x: r[x] - 1 for x in odds if r[x] > 1}
    if sum(rho.values()) != eo:
        return False
    # even half: A_x + B_x >= 1 on E \ {0}
    pairA = Counter()
    pairB = Counter()
    for i in range(len(A)):
        for j in range(i):
            pairA[A[i] ^ A[j]] += 1
    for i in range(len(B)):
        for j in range(i):
            pairB[B[i] ^ B[j]] += 1
    evs = [x for x in range(N) if not dot(N - 1, x) and x != 0]
    if any(pairA[x] + pairB[x] < 1 for x in evs):
        return False
    P = s * (s - 1) // 2 + t * (t - 1) // 2
    bound = s + t + 2 * P - N
    # characters off {0, 1}
    for u in range(N):
        if u in (0, N - 1):
            continue
        f_hat = sum(1 - 2 * dot(u, a) for a in A)
        g_hat = sum(1 - 2 * dot(u, b) for b in B)
        if f_hat % 2 != s % 2 or g_hat % 2 != t % 2:
            return False
        rho_hat = sum(c * (1 - 2 * dot(u, x)) for x, c in rho.items())
        if f_hat * g_hat != rho_hat:
            return False
        if abs(rho_hat) > eo or rho_hat % 2 != eo % 2:
            return False
        if f_hat * f_hat + g_hat * g_hat > bound:
            return False
    return True


def squeeze_numbers(n, s, t):
    """The PR 2870-style Parseval deficit bookkeeping for one split, extended
    to equal parity: per-side remainders vs the strongest uniform character
    bound the parity class allows."""
    eo = s * t - (1 << (n - 1))
    N = 1 << n
    res = {"n": n, "split": (s, t), "odd_excess": eo}
    if eo < 0:
        res.update(
            bounded_side=None,
            parseval_remainder=None,
            max_allowed=None,
            deficit=None,
            contradiction=True,
            reason="counting: fewer cross pairs than odd masks",
        )
        return res
    opposite = (s % 2) != (t % 2)
    sides = []
    for name, card, par in (("A", s, s % 2), ("B", t, t % 2)):
        remainder = N * card - 2 * card * card
        if opposite and par == 0:
            max_char = 2 * (eo // 2)  # largest even <= E_o
        elif (not opposite) and par == 1:
            max_char = eo if eo % 2 == 1 else eo - 1  # largest odd <= E_o
        else:
            max_char = None  # side can vanish: no uniform bound
        allowed = None if max_char is None else (N - 2) * max_char * max_char
        deficit = None if allowed is None else remainder - allowed
        sides.append(
            dict(
                side=name,
                cardinality=card,
                max_char=max_char,
                parseval_remainder=remainder,
                max_allowed=allowed,
                deficit=deficit,
            )
        )
    res["opposite_parity"] = opposite
    res["sides"] = sides
    if opposite:
        bounded = next(x for x in sides if x["max_char"] is not None)
        res.update(
            bounded_side=bounded["side"],
            parseval_remainder=bounded["parseval_remainder"],
            max_allowed=bounded["max_allowed"],
            deficit=bounded["deficit"],
            contradiction=bounded["deficit"] > 0,
            reason=(
                "PR 2870 squeeze applies (opposite parity): %d > %d"
                % (bounded["parseval_remainder"], bounded["max_allowed"])
                if bounded["deficit"] > 0
                else "PR 2870 squeeze applies but reaches no contradiction"
            ),
        )
    else:
        res.update(
            bounded_side=None,
            parseval_remainder=None,
            max_allowed=None,
            deficit=None,
            contradiction=False,
            reason=(
                "equal character parities (s+t even): PR 2870's squeeze "
                "hypothesis fails for this split; see sides[] for the "
                "equal-parity remainders vs bounds"
            ),
        )
    return res


# ------------------------------------------------------ pairing sums


def pairing_sums(da, db):
    """All sums sum_i a_i b_{pi(i)} over bijections pi of two equal-length
    multisets, by contingency-table enumeration (the vendored O(m!) loop
    cannot run at 18-point row sizes)."""
    ca = Counter(da)
    cb = Counter(db)
    va = sorted(ca)
    vb = sorted(cb)
    acounts = [ca[v] for v in va]
    bcounts = [cb[v] for v in vb]
    out = set()

    def rec(i, caps, acc):
        if i == len(va):
            if all(c == 0 for c in caps):
                out.add(acc)
            return
        need = acounts[i]
        va_i = va[i]

        def dist(j, remaining, add):
            if j == len(vb) - 1:
                if remaining <= caps[j]:
                    caps[j] -= remaining
                    rec(i + 1, caps, acc + add + va_i * vb[j] * remaining)
                    caps[j] += remaining
                return
            for take in range(min(caps[j], remaining) + 1):
                caps[j] -= take
                dist(j + 1, remaining - take, add + va_i * vb[j] * take)
                caps[j] += take

        dist(0, need, 0)

    rec(0, list(bcounts), 0)
    return out


@lru_cache(maxsize=None)
def _pairing_sums_cached(da, db):
    return frozenset(pairing_sums(da, db))


@lru_cache(maxsize=None)
def draw_multisets(shared, budget, min_excess=0):
    """Deduped draws: multisets of `shared` values >= 1 with total excess
    sum(v-1) in [min_excess, budget].  (Embeddable in some multiplicity shape
    of support `shared` + complement with total excess `budget`.)"""
    out = set()

    def rec(lo, remaining, excess_left, acc):
        if remaining == 0:
            out.add(tuple(sorted(acc)))
            return
        for v in range(lo, excess_left + 2):
            new_left = excess_left - (v - 1)
            if new_left < 0:
                break
            rec(v, remaining - 1, new_left, acc + [v])

    for used in range(min_excess, budget + 1):
        rec(1, shared, used, [])
    return sorted(out)


def attainable_c_values(n, s, t, e_ex, b_ex, targets=None, cap=200000):
    """Exact attainable c = sum_x A_x B_x on the shared support positions
    (targets given: only membership in targets is decided).  Returns
    (values_or_flags, status) with status in {"exact", "capped"}."""
    odd_masks_n = 1 << (n - 1)
    even_nonzero = odd_masks_n - 1
    A = s * (s - 1) // 2
    B = t * (t - 1) // 2
    shared = A + B - e_ex - b_ex - even_nonzero
    if shared < 0:
        return (set(), "exact")
    if shared == 0:
        return ({0}, "exact")
    comp_a = A - e_ex - shared
    comp_b = B - b_ex - shared
    das = draw_multisets(shared, e_ex, e_ex if comp_a == 0 else 0)
    dbs = draw_multisets(shared, b_ex, b_ex if comp_b == 0 else 0)
    found = set()
    steps = 0
    for da in das:
        for db in dbs:
            steps += 1
            if steps > cap:
                return (found, "capped")
            vals = _pairing_sums_cached(da, db)
            if targets is not None:
                found |= vals & set(targets)
            else:
                found |= vals
    return (found, "exact")


# ------------------------------------------------------------ rows


def max_attain(e_ex, b_ex, shared):
    """Largest attainable c for one row (rearrangement on the extreme draws)."""
    if shared <= 0:
        return 0
    return (e_ex + 1) * (b_ex + 1) + shared - 1


def sharp_rows_fast(n, s, t, min_e_ex=0, min_b_ex=0, cap=200000):
    """PR 2773's sharp pair-representation rows for one split, with census
    floors applied.  Row status: "sharp" (exact attainability computed),
    "interval" (kept conservatively: exact check capped), "dead" (dropped)."""
    odd_masks_n = 1 << (n - 1)
    even_nonzero = odd_masks_n - 1
    A = s * (s - 1) // 2
    B = t * (t - 1) // 2
    excess = s * t - odd_masks_n
    need = (excess + 1) // 2 if excess > 0 else 0
    c_vals = c17.profile_c_values(n, s, t)
    rows = []
    best = -1
    capped_rows = 0
    if excess < 0 or A + B < even_nonzero:
        return dict(feasible=False, rows=[], best=best, need=need, c_vals=c_vals)
    for e_ex in range(min_e_ex, A + 1):
        for b_ex in range(min_b_ex, B + 1):
            shared = A + B - e_ex - b_ex - even_nonzero
            if shared < 0:
                continue
            attain, status = attainable_c_values(n, s, t, e_ex, b_ex, cap=cap)
            if status == "capped":
                capped_rows += 1
                best = max(best, max_attain(e_ex, b_ex, shared))
                hits = [c for c in c_vals if c <= max_attain(e_ex, b_ex, shared)]
                for c in hits:
                    rows.append(
                        dict(e_ex=e_ex, b_ex=b_ex, shared=shared, c=c, status="interval")
                    )
                continue
            if not attain:
                continue
            best = max(best, max(attain))
            for c in sorted(set(attain) & set(c_vals)):
                rows.append(
                    dict(e_ex=e_ex, b_ex=b_ex, shared=shared, c=c, status="sharp")
                )
    return dict(
        feasible=bool(rows),
        rows=rows,
        best=best,
        need=need,
        c_vals=c_vals,
        capped_rows=capped_rows,
    )


def surviving_rows_fast(n, s, t, min_e_ex=0, min_b_ex=0):
    return sharp_rows_fast(n, s, t, min_e_ex=min_e_ex, min_b_ex=min_b_ex)


# ------------------------------------------------------------- search


def _score_pair(A, D, ev_index):
    """Coverage score of a candidate (A, D) pair over the even group:
    |A + D| + |(A+A) u (D+D)|, target 128 (two sets of 64)."""
    cross = set(a ^ d for a in A for d in D)
    selfs = set(a ^ a2 for i, a in enumerate(A) for a2 in A[i:])
    selfs |= set(d ^ d2 for i, d in enumerate(D) for d2 in D[i:])
    return len(cross) + len(selfs)


def search_split(s, t, restarts=20, seed=1, seconds=20.0, n=7):
    """Bounded seeded local search for a covering pair (A, D) in the even
    group E =~ F2^6 with |A| = s, |D| = t (reduction lemma).  A found pair is
    a falsifying instance; otherwise a scoped search failure."""
    rng = random.Random(seed)
    ev = even_masks(n)
    pool = ev[:]
    best = (0, None)
    t0 = time.time()
    moves = 0
    for _ in range(restarts):
        if time.time() - t0 > seconds:
            break
        A = rng.sample(pool, s)
        D = rng.sample(pool, t)
        sc = _score_pair(A, D, None)
        improved = True
        while improved and time.time() - t0 < seconds:
            improved = False
            for side, size in ((0, s), (1, t)):
                cur = A if side == 0 else D
                outside = [x for x in pool if x not in cur]
                for i in range(size):
                    for v in outside:
                        moves += 1
                        old = cur[i]
                        cur[i] = v
                        new = _score_pair(A, D, None)
                        if new > sc:
                            sc = new
                            improved = True
                            outside[outside.index(v)] = old
                            if sc == 128:
                                return dict(
                                    found=True,
                                    score=128,
                                    A=sorted(A),
                                    D=sorted(D),
                                    restarts=_,
                                    moves=moves,
                                    seconds=round(time.time() - t0, 2),
                                )
                        else:
                            cur[i] = old
        if sc > best[0]:
            best = (sc, (sorted(A), sorted(D)))
    return dict(
        found=False,
        score=best[0],
        best_pair=best[1],
        restarts=restarts,
        moves=moves,
        seconds=round(time.time() - t0, 2),
    )


def search_direct(k=18, restarts=30, seed=1, seconds=20.0, n=7):
    """Bounded seeded local search for a k-point cover of F2^n directly
    (0 in S, translation WLOG)."""
    rng = random.Random(seed)
    pool = list(range(1 << n))
    best = (0, None)
    t0 = time.time()
    for _ in range(restarts):
        if time.time() - t0 > seconds:
            break
        S = [0] + rng.sample(pool[1:], k - 1)
        sc = coverage_mask(S).bit_count()
        improved = True
        while improved and time.time() - t0 < seconds:
            improved = False
            outside = [x for x in pool if x not in S]
            for i in range(1, k):
                for v in outside:
                    old = S[i]
                    S[i] = v
                    new = coverage_mask(S).bit_count()
                    if new > sc:
                        sc = new
                        improved = True
                        outside[outside.index(v)] = old
                        if sc == (1 << n):
                            return dict(
                                found=True,
                                score=sc,
                                S=sorted(S),
                                seconds=round(time.time() - t0, 2),
                            )
                    else:
                        S[i] = old
        if sc > best[0]:
            best = (sc, sorted(S))
    return dict(
        found=False,
        score=best[0],
        best_set=best[1],
        restarts=restarts,
        seconds=round(time.time() - t0, 2),
    )
