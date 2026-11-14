"""P104 methods: signed-row group rule, Rado transversal test, and LU into elementary ADDs (FANOUTOPT's exact group algebra).

Standard library only, exact Fractions. Source lane: FANOUTOPT (RESULT.md section 1 "Group rule", Lemma 1, "One helper can
fix a deficit of 2"; build2.ops_from_T). This file is a small ABSTRACT demo of the algebra, not the FANOUT56 geometry.

Model [P, FANOUTOPT section 1]. A group of m co-located members holds incoming need rows R (m x d, rows in Q^d), row space
Omega, rank r. Member p leaves for a frame whose allowed coordinate set is A'_p, so its outgoing row must lie in
Omega_p = Omega  intersect  R^{A'_p}.  Every ADD (row_x += c * row_y) is a transvection, so the group's total effect is
N = T R with T in SL(m).  The group is feasible (without new helpers) iff one vector v_p in Omega_p can be chosen per member
with the v_p spanning Omega (Rado); then N = (v_p) is reached from R by some T in SL, realised by LU as transvections.
A helper is a member with a free signed incoming row h that leaves with row 0 (A' = empty set).

Rado test used here (exact): max independent partial transversal size = min over member subsets S of
(dim sum_{p in S} Omega_p + m - |S|)   [matroid Rado/Hall deficiency form, linear matroid].  Feasible iff that is >= r.
A transversal is then constructed (random integer combinations) and verified in Fractions, so every "feasible" verdict
carries an exact certificate, and every "infeasible" verdict is cross-checked by brute force (small-integer box).

Checked (all exact):
  (a) case (i): a feasible group: certificate, T in SL by LU, replay of the ADDs gives every member its chosen row;
  (b) case (ii): two proportional members leaving on different coordinate sets: Omega_1 = Omega_2 = {0}, infeasible
      without a helper; infeasible by brute force too; ONE helper with a free signed row fixes it (deficit 2 -> 0), the
      helper leaves with row 0, ADD replay exact;
  (c) control (iii): helpers whose row is restricted to a single coordinate e_k (the old pure-helper rule, modelled as a
      restriction of the helper row) fail on the same group for every k, while a free signed row succeeds;
  (d) seeded random sweep: Rado verdict == brute-force verdict (box [-3,3]) on every instance; every feasible verdict has
      an exact replayed certificate;
  (e) group rule controls: a transversal that does not span is rejected by the verifier; a corrupted ADD list fails replay.
The lane's full build is QUOTED, not reproduced here: F = 408.68 D0/call with 50 helpers vs FANOUT56's 1,692.1 (4.14x),
proved floor 315.05  [lane exact run, not reproduced in this package].
Prints PASS_METHODS_RADO_LU."""
import itertools, random, sys
from fractions import Fraction as Fr


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


