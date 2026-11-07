#!/usr/bin/env python3
"""Exact checks for: every set of >= 97 of the 120 E8 lines contains an F13 witness (a Hall-deficient 13-line
configuration), so no such set has a rank-8k realisation under the complex label pattern.  Standard library only.

  python3.12 -I -B check.py            # all steps (about 1 minute); the SAT proof is pinned by hash but not re-run
  python3.12 -I -B check.py --drat     # additionally decompress retained/local-lemma.drat.xz and run drat-trim
                                       # (drat-trim on PATH or in $DRAT_TRIM)
Steps
 1 lines, forced-zero graph NO (non-orthogonal pairs), SRG(120,56,28,24), (2A+8I-J)^2 = 24(2A+8I-J)
 2 F13: all witnesses K u O built from the graph; every instance passes the Hall-deficiency test; k = 1 exhaustive control
 3 symmetry: 9 reflections preserve NO (F13 is defined from NO alone) and move line 0 to every line
 4 local lemma CNF at line 0, regenerated and pinned by sha256; proof pinned by sha256
 5 counting; tightness: an explicit 24-line hitting set
"""
import sys, os, itertools, hashlib, random, lzma, subprocess, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
CNF_SHA = '987af2501ed8c602b9d4e3606f0ab1c5888b9e860b726606a40ebc922545610f'
DRAT_SHA = 'fea6c9f3933039cd85c054146b2fb8b19bdecc716a627de0edaea480288db192'
F13_SHA = '86e9b8b48f053ec6dbbc26e2f75cd489bc51b8a1879ac187d7d3bf17cb43f838'
D24 = [0, 1, 2, 3, 12, 13, 14, 15, 24, 25, 34, 35, 36, 37, 38, 39, 40, 41, 44, 45, 46, 47, 50, 51]
KB, AMAX = 23, 11          # |D| <= 23 and |D cap N(0)| <= 11 in the local lemma


def ip(a, b): return sum(x * y for x, y in zip(a, b))


def e8_lines():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for a in (2, -2):
            for b in (2, -2):
                v = [0] * 8; v[i] = a; v[j] = b; roots.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0: roots.append(s)          # coordinates doubled: roots have norm 8
    assert len(roots) == 240 and all(ip(r, r) == 8 for r in roots)
    seen, L = set(), []
    for r in roots:
        if r in seen: continue
        seen.add(r); seen.add(tuple(-x for x in r)); L.append(r)
    assert len(L) == 120
    return L


