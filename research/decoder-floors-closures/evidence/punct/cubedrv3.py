r"""PUNCT7 ORBIT-TREE driver (cubedrv3.py typ P [leafTO]); leaf machinery = cubedrv2 (reduction + end-to-end DRAT); tree: see tree() docstring.\n(cubedrv2 header kept below for the leaf/symmetry details; its line-by-line node() split is replaced.)
Tree/symmetry exactly as cubedrv.py (PUNCT6): node = path of 'in' lines (S_s true, s outside F*); split on next outside line s:
leaves = one orbit rep z of options of s under the pointwise stabiliser in W_J of path+{s} (cube = path units + z), plus the S_s branch
(leaf, recursed as a node if it times out). Completeness: head clause S_s v OR z; WLOG-by-symmetry: g in W_J fixing the path lines maps a
model of F ∧ path to a model of F ∧ path with option set g(e) (CNF is W_J-invariant: checked below for every generator).
Leaf: cubered.reduce (UP + card-elim, see cubered.py) -> F'; kissat --no-binary on F'; proof = prefix (units of A, shortened clauses, deletions)
+ kissat DRAT, drat-trim against the UNREDUCED cube F ∧ units (no trust in the reducer). State: cube/st2_T_P.json (resumable)."""
import sys, json, os, subprocess, time, hashlib
from collections import defaultdict
typ, P = int(sys.argv[1]), int(sys.argv[2]); TO = int(sys.argv[3]) if len(sys.argv) > 3 else 120
sys.path.insert(0, '/Users/mason/repo_clones/intmult-work/cards/PUNCT4')
from p4lib import FLATREP, L
from sympy.combinatorics import Permutation, PermutationGroup
DT = '/Users/mason/repo_clones/intmult-work/tmp_dratchk/drat-trim/drat-trim'
flat = FLATREP[typ][1]
idx = {}
for t in range(120): idx[tuple(L[t])] = t; idx[tuple(-L[t])] = t
def refl(r): return [idx[tuple(L[t] - (2 * (L[t] @ L[r]) // (L[r] @ L[r])) * L[r])] for t in range(120)]
Wj = PermutationGroup([Permutation(refl(r)) for r in range(120) if flat[r]])
out = [s for s in range(120) if not flat[s]]
fn = f'cnf/rkd_{typ}_{P}.cnf'
raw = open(fn, 'rb').read(); md5 = hashlib.md5(raw).hexdigest()
lines = raw.decode().split('\n'); nv = int(lines[0].split()[2]); body = [l for l in lines[1:] if l.strip()]
cls = [list(map(int, l.split()))[:-1] for l in body]
del raw, lines
zset = defaultdict(set)
for c in cls:
    if len(c) == 2 and c[0] < -120 and 0 < c[1] <= 120: zset[-c[0]].add(c[1] - 1)
head = {}
for c in cls:
    if len(c) > 1 and 0 < c[0] <= 120 and all(x > 120 for x in c[1:]): head[c[0] - 1] = c[1:]
assert sorted(head) == out, 'every outside line has a head clause'
occ = defaultdict(list)
for i, c in enumerate(cls):
    for l in c: occ[l].append(i)
# W_J-invariance of the option structure (frames and cardinality are W-invariant by definition)
optsets = {s: {frozenset(zset[z]) for z in head[s]} for s in out}
for g in Wj.generators:
    for s in out:
        assert {frozenset(g(t) for t in e) for e in optsets[s]} == optsets[g(s)], 'CNF not W_J-invariant'
print(f'type {typ} P {P} md5 {md5} |W_J| {Wj.order()} out {len(out)} options {len(zset)} invariance OK', flush=True)

import numpy as np
from p4lib import G
def direct(model):
    """chkenc direct test on S = {t : var t true}: |S|<=P, frames hit, every live outside line has rank(live orth lines) < 7."""
    S = {v - 1 for v in model}
    if len(S) > P: return False
    orth = [set(np.flatnonzero(G[t] == 0).tolist()) for t in range(120)]
    def frames(cur, cand):
        if len(cur) == 8: yield cur; return
        for s in sorted(cand):
            if s > cur[-1]: yield from frames(cur + [s], cand & orth[s])
    if any(all(t not in S for t in f) for t0 in range(120) for f in frames([t0], orth[t0])): return False
    live = [t for t in range(120) if t not in S]
    return all(np.linalg.matrix_rank(L[[t for t in live if G[s, t] == 0]].astype(float)) < 7 for s in live if not flat[s])
class Conflict(Exception): pass
def reduce(U):
    val = {}; order = []; nfalse = defaultdict(int); sat = set()
    def assign(l, q):
        v = abs(l)
        if v in val:
            if val[v] != (l > 0): raise Conflict
            return
        val[v] = l > 0; order.append(l); q.append(l)
    def prop(q):
        while q:
            l = q.pop()
            sat.update(occ[l])
            for i in occ[-l]:
                if i in sat: continue
                nfalse[i] += 1; c = cls[i]
                if nfalse[i] >= len(c) - 1:
                    if any(val.get(abs(x)) == (x > 0) for x in c): sat.add(i); continue
                    free = [x for x in c if abs(x) not in val]
                    if not free: raise Conflict
                    if len(free) == 1: assign(free[0], q)
    q = []
    try:
        for u in U: assign(u, q)
        prop(q)
        while True:
            T = {t for t in range(120) if val.get(t + 1)}
            new = [z for z, e in zset.items() if z not in val and len(T | e) > P]
            if not new: break
            for z in new: assign(-z, q)
            prop(q)
    except Conflict:
        return order, None
    red = []
    for c in cls:
        if any(val.get(abs(x)) == (x > 0) for x in c): continue
        red.append([x for x in c if abs(x) not in val])
    return order, red
def wcnf(path, clauses, extra_units=()):
    with open(path, 'w') as f:
        f.write(f'p cnf {nv} {len(clauses) + len(extra_units)}\n')
        for c in clauses: f.write(' '.join(map(str, c)) + ' 0\n')
        for u in extra_units: f.write(f'{u} 0\n')
SF = f'cube/st3_{typ}_{P}.json'
state = json.load(open(SF)) if os.path.exists(SF) else {}
state['_md5'] = md5
def save(): json.dump(state, open(SF, 'w'), indent=0)
os.makedirs('red', exist_ok=True)
def leaf(name, units):
    if state.get(name, {}).get('res') in ('UNSAT-VERIFIED', 'SAT'): return state[name]['res']
    t0 = time.time()
    order, red = reduce(units)
    pre = f'red/{name}.full'
    with open(pre, 'w') as f:
        for l in order: f.write(f'{l} 0\n')
        if red is None: f.write('0\n')
        else:
            for c in red: f.write(' '.join(map(str, c)) + ' 0\n')
            for c in cls: f.write('d ' + ' '.join(map(str, c)) + ' 0\n')
    info = {'units': units, 'assigned': len(order)}
    if red is not None:
        rc = f'red/{name}.cnf'; wcnf(rc, [[l] for l in order] + red); info['red_clauses'] = len(order) + len(red)
        try:
            r = subprocess.run(['kissat', '-q', '--no-binary', rc, f'red/{name}.tdrat'], capture_output=True, text=True, timeout=TO).stdout
        except subprocess.TimeoutExpired:
            state[name] = dict(info, res='TIMEOUT'); save(); os.remove(pre); print(name, 'TIMEOUT', flush=True); return 'TIMEOUT'
        if 's SATISFIABLE' in r:
            state[name] = dict(info, res='SAT', model=[int(x) for x in ' '.join(l[2:] for l in r.split('\n') if l.startswith('v ')).split() if 0 < int(x) <= 120])
            state[name]['direct'] = direct(state[name]['model']); save(); print(name, 'SAT direct', state[name]['direct'], flush=True); return 'SAT'
        assert 's UNSATISFIABLE' in r, r[:300]
        info['kissat_s'] = round(time.time() - t0, 1)
        os.system(f"cat red/{name}.tdrat >> {pre}")
    else: info['up_conflict'] = True
    cube = f'red/{name}.cube.cnf'; wcnf(cube, cls, units)
    d = subprocess.run([DT, cube, pre, '-t', '1000'], capture_output=True, text=True).stdout
    ok = 's VERIFIED' in d
    info['res'] = 'UNSAT-VERIFIED' if ok else 'UNSAT-UNVERIFIED'; info['total_s'] = round(time.time() - t0, 1)
    os.remove(cube); os.remove(pre)
    if not ok: info['dt_tail'] = d[-400:]
    state[name] = info; save(); print(name, info, flush=True); return info['res']
def reps_of(path, s):
    grp = Wj
    for p in path: grp = grp.stabilizer(p)
    st = grp.stabilizer(s)
    sets = {frozenset(zset[z]): z for z in head[s]}
    seen = set(); reps = []
    for fs, z in sets.items():
        if fs in seen: continue
        reps.append(z); orb = {fs}; fr = [fs]
        while fr:
            x = fr.pop()
            for g in st.generators:
                y = frozenset(g(t) for t in x)
                if y not in orb: orb.add(y); fr.append(y)
        assert orb <= set(sets)
        seen |= orb
    return reps
def tree():
    """Orbit tree. W_J-orbits O_1, O_2, ... of outside lines (largest first). Every model of F has, for the first i with O_i not inside S,
    a live line of O_i; WLOG (g in W_J preserves every O_j, hence the units 'O_1..O_{i-1} inside S') it is the rep s_i = min(O_i);
    a live outside line is bad, so some option z of s_i holds (head clause with S_{s_i} false); WLOG z is an orbit rep under Stab(s_i).
    Once |O_1|+...+|O_i| > P the branch 'all inside S' is refuted by the cardinality constraint (leaf 'card', checked like the others)."""
    orbs = sorted({tuple(sorted(Wj.orbit(s))) for s in out}, key=lambda o: (-len(o), o))
    print('orbits', [len(o) for o in orbs], flush=True)
    forced = []; results = []
    for i, O in enumerate(orbs):
        if len(forced) > P:
            break
        s = O[0]; units = [t + 1 for t in forced]
        reps = reps_of([], s); print('LEVEL', i, '|forced|', len(forced), 'rep', s, 'option reps', len(reps), flush=True)
        for z in reps:
            results.append(leaf(f'T{typ}_{P}_o{i}_s{s}_z{z}', units + [z]))
        forced += list(O)
    if len(forced) > P:
        results.append(leaf(f'T{typ}_{P}_card{len(forced)}', [t + 1 for t in forced]))
    else:
        results.append('INCOMPLETE-all-outside-in-S')
    res = 'SAT' if 'SAT' in results else ('UNSAT-VERIFIED' if all(x == 'UNSAT-VERIFIED' for x in results) else 'INCOMPLETE')
    print('leaves', len(results), 'counts', {r: results.count(r) for r in set(results)}, flush=True)
    return res
res = tree(); print('TYPE', typ, 'P', P, 'RESULT', res, flush=True)
