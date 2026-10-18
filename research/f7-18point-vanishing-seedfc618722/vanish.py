"""KB3f engine: vanishing-character classification for the 18-point cover
question for F2^7 (set level; no words).

Object (unchanged from PR 2911, which this package presses): in the PR943
prefix-walk model a restored seven-source singleton word is universal exactly
when its prefix set P covers, P + P = F2^7.  A parity split S = A u B has A in
the even coset E (s points), B in the odd coset O (t points), s + t = 18.
PR 2911 PROVED that any (12,6) or (10,8) cover must have a vanishing
character off the all-ones hyperplane; this module classifies those
vanishing configurations and tests each class against coverage of the
remaining masks.

Everything is exact Python integer arithmetic; no floats are used.

Conventions.  The even coset E is identified with F2^6 (m = 6); a character
of E is nontrivial psi_v(x) = (-1)^(v.x), v in 1..2^m-1.  The (A, D)
reduction (PR 2911, PROVEN there): fix an odd p in F2^7 and D = p + B inside
E; S covers iff (i) A + D = E and (ii) (A+A) u (D+D) = E.

Classification lemmas (all machine-checked in test_engine.py):

L2 (halving).  char_sum(A, v) = 0 iff A splits |A|/2 + |A|/2 across
   ker(psi_v); so a vanishing on side A needs s even and forces the split
   (s/2, s/2), and on side D needs t even and forces (t/2, t/2).  At
   (11,7) and (9,9) both sides are odd: NO character can vanish there.

L3 (half-decomposition).  With H = ker(psi_v), H' = E \\ H and A = A0 u A1,
   D = D0 u D1 the two sides of ker(psi_v), coverage is equivalent to
   (A0+D0) u (A1+D1) = H, (A0+D1) u (A1+D0) = H',
   (A0+A0) u (A1+A1) u (D0+D0) u (D1+D1) = H, (A0+A1) u (D0+D1) = H'.

L4 (class floors, exact union-size bounds on L3).  With a split (a0, a1) of
   A and (d0, d1) of D across ker(psi_v), the H'-even line forces
   (F1) a0*a1 + d0*d1 >= 2^(m-1); the H-even line forces
   (F2) sum over the four parts p of (1 + C(p,2) if p >= 1 else 0) >= 2^(m-1);
   the odd lines force (F3) a0*d0 + a1*d1 >= 2^(m-1) and
   (F4) a0*d1 + a1*d0 >= 2^(m-1).  A class whose forced splits violate any
   floor is PROVEN impossible: no cover realizes it.

A class = (vanishing side, forced split of the vanishing side, split of the
other side).  class_table enumerates all classes of a split; classify_cover
decides the classes of a concrete cover; census_f4/census_f5 enumerate the
smallest covers as ground truth for which classes actually occur.
"""

import hashlib
import itertools
import random
import time
from collections import Counter


# ---------------------------------------------------------- F2^n basics


def dot(x, y):
    return (x & y).bit_count() & 1


def char_sum(pts, v):
    """sum over pts of (-1)^(v.x)."""
    return sum(1 - 2 * dot(p, v) for p in pts)


def split_sizes(pts, v, n):
    """(|pts int ker(psi_v)|, |pts \\ ker(psi_v)|)."""
    h0 = sum(1 for p in pts if not dot(v, p))
    return (h0, len(pts) - h0)


def char_representatives(n):
    """One representative per nontrivial character of E: min(v, v ^ all1)."""
    all1 = (1 << n) - 1
    out = []
    for v in range(1, all1):
        if v < (v ^ all1):
            out.append(v)
    return out


def vanishing_set(pts, n):
    """Character-level vanishing set (one entry per nontrivial character)."""
    return {v for v in char_representatives(n) if char_sum(pts, v) == 0}


def vanishing_set_u(pts, n):
    """u-level vanishing set: all indices v off {0, all-ones} with sum 0."""
    all1 = (1 << n) - 1
    return {v for v in range(1, all1) if char_sum(pts, v) == 0}


def sumset_xor(x, y):
    return {a ^ b for a in x for b in y}


def selfsum_xor(x):
    return {a ^ b for i, a in enumerate(x) for b in x[i:]}


def covers_f2n(pts, n):
    cov = selfsum_xor(pts)
    return len(cov) == (1 << n)


