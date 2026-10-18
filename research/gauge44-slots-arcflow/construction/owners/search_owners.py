"""Whole-owner packing search for the gauge44 seven-slot k8 word (search input only; the verifier never runs it).

1. Aggregate LP/MILP over bin patterns per (owner replica, idle child) class and per-call width counts (agg1):
   its LP optimum equals the time-free relaxation, so the owner windows do not bind.
2. Exactly liftable MILP (agg2): pattern counts n(c,p) and per-pattern time incidences x(c,p,t,w) with
   sum_t x = n*mult, sum_w x <= n per call, sum over classes/patterns = the call's width inventory.
3. Lift (lift2): each pattern's times x positions multigraph has maximum degree n and is properly n-edge-coloured
   (Konig); every colour class is one literal port; offsets are the partial sums of the pattern positions.
Requires numpy and scipy (HiGHS). Usage: python3 search_owners.py PLAN.json OWNERS.json.gz [milp seconds]
Prepared by G. V. Chudnovsky with Anthropic Claude assistance. Apache-2.0.
"""
import json, gzip, math, sys, time
from collections import Counter, defaultdict
import numpy as np, scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds


def phi(r): return 0.0 if r == 0 else r * math.log(73 / r)

def patterns(cap, widths, maxrem):
    out = []
    def rec(i, rem, cur):
        if i == len(widths):
            if rem <= maxrem or rem == cap: out.append(tuple(cur))
            return
        w = widths[i]
        for k in range(rem // w + 1):
            rec(i + 1, rem - k * w, cur + [k])
    rec(0, cap, [])
    return out

def build(plan, inv, maxrem=3, ports=112):
    widths = sorted(inv)
    classes = []
    for key, (cap, times) in sorted(plan['windows'].items(), key=lambda kv: tuple(map(int, kv[0].split(',')))):
        rep, i = map(int, key.split(',')); classes.append((rep, i, cap, list(times)))
    ncalls = len(plan['order'])
    pats = {cap: patterns(cap, widths, maxrem) for cap in {c[2] for c in classes}}
    var = []; cost = []
    nidx = {}; yidx = {}
    for ci, (rep, i, cap, times) in enumerate(classes):
        for pi, p in enumerate(pats[cap]):
            nidx[ci, pi] = len(var); var.append(('n', ci, pi)); cost.append(phi(cap - sum(k * w for k, w in zip(p, widths))))
        for t in times:
            for w in widths:
                yidx[ci, t, w] = len(var); var.append(('y', ci, t, w)); cost.append(0.0)
    rows, cols, vals, lo, hi = [], [], [], [], []
    r = 0
    def addrow(entries, a, b):
        nonlocal r
        for j, v in entries: rows.append(r); cols.append(j); vals.append(v)
        lo.append(a); hi.append(b); r += 1
    for ci, (rep, i, cap, times) in enumerate(classes):
        addrow([(nidx[ci, pi], 1.0) for pi in range(len(pats[cap]))], ports, ports)
        for wi, w in enumerate(widths):
            e = [(yidx[ci, t, w], 1.0) for t in times] + [(nidx[ci, pi], -float(p[wi])) for pi, p in enumerate(pats[cap]) if p[wi]]
            addrow(e, 0, 0)
        for t in times:
            addrow([(yidx[ci, t, w], 1.0) for w in widths], 0, ports)
    bycall = defaultdict(list)
    for (ci, t, w), j in yidx.items(): bycall[t, w].append(j)
    for t in range(ncalls):
        for w in widths:
            addrow([(j, 1.0) for j in bycall[t, w]], inv[w], inv[w])
    A = sp.csr_matrix((vals, (rows, cols)), shape=(r, len(var)))
    return dict(classes=classes, pats=pats, widths=widths, var=var, cost=np.array(cost), A=A, lo=np.array(lo), hi=np.array(hi), nidx=nidx, yidx=yidx)

def solve(M, time_limit=600, integral=True, gap=1e-6):
    t = time.time()
    res = milp(M['cost'], constraints=LinearConstraint(M['A'], M['lo'], M['hi']),
               integrality=np.ones(len(M['cost'])) if integral else np.zeros(len(M['cost'])),
               bounds=Bounds(0, np.inf), options=dict(time_limit=time_limit, mip_rel_gap=gap))
    print('status', res.status, res.message, 'obj', res.fun, 'secs', round(time.time() - t, 1), flush=True)
    return res

def remainders(M, x):
    prof = Counter()
    for (ci, pi), j in M['nidx'].items():
        if x[j] > 1e-6:
            cap = M['classes'][ci][2]; p = M['pats'][cap][pi]
            rem = cap - sum(k * w for k, w in zip(p, M['widths']))
            if rem: prof[rem] += x[j]
    return prof


def build2(plan, inv, allowed, ports=112):
    widths = sorted(inv)
    classes = []
    for key, (cap, times) in sorted(plan['windows'].items(), key=lambda kv: tuple(map(int, kv[0].split(',')))):
        rep, i = map(int, key.split(',')); classes.append((rep, i, cap, list(times)))
    ncalls = len(plan['order'])
    var = []; cost = []; nidx = {}; xidx = {}
    for ci, (rep, ch, cap, times) in enumerate(classes):
        for p in allowed[ci]:
            nidx[ci, p] = len(var); var.append(('n', ci, p)); cost.append(phi(cap - sum(k * w for k, w in zip(p, widths))))
            for t in times:
                for wi, w in enumerate(widths):
                    if p[wi]:
                        xidx[ci, p, t, w] = len(var); var.append(('x', ci, p, t, w)); cost.append(0.0)
    rows, cols, vals, lo, hi = [], [], [], [], []; r = 0
    def add(ent, a, b):
        nonlocal r
        for j, v in ent: rows.append(r); cols.append(j); vals.append(v)
        lo.append(a); hi.append(b); r += 1
    for ci, (rep, ch, cap, times) in enumerate(classes):
        add([(nidx[ci, p], 1.0) for p in allowed[ci]], ports, ports)
        for p in allowed[ci]:
            for wi, w in enumerate(widths):
                if p[wi]:
                    add([(xidx[ci, p, t, w], 1.0) for t in times] + [(nidx[ci, p], -float(p[wi]))], 0, 0)
            for t in times:
                e = [(xidx[ci, p, t, w], 1.0) for w in widths if (ci, p, t, w) in xidx]
                add(e + [(nidx[ci, p], -1.0)], -np.inf, 0)
    bycall = defaultdict(list)
    for (ci, p, t, w), j in xidx.items(): bycall[t, w].append(j)
    for t in range(ncalls):
        for w in widths:
            add([(j, 1.0) for j in bycall[t, w]], inv[w], inv[w])
    A = sp.csr_matrix((vals, (rows, cols)), shape=(r, len(var)))
    return dict(classes=classes, widths=widths, var=var, cost=np.array(cost), A=A, lo=np.array(lo), hi=np.array(hi), nidx=nidx, xidx=xidx)


def edge_colour(edges, delta):
    """edges: list of (left, right). Proper edge colouring with delta colours (bipartite, max degree <= delta)."""
    colL = defaultdict(dict); colR = defaultdict(dict)   # node -> colour -> edge index
    colour = [None] * len(edges)
    for ei, (u, v) in enumerate(edges):
        a = next(c for c in range(delta) if c not in colL[u])
        b = next(c for c in range(delta) if c not in colR[v])
        if a != b and a in colR[v]:
            # flip a/b alternating path starting at v via colour a
            path = []; side = 'R'; node = v; cur = a
            while True:
                d = colR if side == 'R' else colL
                if cur not in d[node]: break
                e = d[node][cur]; path.append(e)
                uu, vv = edges[e]; node = uu if side == 'R' else vv; side = 'L' if side == 'R' else 'R'
                cur = b if cur == a else a
            for e in path:
                uu, vv = edges[e]; c = colour[e]
                del colL[uu][c]; del colR[vv][c]
            for e in path:
                uu, vv = edges[e]; c = b if colour[e] == a else a
                colour[e] = c; colL[uu][c] = e; colR[vv][c] = e
        assert a not in colL[u] and a not in colR[v]
        colour[ei] = a; colL[u][a] = ei; colR[v][a] = ei
    return colour

def idle_profile(plan, roles):
    V = 112; used = defaultdict(set)
    for z in roles:
        cells = set(range(z['offset'], z['offset'] + z['width'])); key = (z['owner_replica'], z['child'], z['port'])
        assert not used[key] & cells; used[key] |= cells
    prof = Counter()
    for key, (cap, times) in plan['windows'].items():
        owner, ch = map(int, key.split(','))
        for port in range(V):
            cells = used[owner, ch, port]
            assert cells == set(range(len(cells))), 'gap'
            if cap - len(cells): prof[cap - len(cells)] += 1
    return prof


def lift2(plan, sol, inv_order):
    classes, widths, var, x = sol; V = 112
    npat = defaultdict(dict); xs = defaultdict(lambda: defaultdict(int))
    for j, v in enumerate(var):
        c = int(round(x[j]))
        if c <= 0: continue
        if v[0] == 'n': npat[v[1]][v[2]] = c
        else: xs[v[1], v[2]][(v[3], v[4])] += c
    slots = []
    for ci, (rep, ch, cap, times) in enumerate(classes):
        port0 = 0
        assert sum(npat[ci].values()) == V, (ci, sum(npat[ci].values()))
        for p, n in sorted(npat[ci].items()):
            positions = sorted([w for wi, w in enumerate(widths) for _ in range(p[wi])], reverse=True)
            need = {k: n for k in range(len(positions))}; edges = []
            for (t, w), c in sorted(xs[ci, p].items()):
                for _ in range(c):
                    k = next(k for k in range(len(positions)) if positions[k] == w and need[k] > 0)
                    need[k] -= 1; edges.append((t, k))
            assert all(v == 0 for v in need.values()), (ci, p, need)
            col = edge_colour(edges, n) if edges else []
            offs = [sum(positions[:k]) for k in range(len(positions))]
            for (t, k), c in zip(edges, col):
                slots.append((rep, ch, port0 + c, offs[k], t, positions[k]))
            port0 += n
    bycall = defaultdict(list)
    for s in slots: bycall[s[4], s[5]].append(s)
    roles = []
    for t, (r, s, wl) in inv_order.items():
        for w in set(wl):
            hs = [h for h, ww in enumerate(wl) if ww == w]; sl = sorted(bycall[t, w])
            assert len(hs) == len(sl), (t, w, len(hs), len(sl))
            for h, (owner, ch, port, off, tt, ww) in zip(hs, sl):
                fam = owner * 896 + (2 * plan['pairs'][str(ch)] + plan['sides'][str(ch)]) * V + port
                roles.append(dict(child=ch, copy=V * owner + port, family=fam, helper=h, offset=off, owner_replica=owner,
                                  port=port, replica=r, stage=s, time=t, width=w))
    roles.sort(key=lambda z: (z['time'], z['helper']))
    return roles
if __name__ == '__main__':
    plan = json.load(open(sys.argv[1]))
    INV = Counter(plan['per_call_widths'][0]['widths'])
    assert all(Counter(z['widths']) == INV for z in plan['per_call_widths']), 'one provider inventory expected'
    limit = float(sys.argv[3]) if len(sys.argv) > 3 else 600
    M1 = build(plan, INV, maxrem=3)
    lp = solve(M1, integral=False)
    print('LP remainder bound', {k: round(v, 2) for k, v in sorted(remainders(M1, lp.x).items())}, flush=True)
    r1 = solve(M1, time_limit=limit)
    allowed = defaultdict(set)
    for (ci, pi), j in M1['nidx'].items():
        if lp.x[j] > 1e-7 or r1.x[j] > 0.5: allowed[ci].add(M1['pats'][M1['classes'][ci][2]][pi])
    allowed = {ci: sorted(s) for ci, s in allowed.items()}
    M = build2(plan, INV, allowed)
    t = time.time()
    res = milp(M['cost'], constraints=LinearConstraint(M['A'], M['lo'], M['hi']), integrality=np.ones(len(M['cost'])),
               bounds=Bounds(0, np.inf), options=dict(time_limit=limit, mip_rel_gap=1e-7))
    print('liftable MILP status', res.status, 'obj', res.fun, 'secs', round(time.time() - t, 1), flush=True)
    sol = (M['classes'], M['widths'], M['var'], res.x)
    pcw = {(z['replica'], z['stage']): z['widths'] for z in plan['per_call_widths']}
    inv_order = {c['time']: (c['replica'], c['stage'], pcw[c['replica'], c['stage']]) for c in plan['provider_calls']}
    roles = lift2(plan, sol, inv_order)
    prof = idle_profile(plan, roles)
    fam = Counter((z['time'], z['family']) for z in roles); assert max(fam.values()) == 1
    assert all(z['time'] in plan['windows'][f"{z['owner_replica']},{z['child']}"][1] for z in roles)
    print('roles', len(roles), 'idle profile', dict(sorted(prof.items())))
    open(sys.argv[2], 'wb').write(gzip.compress(json.dumps(roles, separators=(',', ':')).encode(), mtime=0))
