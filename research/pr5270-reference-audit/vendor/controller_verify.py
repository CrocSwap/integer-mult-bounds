#!/usr/bin/env python3
"""Checks for consuming the center-free coded native word (PR4929) in the query-thinned controller.

Coded reverse stages carry the code A; every forward stage is a query-only shear that first mixes its
source by A^-1. Standard library only; reads existing repo files. Python 3.9+.
"""
import gzip, importlib.util, json, math, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/bit-compression/carrier-reuse/reference'),
                str(ROOT/'research/kappa-rebuild/bit')]
import complex_controller_factor as C

def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: '+why)
    print('PASS', why, flush=True)

# ---- 1. the code A of PR4929 --------------------------------------------------------------
NP = 112
A = [[Q(x) for x in row] for row in json.load(open(ROOT/'research/native-center-free-code/CODE.json'))['A']]
I = [[Q(int(i == j)) for j in range(NP)] for i in range(NP)]
def mm(X, Y): return [[sum(X[i][k]*Y[k][j] for k in range(NP) if X[i][k]) for j in range(NP)] for i in range(NP)]
Ainv = [[I[i][j]+(A[i][j]-I[i][j])/13 for j in range(NP)] for i in range(NP)]
R = [[int(json.load(gzip.open(ROOT/'research/kappa-native-resume/causal-controller/sources/research/joint-query/certificate.json.gz'))['R_rows'][a].get(str(p), 0)) for p in range(NP)] for a in range(8)]
need(all(A[i][j] == A[j][i] for i in range(NP) for j in range(NP)) and all(A[i][i] == 0 for i in range(NP)), 'A symmetric with zero diagonal')
need(all(A[p][q] == I[p][q]-Q(sum(R[a][p]*R[a][q] for a in range(8)), 4) for p in range(NP) for q in range(NP)), 'A = I - R^T R / 4 for the joint-query packet')
need(mm([[A[i][j]-I[i][j] for j in range(NP)] for i in range(NP)], [[A[i][j]+13*I[i][j] for j in range(NP)] for i in range(NP)]) == [[Q(0)]*NP for _ in range(NP)], '(A-I)(A+13I)=0: modes 1 (104) and -13 (8)')
need(mm(A, Ainv) == I, 'A^-1 = I + (A-I)/13')