def step1(L):
    n = len(L)
    NO = [[i != j and ip(L[i], L[j]) != 0 for j in range(n)] for i in range(n)]
    assert all(ip(L[i], L[j]) in (0, 4, -4) for i in range(n) for j in range(n) if i != j)
    assert all(sum(r) == 56 for r in NO)
    nb = [sum(1 << j for j in range(n) if NO[i][j]) for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j: assert bin(nb[i] & nb[j]).count('1') == (28 if NO[i][j] else 24)
    M = [[2 * NO[i][j] + (8 if i == j else 0) - 1 for j in range(n)] for i in range(n)]
    cols = list(zip(*M))
    for i in range(n):
        for j in range(n):
            assert sum(a * b for a, b in zip(M[i], cols[j])) == 24 * M[i][j]
    print('step1: SRG(120,56,28,24); M=2A+8I-J satisfies M^2=24M, so M is 24 times a projection (rank %d)' % (sum(M[i][i] for i in range(n)) // 24))
    return NO, nb


def build_f13(n, NO, nb):
    cliques = []
    def rec(cur, cand):
        if len(cur) == 8: cliques.append(tuple(cur)); return
        while cand:
            v = (cand & -cand).bit_length() - 1; cand &= cand - 1
            rec(cur + [v], cand & nb[v])
    rec([], (1 << n) - 1)
    assert len(cliques) == 8640
    fam = {}; inst = 0
    for K in cliques:
        Ks = set(K)
        A = {t: tuple(c for c in K if not NO[t][c]) for t in range(n) if t not in Ks}
        pl = {}
        for t, a in A.items():
            if len(a) == 2: pl.setdefault(a, []).append(t)
        assert all(len(v) == 1 for v in pl.values())          # at most one line per pair of K-coordinates
        for C in itertools.combinations(K, 4):
            ps = list(itertools.combinations(C, 2))
            for drop in range(6):                              # O = K4-minus-an-edge of pair lines on C
                if any(p not in pl for p in ps): break
                O = [pl[p][0] for k, p in enumerate(ps) if k != drop]
                # Hall-deficiency test: |O| = 5 lines, supports A(t) inside the 4 coordinates of C, so at most 4k rank
                assert len(O) == 5 and len(set(O)) == 5 and not (set(O) & Ks)
                assert set().union(*[set(A[t]) for t in O]) <= set(C) and len(C) == 4
                for c in C:                                    # lines of O sharing a coordinate are forced zero
                    g = [t for t in O if c in A[t]]
                    assert all(NO[s][t] for s, t in itertools.combinations(g, 2))
                for s, t in itertools.combinations(O, 2):      # and share exactly one coordinate
                    assert len(set(A[s]) & set(A[t])) <= 1
                inst += 1
                fam[frozenset(K) | frozenset(O)] = (K, tuple(O), tuple(C))
    return fam, inst


def k1_control(fam, NO, seed=3, count=8):
    """k = 1, gauge U_K = W_K = I.  Line t of O carries W_t[c], U_t[c] on A(t) only (zero on the other K lines, since
    forced zero), needs W_t.U_t != 0, and forced-zero pairs need W_s[c]U_t[c] = 0 = W_t[c]U_s[c] on shared c."""
    rnd = random.Random(seed)
    keys = sorted(fam, key=lambda w: sorted(w))
    for w in rnd.sample(keys, count):
        K, O, C = fam[w]
        A = {t: tuple(c for c in K if not NO[t][c]) for t in O}
        for p in (2, 3):
            for drop in (None, O[0]):
                Os = [t for t in O if t != drop]
                states = {}
                for t in Os:
                    cs = A[t]; st = []
                    for v in itertools.product(range(p), repeat=4):
                        W = {cs[0]: v[0], cs[1]: v[1]}; U = {cs[0]: v[2], cs[1]: v[3]}
                        if sum(W[c] * U[c] for c in cs) % p: st.append((W, U))
                    states[t] = st
                asg = {}
                def rec(i):
                    if i == len(Os): return True
                    t = Os[i]
                    for W, U in states[t]:
                        if all(not NO[t][s] or (not sum(W[c] * Us[c] for c in set(W) & set(Ws)) % p
                                                and not sum(Ws[c] * U[c] for c in set(W) & set(Ws)) % p)
                               for s, (Ws, Us) in asg.items()):
                            asg[t] = (W, U)
                            if rec(i + 1): return True
                            del asg[t]
                    return False
                found = rec(0)
                assert found == (drop is not None), (p, drop)
    print('step2b: k=1 exhaustive search over F_2, F_3 on %d witnesses: no solution; with one O line removed: solution' % count)


def step3(L, NO, fam):
    n = len(L); idx = {}
    for t, r in enumerate(L): idx[r] = t; idx[tuple(-x for x in r)] = t
    def refl(r):   # s_r(x) = x - (x.r/4) r  on doubled coordinates
        return tuple(idx[tuple(a - (ip(L[t], r) // 4) * b for a, b in zip(L[t], r))] for t in range(n))
    gens, orb = [], {0}
    for r in L:
        g = refl(r); new = set(orb); st = list(orb)
        while st:
            a = st.pop()
            for h in gens + [g]:
                b = h[a]
                if b not in new: new.add(b); st.append(b)
        if len(new) > len(orb): gens.append(g); orb = new
        if len(orb) == n: break
    assert len(orb) == n
    for g in gens:
        assert sorted(g) == list(range(n))
        assert all(NO[g[i]][g[j]] == NO[i][j] for i in range(n) for j in range(n))
    # F13 is defined from NO alone, so it is invariant under any automorphism of NO; also checked on a sample
    keys = sorted(fam, key=lambda w: sorted(w)); rnd = random.Random(9)
    for w in rnd.sample(keys, 3000):
        for g in gens: assert frozenset(g[i] for i in w) in fam
    print('step3: %d reflections preserve NO (and F13 on a 3000-set sample); orbit of line 0 = all 120 lines' % len(gens))


def local_cnf(n, NO, fam, x=0, K=KB, A=AMAX):
    W = sorted(sorted(i for i in w if i != x) for w in fam if x in w)
    items = [i for i in range(n) if i != x]; vid = {i: t + 1 for t, i in enumerate(items)}
    cl = [[vid[i] for i in w] for w in W]; nv = len(items)
    def totalizer(lits, k):
        nonlocal nv
        def build(ls):
            nonlocal nv
            if len(ls) == 1: return [ls[0]]
            m = len(ls) // 2; a = build(ls[:m]); b = build(ls[m:])
            cap = min(len(ls), k + 1); out = []
            for _ in range(cap): nv += 1; out.append(nv)
            for i in range(len(a) + 1):
                for j in range(len(b) + 1):
                    s = i + j
                    if s == 0: continue
                    c = [out[min(s, cap) - 1]]
                    if i > 0: c.append(-a[i - 1])
                    if j > 0: c.append(-b[j - 1])
                    cl.append(c)
            return out
        o = build(lits)
        if len(o) > k: cl.append([-o[k]])
    totalizer([vid[i] for i in items], K)
    Nx = [vid[i] for i in items if NO[x][i]]; assert len(Nx) == 56
    totalizer(Nx, A)
    return len(W), nv, cl


def cnf_bytes(nv, cl):
    return ('p cnf %d %d\n' % (nv, len(cl)) + ''.join(' '.join(map(str, c)) + ' 0\n' for c in cl)).encode()


def e_in(D, NO): return sum(1 for a, b in itertools.combinations(D, 2) if NO[a][b])


def main():
    L = e8_lines(); n = 120
    NO, nb = step1(L)
    fam, inst = build_f13(n, NO, nb)
    h = hashlib.sha256()
    for w in sorted(sorted(x) for x in fam): h.update((','.join(map(str, w)) + '\n').encode())
    print('step2: %d (K,O) instances, %d distinct 13-line sets, each passes the Hall-deficiency test (5 lines on 4 coordinates); sha256 %s' % (inst, len(fam), h.hexdigest()))
    assert len(fam) == 1209600 and h.hexdigest() == F13_SHA
    k1_control(fam, NO)
    step3(L, NO, fam)
    nW, nv, cl = local_cnf(n, NO, fam)
    data = cnf_bytes(nv, cl); sha = hashlib.sha256(data).hexdigest()
    print('step4: local CNF at line 0: %d witnesses through it, %d variables, %d clauses, sha256 %s' % (nW, nv, len(cl), sha))
    assert nW == 131040 and sha == CNF_SHA
    pf = os.path.join(HERE, 'retained', 'local-lemma.drat.xz')
    if os.path.exists(pf):
        proof = lzma.decompress(open(pf, 'rb').read()); assert hashlib.sha256(proof).hexdigest() == DRAT_SHA
        print('step4: retained proof matches its pinned sha256 (%d bytes)' % len(proof))
        if '--drat' in sys.argv:
            dt = os.environ.get('DRAT_TRIM') or shutil.which('drat-trim'); assert dt, 'drat-trim not found'
            with tempfile.TemporaryDirectory() as td:
                a, b = os.path.join(td, 'l.cnf'), os.path.join(td, 'l.drat')
                open(a, 'wb').write(data); open(b, 'wb').write(proof)
                r = subprocess.run([dt, a, b, '-t', '20000'], capture_output=True, text=True)
            assert 's VERIFIED' in r.stdout, r.stdout[-400:]
            print('step4: drat-trim: s VERIFIED  (the CNF is unsatisfiable)')
    else:
        print('step4: retained proof missing')
        assert False
    # step 5
    emin = -((-(KB * KB - 8 * KB)) // 4); assert emin == 87
    lhs, rhs = 97 * (AMAX + 1), 56 * KB - 2 * emin
    print('step5: 97*12 = %d > 56*23 - 2*87 = %d: no hitting set of F13 has <= 23 lines' % (lhs, rhs)); assert lhs > rhs
    masks = [sum(1 << i for i in w) for w in fam]; dm = sum(1 << i for i in D24)
    assert len(set(D24)) == 24 and all(m & dm for m in masks)
    assert e_in(D24, NO) == 96 == (24 * 24 - 8 * 24) // 4
    print('step5: the 24-line set %s hits all %d witnesses (e = 96): minimum hitting set of F13 is exactly 24' % (D24, len(fam)))
    print('THEOREM CHECKED: every set of >= 97 of the 120 E8 lines contains an F13 witness.')


if __name__ == '__main__':
    main()
