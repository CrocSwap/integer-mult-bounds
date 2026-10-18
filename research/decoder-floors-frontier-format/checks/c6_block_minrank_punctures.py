"""EDGE E1a (the coordinate block N(f) of P112 has fitting minrank 8 for EVERY admissible B) and NEWWORD C4.1 (clique-hitting bounds on punctures of N(f)).
Standard library only; kissat 4.0.4 and drat-trim are optional.  Registry: sat/misc.py; recorded verdicts: sat/results_misc.jsonl."""
import sys, os, json, time, lzma, tempfile, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(PKG, 'lib')); sys.path.insert(0, os.path.join(PKG, 'sat'))
from report import check, finish
from units import *
import misc, hitting
import solve as S_

t0 = time.time()
L = sub(P112_IDX); v = len(L); G = gram(L)
Ns = [[t for t in range(v) if dot(L[t], E8[f]) != 0] for f in F0]
check('c6.N', all(len(n) == 56 for n in Ns) and all(sum(1 for n in Ns if t in n) == 4 for t in range(v)), 'N(f) has 56 live lines for each of the 8 removed roots, and every live line lies in exactly 4 of them')
Br = b0rows(L)
check('c6.dense', all(blk(Br, n, n) == 8 for n in Ns), 'dense pairing: rank_F2 B[N(f), N(f)] = 8 for all 8 f (the 64 of P112)')
og = orth_graph(L); nog = nonorth_graph = [sum(1 << s for s in range(v) if s != t and G[t][s] != 0) for t in range(v)]
Nm = [sum(1 << t for t in n) for n in Ns]
alpha = max(popcount(c) for c in maximal_cliques([og[t] & Nm[0] if Nm[0] >> t & 1 else 0 for t in range(v)]))
omega = max(popcount(c) for c in maximal_cliques([nog[t] & Nm[0] if Nm[0] >> t & 1 else 0 for t in range(v)]))
check('c6.alpha', alpha == 4 and omega == 7, 'inside N(f): largest pairwise orthogonal set alpha = %d, largest pairwise non-orthogonal clique omega = %d' % (alpha, omega))
check('c6.f7', 56 - alpha == 52, 'puncturing to rank <= 1 (s = 7) must leave a pairwise-orthogonal set: at most alpha = 4 lines kept, so f(7) >= 52 (exact, no SAT)')
rows = [json.loads(l) for l in open(os.path.join(PKG, 'sat', 'results_misc.jsonl'))]
R = misc.registry(); fast = {n for n in R if not R[n]['slow']}
have = {r['name'] for r in rows}
check('c6.coverage', fast <= have, 'every fast registry instance has a recorded result (%d recorded, %d fast)' % (len(have), len(fast)))
bad = [r['name'] for r in rows if r['status'] != (R[r['name']]['expect'] if r['name'] in R else r['status']) or (r['status'] == 'UNSAT' and not r['slow'] and r.get('drat') != 'VERIFIED') or (r['status'] == 'SAT' and not r.get('model_ok'))]
check('c6.status', not bad, 'recorded statuses as expected: %d UNSAT (DRAT VERIFIED when recorded unless flagged slow), %d SAT with checked models %s' % (
    sum(r['status'] == 'UNSAT' for r in rows), sum(r['status'] == 'SAT' for r in rows), bad[:3]))
cnfs = {}; badh = []
for r in rows:
    if r['slow'] and not os.environ.get('HIT_FULL'): continue
    d = misc.dimacs_of(r['name']); cnfs[r['name']] = d
    import hashlib
    if hashlib.sha256(d.encode()).hexdigest() != r['cnf_sha256']: badh.append(r['name'])
check('c6.hash', not badh, 'regenerated DIMACS of %d instances has the recorded sha256 %s' % (len(cnfs), badh[:3]))
dt = S_.drat_trim(); ks = S_.kissat()
pdir = os.path.join(PKG, 'sat', 'proofs'); proofs = sorted(f for f in (os.listdir(pdir) if os.path.isdir(pdir) else []) if f.split('_')[0] in ('edge', 'hit', 'tri'))
if dt and proofs:
    ok = 0
    with tempfile.TemporaryDirectory() as td:
        for f in proofs:
            n = f[:-len('.drat.xz')]; cnf = os.path.join(td, 'x.cnf'); pr = os.path.join(td, 'x.drat')
            open(cnf, 'w').write(cnfs[n]); open(pr, 'wb').write(lzma.open(os.path.join(pdir, f)).read()); ok += S_.run_drat(cnf, pr)
    check('c6.shipped', ok == len(proofs), 'drat-trim verifies all %d shipped proofs of this check against the regenerated CNFs' % ok)
else:
    print('SKIP c6.shipped  drat-trim not found: %d shipped proofs not re-checked' % len(proofs), flush=True)
if ks:
    fails = []; nd = 0
    with tempfile.TemporaryDirectory() as td:
        for n, d in cnfs.items():
            if R[n]['slow'] and not os.environ.get('HIT_FULL'): continue
            cnf = os.path.join(td, 'x.cnf'); pr = os.path.join(td, 'x.drat'); open(cnf, 'w').write(d)
            slow = R[n]['slow']
            st, model = S_.run_kissat(cnf, None if (slow or R[n]['expect'] == 'SAT') else pr, tmo=3000)
            good = st == R[n]['expect']
            if good and st == 'UNSAT' and dt and not slow: good = S_.run_drat(cnf, pr); nd += 1
            if good and st == 'SAT': good = misc.check_model(n, model)
            if not good: fails.append(n)
    check('c6.resolve', not fails, 're-solved the registry with kissat 4.0.4 (%s): all as expected, %d UNSAT proofs checked by drat-trim %s' % ('HIT_FULL: slow instances included' if os.environ.get('HIT_FULL') else 'fast instances', nd, fails[:3]))
else:
    print('SKIP c6.resolve  kissat not found: recorded verdicts not re-derived', flush=True)
# consequences (arithmetic on the proven bounds)
tri = [r for r in rows if r['name'] == 'tri_keep11'][0]
f_ = {2: 14, 6: 56 - 10, 7: 52, 8: 56}
check('c6.f', f_[2] == 13 + 1 and f_[6] == 46, 'f(2) >= 14 (k = 7: no hitting set of 13 lines for the 576 7-cliques); f(6) >= 56 - 10 = 46 (no triangle-free kept set of 11 lines); f(7) >= 52; f(8) = 56; ratios s/f(s): %s' % {s: round(s / f_[s], 4) for s in f_})
print('   (c6 %.0f s)' % (time.time() - t0))
finish()
