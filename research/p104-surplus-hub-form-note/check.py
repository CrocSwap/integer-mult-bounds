#!/usr/bin/env python3
"""Single driver: prints one PASS line per claim of THEOREM.md (exit 1 on any FAIL); ends with PASS_P104_SURPLUS_HUB_FORM_NOTE.
Run from anywhere:  python3.12 -I -B research/p104-surplus-hub-form-note/check.py   (writes nothing).
Dependencies: Python 3.12 standard library plus numpy (declared in VERIFY.json; used only by the Theorem 5 numerical cells).
The quote checks read the repository files named in data/quotes.json at the repository root (two levels above this package);
a missing file or a changed line is a FAIL, never a skip."""
import os, sys, json, subprocess, itertools, random
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, 'checks')
PKG = os.path.dirname(os.path.dirname(HERE))   # repository root: HERE = <root>/research/p104-surplus-hub-form-note
fails = []
def PASS(tag, msg): print(f'PASS [{tag}] {msg}', flush=True)
def FAIL(tag, msg): fails.append(tag); print(f'FAIL [{tag}] {msg}', flush=True)
def ck(tag, cond, msg): (PASS if cond else FAIL)(tag, msg)
def run(script, *args, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run([sys.executable, '-I', '-B', script, *args], cwd=CH, capture_output=True, text=True, env=e, timeout=600)
    return p.stdout + p.stderr

# ---- Q: quotes (relabel evidence) ---------------------------------------------------------------
quotes = json.load(open(os.path.join(HERE, 'data', 'quotes.json')))
for grp, root in (('pkg', PKG),):
    for rel, ln, sub in quotes[grp]:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            FAIL(f'Q-{grp}', f'{rel}:{ln} (file absent)'); continue
        lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
        ck(f'Q-{grp}', ln <= len(lines) and sub in lines[ln-1], f'{rel}:{ln} contains {sub[:60]!r}')

# ---- S: selected record profile --------------------------------------------------------------
d = json.load(open(os.path.join(HERE, 'data', 'selected_record_profile.json')))
tt = sum(int(k)*v for k, v in d['targets'].items()); pp = sum(int(k)*v for k, v in d['paid'].items())
ck('S-record', tt - pp == 760 == d['rank_mass_surplus'], f'selected record: sum rank*targets - sum rank*paid = {tt}-{pp} = {tt-pp}')
ck('S-record', sum(d['targets'].values()) == d['productive_fields'] == 13444 and sum(d['paid'].values()) == d['paid_calls'] == 66834, 'fields 13444, paid calls 66834')
v, L, c = 104, 18, 56
ck('S-formula', v*(L-1) - L*c == 760, 'v(L-1) - L c = 104*17 - 18*56 = 760 (equality at the selected record)')

# ---- S: ratio lemma, independent exact re-derivation ------------------------------------------
def rank(M):
    M = [r[:] for r in M]; r = 0
    for cc in range(len(M[0]) if M else 0):
        p = next((i for i in range(r, len(M)) if M[i][cc] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][cc] != 0:
                f = M[i][cc]/M[r][cc]; M[i] = [a-f*b for a, b in zip(M[i], M[r])]
        r += 1
    return r
def mm(A, B):
    Bt = list(zip(*B)); return [[sum(a*b for a, b in zip(r, cc)) for cc in Bt] for r in A]
def inv(A):
    n = len(A); M = [A[i][:]+[Q(int(i == j)) for j in range(n)] for i in range(n)]
    for cc in range(n):
        p = next(r for r in range(cc, n) if M[r][cc] != 0); M[cc], M[p] = M[p], M[cc]
        pv = M[cc][cc]; M[cc] = [x/pv for x in M[cc]]
        for r in range(n):
            if r != cc and M[r][cc] != 0:
                f = M[r][cc]; M[r] = [a-f*b for a, b in zip(M[r], M[cc])]
    return [r[n:] for r in M]
def eye(n): return [[Q(int(i == j)) for j in range(n)] for i in range(n)]
def unit(x, y, cq):
    n = len(x); return [[Q(int(i == j)) + cq*x[i]*y[j] for j in range(n)] for i in range(n)]
random.seed(11)
def rand_iso(n):
    while True:
        x = [Q(random.randint(-3, 3)) for _ in range(n)]; y = [Q(random.randint(-3, 3)) for _ in range(n)]
        if sum(a*b for a, b in zip(x, y)) == 0 and any(x) and any(y): return x, y
# step 1-3: A(c) = I + c X (I - cL)^-1 Y^T and A(1)+A(-1)-2I = 2X(I-L)^-1 L (I+L)^-1 Y^T, rank <= N-1
okA = okB = True; trials = 0
for n, N in ((4, 3), (4, 4), (4, 5), (3, 6)):
    for _ in range(12):
        us = [rand_iso(n) for _ in range(N)]
        G = [[sum(us[k][1][i]*us[l][0][i] for i in range(n)) for l in range(N)] for k in range(N)]  # y_k . x_l
        Lm = [[G[k][l] if k < l else Q(0) for l in range(N)] for k in range(N)]  # strict triangle, product order
        X = [[us[k][0][i] for k in range(N)] for i in range(n)]; Yt = [[us[k][1][i] for i in range(n)] for k in range(N)]
        def Aprod(cq):
            P = eye(n)
            for x, y in us: P = mm(P, unit(x, y, cq))
            return P
        for cq in (Q(1), Q(-1), Q(3)):
            IL = [[Q(int(i == j)) - cq*Lm[i][j] for j in range(N)] for i in range(N)]
            R_ = mm(mm(X, inv(IL)), Yt); F = [[Q(int(i == j)) + cq*R_[i][j] for j in range(n)] for i in range(n)]
            okA &= (F == Aprod(cq))
        S_ = [[Aprod(1)[i][j] + Aprod(-1)[i][j] - 2*(i == j) for j in range(n)] for i in range(n)]
        okB &= rank(S_) <= N-1; trials += 1
ck('S-ratio', okA, f'A(c) = I + cX(I-cL)^-1 Y^T exact, {trials} random isotropic instances, c in {{1,-1,3}}')
ck('S-ratio', okB, 'rank(A(1)+A(-1)-2I) <= N-1 on the same instances')
# the chain: dim ker(R+I) <= N-1 on exact root instances (R = A(-1)A(1)^-1 up to the Q-even factor)
sys.path.insert(0, CH)
from chain_root import units, T as Tf
tight = []
for gL, gR in ((1, 1), (2, 2)):
    n, Ls, Rs, th = units(gL, gR); N = len(Ls)+len(Rs)+len(th)
    found = False
    for pos in itertools.combinations(range(N), len(th)):
        for perm in itertools.permutations(range(len(th))):
            seq = []; li = iter(Ls+Rs); ti = iter(perm)
            for k in range(N): seq.append(th[next(ti)] if k in pos else next(li))
            P = eye(n)
            for (x, y, m) in seq: P = mm(Tf(x, y, Q(2)), P)
            if P == [[Q(-1) if i == j else Q(0) for j in range(n)] for i in range(n)]:
                found = True; break
        if found: break
    ck('S-tight', found and N == n+1, f'chain root (gL,gR)=({gL},{gR}): n={n}, product = -I with N={N} = 1 + r units (r=n): equality in N >= 1 + dim ker(R+I) = 1+n')
    # hub law part (1), independent: W = prod(I-2xy^T) = I - 2 X A^-1 Y^T, A = I+2U ; W=-I => A-G has rank N-n
    us = [(x, y) for (x, y, m) in reversed(seq)]  # W = T_N ... T_1, left to right = reversed(seq)
    W = eye(n)
    for x, y in us: W = mm(W, unit(x, y, Q(-2)))
    G = [[sum(us[k][1][i]*us[l][0][i] for i in range(n)) for l in range(N)] for k in range(N)]
    U = [[G[k][l] if k < l else Q(0) for l in range(N)] for k in range(N)]
    Ls_ = [[G[k][l] if k > l else Q(0) for l in range(N)] for k in range(N)]
    A = [[Q(int(i == j)) + 2*U[i][j] for j in range(N)] for i in range(N)]
    X = [[us[k][0][i] for k in range(N)] for i in range(n)]; Yt = [[us[k][1][i] for i in range(n)] for k in range(N)]
    Wf = mm(mm(X, inv(A)), Yt); Wf = [[Q(int(i == j)) - 2*Wf[i][j] for j in range(n)] for i in range(n)]
    Zm = [[Q(int(i == j)) + U[i][j] - Ls_[i][j] for j in range(N)] for i in range(N)]
    ck('H-rank', Wf == W and rank(Zm) == N-n, f'({gL},{gR}): product formula exact; rank(I+U-L) = N-n = {rank(Zm)} (idempotent argument)')

# ---- S: run the check scripts ------------------------------------------------------------------
o = run('surplus_check.py'); ck('S-lemma', 'SURPLUS CHECK PASS' in o, 'ratio/seam/ledger script prints its PASS marker (exact; includes F2^4 subspace inequality, pin bookkeeping, S arithmetic, tightness)')
o = run('hub_law.py'); ck('H-law', 'PASS_HUB_LAW' in o and 'FAIL' not in o and o.count(': ok') == 10, 'hub law: rank, cocycle, divisibility, overlap at generic and degenerate nonzero D; v=1 control; 10 instances')
# ---- typed query ---------------------------------------------------------------------------
o = run('typed_query.py')
for sub in ('C=HSH == aI+bX: True | C^2==X: True', 'B-block rank_F2 = 1', 'C in F (free)? False | C in F*H*F (one H-cell, C-rank 1)? True',
            'check: True', 'K_P == H(x)H diag((-1)^(x1x2)) H(x)H : True', 'rank_F2 B:  K_P = 2 | C(x)C = 2 | C(x)I = 1',
            'K_P in F*(C(x)C)*F (same Bruhat cell, rank 2)? True',
            ):
    ck('typed-query', sub in o, f'typed query output: {sub[:70]}')
# ---- Theorem C ----------------------------------------------------------------------------------
def capacity(v, rs, dbl, cells, fam='onepass'):
    out = run('form_capacity.py', str(v), str(rs), dbl, *[f'{a},{b}' for a, b in cells], env={'FAM': fam})
    res = []
    for ln in out.splitlines():
        if ln.startswith('v='):
            kd = int(ln.split('kd=')[1].split()[0]); ku = int(ln.split('ku=')[1].split()[0])
            K = int(ln.split('|K|=')[1].split()[0]); solved = int(ln.split('solved ')[1].split('/')[0])
            t_ = ln.split('pirank max=')[1].split()[0]; mx = -1 if t_ == 'None' else int(t_); res.append((kd, ku, K, solved, mx))
    return res
cells = [(1, 0), (1, 1), (2, 1), (3, 0), (3, 1), (3, 2), (3, 3), (6, 2)]
r = capacity(3, 4, 'nodbl', cells)
ntight = sum(1 for kd, ku, K, sv, mx in r if mx == K+ku)
ck('thm5', len(r) == len(cells) and all(sv >= 1 and mx <= K+ku for kd, ku, K, sv, mx in r), f'one-pass v=3: pi-rank <= |K|+ku in all {len(r)} cells with a solution (equality in {ntight})')
ck('thm5', all(mx < 3+K for kd, ku, K, s, mx in r if ku < 3), 'hence ku < v = 3 never reaches the target pi-rank v+|K|')
r2 = capacity(2, 4, 'nodbl', [(0, 1), (2, 1), (3, 0), (2, 2)])
ck('thm5', sum(1 for *_, s, mx in r2 if s >= 1) >= 2 and all(mx <= K+ku for kd, ku, K, s, mx in r2), f'one-pass v=2: bound holds in all solved cells ({sum(1 for *_, s, mx in r2 if s >= 1)} of {len(r2)} solved; unsolved cells are not evidence)')
rr = capacity(3, 4, 'nodbl', [(2, 1), (3, 2)], fam='rowline')
ck('thm5-scope', any(mx > K+ku for kd, ku, K, s, mx in rr), 'control: the rowline landing family exceeds the bound (outside the stated family, as stated)')

# ---- retained arithmetic on stated numbers --------------------------------------------------------------
o = run('ledger_arith.py')
for sub in ('f(145)*v 75049 share 0.331', 'public stop tax*18 142686 share 0.629', 'sum check 226935 vs 226939',
            'BIT cap +14.3%: needs D cut 28392 R0 = 1577 R0/call', '+2% variant: (7927-7690)*18 = 4266 share 0.0188',
            'S parts: L*Omega 864 delta*v 104 S 760', 'DONE_LEDGER'):
    ck('ledger-arith', sub in o, sub)
# multi-affine vanishing on a two-point grid (symbolic D versus character grid)
for k in (2, 3, 4):
    pts = list(itertools.product((1, -1), repeat=k))
    mons = list(itertools.product((0, 1), repeat=k))
    M = [[Q(1) if True else 0 for _ in mons] for _ in pts]
    M = [[Q(__import__('math').prod(p[i] for i in range(k) if m[i])) for m in mons] for p in pts]
    ck('multiaffine', rank(M) == 2**k, f'{k} variables: multi-affine polynomial vanishing on {{+1,-1}}^{k} is zero (evaluation matrix rank {2**k})')
print('PASS_P104_SURPLUS_HUB_FORM_NOTE' if not fails else f'FAILED: {sorted(set(fails))}')
sys.exit(1 if fails else 0)
