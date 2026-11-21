# QZERO qz2: generate a kernel-checkable Lean legality proof of C1 (stages relabelled to call order).
# Polynomials: dict monomial (qa, ib, nu, d0, d1, d2) -> int (Lean form) or (qa, ib, d0, d1, d2) -> Fraction (true form).
import json, sys
from fractions import Fraction as F
N = 390
C = json.load(open('caller_C1.json')); n, k = 4, 3
relab = {2: 0, 0: 1, 1: 2}   # old 0-based stage -> call-order stage
ev = []
for e in C['events']:
    op = e[0]
    if op == 'HOST':
        t = relab[e[1]-1]; ev += [('host', e[2], e[3], F(e[4]), F(e[5])), ('idle', e[2], t), ('idle', e[3], t)]
    elif op == 'ADD': ev.append(('add', e[1], e[2], F(e[3])))
    elif op == 'SCALE': ev.append(('scale', e[1], F(e[2])))
    elif op == 'LAMBDA': ev.append(('lam', e[1], e[2]))
    elif op == 'IDLE_ONE': assert len(e[2]) == 1; ev.append(('idle', e[1], relab[e[2][0]-1]))
    else: raise ValueError(op)
masks = [frozenset(relab[s] for s, b in enumerate(dg[2:]) if b) for dg in C['diagonal']]
# ---- true arithmetic: poly in q (mod q^4-1), i (mod i^2+1), D: key (qa, ib, d0, d1, d2) -> Fraction
def padd(a, b, s=1):
    r = dict(a)
    for m, c in b.items():
        r[m] = r.get(m, 0) + s*c
        if r[m] == 0: del r[m]
    return r
def pmul(a, b):
    r = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            qa = (m1[0]+m2[0]) % 4; ib = m1[1]+m2[1]; c = c1*c2
            if ib >= 2: ib -= 2; c = -c
            m = (qa, ib, m1[2]+m2[2], m1[3]+m2[3], m1[4]+m2[4])
            r[m] = r.get(m, 0) + c
            if r[m] == 0: del r[m]
    return r
def cst(c): return {(0, 0, 0, 0, 0): F(c)} if c != 0 else {}
Q = {(1, 0, 0, 0, 0): F(1)}; Q3 = {(3, 0, 0, 0, 0): F(1)}; Q2 = {(2, 0, 0, 0, 0): F(1)}; Ii = {(0, 1, 0, 0, 0): F(1)}
def Dv(t): m = [0, 0, 0]; m[t] = 1; return {(0, 0) + tuple(m): F(1)}
def ident(): return [[cst(1) if a == b else {} for b in range(n)] for a in range(n)]
def evmat(e):
    M = ident(); op = e[0]
    if op == 'add': M[e[1]][e[2]] = padd(M[e[1]][e[2]], cst(e[3]))
    elif op == 'scale': M[e[1]][e[1]] = cst(e[2])
    elif op == 'lam':
        s = e[2]; M[e[1]][e[1]] = padd(padd(cst(F(1, 2)), {(0, 1, 0, 0, 0): F(s, 2)}), padd({(2, 0, 0, 0, 0): F(1, 2)}, {(2, 1, 0, 0, 0): F(-s, 2)}))
    elif op == 'idle': M[e[1]][e[1]] = Dv(e[2])
    elif op == 'host':
        s, t, a, b = e[1:]; M[s][t] = {(1, 0, 0, 0, 0): a}; M[t][s] = {(3, 0, 0, 0, 0): b}; M[t][t] = cst(1+a*b)
    return M
def mmul(A, B): return [[ {m: c for m, c in sum_polys([pmul(A[r][x], B[x][cc]) for x in range(n)]).items()} for cc in range(n)] for r in range(n)]
def sum_polys(ps):
    r = {}
    for p in ps: r = padd(r, p)
    return r
chk = [ident()]
for e in ev: chk.append(mmul(evmat(e), chk[-1]))
T = [[{(1, 0) + tuple(int(t in masks[r]) for t in range(3)): F(1)} if r == cc else {} for cc in range(n)] for r in range(n)]
assert chk[-1] == T, 'final checkpoint != target'
print('events', len(ev), 'final = target q*D^mask OK; masks', [sorted(m) for m in masks], file=sys.stderr)
# ---- Lean (integer) form: rational c -> m * nu^e (minimal e)
def lform(p):  # true poly -> int poly with nu exponent
    r = {}
    for (qa, ib, d0, d1, d2), c in p.items():
        e = 0
        while (c * N**e).denominator != 1: e += 1
        r[(qa, ib, e, d0, d1, d2)] = int(c * N**e)
    return r
