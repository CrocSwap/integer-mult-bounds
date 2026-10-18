r"""Orbit-tree driver with DIRECT leaf encoding.  usage: middrv.py typ P k [leafTO] [maxleaves]
Problem (type typ, bound P, residue k): S ⊆ L, |S| <= P, every orthogonal 8-frame hit, q_g = |S ∩ g^perp| >= k for all 120 lines g
(for typ 7 also q_alpha >= 16 at the normal alpha of F*), and every live line s outside F* is bad: S ⊇ e for some option e of s
(opts56_T.npz from opts.py = rkdirect.py's inclusion-minimal sets s^perp \ F', F' a rank-7 flat through s, here kept for |e| <= 56).
Tree (as PUNCT5 cubedrv3): W_J-orbits O_1, O_2, ... of outside lines, largest first.  Every model has a first i with O_i ⊄ S; WLOG
(g in W_J preserves every orbit and the whole problem) s_i = min O_i is live, and WLOG its (some) option e is an orbit rep under
Stab_{W_J}(s_i).  Leaf (i, e): T = O_1 ∪ .. ∪ O_{i-1} ∪ e forced into S, s_i live.  If |T| > P the leaf is refuted by counting.
Once |O_1 ∪ .. ∪ O_i| > P the branch 'all inside S' is refuted by counting.
Leaf CNF (direct, written from scratch, no reduction step): vars S_t = t+1; units S_t (t in T), -S_{s_i}; |S| <= P (pysat seqcounter);
frames not hit by T; q-counters (own sequential counter, see qcnt); for every outside s not in T: head (S_s ∨ OR z_e) over the options
e of s with |T ∪ e| <= P, and z_e -> S_t for t in e \ T.  Soundness: a model S of the full problem in this branch has S ⊇ T and
|S| <= P, so any option e ⊆ S of a live s has |T ∪ e| <= P and is kept: the leaf CNF is satisfied by S (+ counters).  So UNSAT of
the leaf CNF refutes the branch.  Certificate: kissat --no-binary DRAT, drat-trim against exactly this leaf CNF.
State cube st/T{typ}_P{P}_k{k}.json (resumable)."""
import sys, json, os, subprocess, time, hashlib
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from e8punct import G, L
from pysat.card import CardEnc, EncType
from sympy.combinatorics import Permutation, PermutationGroup
typ, P, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
TO = int(sys.argv[4]) if len(sys.argv) > 4 else 600
MAXL = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
DT = os.environ.get('DRAT_TRIM', 'drat-trim'); KISSAT = os.environ.get('KISSAT', 'kissat')
WORK = os.environ.get('MIDWORK', '.'); os.makedirs(WORK + '/st', exist_ok=True); os.makedirs(WORK + '/red', exist_ok=True); os.chdir(WORK)   # opts56_T.npz (sat/opts.py), st/ and red/ live here
Z = np.load(f'opts56_{typ}.npz')
fl = set(Z['flat'].tolist()); out = Z['out'].tolist()
orbs = []; i = 0
while f'orb{i}' in Z.files: orbs.append(tuple(Z[f'orb{i}'].tolist())); i += 1
OPT = {}
for s in out:
    A = np.unpackbits(Z[f'o{s}'], axis=1)[:, :120].astype(bool); OPT[s] = A[A.sum(1) <= P]
Wj = PermutationGroup([Permutation(g.tolist()) for g in Z['gens']])
def rowkeys(A): return np.packbits(A, axis=1)
def permrows(A, g):        # rows e -> g(e)
    B = np.zeros_like(A); B[:, np.array(g.array_form)] = A; return B
for g in ([] if os.environ.get('MIDSKIPINV') else Wj.generators):    # (MIDSKIPINV=1: replay.py, which uses no W_J) W_J-invariance of the option structure (frames, q-counters, card are W-invariant)
    for s in out:
        a = np.unique(rowkeys(permrows(OPT[s], g)), axis=0); b = np.unique(rowkeys(OPT[g(s)]), axis=0)
        assert a.shape == b.shape and (a == b).all(), 'not W_J-invariant'
orth = [set(np.flatnonzero(G[t] == 0).tolist()) for t in range(120)]
FR = []
def dfs(cur, cand):
    if len(cur) == 8: FR.append(cur); return
    for s in sorted(cand):
        if s > cur[-1]: dfs(cur + [s], cand & orth[s])
for t in range(120): dfs([t], orth[t])
assert len(FR) == 2025
alpha = None
if typ == 7:
    alpha = [s for s in out if all(G[s, t] == 0 for t in fl)]; assert len(alpha) == 1; alpha = alpha[0]
    assert all(len(O) != 1 or O[0] == alpha for O in orbs)