def cover_conditions(A, D, m):
    """(A + D = F2^m, (A+A) u (D+D) = F2^m) -- the (A, D) reduction."""
    full = set(range(1 << m))
    odd_ok = sumset_xor(A, D) == full
    even_ok = selfsum_xor(A) | selfsum_xor(D) == full
    return odd_ok, even_ok


# ------------------------------------------------- half decomposition


def half_conditions(A, D, v, m):
    """The four half lines of L3 for character psi_v."""
    A0 = [a for a in A if not dot(v, a)]
    A1 = [a for a in A if dot(v, a)]
    D0 = [d for d in D if not dot(v, d)]
    D1 = [d for d in D if dot(v, d)]
    H = {x for x in range(1 << m) if not dot(v, x)}
    Hp = {x for x in range(1 << m) if dot(v, x)}
    od0 = sumset_xor(A0, D0) | sumset_xor(A1, D1)
    od1 = sumset_xor(A0, D1) | sumset_xor(A1, D0)
    ev0 = selfsum_xor(A0) | selfsum_xor(A1) | selfsum_xor(D0) | selfsum_xor(D1)
    ev1 = sumset_xor(A0, A1) | sumset_xor(D0, D1)
    return (
        H <= od0,
        Hp <= od1,
        H <= ev0,
        Hp <= ev1,
        (len(A0), len(A1), len(D0), len(D1)),
    )