def iadd(a, b, s=1):
    r = dict(a)
    for m, c in b.items():
        r[m] = r.get(m, 0) + s*c
        if r[m] == 0: del r[m]
    return r
def imul(a, b):  # raw product, no reduction
    r = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            m = tuple(x+y for x, y in zip(m1, m2)); r[m] = r.get(m, 0) + c1*c2
            if r[m] == 0: del r[m]
    return r
def lev(e):  # event matrix in Lean int form (constants in nu form), raw (q^3 kept, i^1)
    M = evmat(e)
    if e[0] == 'lam':  # keep literal: 1/2(1+s i) + 1/2(1-s i) q^2, all have denominator 2 -> nu form
        pass
    return [[lform(x) for x in row] for row in M]
def divide(f):
    f = dict(f); Aq = {}; Ai = {}; An = {}
    changed = True
    while True:
        bad = [m for m in f if m[0] >= 4]
        if not bad: break
        for m in bad:
            c = f.pop(m); m2 = (m[0]-4,) + m[1:]
            Aq = iadd(Aq, {m2: c}); f = iadd(f, {m2: c})
    while True:
        bad = [m for m in f if m[1] >= 2]
        if not bad: break
        for m in bad:
            c = f.pop(m); m2 = (m[0], m[1]-2) + m[2:]
            Ai = iadd(Ai, {m2: c}); f = iadd(f, {m2: -c})
    # f = (N nu - 1) g, per (q,i,D) monomial a polynomial in nu
    groups = {}
    for m, c in f.items(): groups.setdefault((m[0], m[1]) + m[3:], {})[m[2]] = c
    for key, p in groups.items():
        E = max(p); g = {}; prev = 0
        for e in range(E+1):
            ge = N*prev - p.get(e, 0); g[e] = ge; prev = ge
        assert g[E] == 0, ('nu division failed', key, p)   # top: c_{E+1}=0 => N g_E - 0 = ... need g_E = 0
        for e, ge in g.items():
            if ge: An = iadd(An, {(key[0], key[1], e) + key[2:]: ge})
    return Aq, Ai, An
def lean_poly(p):
    if not p: return '0'
    terms = []
    for (qa, ib, e, d0, d1, d2), c in sorted(p.items()):
        fac = []
        for v, x in (('q', qa), ('i', ib), ('ν', e), ('D 0', d0), ('D 1', d1), ('D 2', d2)):
            if x == 1: fac.append(v if ' ' not in v else '(' + v + ')')
            elif x > 1: fac.append(('(%s)' % v if ' ' in v else v) + '^' + str(x))
        terms.append('(%d : S)' % c + ''.join(' * ' + f for f in fac))
    return ' + '.join(terms)
def lean_mat(M): return '!![' + '; '.join(', '.join(lean_poly(x) for x in row) for row in M) + ']'

def lev_exact(e):
    M = [[({(0,0,0,0,0,0): 1} if a == b else {}) for b in range(n)] for a in range(n)]
    op = e[0]
    if op == 'add': M[e[1]][e[2]] = iadd(M[e[1]][e[2]], lform(cst(e[3])))
    elif op == 'scale': M[e[1]][e[1]] = lform(cst(e[2]))
    elif op == 'lam':
        s = e[2]; M[e[1]][e[1]] = {(0,0,1,0,0,0): 195, (0,1,1,0,0,0): 195*s, (2,0,1,0,0,0): 195, (2,1,1,0,0,0): -195*s}
        M[e[1]][e[1]] = {m: c for m, c in M[e[1]][e[1]].items() if c}
    elif op == 'idle': m = [0,0,0]; m[e[2]] = 1; M[e[1]][e[1]] = {(0,0,0)+tuple(m): 1}
    elif op == 'host':
        s, t, a, b = e[1:]
        M[s][t] = imul(lform(cst(a)), {(1,0,0,0,0,0): 1}); M[t][s] = imul(lform(cst(b)), {(3,0,0,0,0,0): 1})
        M[t][t] = iadd({(0,0,0,0,0,0): 1}, lform(cst(a*b)))
    return M