qb = {g: k for g in range(120)}
if alpha is not None and not os.environ.get('NOALPHA'): qb[alpha] = max(k, 16)
print(f'type {typ} P {P} k {k} |F*| {len(fl)} orbits {[len(O) for O in orbs]} options {sum(len(A) for A in OPT.values())} alpha {alpha} invariance OK', flush=True)

def qcnt(lits, kk, nv, cls):
    """at least kk of lits true: r[i][j] = 'at least j true among first i'; r[i][0] = True, r[0][j>0] = False implicit.
    r[i][j] -> r[i-1][j] ∨ x_i ; r[i][j] -> r[i-1][j] ∨ r[i-1][j-1] ; assert r[n][kk].  Sound by induction on i."""
    n = len(lits); r = {}
    if kk <= 0: return nv
    for i in range(1, n + 1):
        for j in range(1, min(i, kk) + 1):
            nv += 1; r[i, j] = nv
            prev = r.get((i - 1, j))            # None => False (j > i-1)
            pj = r.get((i - 1, j - 1)) if j > 1 else 'T'
            c1 = [-nv, lits[i - 1]] + ([prev] if prev else []); cls.append(c1)
            if pj != 'T':
                c2 = [-nv] + ([prev] if prev else []) + ([pj] if pj else []); cls.append(c2)
    cls.append([r[n, kk]]) if kk <= n else cls.append([])
    return nv

def kept(s, T):
    Tv = np.zeros(120, bool); Tv[list(T)] = True; A = OPT[s]; return A[(A | Tv).sum(1) <= P]

def leafcnf(T, live, restrict=None):
    cls = [[t + 1] for t in sorted(T)] + [[-(s + 1)] for s in live]
    card = CardEnc.atmost(lits=list(range(1, 121)), bound=P, top_id=120, encoding=EncType.seqcounter)
    cls += card.clauses; nv = card.nv
    for f in FR:
        if not (set(f) & T): cls.append([t + 1 for t in f])
    for g in range(120):
        lits = [t + 1 for t in sorted(orth[g])]
        nv = qcnt(lits, qb[g], nv, cls)
    nopt = 0; Tv = np.zeros(120, bool); Tv[list(T)] = True
    for s in out:
        if s in T: continue
        head = [s + 1]; A = OPT[s]; KA = A[(A | Tv).sum(1) <= P]
        if restrict and s in restrict: KA = np.array([r for r in KA if frozenset(np.flatnonzero(r).tolist()) in restrict[s]], dtype=bool).reshape(-1, 120)     # branch: s live and one of these options holds
        for row in KA:
            nv += 1; head.append(nv); nopt += 1
            for t in np.flatnonzero(row & ~Tv): cls.append([-nv, int(t) + 1])
        cls.append(head)
    return nv, cls, nopt

def direct(S):
    S = set(S)
    if len(S) > P or any(len(S & orth[g]) < qb[g] for g in range(120)): return False
    if any(not (set(f) & S) for f in FR): return False
    live = [t for t in range(120) if t not in S]
    return all(np.linalg.matrix_rank(L[[t for t in live if G[s, t] == 0]].astype(float)) < 7 for s in live if s not in fl)