# ---- 2. coded controller: exact diagonalization after thinning -------------------------------
def controller(p, keep, coupling):
    """C.controller with a per-stage coupling: forward lower-left coupling*Q^-1, reverse upper-right -coupling*Q."""
    n, stages = 2*p, 2*p+1
    zero = (0,)*(stages+1)
    matrix = [[{zero: 1} if i == j else {} for j in range(n)] for i in range(n)]
    idle = []
    term = lambda q, sel: (q,)+tuple(int(s in sel) for s in range(stages))
    def idle_call(pair, sel, kind):
        retained = bool(keep >> len(idle) & 1)
        idle.append(dict(kind=kind, pair=pair, retained=retained))
        if retained:
            for role in (2*pair, 2*pair+1):
                matrix[role] = [C.monomial_times(x, term(0, sel)) for x in matrix[role]]
    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse: x, y = y, x
        coef = (-1 if reverse else 1)*coupling[stage]
        matrix[y] = [C.plus(a, C.monomial_times(b, term(1 if reverse else -1, []), coef)) for a, b in zip(matrix[y], matrix[x])]
        for role in (x, y): matrix[role] = [C.monomial_times(z, term(0, [stage])) for z in matrix[role]]
        if stage % 2 and stage <= 2*p-3: idle_call((stage+1)//2, list(range(stage+1)), 'initial')
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2: idle_call(stage//2, [stage], 'middle')
        elif stage == 2*p:
            for j in range(p-1): idle_call(j, list(range(2*j+3, 2*p+1)), 'terminal')
    def bridge(dst, src, c):
        for d, s, cc in ((2*dst, 2*src, c), (2*src+1, 2*dst+1, -c)):
            matrix[d] = [C.plus(a, b, cc) for a, b in zip(matrix[d], matrix[s])]
    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1: bridge(j, j+1, 1)
        local(2*j+2, j, False)
        if j < p-1: bridge(j, j+1, -1)
    for j in reversed(range(p-1)): bridge(j+1, j, 1)
    for j in range(p): matrix[2*j], matrix[2*j+1] = matrix[2*j+1], [C.monomial_times(x, zero, -1) for x in matrix[2*j]]
    co = {}
    for i, row in enumerate(matrix):
        for j, poly in enumerate(row):
            for key, v in poly.items(): co.setdefault(key, [[Q(0)]*n for _ in range(n)])[i][j] += v
    return {k: m for k, m in co.items() if any(any(r) for r in m)}, idle

def keep_of(p, pat):
    _, idle = controller(p, 0, {s: 1 for s in range(2*p+1)})
    return sum(1 << i for i, r in enumerate(idle) if r['kind'] == 'middle' or (r['kind'] == 'initial' and pat[r['pair']-1] in 'IB') or (r['kind'] == 'terminal' and pat[r['pair']] in 'TB'))

def thin(co, thick):
    out = {}
    for term, m in co.items():
        key = (term[0],)+tuple(x if s in thick else 0 for s, x in enumerate(term[1:]))
        t = out.setdefault(key, [[Q(0)]*len(m) for _ in m])
        for i, row in enumerate(m):
            for j, v in enumerate(row): t[i][j] += v
    return {k: m for k, m in out.items() if any(any(r) for r in m)}

C.scalar_program = lambda m: None      # the dyadic boundary test is reported below as a denominator instead
def diagonalize(p, pat, coupling):
    r = C.factor(thin(controller(p, keep_of(p, pat), coupling)[0], set(range(1, 2*p, 2))))
    if r is None: return None
    return sorted(Counter(sum(t[1:]) for t in r['diagonal']).items()), sorted({q.denominator for m in (r['left'], r['right']) for row in m for q in row})

c = Q(-13)
for p, pat in [(3, 'IT'), (4, 'IIT'), (5, 'IITT'), (8, 'IIIITTT')]:
    coded = {s: (c if s % 2 else 1/c) for s in range(2*p+1)}      # reverse = A, forward (incl. both ends) = A^-1
    std = diagonalize(p, pat, {s: Q(1) for s in range(2*p+1)})
    cod = diagonalize(p, pat, coded)
    need(std is not None and cod is not None and std[0] == cod[0] and std[1] == [1] and cod[1] == [1, 13],
         'p=%d %s: coded controller diagonalizes with the standard outputs %s; new boundary denominator 13' % (p, pat, cod[0] if cod else None))
p, pat = 3, 'IT'
need(diagonalize(p, pat, {s: (c if s % 2 else Q(1)) for s in range(2*p+1)}) is None, 'control: coded reverse with uncoded forward stages does not diagonalize')
need(diagonalize(p, pat, {s: (c if (s % 2 or s in (0, 2*p)) else 1/c) for s in range(2*p+1)}) is None, 'control: coded (thick) forward end stages do not diagonalize')
need(diagonalize(p, pat, {s: (c if s % 2 else Q(1, 169)) for s in range(2*p+1)}) is None, 'control: wrong inverse code does not diagonalize')

# ---- 3. explicit conjugation with the real 112 x 112 code (p=2, numeric Q and D_s) -----------
def sparse(M): return [[(j, v) for j, v in enumerate(row) if v] for row in M]
SI, SA, SAi = sparse(I), sparse(A), sparse(Ainv)
def build(p, rev, fwd, Qv, Dv):
    rows = {(r, q): {(r, q): Q(1)} for r in range(2*p) for q in range(NP)}
    def addrow(dst, src, M, coef):
        new = {}
        for pp in range(NP):
            acc = dict(rows[(dst, pp)])
            for q, mv in M[pp]:
                for k, v in rows[(src, q)].items(): acc[k] = acc.get(k, 0)+coef*mv*v
            new[pp] = {k: v for k, v in acc.items() if v}
        rows.update({(dst, pp): new[pp] for pp in range(NP)})
    def scale(role, m):
        for q in range(NP):
            for k in rows[(role, q)]: rows[(role, q)][k] *= m
    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse: x, y = y, x; addrow(y, x, rev, -Qv)
        else: addrow(y, x, fwd, 1/Qv)
        if stage % 2: scale(x, Dv[stage]); scale(y, Dv[stage])
    def bridge(dst, src, cf):
        for d, s, cc in ((2*dst, 2*src, cf), (2*src+1, 2*dst+1, -cf)):
            for pp in range(NP):
                acc = dict(rows[(d, pp)])
                for k, v in rows[(s, pp)].items(): acc[k] = acc.get(k, 0)+cc*v
                rows[(d, pp)] = {k: v for k, v in acc.items() if v}
    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1: bridge(j, j+1, 1)
        local(2*j+2, j, False)
        if j < p-1: bridge(j, j+1, -1)
    for j in reversed(range(p-1)): bridge(j+1, j, 1)
    return rows
def mix(rows, p, roles, M, side):
    out = {}
    for (r, pp), rw in rows.items():
        if side == 'rows' and r in roles:
            acc = {}
            for q, mv in M[pp]:
                for k, v in rows[(r, q)].items(): acc[k] = acc.get(k, 0)+mv*v
        elif side == 'cols':
            acc = {}
            for (cc, q), v in rw.items():
                if cc in roles:
                    for k, mv in M[q]: acc[(cc, k)] = acc.get((cc, k), 0)+v*mv
                else: acc[(cc, q)] = acc.get((cc, q), 0)+v
        else: acc = rw
        out[(r, pp)] = {k: v for k, v in acc.items() if v}
    return out
p = 2; Dv = {s: Q(2*s+3) for s in range(2*p+1)}
std, cod = build(p, SI, SI, Q(2), Dv), build(p, SA, SAi, Q(2), Dv)
xr = set(range(0, 2*p, 2))
need(mix(mix(std, p, xr, SA, 'rows'), p, xr, Ainv and sparse(Ainv), 'cols') == cod, 'p=2, 448x448: coded controller == (A on x-roles) * standard * (A^-1 on x-roles), exact')
need(mix(mix(std, p, xr, SA, 'rows'), p, xr, SA, 'cols') != cod, 'control: wrong conjugation rejected')

# ---- 4. invoice and moment root -------------------------------------------------------------
H = {4: 28, 7: 7, 8: 47, 9: 326}                        # helpers (unchanged by PR4929)
P_OLD = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}  # joint-helper-lattice local paid profile
P_NEW = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}        # PR4929 paid profile, both orientations
need(sum(r*n for r, n in P_OLD.items())-sum(r*n for r, n in P_NEW.items()) == 64, 'PR4929 removes exactly 64 rank mass per call')
def invoice(p, pat, thick, prof):
    full = frozenset(range(2*p+1)); T, D = Counter(), Counter()
    outs = [full, full]
    for i, ch in enumerate(pat, 1): outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    for s in outs: T[1+8*len(s & thick)] += 112
    for i, ch in enumerate(pat, 1):
        if ch == 'I': D[8*len(frozenset(range(0, 2*i)) & thick)] += 224
        else: D[8*len(frozenset(range(2*i+1, 2*p+1)) & thick)] += 224
    for j in range(1, p): D[8*len(frozenset([2*j]) & thick)] += 224
    for r, n in H.items(): T[r] += len(thick)*n
    for r, n in prof.items(): D[r] += len(thick)*n
    D[1] += 112*(2*p+1-len(thick))
    T.pop(0, None); D.pop(0, None)
    return T, D
