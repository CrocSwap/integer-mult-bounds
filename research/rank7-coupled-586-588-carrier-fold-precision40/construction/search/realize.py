"""realize.py -- realise a rank-8 composition at normal N restricted to support X (+ registers already at E_N), prescribed pivots,
exact: GL(Z[1/2]) synthesis, structure.py, certified frames, PR2833 auditor at every step.
usage: python -B realize.py WORD.json.gz N 'x1,x2,..' 'p1,p2,..' TAG"""
import sys, json, itertools, collections
sys.path.insert(0, 'S/r13/agents/A-extract/code')
from synth import *
from lower import per_normal_R, terminal_lower, lower_pool
from pairsearch import restrict
BE = 2091300
w0 = load(sys.argv[1]); N = int(sys.argv[2]); X = set(int(a) for a in sys.argv[3].split(',')); order = [int(a) for a in sys.argv[4].split(',')]; tag = sys.argv[5]
base0 = solve_frames(w0, key='b0'); cur = w0; cur_pf = base0; rows = []
for k, h in enumerate(order, 1):
    fr = frames(cur); sp = CE.spaces(cur, fr=fr); tl, g, al = terminal_lower(cur); R, E = lower_pool(cur, tl, N)
    Eb = tuple(PM.basis(E)); F0 = {r for r in R if fr['terminal'][r] == Eb}
    res = per_normal_R(cur, sp, N, R); allowed = ((X | F0) & set(R)) | {h}
    A, Au = restrict(res['alphas'], res['us'], allowed); Y, Yv = restrict(res['ys'], res['vs'], allowed)
    best = None; rng = [Q(-1), Q(0), Q(1)]
    for ac in itertools.product(rng, repeat=len(A)):
        if not any(ac): continue
        c = {i: x for i, x in enumerate(ac) if x}; alpha = comb(c, A); u = comb(c, Au)
        for bc in itertools.product(rng, repeat=len(Y)):
            if not any(bc): continue
            d = {j: x for j, x in enumerate(bc) if x}; y = comb(d, Y); v = comb(d, Yv)
            if dot(alpha, y) == 0: continue
            pr = normalise_pair(alpha, u, v, y)
            if pr is None: continue
            T = set(pr['alpha']) | set(pr['y']); key = (len(T - F0 - {h}), 0 if h in pr['alpha'] else 1, len(T))
            if best is None or key < best[0]: best = (key, pr)
    if best is None: rows.append(dict(step=k, pivot=h, status='no pair')); print(tag, k, h, 'no pair', flush=True); break
    r = run_direction_general(cur, h, N, best[1], cur_pf, label=f'{tag}/{h}')
    if r.get('status') != 'PASS': rows.append(dict(step=k, pivot=h, status=r.get('status'), structure=r.get('structure'))); print(tag, k, h, r.get('status'), flush=True); break
    cur = r['word']; cur_pf = solve_frames(cur); cum = cur_pf['cost'] - base0['cost']
    dp = collections.Counter(cur_pf['profile']); dp.subtract(collections.Counter(base0['profile']))
    rows.append(dict(step=k, pivot=h, delta=r['delta_units'], cumulative=cum, margin=-cum - k * BE, structure=r['structure'][:30], audit=r['audit'],
                     touched=r['touched'], profile=cur_pf['profile'], profile_delta={a: b for a, b in sorted(dp.items()) if b}, inventory=cur['report']['width_inventory'], transform=r['transform']))
    print(tag, 'step', k, 'pivot', h, 'delta', r['delta_units'], 'cumulative', cum, 'margin', -cum - k * BE, r['structure'][:12], 'audit', r['audit'], 'touched', r['touched'], flush=True)
    dump(cur, f'{tag}-step{k}.json.gz')
json.dump(rows, open(f'{tag}.json', 'w'), indent=1, default=str)