SF = f'st/T{typ}_P{P}_k{k}.json'
state = json.load(open(SF)) if os.path.exists(SF) else {}
def save(): json.dump(state, open(SF, 'w'), indent=0)
nleaf = [0]
def leaf(name, T, live, restrict=None):
    c = state.get(name)
    if c and 'T' in c and (c['T'] != sorted(T) or c.get('live') != live):   # audit fix: never reuse a cached result for a different cube
        name = name + '_' + hashlib.md5(str((sorted(T), live, sorted((a, sorted(map(sorted, b))) for a, b in (restrict or {}).items()))).encode()).hexdigest()[:10]
    if state.get(name, {}).get('res') in ('UNSAT-VERIFIED', 'SAT', 'COUNT'): return state[name]['res']
    if nleaf[0] >= MAXL: return 'SKIPPED'
    nleaf[0] += 1
    t0 = time.time(); info = {'T': sorted(T), 'live': live, 'restrict': {str(a): len(b) for a, b in (restrict or {}).items()}}
    if len(T) > P:
        info['res'] = 'COUNT'; state[name] = info; save(); return 'COUNT'
    nv, cls, nopt = leafcnf(T, live, restrict)
    fn = f'red/{name}.cnf'
    with open(fn, 'w') as f:
        f.write(f'p cnf {nv} {len(cls)}\n')
        for c in cls: f.write(' '.join(map(str, c)) + ' 0\n')
    info.update(clauses=len(cls), nopt=nopt, md5=hashlib.md5(open(fn, 'rb').read()).hexdigest())
    try:
        r = subprocess.run([KISSAT, '-q', '--no-binary', fn, f'red/{name}.drat'], capture_output=True, text=True, timeout=TO).stdout
    except subprocess.TimeoutExpired:
        info['res'] = 'TIMEOUT'; info['s'] = round(time.time() - t0, 1); state[name] = info; save()
        os.remove(f'red/{name}.drat'); print(name, info['res'], info['clauses'], nopt, flush=True); return 'TIMEOUT'
    info['kissat_s'] = round(time.time() - t0, 1)
    if 's SATISFIABLE' in r:
        mdl = [int(x) for x in ' '.join(l[2:] for l in r.split('\n') if l.startswith('v ')).split() if 0 < int(x) <= 120]
        info.update(res='SAT', model=mdl, direct=direct([v - 1 for v in mdl])); state[name] = info; save()
        print(name, 'SAT direct', info['direct'], flush=True); return 'SAT'
    assert 's UNSATISFIABLE' in r, r[:300]
    d = subprocess.run([DT, fn, f'red/{name}.drat', '-t', '540'], capture_output=True, text=True).stdout
    ok = 's VERIFIED' in d
    info['res'] = 'UNSAT-VERIFIED' if ok else 'UNSAT-UNVERIFIED'; info['s'] = round(time.time() - t0, 1)
    if not ok: info['dt_tail'] = d[-300:]; os.remove(f'red/{name}.drat'); os.remove(fn)
    else: os.remove(f'red/{name}.drat'); os.remove(fn)
    state[name] = info; save(); print(name, info['res'], 'cls', info['clauses'], 'opt', nopt, 'k', info['kissat_s'], 'tot', info['s'], flush=True)
    return info['res']

NCH = int(os.environ.get('NCH', '6'))
ID = list(range(120))
def compose(a, b): return [a[b[t]] for t in range(120)]          # (a∘b)(t) = a(b(t))
def inverse(a):
    r = [0] * 120
    for t in range(120): r[a[t]] = t
    return r
def schreier(gens, x0, act, cap=300):
    """orbit of x0 under <gens> with action act(g, x); returns (orbit dict x -> transversal element, Schreier generators of Stab(x0)).
    A capped generator list generates a SUBGROUP of the stabiliser: orbit reps under it are still a valid WLOG (only coarser)."""
    tr = {x0: ID}; fr = [x0]; sg = []
    while fr:
        x = fr.pop()
        for g in gens:
            y = act(g, x); gx = compose(g, tr[x])
            if y not in tr: tr[y] = gx; fr.append(y)
            elif len(sg) < cap:
                w = compose(inverse(tr[y]), gx)
                if w != ID and w not in sg: sg.append(w)
    return tr, sg
def actline(g, x): return g[x]
def actset(g, x): return frozenset(g[t] for t in x)
def orbits_under(gens, items, act):
    seen = {}; reps = []
    for x in items:
        if x in seen: continue
        reps.append(x); o = {x}; fr = [x]
        while fr:
            y = fr.pop()
            for g in gens:
                z = act(g, y)
                if z not in o: o.add(z); fr.append(z)
        for y in o: seen[y] = x
    return reps, seen