L = [[[lform(x) for x in row] for row in M] for M in chk]
out = []
consts = set()
for e in ev:
    if e[0] in ('add', 'scale'): consts.add(e[3] if e[0] == 'add' else e[2])
    if e[0] == 'host': consts |= {e[3], e[4], ('prod', e[3], e[4])}
def qlit(c):
    return '(%d)' % c.numerator if c.denominator == 1 else '(%d/%d)' % (c.numerator, c.denominator)
def evlean(e):
    op = e[0]
    if op == 'add': return '.add %d %d %s' % (e[1], e[2], qlit(e[3]))
    if op == 'scale': return '.scale %d %s' % (e[1], qlit(e[2]))
    if op == 'lam': return '.lam %d (%d)' % (e[1], e[2])
    if op == 'idle': return '.idle %d {%d} 0' % (e[1], e[2])
    if op == 'host': return '.host %d %d %s %s' % (e[1], e[2], qlit(e[3]), qlit(e[4]))
def castl(m):
    if m == 1: return 'show (1 : S) = algebraMap ℚ S 1 from (map_one _).symm'
    if m == -1: return 'show (-1 : S) = algebraMap ℚ S (-1) by rw [map_neg, map_one]'
    if m >= 2: return 'show (%d : S) = algebraMap ℚ S %d from (map_ofNat (algebraMap ℚ S) %d).symm' % (m, m, m)
    return 'show (%d : S) = algebraMap ℚ S (%d) by rw [map_neg, map_ofNat]' % (m, m)
def nuform(c):
    e = 0
    while (c * N**e).denominator != 1: e += 1
    return int(c * N**e), e
W = []
W.append('/-\nCallerQZero C1 legality data (generated by cards/WILD/NOVEL/qzero/qz2.py from caller_C1.json; stages relabelled to call order).\n-/')
W.append('import Nov15.CallerAsm\nimport Mathlib.Tactic.LinearCombination\nset_option linter.unusedSectionVars false\nset_option linter.unusedVariables false\nnamespace CallerQZero\nopen Matrix CallerWord\n')
W.append('def c1Evs : List (Ev 4 3) := [' + ',\n  '.join(evlean(e) for e in ev) + ']\n')
W.append('section data\nvariable {S : Type} [CommRing S] [Algebra ℚ S]\n')

W.append('theorem hν0 : (390 : S) * ν0 S = 1 := by\n  rw [← map_ofNat (algebraMap ℚ S) 390, ← map_mul]; norm_num\n')
cl = []
for idx, c in enumerate(sorted([c for c in consts if not isinstance(c, tuple)]) + sorted([c for c in consts if isinstance(c, tuple)], key=lambda x: (x[1], x[2]))):
    if isinstance(c, tuple):
        lhs = '%s * %s' % (qlit(c[1]), qlit(c[2])); val = c[1]*c[2]
    else:
        lhs = qlit(c); val = c
    m, e = nuform(val)
    nm = 'k%d' % idx; cl.append(nm)
    W.append('theorem %s : algebraMap ℚ S (%s) = (%d : S) * ν0 S ^ %d := by\n  rw [%s, ← map_pow, ← map_mul]; congr 1; norm_num\n' % (nm, lhs, m, e, castl(m)))
m, e = nuform(F(1, 2)); W.append('theorem khalf : algebraMap ℚ S (1/2) = (%d : S) * ν0 S ^ %d := by\n  rw [%s, ← map_pow, ← map_mul]; congr 1; norm_num\n' % (m, e, castl(m))); cl.append('khalf')
for j in range(len(chk)):
    W.append('def ck%d (q i ν : S) (D : Fin 3 → S) : Matrix (Fin 4) (Fin 4) S := %s\n' % (j, lean_mat(L[j])))
