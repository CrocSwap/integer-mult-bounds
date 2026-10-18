"""Theorem R (rigidity of the minimal-rank label table), replayed.  Standard library only; kissat 4.0.4 and drat-trim are optional (SKIP lines without them).
For each registry instance (sat/rigid.py): the regenerated DIMACS must have the recorded sha256 (sat/results.jsonl); recorded statuses must equal the expected ones
(alt instances at the minimal rank: UNSAT, DRAT-VERIFIED when recorded; controls and negative controls: SAT with a decoded model); shipped proofs
(sat/proofs/*.drat.xz) are replayed with drat-trim; with kissat available every instance is re-solved, UNSAT proofs are checked, SAT models are decoded."""
import sys, os, json, time, lzma, tempfile, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(PKG, 'lib')); sys.path.insert(0, os.path.join(PKG, 'sat'))
from report import check, finish
from rigid import *
import solve as S_

rows = [json.loads(l) for l in open(os.path.join(PKG, 'sat', 'results.jsonl'))]
R = registry(); t0 = time.time()
check('c1.coverage', set(r['name'] for r in rows) == set(R) and len(rows) == len(R), 'every one of the %d registry instances has a recorded result' % len(R))
bad = [r['name'] for r in rows if r['status'] != r['expect'] or (r['status'] == 'UNSAT' and r.get('drat') != 'VERIFIED')]
check('c1.status', not bad, 'recorded statuses: %d UNSAT (all DRAT VERIFIED when recorded), %d SAT, none unexpected %s' % (
    sum(r['status'] == 'UNSAT' for r in rows), sum(r['status'] == 'SAT' for r in rows), bad[:3]))
badh = []; cnfs = {}
for r in rows:
    nv, cls, info, *_ = build_named(r['name']); d = dimacs(nv, cls)
    if sha(d) != r['cnf_sha256'] or nv != r['nv'] or len(cls) != r['ncls']: badh.append(r['name'])
    cnfs[r['name']] = d
check('c1.hash', not badh, 'regenerated DIMACS of all %d instances has the recorded sha256, #vars, #clauses %s (%.0f s)' % (len(rows), badh[:3], time.time() - t0))
# gauge cliques are pairwise non-orthogonal
def of_for(r):
    return p111()[1] if r['unit'] == 'P111' else orth
badg = [n for n, r in R.items() if any(of_for(r)(a, b) for a, b in itertools.combinations(r['S'], 2))]
check('c1.gauge', not badg, 'every gauge set S is a pairwise non-orthogonal clique (|S| = 8 for E8/P112/P104/P111, 7 for E7, 5 for E6)')
# the alt instances at the minimal rank: UNSAT <=> every fitting B of rank <= h is dense.  Controls: SAT and the decoded model is dense for h = rank(dense B)
ctl = [r for r in rows if r['mode'] == 'ctl']
check('c1.ctl', all(r['status'] == 'SAT' and r['model_fitting'] and r['orth_zero'] == 0 for r in ctl),
      'controls (no alt clause): all %d are SAT, every decoded model is a fitting matrix with 0 of its orthogonal entries equal to 0, i.e. equal to the dense B (h = rank of the dense B)' % len(ctl))
neg = [r for r in rows if r['name'].startswith('SUB') or r['name'].startswith('P112_') and r['h'] == 10]
check('c1.neg', all(r['status'] == 'SAT' and r['model_fitting'] and r['orth_zero'] > 0 for r in neg),
      'negative controls: %s are SAT with decoded fitting matrices that are NOT dense (orthogonal entries equal to 0: %s)' % (
          [r['name'] for r in neg], {r['name']: '%d/%d' % (r['orth_zero'], r['orth_total']) for r in neg}))
# shipped proofs
dt = S_.drat_trim(); ks = S_.kissat()
pdir = os.path.join(PKG, 'sat', 'proofs'); proofs = sorted(f for f in os.listdir(pdir) if f[:-len('.drat.xz')] in R) if os.path.isdir(pdir) else []
if dt and proofs:
    okp = 0; badp = []
    with tempfile.TemporaryDirectory() as td:
        for f in proofs:
            n = f[:-len('.drat.xz')]; cnf = os.path.join(td, 'x.cnf'); pr = os.path.join(td, 'x.drat')
            open(cnf, 'w').write(cnfs[n]); open(pr, 'wb').write(lzma.open(os.path.join(pdir, f)).read())
            if S_.run_drat(cnf, pr): okp += 1
            else: badp.append(n)
    check('c1.shipped', okp == len(proofs), 'drat-trim verifies all %d shipped DRAT proofs (sat/proofs, binary format) against the regenerated CNFs %s' % (okp, badp))
else:
    print('SKIP c1.shipped  drat-trim not found (set DRAT_TRIM=/path/to/drat-trim): %d shipped proofs not re-checked' % len(proofs), flush=True)
# re-solve with kissat
if ks:
    only = os.environ.get('RIGID_ONLY'); okr = 0; fails = []; nd = 0; t1 = time.time()
    with tempfile.TemporaryDirectory() as td:
        for r in rows:
            if only and only not in r['name']: continue
            cnf = os.path.join(td, 'x.cnf'); pr = os.path.join(td, 'x.drat'); open(cnf, 'w').write(cnfs[r['name']])
            st, model = S_.run_kissat(cnf, pr if r['expect'] == 'UNSAT' else None)
            good = st == r['expect']
            if good and st == 'UNSAT' and dt:
                good = S_.run_drat(cnf, pr); nd += 1
            if good and st == 'SAT':
                fit, z, n = decode_model(r['name'], model)
                good = fit and ((z == 0) if r['mode'] == 'ctl' else (z > 0))
            okr += good
            if not good: fails.append(r['name'])
    check('c1.resolve', not fails, 're-solved %d instances with kissat 4.0.4 (%s): all as expected (UNSAT, %d proofs checked by drat-trim; SAT: models decode to fitting matrices, dense for controls, non-dense for negative controls) %s (%.0f s)' % (
        okr, 'DRAT checked' if dt else 'drat-trim absent: UNSAT proofs NOT checked', nd, fails[:3], time.time() - t1))
else:
    print('SKIP c1.resolve  kissat not found (set KISSAT=/path/to/kissat): the %d recorded solver verdicts are not re-derived' % len(rows), flush=True)
print('   (c1 %.0f s)' % (time.time() - t0))
finish()
