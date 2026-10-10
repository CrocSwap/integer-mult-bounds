"""Re-derive target-prefix square groups (eumemic #268 / #287 transform) on a word.
usage: target_search.py PKG DESCENT_SELECTION OUT.json [--compare FROZEN]"""
import sys, importlib.util, json, time, math, hashlib
from itertools import combinations
from collections import Counter, defaultdict
from pathlib import Path
root = Path(sys.argv[1]).resolve(); dsel = sys.argv[2]; outp = Path(sys.argv[3])
def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
t0 = time.time()
context = load('portable527_prepare', root / 'prepare.py').prepare()
producer = load('portable527_physical', root / 'code/physical527.py').run(dict(context), context['SOURCE_TEXT'], output_dir=None)
pr = load('portable527_parity', root / 'parity_transform.py').run(producer, output_dir=None)
dr = load('portable527_descent', root / 'descent_transform.py').run(pr, output_dir=None, selection_path=dsel)
print('descent done %.0fs' % (time.time() - t0), flush=True)
W, C = dr['W'], dr['C']; v = W.v; rec = dr['records']; initial = dr['initial_state']; n = len(initial); ZERO, FULL = dr['ZERO'], dr['FULL']
N = len(rec) // 6
final = {i: FULL for i in initial}
for t in range(v): final[v + t] = W.register(W.module.kernel([C.cov[t]], W.h)[0])
cut = None
for i in range(N):
    if rec[6*i] == 0 and v <= rec[6*i+1] < 2*v: cut = i; break
print('cut', cut, flush=True)
# pass: columns as int bitsets; per-target add list (i, dim, frame, src) and response snapshots after cut; first move per target
columns = [1 << i for i in range(n)]; center = None
adds = defaultdict(list); snaps = defaultdict(list); resp = defaultdict(int); firstmove = {}; src_use = defaultdict(list)
needs = {s: [] for s in initial}   # (record, frame) for census simulation
for i in range(N):
    op, a, b, c, f, z = rec[6*i:6*i+6]
    if op == 0:
        if v <= a < 2*v and a - v not in firstmove: firstmove[a - v] = i
        continue
    if op == 2: center = a; needs[a].append((i, c)); continue
    if op == 3: center = None; continue
    actual = center if b == n else b
    needs[a].append((i, f))
    if b != n: needs[b].append((i, f))
    if v <= actual < 2*v: src_use[actual - v].append(i)
    if v <= a < 2*v:
        t = a - v; adds[t].append((i, C.dimf[f], f, actual))
        if i > cut and not (v <= actual < 2*v):
            resp[t] ^= columns[actual]; snaps[t].append((i, resp[t]))
    columns[a] ^= columns[actual]
assert center is None
print('scan done %.0fs' % (time.time() - t0), flush=True)
def resp_upto(t, close):
    r = 0
    for i, x in snaps[t]:
        if i <= close: r = x
        else: break
    return r
LN = [0.0] + [d * math.log(120 / d) for d in range(1, 121)]
def chain_hist(s, seq):
    H = Counter(); bef = initial[s]
    for f in seq + [final[s]]:
        assert C.sub(bef, f), ('nest', s); d = C.dimf[f] - C.dimf[bef]
        if d: H[d] += 1
        bef = f
    return H