def root(T, D):
    f = lambda cc: sum(n*r**(1-cc) for r, n in T.items())-sum(n*r**(1-cc) for r, n in D.items())
    lo, hi = 0.0, 0.05
    for _ in range(200):
        mid = (lo+hi)/2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return lo
pub = root(*invoice(16, 'I'*7+'T'*8, frozenset({0, 32} | set(range(1, 32, 2))), P_OLD))
need(abs(pub-0.0030201659770) < 1e-12, 'model reproduces the published p16 raw root 0.0030201659770 (got %.13f)' % pub)
res = {p: root(*invoice(p, 'I'*((p-1)//2)+'T'*(p-1-(p-1)//2), frozenset(range(1, 2*p, 2)), P_NEW)) for p in (8, 19)}
print('coded controller raw complex root: p=8 %.6f, p=19 %.6f' % (res[8], res[19]))
need(res[19] > 0.0034*1.5, 'p=19 raw root is more than 1.5x the BIT cap 0.0034')
def guards(T, D, cc, u=0.2, cut=20, floor=21):
    t = 1-cc; Tt = sum(n*r**t for r, n in T.items()); Pt = sum(n*r**t for r, n in D.items())
    return Pt/Tt, sum(n*r**(t+u) for r, n in D.items())/(cut**u*Tt), floor*sum(T.values())/(cut**cc*Tt)
a, g, d = guards(*invoice(19, 'I'*9+'T'*9, frozenset(range(1, 38, 2)), P_NEW), 0.0034)
need(a < 1-1e-9 and g < 0.97 and d < 0.97, 'p=19 tail guards at C=0.0034: alpha=%.8f gamma=%.4f delta=%.4f' % (a, g, d))

# ---- 5. the repo's strict outer ledger ---------------------------------------------------------
sys.path.insert(0, str(ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill'))
spec = importlib.util.spec_from_file_location('ledger_mod', ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py')
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
gap, atom = Q(1, 1400000000), Q(1, 250)
def failing(kappa):
    prm = {'kappa': kappa, 'tested_saving': kappa+7*gap, 'complex_uniform_saving': kappa+6*gap, 'b': kappa+5*gap, 'a': kappa+4*gap,
           'q': kappa+3*gap, 'bit_saving': Q(17, 5000), 'epsilon': 1-gap, 'beta': 1-3*gap, 'r0': gap/10, 'stop': gap, 'layout': gap, 'd': gap}
    out = L.ledger(prm); out['functional_checks']['actual_new_BIT_stock_sublinear'] = prm['beta']*(1-atom)
    return [k for part in ('strict_checks', 'functional_checks') for k, x in out[part].items() if x <= 0]
need(failing(Q(60403, 20000000)) == [], 'ledger passes at the selected kappa 0.00302015 (control)')
need(failing(Q(3324, 1000000)) == [] and failing(Q(33999, 10000000)) == [], 'ledger passes at 0.003324 (+10%) and 0.0033999')
need(failing(Q(34, 10000)) == ['actual_bit_above_effective'], 'at 0.0034 the only failing predicate is the BIT cap')
print('DONE: formal and arithmetic checks pass; physical admission of the adapter is NOT checked here')
