"""E7 / punctured-unit facts used by the closures (standard library; kissat and drat-trim optional).
 (a) E7 = 63 lines, 135 orthogonal 7-frames; every one is a maximal orthogonal clique (PUNCTTHEORY D5 data).
 (b) hitting every 7-frame needs >= 10 lines: UNSAT at z = 9 (kissat + drat-trim if present, else SKIP), SAT at z = 10 (kissat).
 (c) Lemma H fact: omega of the non-orthogonality graph on N'(alpha) (56 lines) is 7; N(alpha) has omega 8.
 (d) Lemma CA (clique averaging) inputs: E7-minus-frame coordinate support, P112 coordinate support, E8 root support."""
import os, sys, hashlib, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('lib', 'sat'): sys.path.insert(0, os.path.join(HERE, '..', d))
from units import *
import solve, e7hit
from collections import Counter
ok = True
def chk(name, cond, extra=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + extra if extra else ''), flush=True); ok &= bool(cond)
def skip(name, why): print('SKIP ' + name + ' (' + why + ')', flush=True)
E7 = E7_IDX
F = e7hit.frames7()
chk('2.a E7 has 63 lines and 135 orthogonal 7-frames', len(E7) == 63 and len(F) == 135)
chk('2.a every 7-frame is a maximal orthogonal clique of E7 (no 8th orthogonal line inside E7)',
    all(not any(s not in [E7[i] for i in f] and all(orth(s, E7[i]) for i in f) for s in E7) for f in F))
def nonorth_cliques(S, w=None):
    adj = [sum(1 << j for j, s in enumerate(S) if s != t and not orth(t, s)) for t in S]
    return [bits(c) for c in maximal_cliques(adj)]
def omega_stats(S):
    C = nonorth_cliques(S); w = max(len(c) for c in C); top = [c for c in C if len(c) == w]
    cnt = Counter(i for c in top for i in c)
    return w, len(top), sorted(set(cnt.get(i, 0) for i in range(len(S))))
a = 0; Na = [t for t in range(120) if not orth(t, a)]
w, n, per = omega_stats([t for t in Na if t != a])
chk('2.c Lemma H: omega_non(N\'(alpha)) = 7 on 56 lines', len(Na) == 57 and w == 7, '(%d-cliques: %d)' % (w, n))
w8, n8, per8 = omega_stats(Na)
chk('2.d E8 root support N(alpha): 57 lines, omega 8, per-line counts not uniform', w8 == 8 and len(per8) > 1, 'per-line %s, #8-cliques %d' % (per8, n8))
fr7 = [E7[i] for i in F[0]]; f = fr7[0]
R7 = [t for t in E7 if t not in fr7 and not orth(t, f)]
w, n, per = omega_stats(R7)
chk('2.d Lemma CA input, E7 coordinate support (N(f) minus the 7-frame): |R|=32, omega=6, 32 six-cliques, 6 per line', len(R7) == 32 and w == 6 and n == 32 and per == [6], str((len(R7), w, n, per)))
P = P112_IDX; f0 = F0[0]; RP = [t for t in P if not orth(t, f0)]
w, n, per = omega_stats(RP)
chk('2.d P112 coordinate support (N(f) minus frame): |R|=56, omega=7 < rank 8, 576 seven-cliques, 72 per line', len(RP) == 56 and w == 7 and n == 576 and per == [72], str((len(RP), w, n, per)))
# (b) SAT
here = os.path.join(HERE, '..', 'sat', 'e7hit_cnf.sha256'); want = dict(l.split() for l in open(here))
tmp = tempfile.mkdtemp(prefix='e7hit.')
for z, exp in ((9, 'UNSAT'), (10, 'SAT')):
    nv, cl, nf = e7hit.cnf(z); txt = e7hit.dimacs(nv, cl); h = hashlib.sha256(txt.encode()).hexdigest()
    chk('2.b e7hit z=%d CNF regenerated: %d vars, %d clauses, sha256 matches' % (z, nv, len(cl)), h == want[str(z)])
    cnf = os.path.join(tmp, 'e7hit_%d.cnf' % z); open(cnf, 'w').write(txt)
    if not solve.kissat(): skip('2.b e7hit z=%d %s' % (z, exp), 'kissat absent'); continue
    pr = os.path.join(tmp, 'e7hit_%d.drat' % z)
    st, _ = solve.run_kissat(cnf, pr if exp == 'UNSAT' else None, 600)
    chk('2.b e7hit z=%d kissat verdict %s' % (z, exp), st == exp)
    if exp == 'UNSAT':
        if solve.drat_trim(): chk('2.b e7hit z=9 drat-trim VERIFIED (hitting number of the 135 frames is 10)', solve.run_drat(cnf, pr))
        else: skip('2.b e7hit z=9 drat-trim', 'drat-trim absent')
raise SystemExit(0 if ok else 1)