def check_half_decomposition(m, exhaustive=True, samples=0, seed=1):
    """Verify L2 and L3 on every (A, D) pair (m <= 3) or on random samples."""
    rng = random.Random(seed)
    N = 1 << m
    pairs = 0
    if exhaustive:
        sets = []
        for mask in range(1 << N):
            sets.append([x for x in range(N) if (mask >> x) & 1])
        iterator = itertools.product(sets, repeat=2)
    else:
        def rand_iter():
            for _ in range(samples):
                A = [x for x in range(N) if rng.randrange(2)]
                D = [x for x in range(N) if rng.randrange(2)]
                yield (A, D)
        iterator = rand_iter()
    for A, D in iterator:
        pairs += 1
        for v in range(1, N):
            cs = char_sum(A, v)
            a0, a1 = split_sizes(A, v, m)
            l2 = (cs == 0) == (len(A) % 2 == 0 and a0 == len(A) // 2)
            if not l2:
                return dict(ok=False, pairs=pairs, fail="L2", A=A, D=D, v=v)
            od0, od1, ev0, ev1, _ = half_conditions(A, D, v, m)
            direct = cover_conditions(A, D, m)
            if (od0 and od1 and ev0 and ev1) != all(direct):
                return dict(ok=False, pairs=pairs, fail="L3", A=A, D=D, v=v)
    return dict(ok=True, pairs=pairs)


def two_vanishing_structure(A, v1, v2, m):
    """L5 (multi-vanishing structure).  If char_sum(A, v1) = char_sum(A, v2)
    = 0 for distinct characters, the counts of A across the four parts of the
    (ker(psi_v1), ker(psi_v2)) grid are (x, y, y, x) with x + y = |A|/2.
    Returns (counts, ok) where counts = (n00, n01, n10, n11) in the grid."""
    n00 = n01 = n10 = n11 = 0
    for a in A:
        b1, b2 = dot(v1, a), dot(v2, a)
        if b1 == 0 and b2 == 0:
            n00 += 1
        elif b1 == 0:
            n01 += 1
        elif b2 == 0:
            n10 += 1
        else:
            n11 += 1
    ok = n00 == n11 and n01 == n10
    return (n00, n01, n10, n11), ok


def check_multi_vanishing(m):
    """Verify L5 for every subset A of F2^m and every vanishing pair."""
    N = 1 << m
    checked = 0
    for mask in range(1 << N):
        A = [x for x in range(N) if (mask >> x) & 1]
        van = [v for v in range(1, N) if char_sum(A, v) == 0]
        for i in range(len(van)):
            for j in range(i):
                counts, ok = two_vanishing_structure(A, van[j], van[i], m)
                checked += 1
                if not ok:
                    return dict(ok=False, checked=checked, A=A, v=(van[j], van[i]), counts=counts)
    return dict(ok=True, checked=checked)


def sidon_pair(X, Y):
    """All |X|*|Y| sums x+y distinct (no nontrivial common difference)."""
    return len(sumset_xor(X, Y)) == len(X) * len(Y)


def check_tight_equality(m):
    """L7 (equality analysis of the F1 floor).  Whenever a0*a1 + d0*d1 =
    2^(m-1) and the pair (A, D) covers, the H' even line forces
    |A0+A1| = a0*a1 (a Sidon pair), |D0+D1| = d0*d1 (a Sidon pair), and the
    two cross sumsets are disjoint (their union is H')."""
    N = 1 << m
    need = 1 << (m - 1)
    checked = 0
    sets = [[x for x in range(N) if (mask >> x) & 1] for mask in range(1 << N)]
    for A in sets:
        for D in sets:
            if not all(cover_conditions(A, D, m)):
                continue
            for v in range(1, N):
                A0 = [a for a in A if not dot(v, a)]
                A1 = [a for a in A if dot(v, a)]
                D0 = [d for d in D if not dot(v, d)]
                D1 = [d for d in D if dot(v, d)]
                if len(A0) * len(A1) + len(D0) * len(D1) != need:
                    continue
                checked += 1
                sA = sumset_xor(A0, A1)
                sD = sumset_xor(D0, D1)
                if len(sA) != len(A0) * len(A1):
                    return dict(ok=False, checked=checked, fail="A0+A1 not Sidon", A=A, D=D, v=v)
                if len(sD) != len(D0) * len(D1):
                    return dict(ok=False, checked=checked, fail="D0+D1 not Sidon", A=A, D=D, v=v)
                if sA & sD:
                    return dict(ok=False, checked=checked, fail="cross sumsets overlap", A=A, D=D, v=v)
    return dict(ok=True, checked=checked)


# ------------------------------------------------------- class table


def _bound2(part):
    return (1 + part * (part - 1) // 2) if part >= 1 else 0


def class_table(s, t, m=6):
    """All vanishing classes of the split (s, t) at E = F2^m and their floor
    verdicts.  A class: vanishing side A (forced split s/2 + s/2) with the
    other side's split (d0, d1), or vanishing side D (forced t/2 + t/2) with
    the other side's split (a0, a1).  Verdict dead iff some exact floor of L4
    fails; survives-tight iff F1 holds with equality."""
    need = 1 << (m - 1)
    out = {"split": (s, t), "m": m, "floor_need_F1": need, "vanishing_possible": False}

    def floors(a0, a1, d0, d1):
        return {
            "F1": a0 * a1 + d0 * d1,
            "F2": _bound2(a0) + _bound2(a1) + _bound2(d0) + _bound2(d1),
            "F3": a0 * d0 + a1 * d1,
            "F4": a0 * d1 + a1 * d0,
        }

    def entry(vanishing_side, van_split, other_split, a0, a1, d0, d1):
        fl = floors(a0, a1, d0, d1)
        ok = all(v >= need for v in fl.values())
        tight = ok and fl["F1"] == need
        forced = None
        if ok and tight:
            forced = (
                "equality: |A0+A1| = a0*a1 and |D0+D1| = d0*d1 (both Sidon), "
                "the two cross sumsets disjoint with union the whole odd half"
            )
        elif ok and d0 * d1 == 0:
            forced = "D cross sums empty: |A0+A1| = the whole odd half"
        elif ok and a0 * a1 == 0:
            forced = "A cross sums empty: |D0+D1| = the whole odd half"
        return dict(
            vanishing_side=vanishing_side,
            vanishing_split=van_split,
            other_split=other_split,
            splits=dict(A=(a0, a1), D=(d0, d1)),
            floors=fl,
            floor_value=fl["F1"],
            floor_need=need,
            verdict=("survives" if ok else "dead"),
            tight=tight,
            forced=forced,
        )

    A_rows, D_rows = [], []
    if s % 2 == 0:
        out["vanishing_possible"] = True
        for d0 in range(t, (t - 1) // 2, -1):
            d1 = t - d0
            A_rows.append(entry("A", (s // 2, s // 2), (d0, d1), s // 2, s // 2, d0, d1))
    if t % 2 == 0:
        out["vanishing_possible"] = True
        for a0 in range(s, (s - 1) // 2, -1):
            a1 = s - a0
            D_rows.append(entry("D", (t // 2, t // 2), (a0, a1), a0, a1, t // 2, t // 2))
    out["A_vanish"] = A_rows
    out["D_vanish"] = D_rows
    return out


# ---------------------------------------------------- cover census


def classify_cover(S, n):
    """Classify a covering set S of F2^n by its vanishing classes (ground
    truth for 'which characters can vanish')."""
    A = [x for x in S if x.bit_count() % 2 == 0]
    B = [x for x in S if x.bit_count() % 2 == 1]
    D = [1 ^ b for b in B]
    m = n - 1
    need = 1 << (m - 1)
    k_A = vanishing_set(A, n)
    k_D = vanishing_set(D, n)
    rows = []
    dead = []
    for v in sorted(k_A | k_D):
        a0, a1 = split_sizes(A, v, n)
        d0, d1 = split_sizes(D, v, n)
        val = a0 * a1 + d0 * d1
        verdict = "survives" if val >= need else "dead"
        side = ("A" if v in k_A else "") + ("D" if v in k_D else "")
        rows.append((v, side, (a0, a1), (d0, d1), verdict))
        if verdict == "dead":
            dead.append((v, side, (a0, a1), (d0, d1)))
    return dict(
        S=sorted(S),
        split=(len(A), len(B)),
        k_A=len(k_A),
        k_D=len(k_D),
        vanish_rows=rows,
        dead_classes_hit=dead,
    )


def _aggregate(rec, agg, class_agg):
    agg[("%d_%d" % rec["split"], rec["k_A"], rec["k_D"])] += 1
    for (v, side, a_sp, d_sp, verdict) in rec["vanish_rows"]:
        class_agg[(side, a_sp, d_sp, verdict)] += 1


def _ser_agg(agg):
    return sorted(["%s kA=%d kD=%d" % k, v] for k, v in agg.items())


def _ser_class_agg(class_agg):
    return sorted(
        ["%s a=%d,%d d=%d,%d %s" % (side, a_sp[0], a_sp[1], d_sp[0], d_sp[1], verdict), v]
        for (side, a_sp, d_sp, verdict), v in class_agg.items()
    )


def census_f4(keep=100):
    """Exhaustive: every subset S of F2^4 with S + S = F2^4, classified."""
    N = 16
    full = set(range(N))
    pair = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            pair[i][j] = i ^ j
    agg = Counter()
    class_agg = Counter()
    covers = []
    covers_total = 0
    dead_hit = []
    for mask in range(1, 1 << N):
        S = [x for x in range(N) if (mask >> x) & 1]
        cov = {0}
        for i in range(len(S)):
            for j in range(i):
                cov.add(pair[S[i]][S[j]])
        if cov != full:
            continue
        covers_total += 1
        rec = classify_cover(S, 4)
        _aggregate(rec, agg, class_agg)
        if rec["dead_classes_hit"]:
            dead_hit.append(rec["dead_classes_hit"])
        if len(covers) < keep:
            covers.append(S)
    return dict(
        covers_total=covers_total,
        covers=covers,
        agg=_ser_agg(agg),
        class_agg=_ser_class_agg(class_agg),
        dead_classes_hit=dead_hit,
    )


def census_f5(shard=0, shards=16, keep_covers=5, n=5, k=10, max_combos=None):
    """Shard `shard` of the full k-subset census of F2^n (n = 5, k = 10):
    every k-subset S with S + S = F2^n is classified by vanishing class.
    Independent enumeration route (all C(32,10) combinations) for the
    recorded PR 2773 n5 control value 99,200 ten-point covers.  max_combos
    truncates a shard (smoke tests only; a complete census passes None)."""
    N = 1 << n
    full = (1 << N) - 1
    pairbit = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            pairbit[i][j] = 1 << (i ^ j)
    agg = Counter()
    class_agg = Counter()
    covers = []
    covers_total = 0
    dead_hit = []
    combos = 0
    for S in itertools.combinations(range(N), k):
        if S[0] % shards != shard:
            continue
        combos += 1
        if max_combos is not None and combos > max_combos:
            combos -= 1
            return dict(
                shard=shard,
                shards=shards,
                status="partial",
                combos=combos,
                covers_total=covers_total,
                covers=covers,
                agg=_ser_agg(agg),
                class_agg=_ser_class_agg(class_agg),
                dead_classes_hit=dead_hit,
            )
        cov = 1
        for i in range(k):
            si = S[i]
            row = pairbit[si]
            for j in range(i):
                cov |= row[S[j]]
        if cov != full:
            continue
        covers_total += 1
        rec = classify_cover(list(S), n)
        _aggregate(rec, agg, class_agg)
        if rec["dead_classes_hit"]:
            dead_hit.append(rec["dead_classes_hit"])
        if len(covers) < keep_covers:
            covers.append(sorted(S))
    return dict(
        shard=shard,
        shards=shards,
        status="complete",
        combos=combos,
        covers_total=covers_total,
        covers=covers,
        agg=_ser_agg(agg),
        class_agg=_ser_class_agg(class_agg),
        dead_classes_hit=dead_hit,
    )


# ------------------------------------------------- class-restricted search


def _score_pair(A, D):
    """|A + D| + |(A+A) u (D+D)| as integer bitmasks (target 2^(m+1))."""
    cm = 1
    for a in A:
        for d in D:
            cm |= 1 << (a ^ d)
    sm = 1
    for i, a in enumerate(A):
        for b in A[i:]:
            sm |= 1 << (a ^ b)
    for i, d in enumerate(D):
        for b in D[i:]:
            sm |= 1 << (d ^ b)
    return cm.bit_count() + sm.bit_count()


def search_class(s, t, side, other_split, restarts=20, seed=1, seconds=20.0, m=6):
    """Bounded seeded local search for a covering (A, D) pair in E = F2^m
    constrained to one vanishing class: psi = bit 0 (WLOG under GL(m, 2)),
    the vanishing side split equally across ker(psi), the other side split
    exactly `other_split`.  A found pair is a falsifying instance for the
    class contradiction and (at m = 6) an 18-point cover witness; a failed
    bounded search is a scoped search failure, never an exclusion."""
    rng = random.Random(seed)
    N = 1 << m
    target = 2 * N

    if side == "A_vanish":
        a_h0 = s // 2
        a_h1 = s // 2
        d_h0, d_h1 = other_split
    else:
        d_h0 = t // 2
        d_h1 = t // 2
        a_h0, a_h1 = other_split
    half0 = [x for x in range(N) if not (x & 1)]
    half1 = [x for x in range(N) if (x & 1)]

    def build():
        A = rng.sample(half0, a_h0) + rng.sample(half1, a_h1)
        D = rng.sample(half0, d_h0) + rng.sample(half1, d_h1)
        return A, D

    best = (0, None)
    moves = 0
    t0 = time.time()
    for _ in range(restarts):
        if time.time() - t0 > seconds:
            break
        A, D = build()
        sc = _score_pair(A, D)
        improved = True
        while improved and time.time() - t0 < seconds:
            improved = False
            for cur in (A, D):
                for half in (half0, half1):
                    for i in range(len(cur)):
                        if (cur[i] & 1) != (half[0] & 1):
                            continue
                        for v in half:
                            if v in cur:
                                continue
                            moves += 1
                            old = cur[i]
                            cur[i] = v
                            new = _score_pair(A, D)
                            if new > sc:
                                sc = new
                                improved = True
                                break
                            cur[i] = old
                        if sc == target:
                            break
                    if sc == target:
                        break
                if sc == target:
                    break
            if sc == target:
                return dict(
                    found=True,
                    score=sc,
                    A=sorted(A),
                    D=sorted(D),
                    side=side,
                    other_split=other_split,
                    moves=moves,
                    seconds=round(time.time() - t0, 2),
                )
        if sc > best[0]:
            best = (sc, (sorted(A), sorted(D)))
    return dict(
        found=False,
        score=best[0],
        best_pair=best[1],
        side=side,
        other_split=other_split,
        restarts=restarts,
        moves=moves,
        seconds=round(time.time() - t0, 2),
    )


def search_free(s, t, restarts=20, seed=1, seconds=20.0, m=6):
    """Unconstrained bounded seeded search for a covering (A, D) pair in
    E = F2^m (non-vacuity control for the class-restricted machinery)."""
    rng = random.Random(seed)
    N = 1 << m
    target = 2 * N
    pool = list(range(N))
    best = (0, None)
    t0 = time.time()
    for _ in range(restarts):
        if time.time() - t0 > seconds:
            break
        A = rng.sample(pool, s)
        D = rng.sample(pool, t)
        sc = _score_pair(A, D)
        improved = True
        while improved and time.time() - t0 < seconds:
            improved = False
            for cur, size in ((A, s), (D, t)):
                outside = [x for x in pool if x not in cur]
                for i in range(size):
                    for v in outside:
                        old = cur[i]
                        cur[i] = v
                        new = _score_pair(A, D)
                        if new > sc:
                            sc = new
                            improved = True
                            outside[outside.index(v)] = old
                            if sc == target:
                                return dict(found=True, score=sc, A=sorted(A), D=sorted(D))
                        else:
                            cur[i] = old
        if sc > best[0]:
            best = (sc, (sorted(A), sorted(D)))
    return dict(found=False, score=best[0], best_pair=best[1])


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