# ------------------------------------------------------------------------------------------------ linear algebra
def rref(rows):
    """Reduced row echelon basis (list of rows) of the row space; exact."""
    A = [[Fr(x) for x in r] for r in rows]
    out = []
    ncol = len(A[0]) if A else 0
    piv = []
    for c in range(ncol):
        p = next((i for i in range(len(out), len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        k = len(out)
        A[k], A[p] = A[p], A[k]
        A[k] = [x / A[k][c] for x in A[k]]
        for i in range(len(A)):
            if i != k and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[k])]
        out.append(A[k])
        piv.append(c)
    return out[:len(piv)]


def rank(rows):
    return len(rref(rows)) if rows else 0


def left_null(M, ncols=None):
    """Basis of {w : w M = 0} for M given as list of rows (m x k); returns list of m-vectors."""
    m = len(M)
    k = ncols if ncols is not None else (len(M[0]) if M else 0)
    if k == 0:
        return [[Fr(int(i == j)) for j in range(m)] for i in range(m)]
    # nullspace of M^T (k x m)
    A = [[Fr(M[i][j]) for i in range(m)] for j in range(k)]
    pivc, r = [], 0
    for c in range(m):
        p = next((i for i in range(r, k) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        A[r] = [x / A[r][c] for x in A[r]]
        for i in range(k):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        pivc.append(c)
        r += 1
    out = []
    for f in range(m):
        if f in pivc:
            continue
        v = [Fr(0)] * m
        v[f] = Fr(1)
        for i, c in enumerate(pivc):
            v[c] = -A[i][f]
        out.append(v)
    return out


def omega_section(B, A, d):
    """Basis of Omega_p = rowspace(B) intersect R^{A}: vectors x B with zero entries outside A."""
    if not B:
        return []
    outside = [j for j in range(d) if j not in A]
    sub = [[b[j] for j in outside] for b in B]
    W = left_null(sub, len(outside))
    vecs = [[sum(w[i] * B[i][j] for i in range(len(B))) for j in range(d)] for w in W]
    return rref(vecs) if vecs else []


# ------------------------------------------------------------------------------------------------ Rado test
def rado_max_transversal(R, exits, d):
    """(rank r of Omega, max independent partial transversal size, Omega_p bases) by the exact deficiency formula."""
    B = rref(R)
    r = len(B)
    secs = [omega_section(B, set(A), d) for A in exits]
    m = len(exits)
    best = m + 0
    for k in range(m + 1):
        for S in itertools.combinations(range(m), k):
            rows = [v for p in S for v in secs[p]]
            val = (rank(rows) if rows else 0) + m - k
            best = min(best, val)
    return r, min(best, r), secs


def find_transversal(R, exits, d, rng, tries=40):
    """Exact certificate: one vector per member (0 allowed if Omega_p = 0) spanning Omega; None if the test says infeasible."""
    r, mx, secs = rado_max_transversal(R, exits, d)
    if mx < r:
        return None
    for _ in range(tries):
        N = []
        for S in secs:
            v = [Fr(0)] * d
            for b in S:
                c = rng.randint(1, 10 ** 6)
                v = [x + c * y for x, y in zip(v, b)]
            N.append(v)
        if rank(N) == r:
            return N
    raise SystemExit('FAIL: Rado says feasible but no random transversal found')


def verify_transversal(R, exits, N, d):
    """Independent exact check: v_p in Omega_p (zero outside A'_p and in rowspace R) and the v_p span rowspace R."""
    B = rref(R)
    for v, A in zip(N, exits):
        if any(v[j] != 0 for j in range(d) if j not in set(A)):
            return False
        if rank(B + [v]) != len(B):
            return False
    return rank(N) == len(B)


# ------------------------------------------------------------------------------------------------ LU into transvections
def det_and_ops(T):
    """Reduce T (invertible, det d0) to the identity by ADDs only after pre-scaling is excluded: requires det T = 1.
    Returns the ADD list (x, y, c) meaning row_x += c * row_y that carries I -> T when applied to rows of I
    (equivalently R -> T R)."""
    m = len(T)
    M = [[Fr(x) for x in row] for row in T]
    log = []

    def add(x, y, c):
        M[x] = [a + c * b for a, b in zip(M[x], M[y])]
        log.append((x, y, c))
    for k in range(m):
        if M[k][k] == 0:
            j = next((j for j in range(k + 1, m) if M[j][k] != 0), None)
            if j is None:
                raise ValueError('singular')
            add(k, j, Fr(1))
        if k < m - 1:
            if all(M[j][k] == 0 for j in range(k + 1, m)):
                add(k + 1, k, Fr(1))
            j = next(j for j in range(k + 1, m) if M[j][k] != 0)
            if M[k][k] != 1:
                add(k, j, (1 - M[k][k]) / M[j][k])
        else:
            if M[k][k] != 1:
                raise ValueError('det != 1')
        for i in range(m):
            if i != k and M[i][k] != 0:
                add(i, k, -M[i][k])
    assert all(M[i][j] == (1 if i == j else 0) for i in range(m) for j in range(m))
    # E_N ... E_1 T = I  =>  T = E_1^-1 ... E_N^-1 ; applying T to R applies E_N^-1 first
    return [(x, y, -c) for (x, y, c) in reversed(log)]


def determinant(T):
    m = len(T)
    M = [[Fr(x) for x in row] for row in T]
    det = Fr(1)
    for c in range(m):
        p = next((i for i in range(c, m) if M[i][c] != 0), None)
        if p is None:
            return Fr(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            det = -det
        det *= M[c][c]
        for i in range(c + 1, m):
            if M[i][c] != 0:
                f = M[i][c] / M[c][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[c])]
    return det


def solve_T(R, N, rng):
    """T in SL(m) with T R = N' where N' equals N except one row is rescaled to fix det; None if rowspaces differ."""
    R = [[Fr(x) for x in row] for row in R]
    N = [[Fr(x) for x in row] for row in N]
    m = len(R)
    d = len(R[0])
    r = rank(R)
    if rank(N) != r or rank(R + N) != r:
        return None
    # express each N row in an independent row subset I of R
    I = []
    for i in range(m):
        if rank([R[j] for j in I] + [R[i]]) == len(I) + 1:
            I.append(i)
    RI = [[Fr(x) for x in R[i]] for i in I]
    T0 = []
    for v in N:
        # solve c RI = v by elimination on the augmented transpose
        k = len(I)
        A = [[RI[i][j] for i in range(k)] + [v[j]] for j in range(d)]
        pivc, rr = [], 0
        for c in range(k):
            p = next((i for i in range(rr, d) if A[i][c] != 0), None)
            if p is None:
                continue
            A[rr], A[p] = A[p], A[rr]
            A[rr] = [x / A[rr][c] for x in A[rr]]
            for i in range(d):
                if i != rr and A[i][c] != 0:
                    f = A[i][c]
                    A[i] = [x - f * y for x, y in zip(A[i], A[rr])]
            pivc.append(c)
            rr += 1
        c_ = [Fr(0)] * k
        for i, c in enumerate(pivc):
            c_[c] = A[i][k]
        row = [Fr(0)] * m
        for a, i in enumerate(I):
            row[i] = c_[a]
        T0.append(row)
    W = left_null(R, d)                       # rows w with w R = 0
    for _ in range(60):
        T = [row[:] for row in T0]
        for i in range(m):
            for w in W:
                c = Fr(rng.randint(-5, 5))
                T[i] = [a + c * b for a, b in zip(T[i], w)]
        dt = determinant(T)
        if dt == 0:
            continue
        T[0] = [x / dt for x in T[0]]         # rescale row 0 of T (and so of N) to make det 1
        N2 = [[sum(T[i][k] * R[k][j] for k in range(m)) for j in range(d)] for i in range(m)]
        return T, N2
    return None


def apply_ops(R, ops):
    R = [[Fr(x) for x in r] for r in R]
    for x, y, c in ops:
        R[x] = [a + c * b for a, b in zip(R[x], R[y])]
    return R


def realise(R, exits, d, rng):
    """Feasible group -> (N, ops) with ops an exact ADD list taking R to N, N verified as a transversal. None if infeasible."""
    N = find_transversal(R, exits, d, rng)
    if N is None:
        return None
    assert verify_transversal(R, exits, N, d)
    for _ in range(30):
        st = solve_T(R, N, rng)
        if st is None:
            raise SystemExit('FAIL: no T although transversal spans')
        T, N2 = st
        try:
            ops = det_and_ops(T)
        except ValueError:
            continue
        got = apply_ops(R, ops)
        if got != N2:
            raise SystemExit('FAIL: LU replay mismatch')
        assert verify_transversal(R, exits, N2, d)
        return N2, ops
    raise SystemExit('FAIL: LU failed')


def group_with_helper(R, exits, h, d):
    """Add one helper: free incoming row h, exits with row 0 (allowed set empty)."""
    return R + [h], list(exits) + [()]


# ------------------------------------------------------------------------------------------------ brute force
def projective_box(d, bound):
    out = []
    for v in itertools.product(range(-bound, bound + 1), repeat=d):
        if any(v):
            f = next(x for x in v if x)
            if f > 0:
                out.append(v)
    return out


def brute_feasible(R, exits, d, bound=3):
    """Independent check: DFS over small-integer vectors in each Omega_p (zero allowed), looking for a spanning choice."""
    B = rref(R)
    r = len(B)
    pts = projective_box(d, bound)
    cand = []
    for A in exits:
        As = set(A)
        c = [v for v in pts if all(v[j] == 0 for j in range(d) if j not in As) and rank(B + [list(map(Fr, v))]) == r]
        cand.append(c)
    m = len(exits)

    def dfs(i, chosen):
        if rank(chosen) == r:
            return True
        if i == m:
            return False
        # prune: remaining members cannot reach rank r
        if rank(chosen) + (m - i) < r:
            return False
        for v in cand[i]:
            if rank(chosen + [list(map(Fr, v))]) > rank(chosen) and dfs(i + 1, chosen + [list(map(Fr, v))]):
                return True
        return dfs(i + 1, chosen)
    return dfs(0, [])


# ------------------------------------------------------------------------------------------------ demo
def main():
    rng = random.Random(20261113)
    d = 3
    say('ABSTRACT group algebra demo (FANOUTOPT section 1); not the FANOUT56 geometry')

    # (i) feasible group: three members, rows span a plane, each may exit on a pair of coordinates
    R1 = [[1, 1, 0], [0, 1, 1], [1, 2, 1]]
    X1 = [(0, 1), (1, 2), (0, 2)]
    rk1, mx1, _ = rado_max_transversal(R1, X1, d)
    expect('case (i) rank Omega / max transversal', (rk1, mx1), (2, 2))
    N, ops = realise(R1, X1, d, rng)
    expect('case (i) certificate verifies', verify_transversal(R1, X1, N, d), True)
    expect('case (i) replay of %d ADDs reaches N' % len(ops), apply_ops(R1, ops) == N, True)
    expect('case (i) brute force agrees', brute_feasible(R1, X1, d), True)

    # (ii) two proportional members on different coordinate blocks: Omega = span(1,1,1,1), exits {0,1} and {2,3}
    d = 4
    R2 = [[1, 1, 1, 1], [2, 2, 2, 2]]
    X2 = [(0, 1), (2, 3)]
    rk2, mx2, secs2 = rado_max_transversal(R2, X2, d)
    expect('case (ii) Omega_p dimensions (no helper)', [len(s) for s in secs2], [0, 0])
    expect('case (ii) Rado: rank, max transversal (deficit 2: both sections 0)', (rk2, mx2), (1, 0))
    expect('case (ii) infeasible without helper (brute force box [-3,3] agrees)', brute_feasible(R2, X2, d), False)
    h = [1, 1, 0, 0]                          # one helper, FREE signed incoming row, leaves with row 0
    Rh, Xh = group_with_helper(R2, X2, h, d)
    expect('case (ii) with helper %r: sections now' % (h,), [len(s) for s in rado_max_transversal(Rh, Xh, d)[2]], [1, 1, 0])
    Nh, opsh = realise(Rh, Xh, d, rng)
    expect('case (ii) helper exits with row 0', Nh[2], [0, 0, 0, 0])
    expect('case (ii) members leave inside their sections', verify_transversal(Rh, Xh, Nh, d), True)
    expect('case (ii) ADD replay (%d ADDs) exact' % len(opsh), apply_ops(Rh, opsh) == Nh, True)
    expect('case (ii) brute force agrees (feasible with helper)', brute_feasible(Rh, Xh, d), True)
    def fixes(hh):
        Rq, Xq = group_with_helper(R2, X2, list(hh), d)
        return rado_max_transversal(Rq, Xq, d)[1] == rank(Rq)
    nfree = sum(1 for hh in itertools.product(range(-2, 3), repeat=d) if any(hh) and fixes(hh))
    say('     (signed helper rows in [-2,2]^4 that fix it: %d of 624)' % nfree)

    # (iii) control: old pure-helper rule = helper row restricted to a single coordinate e_k
    pure = []
    for k in range(d):
        Rp, Xp = group_with_helper(R2, X2, [int(j == k) for j in range(d)], d)
        pure.append(rado_max_transversal(Rp, Xp, d)[1] == rank(Rp))
    expect('control (iii) pure helper e_k fixes it for k=0..3', pure, [False] * 4)
    # scope note: with single-coordinate exits a pure row can suffice (so the free row matters for blocks)
    R3 = [[1, 1, 0, 0], [2, 2, 0, 0]]
    X3 = [(0,), (1,)]
    Rp, Xp = group_with_helper(R3, X3, [1, 0, 0, 0], d)
    expect('scope: single-coordinate exits, pure e_0 helper suffices', rado_max_transversal(Rp, Xp, d)[1] == rank(Rp), True)

    # (e) group-rule controls
    bad = [[Fr(1), Fr(1), Fr(0), Fr(0)], [Fr(2), Fr(2), Fr(0), Fr(0)], [Fr(0)] * 4]   # transversal that does not span
    expect('control: non-spanning transversal rejected', verify_transversal(Rh, Xh, bad, d), False)
    corrupted = list(opsh)
    x, y, c = corrupted[0]
    corrupted[0] = (x, y, c + 1)
    expect('control: corrupted ADD list fails replay', apply_ops(Rh, corrupted) == Nh, False)

    # (d) seeded sweep: Rado verdict vs brute force
    srng = random.Random(77)
    dd, tot, nfeas, ninf = 3, 0, 0, 0
    for _ in range(120):
        m = srng.randint(2, 4)
        R = [[srng.choice((-1, 0, 0, 1)) for _ in range(dd)] for _ in range(m)]
        if rank(R) == 0:
            continue
        X = [tuple(j for j in range(dd) if srng.random() < 0.45) for _ in range(m)]
        r_, mx, _ = rado_max_transversal(R, X, dd)
        bf = brute_feasible(R, X, dd)
        if (mx == r_) != bf:
            raise SystemExit('FAIL sweep mismatch R=%r X=%r rado=%r brute=%r' % (R, X, (r_, mx), bf))
        tot += 1
        if bf:
            nfeas += 1
            N, ops = realise(R, X, dd, srng)
            if apply_ops(R, ops) != N or not verify_transversal(R, X, N, dd):
                raise SystemExit('FAIL sweep replay')
        else:
            ninf += 1
    say('sweep: %d instances, %d feasible (all with exact transversal + ADD replay), %d infeasible; Rado == brute force on all'
        % (tot, nfeas, ninf))
    expect('sweep covers both verdicts', nfeas > 5 and ninf > 5, True)

    say('Quoted, NOT reproduced here [lane exact run]: FANOUTOPT full build F = 408.68 D0/call with 50 helpers vs FANOUT56 1,692.1 '
        '(4.14x); proved floor 315.05 D0/call.')
    say('PASS_METHODS_RADO_LU')


if __name__ == '__main__':
    main()