def solve(name, T, live, restrict=None, depth=0, gens=None):
    """leaf; if it times out / fails verification: symmetric orbit split under H = <gens> (H preserves T, the live set, the restriction
    and the whole problem): O = largest H-orbit of outside lines not in T ∪ live.  Branch 'O ⊆ S' (T ∪ O; counting leaf if > P);
    else WLOG s' = min O live, with option e' an orbit rep under Stab_H(s') (Schreier); child group = Stab_{Stab_H(s')}(e').
    If H is trivial or not given: chunk split (s2 in S | s2 live with an option from chunk i)."""
    prior = state.get(name, {}).get('res')
    if prior and (state[name].get('T') not in (None, sorted(T)) or state[name].get('live') not in (None, live)): prior = None
    if prior not in ('UNSAT-VERIFIED', 'SAT', 'COUNT') and gens and depth == 0 and len(T) <= P and sum(len(kept(x, T)) for x in out if x not in T) > 8000:
        prior = 'TIMEOUT'; print(name, 'PRESPLIT (kept options > 8000)', flush=True)    # known-hard shape: split without a first attempt
    r = prior if prior in ('TIMEOUT', 'UNSAT-UNVERIFIED') else leaf(name, T, live, restrict)
    if r not in ('TIMEOUT', 'UNSAT-UNVERIFIED') or depth >= 4: return r
    cand = [x for x in out if x not in T and x not in live]
    if not cand: return r
    res = []
    if gens:
        oreps, seen = orbits_under(gens, cand, actline)
        O = max(([y for y in cand if seen[y] == x] for x in oreps), key=len); s1 = min(O)
        print(name, 'SYM-SPLIT orbit', len(O), 'rep', s1, '|T|', len(T), flush=True)
        if len(set(T) | set(O)) > P: res.append('COUNT')
        else: res.append(solve(name + f'_O{s1}', set(T) | set(O), live, restrict, depth + 1, gens))
        _, h1 = schreier(gens, s1, actline)
        K1 = [frozenset(np.flatnonzero(row).tolist()) for row in kept(s1, T)]
        if restrict and s1 in restrict: K1 = [e for e in K1 if e in restrict[s1]]
        Ks = set(K1)
        ereps, _ = orbits_under(h1, K1, actset)
        assert all(actset(g, e) in Ks for g in h1 for e in K1[:50]), 'option set not invariant'
        print(name, '  rep', s1, 'kept', len(K1), 'option reps', len(ereps), flush=True)
        for e1 in ereps:
            _, h2 = schreier(h1, e1, actset)
            nm = name + f'_L{s1}_' + hashlib.md5(str(sorted(e1)).encode()).hexdigest()[:6]
            res.append(solve(nm, set(T) | e1, live + [s1], restrict, depth + 1, h2))
    else:
        s2 = min(cand, key=lambda x: (len(kept(x, T)), x)); n2 = len(kept(s2, T))
        print(name, 'SPLIT on', s2, 'kept options', n2, flush=True)
        res.append(solve(name + f'_A{s2}', set(T) | {s2}, live, restrict, depth + 1))
        K2 = [frozenset(np.flatnonzero(row).tolist()) for row in kept(s2, T)]
        ch = [set(K2[i::NCH]) for i in range(min(NCH, n2))]
        for i, c in enumerate(ch):
            rr = dict(restrict or {}); rr[s2] = c
            res.append(solve(name + f'_B{s2}c{i}', T, live + [s2], rr, depth + 1))
    out_r = 'SAT' if 'SAT' in res else ('UNSAT-VERIFIED' if set(res) <= {'UNSAT-VERIFIED', 'COUNT'} else 'INCOMPLETE')
    print(name, 'SPLIT RESULT', out_r, {x: res.count(x) for x in set(res)}, flush=True)
    if out_r == 'UNSAT-VERIFIED': state[name] = dict(state.get(name, {}), res='UNSAT-VERIFIED', split=True); save()
    return out_r

def reps_of(s):
    st = Wj.stabilizer(s); A = OPT[s]; key = {r.tobytes(): j for j, r in enumerate(rowkeys(A))}
    par = list(range(len(A)))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for g in st.generators:
        img = rowkeys(permrows(A, g))
        for j, r in enumerate(img):
            par[f(j)] = f(key[r.tobytes()])          # KeyError would mean non-invariance
    roots = sorted({f(j) for j in range(len(A))})
    return [frozenset(np.flatnonzero(A[j]).tolist()) for j in roots]

if not os.environ.get('MIDLIB'):
    forced = []; results = []
    for i, O in enumerate(orbs):
        if len(forced) > P: break
        s = O[0]; reps = reps_of(s)
        WG = [list(g.array_form) for g in Wj.generators]; _, hs = schreier(WG, s, actline)
        reps.sort(key=lambda e: -len(set(forced) | e))     # most-forced first (cheap leaves first)
        print('LEVEL', i, '|forced|', len(forced), 'rep', s, 'option reps', len(reps), flush=True)
        for e in reps:
            nm = f'T{typ}_P{P}_k{k}_o{i}_' + hashlib.md5(str(sorted(e)).encode()).hexdigest()[:10]
            _, he = schreier(hs, e, actset)
            results.append(solve(nm, set(forced) | e, [s], None, 0, he))
        forced += list(O)
    if len(forced) > P: results.append('COUNT')
    else: results.append('INCOMPLETE-all-outside-in-S')
    cnt = {r: results.count(r) for r in set(results)}
    res = 'SAT' if 'SAT' in results else ('UNSAT-VERIFIED' if set(results) <= {'UNSAT-VERIFIED', 'COUNT'} else 'INCOMPLETE')
    print('leaves', len(results), 'counts', cnt, flush=True)
    print('TYPE', typ, 'P', P, 'k', k, 'RESULT', res, flush=True)

