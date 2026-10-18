"""c3 tree coverage (CHECKED).  usage: c3_cover.py TYPE P K OPTSDIR WORKDIR
Re-walks the orbit tree of sat/middrv.py (orbits, Schreier generators, option representatives, symmetric re-splits of the recorded split nodes) with the
driver's own solve() but an ORACLE leaf(): a leaf answers UNSAT-VERIFIED only if data/states records it UNSAT-VERIFIED with the same (T, live);
a counting leaf (|T| > P) answers COUNT; anything else is reported.  PASS iff the walk ends with only UNSAT-VERIFIED / COUNT results, no chunk-restricted
leaf, no missing or mismatching leaf, and every recorded state entry is visited.  No SAT solver is run."""
import os, sys, json, shutil, io, contextlib
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
typ, P, k, optsdir, W = sys.argv[1:6]; W = os.path.abspath(W); os.makedirs(W, exist_ok=True)
shutil.copy(f'{optsdir}/opts56_{typ}.npz', W)
os.environ.update(MIDLIB='1', MIDWORK=W, MIDSKIPINV='1')
sys.argv = ['middrv.py', typ, P, k, '60']
ns = {'__name__': 'cover', '__file__': f'{PKG}/sat/middrv.py'}
cwd = os.getcwd()
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(open(f'{PKG}/sat/middrv.py').read(), 'middrv.py', 'exec'), ns)
os.chdir(cwd)
rec = json.load(open(f'{PKG}/data/states/T{typ}_P{P}_k{k}.json')); P = int(P)
ns['state'] = {n: (dict(v, res='TIMEOUT') if v.get('split') else dict(v)) for n, v in rec.items()}    # split nodes are re-split by the walk
ns['save'] = lambda: None
seen = set(); bad = []
def leaf(name, T, live, restrict=None):
    seen.add(name)
    if restrict: bad.append(('restrict', name))
    if len(T) > P: return 'COUNT'
    v = rec.get(name)
    if not v or v.get('split') or v['res'] != 'UNSAT-VERIFIED': bad.append(('missing', name)); return 'INCOMPLETE'
    if v['T'] != sorted(T) or v['live'] != live: bad.append(('mismatch', name)); return 'INCOMPLETE'
    return 'UNSAT-VERIFIED'
ns['leaf'] = leaf
_solve = ns['solve']
def solve(name, *a, **kw):
    seen.add(name); return _solve(name, *a, **kw)
ns['solve'] = solve
results = []
with contextlib.redirect_stdout(io.StringIO()):
    orbs, Wj = ns['orbs'], ns['Wj']; forced = []
    for i, O in enumerate(orbs):
        if len(forced) > P: break
        s = O[0]; reps = ns['reps_of'](s)
        WG = [list(g.array_form) for g in Wj.generators]; _, hs = ns['schreier'](WG, s, ns['actline'])
        reps.sort(key=lambda e: -len(set(forced) | e))
        for e in reps:
            nm = f'T{typ}_P{P}_k{k}_o{i}_' + ns['hashlib'].md5(str(sorted(e)).encode()).hexdigest()[:10]
            _, he = ns['schreier'](hs, e, ns['actset'])
            results.append(solve(nm, set(forced) | e, [s], None, 0, he))
        forced += list(O)
    results.append('COUNT' if len(forced) > P else 'INCOMPLETE-all-outside-in-S')
unv = [n for n in rec if n not in seen]
ok = set(results) <= {'UNSAT-VERIFIED', 'COUNT'} and not bad and not unv
print(('PASS ' if ok else 'FAIL ') + f'c3 T{typ} P{P} k{k}: tree walk {dict((r, results.count(r)) for r in set(results))}, visited {len(seen)} nodes, recorded {len(rec)}, unvisited {len(unv)}, bad {len(bad)} {bad[:2]}')
sys.exit(0 if ok else 1)