W.append('end data\n')
open('cst_names.txt', 'w').write(' '.join(cl))
stepsW = ['section steps\nvariable {S : Type} [CommRing S] [Algebra ℚ S]\n']
mx = 0
for j, e in enumerate(ev):
    E = lev_exact(e)
    f = [[iadd({}, {}) for _ in range(n)] for _ in range(n)]
    A = {'q': [[{} for _ in range(n)] for _ in range(n)], 'i': [[{} for _ in range(n)] for _ in range(n)], 'n': [[{} for _ in range(n)] for _ in range(n)]}
    for r in range(n):
        for cc in range(n):
            p = {}
            for x in range(n): p = iadd(p, imul(E[r][x], L[j][x][cc]))
            p = iadd(p, L[j+1][r][cc], -1)
            aq, ai, an = divide(p)
            A['q'][r][cc], A['i'][r][cc], A['n'][r][cc] = aq, ai, an
            mx = max(mx, len(p))
    rhs = 'ck%d q i (ν0 S) D' % (j+1)
    for key, rel in (('q', '(q ^ 4 - 1)'), ('i', '(i ^ 2 + 1)'), ('n', '((390 : S) * ν0 S - 1)')):
        if any(A[key][r][cc] for r in range(n) for cc in range(n)):
            rhs += ' + %s • %s' % (rel, lean_mat(A[key]).replace('ν', 'ν0 S'))
    stepsW.append('theorem st%d (q i : S) (D : Fin 3 → S) :\n    evMat q i D (%s : Ev 4 3) * ck%d q i (ν0 S) D = %s := by\n  simp only [evMat, %s]\n  ext r c; fin_cases r <;> fin_cases c <;>\n    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck%d, ck%d, qp] <;> ring\n' % (j, evlean(e), j, rhs, ', '.join(cl), j, j+1))
stepsW.append('end steps\n')
open('<tmpdir>', 'w').write('\n'.join(W).replace('ν0 S', '(algebraMap ℚ S (1/390))'))
open('<tmpdir>', 'w').write('\n'.join(stepsW).replace('ν0 S', '(algebraMap ℚ S (1/390))'))
print('max raw terms per entry', mx, 'consts', len(cl))

# ---- final assembly
NU = '(algebraMap ℚ S (1/390))'
F_ = ['section final\nvariable {S : Type} [CommRing S] [Algebra ℚ S]\n']
F_.append('theorem c1_pre (q i : S) (D : Fin 3 → S) (hq : q ^ 4 = 1) (hi : i ^ 2 = -1) :\n    pre q i D c1Evs %d = ck%d q i %s D := by' % (len(ev), len(ev), NU))
F_.append('  have hq0 : q ^ 4 - 1 = 0 := by rw [hq]; ring\n  have hi0 : i ^ 2 + 1 = 0 := by rw [hi]; ring\n  have hn0 : (390 : S) * %s - 1 = 0 := by rw [hν0]; ring' % NU)
F_.append('  have h0 : pre q i D c1Evs 0 = ck0 q i %s D := by\n    ext r c; fin_cases r <;> fin_cases c <;> simp [pre, ck0]' % NU)
relsteps = set()
for j, e in enumerate(ev):
    st = stepsW[j+1]
    hasrel = '•' in st.split(':= by')[0]
    F_.append('  have h%d : pre q i D c1Evs %d = ck%d q i %s D := by' % (j+1, j+1, j+1, NU))
    F_.append('    rw [show pre q i D c1Evs %d = ((c1Evs[%d]?).map (evMat q i D)).getD 1 * pre q i D c1Evs %d from pre_succ q i D c1Evs %d, h%d,' % (j+1, j, j, j, j))
    F_.append('      show ((c1Evs[%d]?).map (evMat q i D)).getD 1 = evMat q i D (%s : Ev 4 3) from rfl, st%d]' % (j, evlean(e), j))
    if hasrel: F_.append('    simp only [hq0, hi0, hn0, zero_smul, add_zero]')
