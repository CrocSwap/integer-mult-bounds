"""onerank.py -- exact checks behind the ONERANK lane (cards/WILD/ONERANK): the 'exact one-rank law' is a Fredholm tautology,
Lemma LIN (corrections through a drop-dirty wire are linear), Lemma TR (one-block re-solve criterion), and the 'no lower bound'
toy (T = I network that stops rigid at 4 stays; disjoint copies give an unbounded gap).
Standard library only; `python3 -I -B onerank.py` from any cwd; exact arithmetic (Fractions / ints mod 2^31-1); seeded.
The lane toy.py / toy2.py themselves need numpy + the NETCOMPILE-frame engine lin2.py; they are NOT ported.  What is ported here
are the lemma-level checks (self-contained constructions with the same mathematical content), so the 'rigid toy' below is an
independent re-derivation of the toy2 witness (2 wires, meetings carrying M then M^-1), not a replay of lin2.analyse."""
import itertools, random, time, collections
from fractions import Fraction as Fr
T0 = time.time()
P = 2 ** 31 - 1
def ok(msg): print('ok', msg, flush=True)
def check(c, msg):
    if not c: raise AssertionError(msg)

# ---------------------------------------------------------------------------------------------------------------- linear algebra
def rref(M):
    A = [[Fr(x) for x in r] for r in M]; piv = []; r = 0
    nc = len(A[0]) if A else 0
    for c in range(nc):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None: continue
        A[r], A[p] = A[p], A[r]; iv = 1 / A[r][c]; A[r] = [x * iv for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]; A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        piv.append(c); r += 1
        if r == len(A): break
    return A[:r], piv
def rank(M): return len(rref(M)[1]) if M and M[0] else 0
def hcat(A, cols): return [list(r) + [c[i] for c in cols] for i, r in enumerate(A)]
def solve(A, b):
    """exact: x with A x = b, or None."""
    R, piv = rref(hcat(A, [b]))
    n = len(A[0])
    if n in piv: return None
    x = [Fr(0)] * n
    for i, c in enumerate(piv): x[c] = R[i][n]
    return x
def left_witness(A, b):
    """y with y A = 0 and y.b != 0 (Fredholm certificate of infeasibility) or None."""
    At = [list(c) for c in zip(*A)]
    R, piv = rref(At); m = len(A); free = [c for c in range(m) if c not in piv]
    for f in free:
        y = [Fr(0)] * m; y[f] = Fr(1)
        for i, c in enumerate(piv): y[c] = -R[i][f]
        if sum(a * c for a, c in zip(y, b)) != 0: return y
    return None
def lnull(A):
    At = [list(c) for c in zip(*A)]
    R, piv = rref(At); m = len(A); out = []
    for f in [c for c in range(m) if c not in piv]:
        y = [Fr(0)] * m; y[f] = Fr(1)
        for i, c in enumerate(piv): y[c] = -R[i][f]
        out.append(y)
    return out
def matmul(A, B):
    Bt = list(zip(*B)); return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]