def try_group(T, dep):
    if any(C.dimf[f] != 0 or f != ZERO for t in T for (i, f) in needs[v + t] if i <= cut): return None
    if any(initial[v + t] != ZERO for t in T): return None
    l20 = [i for t in T for (i, d, f, s) in adds[t] if i > cut and d == 20]
    if not l20: return None
    close = max(l20)
    if any(i <= close for t in T for i in src_use[t]): return None
    ret = [t for t in T if t != dep]
    if resp_upto(dep, close) ^ resp_upto(ret[0], close) ^ resp_upto(ret[1], close) ^ resp_upto(ret[2], close): return None
    # dependent's deleted adds must have non-target sources (they do by construction of snaps); every add of dep in (cut,close] deleted
    # close frame: the common first need after close of all four targets (the frozen #287 groups all have this form)
    nxts = []
    for t in T:
        nx = [f for (i, f) in needs[v + t] if i > close]
        nxts.append(nx[0] if nx else final[v + t])
    F = nxts[0]
    if not all(C.sub(F, g) and C.sub(g, F) for g in nxts): return None
    if C.dimf[F] != 21 or not C.nondeg(F): return None
    if not all(all(W.module.dot(C.cov[t], b) == 0 for b in C.B[F]) for t in T): return None
    # census simulation for the 4 targets
    delta = Counter(); ok = True
    for t in T:
        s = v + t; seq_old = [f for (i, f) in needs[s]]
        new = []; inserted_cut = False; inserted_close = False
        for (i, f) in needs[s]:
            if i > cut and not inserted_cut:
                new.extend([ZERO] * (3 if t == dep else 1)); inserted_cut = True
            if i > close and not inserted_close:
                new.extend([F] * (3 if t == dep else 1)); inserted_close = True
            if t == dep and cut < i <= close: continue
            new.append(f)
        if not inserted_cut: new.extend([ZERO] * (3 if t == dep else 1))
        if not inserted_close: new.extend([F] * (3 if t == dep else 1))
        try:
            H0 = chain_hist(s, seq_old); H1 = chain_hist(s, new)
        except AssertionError:
            return None
        delta.update(H1); delta.subtract(H0)
    delta = {d: c for d, c in delta.items() if c}
    gain = sum(LN[d] * c for d, c in delta.items())
    return dict(targets=sorted(T), cut_record=cut, close_after_record=close, dependent={str(dep): ret}, retained=ret, close_rank=21,
                close_basis=[list(map(int, r)) for r in C.B[F]], local_histogram_delta={str(d): c for d, c in sorted(delta.items())},
                score=round(-gain, 2), extra_setup_restore_additions=6)
groups = []; used = set()
cubes = v // 8
for cube in range(cubes):
    ports = list(range(8 * cube, 8 * cube + 8))
    cands = []
    for T in combinations(ports, 4):
        for dep in T:
            g = try_group(T, dep)
            if g and g['score'] > 0: cands.append(g)
    cands.sort(key=lambda g: -g['score'])
    for g in cands:
        if not set(g['targets']) & used:
            groups.append(g); used.update(g['targets'])
print('groups', len(groups), 'score sum %.2f' % sum(g['score'] for g in groups), Counter(json.dumps(g['local_histogram_delta']) for g in groups).most_common(5), '%.0fs' % (time.time() - t0), flush=True)
tot = Counter()
for g in groups: tot.update({int(k): v_ for k, v_ in g['local_histogram_delta'].items()})
sel = dict(input_raw_sha256=hashlib.sha256(rec.tobytes()).hexdigest(), input_scalar_sha256=dr['physical']['scalar_projection_sha256'], cut_record=cut,
           rebase_parent='gen5 parity-fused word after the concave-descent retiming (groups re-derived by gen5/target_search.py)',
           expected_total_delta={str(k): c for k, c in sorted(tot.items()) if c}, groups=groups)
outp.write_text(json.dumps(sel, indent=1) + '\n')
if len(sys.argv) > 5 and sys.argv[4] == '--compare':
    fz = json.loads(Path(sys.argv[5]).read_text())
    A = {tuple(g['targets']): g for g in fz['groups']}; B = {tuple(g['targets']): g for g in groups}
    print('frozen', len(A), 'mine', len(B), 'same targets', len(set(A) & set(B)), 'identical rows', sum(json.dumps(A[k], sort_keys=True) == json.dumps(B[k], sort_keys=True) for k in set(A) & set(B)), 'frozen total', fz['expected_total_delta'], 'mine', sel['expected_total_delta'])
    k = next(iter(set(A) & set(B)), None)
    if k: print('frozen', {x: A[k][x] for x in A[k] if x != 'close_basis'}); print('mine  ', {x: B[k][x] for x in B[k] if x != 'close_basis'}, A[k]['close_basis'] == B[k]['close_basis'])