F_.append('  exact h%d\n' % len(ev))
F_.append("def C1W : CWord 4 3 := ⟨c1Evs, fun _ => 1, ![{1, 2}, {1, 2}, {0, 1, 2}, {0, 1, 2}]⟩\n")
F_.append('theorem c1_wf : WF C1W := by\n  intro e he s t a b h\n  subst h\n  simp [C1W, c1Evs] at he\n  rcases he with ⟨rfl, rfl, -, -⟩ | ⟨rfl, rfl, -, -⟩ | ⟨rfl, rfl, -, -⟩ <;> decide\n')
F_.append('theorem c1_legal : Legal C1W := by\n  refine ⟨c1_wf, ?_⟩\n  intro S _ _ q i D hq hi\n  show pre q i D c1Evs %d = target q D C1W\n  rw [c1_pre q i D hq hi]\n  ext r c; fin_cases r <;> fin_cases c <;> simp [ck%d, target, C1W, qp, Matrix.diagonal] <;> ring\n' % (len(ev), len(ev)))
F_.append('end final\n')
hostpos = [j for j, e in enumerate(ev) if e[0] == 'host']
J = ['section nonvac\nopen CallerAsm Finset']
J.append('theorem c1_odd : ∀ r, C1W.ex r % 2 = 1 := by intro r; fin_cases r <;> decide')
J.append('theorem c1_deg : ∀ r, 2 ≤ (C1W.mask r).card := by intro r; fin_cases r <;> decide')
J.append('theorem c1_card : Fintype.card (Iota C1W) = 6 := by\n  rw [Fintype.card_subtype]\n  decide +kernel')
hs = [ev[j] for j in hostpos]
def fv(vals): return '![' + ', '.join(vals) + ']'
J.append('def c1J : JB C1W where\n  pos := ![%s]\n  mono := by intro a b h; fin_cases a <;> fin_cases b <;> simp_all <;> decide\n  lt := fun s => by fin_cases s <;> decide\n  u := ![%s]\n  v := ![%s]\n  a := ![%s]\n  b := ![%s]\n  a0 := fun s => by fin_cases s <;> norm_num\n  b0 := fun s => by fin_cases s <;> norm_num\n  uv := fun s => by fin_cases s <;> decide\n  h0 := fun s => by fin_cases s <;> rfl\n  h1 := fun s => by fin_cases s <;> rfl\n  h2 := fun s => by fin_cases s <;> rfl\n' % (
    ', '.join(map(str, hostpos)), ', '.join(str(h[1]) for h in hs), ', '.join(str(h[2]) for h in hs), ', '.join(qlit(h[3]) for h in hs), ', '.join(qlit(h[4]) for h in hs)))
J.append('''/-- C1 discharges every hypothesis of `word_hp_B` except the stage K-block one (`hlam`, [C exact]: dets 2, -4, -5). -/
theorem c1_hp (hlam : ∀ s, IsUnit ((CallerSign.sgK (βw C1W) (CallerSign.sgG (Aw C1W Complex.I) (Bw C1W Complex.I))).submatrix
      (c1J.col s) (c1J.col s)).det) : cHat C1W ≤ CallerHP.HPr 3 :=
  word_hp_B c1_legal c1J c1_odd (le_refl 3) c1_card (by rw [c1_card]) hlam c1_deg

theorem c1_nonvac : Legal C1W ∧ (∀ r, C1W.ex r % 2 = 1) ∧ Fintype.card (Iota C1W) = 2 * 3 ∧ 4 + 2 = Fintype.card (Iota C1W)
    ∧ ∀ r, 2 ≤ (C1W.mask r).card :=
  ⟨c1_legal, c1_odd, c1_card, by rw [c1_card], c1_deg⟩
end nonvac
end CallerQZero
#print axioms CallerQZero.c1_legal
#print axioms CallerQZero.c1_nonvac
#print axioms CallerQZero.c1_hp
''')
hdr = '''/-
CallerQZero (lane QZERO, Nov 20).  A SPEC-legal caller word with Q = 0 and odd targets EXISTS.
C1 (built by lane D3STAR, Nov 19; JSON = data, cards/WILD/NOVEL/qzero/caller_C1.json): n = 4 roles, k = 3 stages (relabelled to call
order), three type-B J records HOST + 2 contacts, every other event q-even (ADD/SCALE/LAMBDA/IDLE_ONE), targets q * prod_{mask} D,
masks {1,2},{1,2},{0,1,2},{0,1,2}.  Columns = 6 = 2k (Q = 0) = n + 2 (tight).
`c1_legal` : Legal C1W (every commutative Q-algebra with q^4 = 1, i^2 = -1), proved by 69 exact checkpoint steps (generated by
  qz2.py; each step is a polynomial identity modulo q^4 - 1, i^2 + 1 and 390 * nu - 1, nu = 1/390, checked by `ring`).
`c1_nonvac` : Legal, odd targets, |Iota| = 2k, n + 2 = |Iota|, all degrees >= 2;  `c1_hp` : word_hp_B applies given hlam ([C] dets 2,-4,-5).
Kernel only: no sorry, no native_decide, no new axioms.
-/
'''
full = open('<tmpdir>').read().split('-/', 1)[1]
full = hdr + full + '\n' + '\n'.join(stepsW).replace('ν0 S', NU) + '\n' + '\n'.join(F_) + '\n' + '\n'.join(J)
open('<research-tree>/lean/decoder-duality/Nov15/CallerQZero.lean', 'w').write(full)
print('host positions', hostpos, 'lines', full.count('\n'))