def eye(n): return [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
def inv(M):
    n = len(M); R, piv = rref([list(map(Fr, r)) + list(eye(n)[i]) for i, r in enumerate(M)])
    assert piv[:n] == list(range(n)), 'singular'; return [r[n:] for r in R]

# ====================================================================================================================
# 7a. Theorem F (Fredholm): one appended column -> rank rises by 0 or 1, 'misses by exactly one rank' == 'infeasible'
# ====================================================================================================================
def rand_matrix(rng, m, n):
    kind = rng.choice(['dense', 'sparse', 'lowrank'])
    if kind == 'dense': A = [[rng.randint(-3, 3) for _ in range(n)] for _ in range(m)]
    elif kind == 'sparse': A = [[rng.choice([0, 0, 0, 1, -1, 2]) for _ in range(n)] for _ in range(m)]
    else:
        k = rng.randint(1, max(1, min(m, n) - 1)); U = [[rng.randint(-2, 2) for _ in range(k)] for _ in range(m)]
        W = [[rng.randint(-2, 2) for _ in range(n)] for _ in range(k)]
        A = [[sum(U[i][t] * W[t][j] for t in range(k)) for j in range(n)] for i in range(m)]
    return [[Fr(x) for x in r] for r in A], kind

def section_theorem_f(seed=11, trials=3000):
    t = time.time(); rng = random.Random(seed)
    cnt = collections.Counter(); sup_differs = 0; two_col = collections.Counter()
    for _ in range(trials):
        m = rng.randint(2, 7); n = rng.randint(1, 7)
        A, kind = rand_matrix(rng, m, n)
        if rng.random() < 0.5: b = [Fr(rng.randint(-3, 3)) for _ in range(m)]
        else:
            x = [Fr(rng.randint(-2, 2)) for _ in range(n)]; b = [sum(a * c for a, c in zip(r, x)) for r in A]
            if rng.random() < 0.3: b[rng.randrange(m)] += 1        # perturb: usually infeasible
        r1 = rank(A); r2 = rank(hcat(A, [b])); d = r2 - r1
        check(d in (0, 1), 'Theorem F violated: rank rose by %d' % d)
        x = solve(A, b); y = left_witness(A, b)
        if d == 0:
            check(x is not None and all(sum(a * c for a, c in zip(r, x)) == bi for r, bi in zip(A, b)), 'feasible but no solution')
            check(y is None, 'feasible but has a Fredholm witness')
        else:
            check(x is None, 'rank jumped but solvable')
            check(y is not None and all(sum(y[i] * A[i][j] for i in range(m)) == 0 for j in range(n)) and sum(a * c for a, c in zip(y, b)) != 0, 'no Fredholm witness')
            # phi is not canonical: another witness with different support (when the left kernel has dim >= 2)
            Ln = lnull(A)
            if len(Ln) >= 2:
                y2 = [a + c * (1 + rng.randint(1, 3)) for a, c in zip(y, Ln[0] if Ln[0] != y else Ln[1])]
                if sum(a * c for a, c in zip(y2, b)) != 0 and all(sum(y2[i] * A[i][j] for i in range(m)) == 0 for j in range(n)):
                    sup_differs += (tuple(v != 0 for v in y2) != tuple(v != 0 for v in y))
        cnt['d=%d' % d] += 1; cnt[kind] += 1
        # two appended columns (control): rank can rise by 2 (and never by more than 2)
        b2 = [Fr(rng.randint(-3, 3)) for _ in range(m)]
        d2 = rank(hcat(A, [b, b2])) - r1
        check(0 <= d2 <= 2, 'two columns raised rank by %d' % d2); two_col[d2] += 1
    check(cnt['d=0'] > 100 and cnt['d=1'] > 100, 'both outcomes must occur')
    check(two_col[2] > 100, 'control: two appended columns must be able to miss by 2')
    A = [[Fr(1)], [Fr(0)], [Fr(0)]]; b1 = [Fr(0), Fr(1), Fr(0)]; b2 = [Fr(0), Fr(0), Fr(1)]
    check(rank(hcat(A, [b1, b2])) - rank(A) == 2, 'explicit 2-miss')
    ok('ONERANK Theorem F (Fredholm): %d random exact matrices (dense/sparse/low-rank, 2-7 x 1-7), one appended column: rank[A|b]-rank A in {0,1} always (%d zero, %d one); d=0 iff Ax=b has an exact solution, d=1 iff exact left witness y (yA=0, y.b!=0) exists -- "misses by exactly one rank" == "infeasible" (0 violations)' % (trials, cnt['d=0'], cnt['d=1']))
    ok('ONERANK phi not canonical: %d infeasible instances where a second Fredholm witness with a different support exists' % sup_differs)
    ok('ONERANK control: TWO appended columns can miss by 2 (explicit A=e1, b1=e2, b2=e3: rank 1 -> 3; random trials: miss 0/1/2 = %d/%d/%d, never >2) (%.1fs)' % (two_col[0], two_col[1], two_col[2], time.time() - t))

# ====================================================================================================================
# 7b. Lemma LIN: corrections a_i += k_i b_i inserted into G2 are exactly linear iff no source slot is downstream of an earlier target
# ====================================================================================================================
def mat_id(n): return [[int(i == j) for j in range(n)] for i in range(n)]
def mm(A, B):
    n = len(A); m = len(B[0]); k = len(B)
    return [[sum(A[i][t] * B[t][j] for t in range(k)) % P for j in range(m)] for i in range(n)]
def transv(n, a, b, c):
    E = mat_id(n); E[a][b] = c % P; return E            # row_a += c * row_b  acts on a column-state vector
def prod_gates(n, gates):
    C = mat_id(n)
    for (a, b, c) in gates: C = mm(transv(n, a, b, c), C)    # C = E_N ... E_1
    return C
def madd(A, B): return [[(a + b) % P for a, b in zip(r, s)] for r, s in zip(A, B)]

def section_lin(seed=5, trials=1500):
    t = time.time(); rng = random.Random(seed)
    nh = nf = nfeq = nd = 0; nfail_formula_when_hyp = 0
    for _ in range(trials):
        n = rng.randint(3, 6); N = rng.randint(4, 9)
        gate = lambda: (lambda ab: (ab[0], ab[1], rng.randrange(1, P)))(rng.sample(range(n), 2))
        full = [gate() for _ in range(N + 1)]
        use_drop = rng.random() < 0.5
        if use_drop:
            d = rng.randrange(N + 1); G2 = full[:d] + full[d + 1:]; da = full[d][0]
        else: G2 = full[:N]; d = None
        N2 = len(G2)
        m = rng.randint(1, 3); corr = []
        for _ in range(m):
            a, b = rng.sample(range(n), 2); corr.append((rng.randint(0, N2), a, b, rng.randrange(1, P)))   # (position, a, b, k)
        # hypothesis: for all ordered (i, j) with p_i <= p_j, source b_j not reachable from target a_i via G2 gates [p_i, p_j)
        def dirty_from(a0, p0, p1):
            D = {a0}
            for idx in range(p0, p1):
                ga, gb, _ = G2[idx]
                if gb in D: D.add(ga)
            return D
        hyp = True
        for i in range(m):
            for j in range(m):
                if corr[i][0] <= corr[j][0] and corr[j][2] in dirty_from(corr[i][1], corr[i][0], corr[j][0]): hyp = False
        # actual product with insertions (stable by position then list order)
        order = sorted(range(m), key=lambda i: corr[i][0]); seq = []; ci = 0
        for idx in range(N2 + 1):
            while ci < m and corr[order[ci]][0] == idx:
                _, a, b, k = corr[order[ci]]; seq.append((a, b, k)); ci += 1
            if idx < N2: seq.append(G2[idx])
        Cfin = prod_gates(n, seq); C2 = prod_gates(n, G2)
        pred = C2
        for (p, a, b, k) in corr:
            Rp = prod_gates(n, G2[:p]); Sp = prod_gates(n, G2[p:]) if False else None
            # S_p = E_N2 ... E_{p+1}: product of the suffix gates, applied after the prefix
            S = mat_id(n)
            for (ga, gb, gc) in G2[p:]: S = mm(transv(n, ga, gb, gc), S)
            term = [[(k * S[i][a] % P) * Rp[b][j] % P for j in range(n)] for i in range(n)]
            pred = madd(pred, term)
        eq = (pred == Cfin)
        if hyp:
            nh += 1; check(eq, 'Lemma LIN violated (hypothesis holds, formula fails)')
            if use_drop:
                # count instances in which a source slot is dirtied by the drop itself (drop-dirty source)
                for (p, a, b, k) in corr:
                    if p >= d and b in dirty_from(da, d, p): nd += 1; break
        else:
            nf += 1; nfeq += eq
    check(nh > 300 and nf > 100 and nd > 30, 'coverage nh=%d nf=%d nd=%d' % (nh, nf, nd))
    check(nfeq <= nf * 0.05, 'control: when a source is downstream of a target the formula must (nearly always) fail: %d/%d equal' % (nfeq, nf))
    ok('ONERANK Lemma LIN: %d random transvection circuits with 1-3 corrections: %d satisfy the "no source downstream of a target" hypothesis and final = C2 + sum k_i S[:,a_i] R[b_i,:] holds EXACTLY in all %d (0 violations); %d of them have a source dirtied by the dropped gate (drop-dirty relay is a LINEAR source)' % (trials, nh, nh, nd))
    ok('ONERANK Lemma LIN control: %d instances with a source downstream of an earlier target: the linear formula fails in %d/%d (bilinear cross term k_i k_j present; %d coincidental equalities) (%.1fs)' % (nf, nf - nfeq, nf, nfeq, time.time() - t))

# ====================================================================================================================
# 7c. Lemma TR (one-block re-solve) criterion
# ====================================================================================================================
def rand_block(rng, n, Pi):
    while True:
        X = eye(n)
        for i in Pi:
            for j in Pi: X[i][j] = Fr(rng.randint(-3, 3)) + (1 if i == j else 0)
        try: inv(X); return X
        except AssertionError: pass
def section_tr(seed=9, trials=400):
    t = time.time(); rng = random.Random(seed); nsup = nunsup = 0
    for _ in range(trials):
        n = rng.randint(3, 5); nb = rng.randint(3, 5)
        sup = [sorted(rng.sample(range(n), rng.randint(2, min(3, n)))) for _ in range(nb)]
        blocks = [rand_block(rng, n, s) for s in sup]
        j = rng.randrange(nb); Pi = sup[j]
        def prodseq(bs):
            C = eye(n)
            for B in bs: C = matmul(B, C)
            return C
        Pt = prodseq(blocks[:j]); S = prodseq(blocks[j + 1:]); Xo = blocks[j]
        C2 = matmul(S, matmul(Xo, Pt))
        if rng.random() < 0.5: Xnew = rand_block(rng, n, Pi); T = matmul(S, matmul(Xnew, Pt))       # T reachable by re-solving block j
        else: T = rand_block(rng, n, sorted(rng.sample(range(n), rng.randint(2, n))))                  # generic invertible target
        D = matmul(inv(C2), T); Nt = matmul(Pt, matmul([[a - b for a, b in zip(r, e)] for r, e in zip(D, eye(n))], inv(Pt)))
        X = matmul(inv(S), matmul(T, inv(Pt)))
        check(X == matmul(Xo, [[a + b for a, b in zip(r, e)] for r, e in zip(Nt, eye(n))]), 'X = X_o (I + N_t) identity fails')
        supported = all(Nt[a][b] == 0 for a in range(n) for b in range(n) if not (a in Pi and b in Pi))
        inGL = all((X[a][b] == (1 if a == b else 0)) for a in range(n) for b in range(n) if not (a in Pi and b in Pi))
        check(supported == inGL, 'Lemma TR criterion: N_t supported on PixPi must equal X in GL(Pi)')
        if supported: check(matmul(S, matmul(X, Pt)) == T, 're-solved circuit must realise T'); nsup += 1
        else: nunsup += 1
    check(nsup > 50 and nunsup > 50, 'TR coverage')
    ok('ONERANK Lemma TR: %d random block circuits (n=3-5): X = X_o(I+N_t) exact; N_t supported on PixPi <=> the re-solved block lies in GL(Pi) and realises T (%d supported/solvable, %d unsupported/unsolvable by one block; 0 mismatches) (%.1fs)' % (nsup + nunsup, nsup, nunsup, time.time() - t))

# ====================================================================================================================
# 7d. 'No lower bound possible': T = I network, rigid at 4 stays per copy, unbounded gap
# ====================================================================================================================
def rand_gl2(rng):
    while True:
        a, b, c, d = [rng.randint(-3, 3) for _ in range(4)]
        if a * d - b * c != 0: return [[Fr(a), Fr(b)], [Fr(c), Fr(d)]]
def embed(n, w0, w1, B):
    E = eye(n); E[w0][w0], E[w0][w1], E[w1][w0], E[w1][w1] = B[0][0], B[0][1], B[1][0], B[1][1]; return E
def slot_family_feasible(n, blocks_remaining, T):
    """Remaining circuit = list of (w0,w1,B) blocks in time order (each block is a frame where both wires are co-present).
    Linear repair family: single transvection corrections a += k b for (a,b) the two co-present wires, inserted before or
    after a remaining block (a slot lies inside that frame's stay).  final = C2 + sum k S[:,a] R[b,:].  Returns (r1, r2, feasible)."""
    mats = [embed(n, w0, w1, B) for (w0, w1, B) in blocks_remaining]
    C2 = eye(n)
    for E in mats: C2 = matmul(E, C2)
    cols = []
    for pos in range(len(mats) + 1):
        for before in (True, False):
            pass
    slots = []
    for bi, (w0, w1, B) in enumerate(blocks_remaining):
        slots.append((bi, w0, w1)); slots.append((bi + 1, w0, w1))        # position index = number of blocks applied before the slot
    seen = set()
    for (pos, w0, w1) in slots:
        for (a, b) in ((w0, w1), (w1, w0)):
            if (pos, a, b) in seen: continue
            seen.add((pos, a, b))
            R = eye(n)
            for E in mats[:pos]: R = matmul(E, R)
            S = eye(n)
            for E in mats[pos:]: S = matmul(E, S)
            cols.append([S[i][a] * R[b][j] for i in range(n) for j in range(n)])
    A = [[c[r] for c in cols] for r in range(n * n)]
    bvec = [T[i][j] - C2[i][j] for i in range(n) for j in range(n)]
    r1 = rank(A); r2 = rank(hcat(A, [bvec]))
    return r1, r2, r1 == r2

def section_rigid(seed=4):
    t = time.time(); rng = random.Random(seed); stats = []
    # genericity: for most M the linear family cannot repair a lone M (or M^-1) against T = I; a few special M (e.g. M a
    # reflection-like matrix with I-M in the span of the four slot terms) are repairable and are excluded from the toy
    nspecial = 0; nM = 300
    for _ in range(nM):
        M0 = rand_gl2(rng)
        if slot_family_feasible(2, [(0, 1, M0)], eye(2))[2] or slot_family_feasible(2, [(0, 1, inv(M0))], eye(2))[2]: nspecial += 1
    def generic_gl2():
        while True:
            M0 = rand_gl2(rng)
            if not slot_family_feasible(2, [(0, 1, M0)], eye(2))[2] and not slot_family_feasible(2, [(0, 1, inv(M0))], eye(2))[2]: return M0
    for m in (1, 2, 3, 4):
        n = 2 * m; Ms = [generic_gl2() for _ in range(m)]
        # network: copy c has frames F_c1 (block M_c) then F_c2 (block M_c^-1); copies occupy disjoint wire pairs
        net = []
        for c in range(m): net.append((2 * c, 2 * c + 1, Ms[c], 'F%d1' % c)); net.append((2 * c, 2 * c + 1, inv(Ms[c]), 'F%d2' % c))
        T = eye(n); full = eye(n)
        for (w0, w1, B, _) in net: full = matmul(embed(n, w0, w1, B), full)
        check(full == T, 'network must realise T = I')
        stays = 4 * m; rigid = 0; fred = 0; tr_ok = 0
        for fi, (dw0, dw1, dB, name) in enumerate(net):
            for wdrop in (dw0, dw1):               # one wire loses its stay at this frame -> the pair is no longer co-present there
                remaining = [(w0, w1, B) for k, (w0, w1, B, _) in enumerate(net) if k != fi]
                # blocks of OTHER copies are present but cannot interact with this pair; the slot family only uses co-present pairs
                r1, r2, feas = slot_family_feasible(n, remaining, T)
                rigid += (not feas); fred += (r2 - r1 == 1)
                # Lemma TR: re-solve the other meeting of the same copy to X in GL(2) so the product is T again
                c = fi // 2; other = fi ^ 1
                rest = eye(n)
                for k, (w0, w1, B, _) in enumerate(net):
                    if k not in (fi, other): rest = matmul(embed(n, w0, w1, B), rest)
                X = inv(rest) if False else None
                # other copy's blocks commute with this copy's block; new block X must equal T restricted to this pair = identity
                Xnew = eye(2)
                trial = eye(n)
                for k, (w0, w1, B, _) in enumerate(net):
                    if k == fi: continue
                    trial = matmul(embed(n, w0, w1, Xnew if k == other else B), trial)
                tr_ok += (trial == T)
        check(rigid == stays and fred == stays, 'every single-stay drop must be infeasible with r2 = r1+1 (m=%d: %d/%d, fredholm %d)' % (m, rigid, stays, fred))
        check(tr_ok == stays, 'Lemma TR re-solve must repair every drop')
        stats.append((m, stays, rigid))
    # positive controls: a genuinely redundant stay IS repairable by the same linear family
    M = rand_gl2(rng); n = 2
    E = [[Fr(1), Fr(5)], [Fr(0), Fr(1)]]
    r1, r2, feas = slot_family_feasible(2, [(0, 1, eye(2))], E)
    check(feas and r1 == r2, 'positive control: transvection re-inserted at an unchanged co-presence')
    E2 = [[Fr(1), Fr(0)], [Fr(-3), Fr(1)]]
    r1b, r2b, feasb = slot_family_feasible(2, [(0, 1, eye(2))], E2); check(feasb and r1b == r2b, 'positive control 2')
    r1, r2, feas = slot_family_feasible(2, [(0, 1, M)], eye(2))          # M left alone, T = I: rigid (the toy)
    check(not feas and r2 == r1 + 1 and r1 == 3, 'single remaining block M, target I: rank 3 vs 4')
    ok('ONERANK no-lower-bound toy: network = per-copy meetings M then M^-1 on disjoint wire pairs, T = I (optimum 0 stays, drop everything): every single-stay drop (4m of them) is infeasible for the whole linear single-transvection slot family, with r2 = r1+1 each time (Fredholm); m = 1,2,3,4 copies: rigid %s; Lemma TR re-solve (other meeting := X in GL(2)) repairs 4m/4m' % ', '.join('%d/%d' % (r, s) for _, s, r in stats))
    ok('ONERANK genericity: %d/%d random M in GL(2) (entries -3..3) have a lone-block M or M^-1 repairable by the linear slot family; the rest are rigid (r1=3, r2=4)' % (nspecial, nM))
    ok('ONERANK unbounded gap: a locally rigid network with %s interior stays vs optimum 0 for m = 1,2,3,4 (4m vs 0, ratio unbounded); positive controls (redundant/unchanged co-presence) are repairable (rank equal) (%.1fs)' % (', '.join(str(4 * m) for m in (1, 2, 3, 4)), time.time() - t))

if __name__ == '__main__':
    section_theorem_f()
    section_lin()
    section_tr()
    section_rigid()
    print('total %.1fs' % (time.time() - T0))
    print('PASS_ONERANK')
