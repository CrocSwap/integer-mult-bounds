"""Replay of the SAT/DRAT evidence (standard library only; drat-trim optional).
  * every instance of the registry (sat/instances.py) is regenerated from its generator and its DIMACS sha256 must equal the recorded one
    (sat/results.jsonl for the 51 primary instances + controls, sat/joint_results.jsonl for the 1,262 shared-B instances and 156 floor instances);
  * every recorded status equals the expected status (UNSAT for all lower bounds, SAT for all controls and existence claims);
  * every SAT model is checked clause by clause against the regenerated CNF;
  * every shipped DRAT proof (sat/proofs/*.drat.xz) is checked with drat-trim when it is available (environment DRAT_TRIM, or `drat-trim` on PATH);
    otherwise those lines are reported as SKIP (not PASS).
Set KISSAT_RESOLVE=n to also re-solve the first n joint instances with kissat and check their proofs."""
import sys, os, json, hashlib, lzma, subprocess, shutil, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(PKG, 'lib')); sys.path.insert(0, os.path.join(PKG, 'sat'))
from report import check, finish
import instances as I
from run import model_satisfies
from fractions import Fraction
from roots import UNITS, dot, gram, rank_q

def sha(b): return hashlib.sha256(b).hexdigest()
def rows(fn): return [json.loads(l) for l in open(os.path.join(PKG, 'sat', fn))]
prim = rows('results.jsonl'); joint = rows('joint_results.jsonl')
A = I.all_instances(); J = I.joint_instances(); ALL = dict(A); ALL.update(J)
t0 = time.time()
# registry coverage
check('c6.coverage', set(r['name'] for r in prim) == set(A) | {k for k in J if k.startswith('jointctrl')} and set(r['name'] for r in joint) == {k for k in J if not k.startswith('jointctrl')},
      'every registered instance has a recorded result: %d primary (incl. controls), %d shared-B and floor instances' % (len(prim), len(joint)))
plan = json.load(open(os.path.join(PKG, 'data', 'e6_joint_plan.json')))
check('c6.plan', all(sum(p['lo']) <= plan['total'] for p in plan['plan']) and len(plan['plan']) == 26 and sum(1 for k in J if k.startswith('joint_d')) == 1262 and sum(1 for k in J if k.startswith('floor_')) == 156,
      'plan: 26 decoders, floors sum to <= 35 for each (so the cap vectors with c_j >= lo_j, sum 35 are non-empty), 1,262 cap-vector instances, 156 floor instances')
# statuses
bad = [r['name'] for r in prim + joint if r['status'] != r['expect'] or (r['status'] == 'UNSAT' and r.get('drat') != 'VERIFIED') or (r['status'] == 'SAT' and not r.get('model_ok'))]
check('c6.status', not bad, 'recorded statuses: %d UNSAT instances DRAT-VERIFIED when recorded, %d SAT instances with checked models, none unexpected %s' % (
    sum(r['status'] == 'UNSAT' for r in prim + joint), sum(r['status'] == 'SAT' for r in prim + joint), bad[:3]))
# hashes
def regen_hash(name):
    c = ALL[name]['build'](); return sha(c.dimacs().encode()), c
badh = []; cnfs = {}
for r in prim:
    h, c = regen_hash(r['name'])
    if h != r['cnf_sha256']: badh.append(r['name'])
    if r['status'] == 'SAT': cnfs[r['name']] = c
check('c6.hash_primary', not badh, 'regenerated DIMACS of all %d primary instances has the recorded sha256 %s' % (len(prim), badh[:3]))
t1 = time.time(); badj = []
for r in joint:
    h, _ = regen_hash(r['name'])
    if h != r['cnf_sha256']: badj.append(r['name'])
check('c6.hash_joint', not badj, 'regenerated DIMACS of all %d shared-B/floor instances has the recorded sha256 (%.0f s) %s' % (len(joint), time.time() - t1, badj[:3]))
# shipped CNFs
badc = []; nc = 0
for f in sorted(os.listdir(os.path.join(PKG, 'sat', 'cnf'))):
    name = f[:-len('.cnf.xz')]
    if lzma.open(os.path.join(PKG, 'sat', 'cnf', f)).read().decode() != ALL[name]['build']().dimacs(): badc.append(name)
    nc += 1
check('c6.cnf', not badc and nc == len(prim), 'the %d shipped CNFs (sat/cnf/*.cnf.xz) equal the regenerated DIMACS text %s' % (nc, badc[:3]))
# models
nm = 0; okm = True
for r in prim:
    if r['status'] != 'SAT': continue
    pos = set(map(int, open(os.path.join(PKG, 'sat', 'models', r['name'] + '.model')).read().split()))
    okm &= model_satisfies(cnfs[r['name']].dimacs(), pos); nm += 1
check('c6.models', okm and nm > 0, 'all %d shipped SAT models satisfy the regenerated CNF clause by clause' % nm)
# the 26 E6 square decoders are exact (stdlib exact arithmetic): x_j, y_j span a 6-dim space, <y_i, x_j> != 0 iff i = j (so sum_j x_j y_j^T / <y_j,x_j> = id),
# the realised matrix M_ts = sum_j <l_t,x_j><l_s,y_j>/<y_j,x_j> equals the Gram matrix of the 36 lines exactly, and the stored dense sums equal the F2 ranks
from roots import b0rows, blk
from dirs import support
_L = UNITS['E6'][0]; _G = gram(_L); _Br = b0rows(_L); _n = len(_L)
_dec = json.load(open(os.path.join(PKG, 'data', 'e6_square_decoders.json')))['decoders']; _bad = []
for _d, _x in enumerate(_dec):
    X, Y = _x['X'], _x['Y']; dd = [dot(Y[j], X[j]) for j in range(6)]
    okd = rank_q([[Fraction(v) for v in r] for r in X]) == 6 and rank_q([[Fraction(v) for v in r] for r in Y]) == 6
    okd &= all((dot(Y[i], X[j]) != 0) == (i == j) for i in range(6) for j in range(6))
    okd &= all(sum(Fraction(dot(_L[t], X[j]) * dot(_L[s], Y[j]), dd[j]) for j in range(6)) == _G[t][s] for t in range(_n) for s in range(_n))
    dn = [blk(_Br, support(_L, X[j]), support(_L, Y[j])) for j in range(6)]
    okd &= dn == _x['dense'] and sum(dn) == _x['sum']
    if not okd: _bad.append(_d)
check('c6.decoders', len(_dec) == 26 and not _bad, 'the 26 E6 square decoders of data/e6_square_decoders.json are exact: rank 6 factors, <y_i,x_j> != 0 iff i = j, M = Gram of the 36 lines (Fractions), stored dense ranks and sums recomputed %s' % _bad[:3])
# DRAT
drat = os.environ.get('DRAT_TRIM') or shutil.which('drat-trim')
proofs = sorted(f for f in os.listdir(os.path.join(PKG, 'sat', 'proofs')) if f.endswith('.drat.xz'))
if drat and os.path.exists(drat):
    ok = 0; badp = []
    with tempfile.TemporaryDirectory() as td:
        for f in proofs:
            name = f[:-len('.drat.xz')]
            cnf = os.path.join(td, name + '.cnf'); pr = os.path.join(td, name + '.drat')
            open(cnf, 'w').write(ALL[name]['build']().dimacs()); open(pr, 'wb').write(lzma.open(os.path.join(PKG, 'sat', 'proofs', f)).read())
            d = subprocess.run([drat, cnf, pr, '-t', '3000'], capture_output=True, text=True)
            if 's VERIFIED' in d.stdout: ok += 1
            else: badp.append(name)
            os.remove(cnf); os.remove(pr)
    check('c6.drat', ok == len(proofs) and ok > 0, 'drat-trim (%s) verifies all %d shipped DRAT proofs against the regenerated CNFs %s' % (os.path.basename(drat), ok, badp[:3]))
else:
    print('SKIP c6.drat  drat-trim not found (set DRAT_TRIM=/path/to/drat-trim): %d shipped proofs not re-checked' % len(proofs), flush=True)
n = int(os.environ.get('KISSAT_RESOLVE', '0') or 0)
if n and shutil.which('kissat') and drat:
    from run import solve
    names = [r['name'] for r in joint if r['name'].startswith('joint_')][:n]; okk = 0
    with tempfile.TemporaryDirectory() as td:
        for nm_ in names:
            res = solve(nm_, ALL[nm_], td, tmo=600); okk += res['status'] == 'UNSAT' and res.get('drat') == 'VERIFIED'
    check('c6.resolve', okk == len(names), 're-solved %d shared-B instances with kissat; all UNSAT and DRAT-VERIFIED' % len(names))
print('   (replay %.0f s)' % (time.time() - t0))
finish()
