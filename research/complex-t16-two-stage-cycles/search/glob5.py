"""Stage 2 of the global repack (glob.py): realise a stage-1 class solution on concrete bins. Per class, patterns are
assigned to bins (keeping each bin's current pattern where possible), then each width is placed by a max-flow from
calls to bins with distinct calls per bin, over 40 random width orders / pattern assignments. Helpers left unplaced
(80 in the session's run) are inserted greedily where they lower sum f ln f the least. Output: OUT.OWNERS.json.gz,
audited (seed67 rules) and priced. Standard library only besides lib.py.
argv: LIBDIR START STAGE1_JSON OUT [SEED]"""
import sys, json, gzip, random, itertools
sys.path.insert(0, sys.argv[1]); import lib
from collections import Counter, defaultdict, deque
start, s1, out = sys.argv[2], sys.argv[3], sys.argv[4]; SEED = int(sys.argv[5]) if len(sys.argv) > 5 else 0
rng = random.Random(SEED)
roles = lib.read(start); m = lib.Model(roles)
W = [4, 5, 7, 8, 9]
classes = defaultdict(list)
for k in m.cap: classes[m.cap[k], frozenset(m.allowed[k])].append(k)
CL = list(classes)
d = json.load(open(s1))
X = defaultdict(list); Y = defaultdict(Counter)
for ci, p, v in d['x']: X[ci] += [tuple(p)] * v
for ci, t, w, v in d['y']: Y[ci][t, w] += v
def pat_of(k): c = Counter(m.roles[i]['width'] for i in m.members[k]); return tuple(c[w] for w in W)

def maxflow(sup, cap_b, ok):
    """sup: {t: s}, cap_b: {b: c}, ok(t,b) bool. Returns {(t,b)} with flow 1. Simple augmenting paths (BFS)."""
    T = list(sup); B = list(cap_b)
    flow = set(); fs = Counter(); fb = Counter()
    adj = {t: [b for b in B if ok(t, b)] for t in T}
    # greedy init
    for t in sorted(T, key=lambda t: len(adj[t])):
        for b in sorted(adj[t], key=lambda b: fb[b] - cap_b[b]):
            if fs[t] >= sup[t]: break
            if fb[b] < cap_b[b] and (t, b) not in flow: flow.add((t, b)); fs[t] += 1; fb[b] += 1
    inb = defaultdict(set)
    for (t, b) in flow: inb[b].add(t)
    while True:
        # BFS from times with spare supply to bins with spare capacity, alternating t->b (not in flow), b->t (in flow)
        srcs = [t for t in T if fs[t] < sup[t]]
        if not srcs: break
        par = {('t', t): None for t in srcs}; q = deque(('t', t) for t in srcs); end = None
        while q and end is None:
            node = q.popleft()
            if node[0] == 't':
                t = node[1]
                for b in adj[t]:
                    if (t, b) in flow or ('b', b) in par: continue
                    par[('b', b)] = node
                    if fb[b] < cap_b[b]: end = ('b', b); break
                    q.append(('b', b))
            else:
                b = node[1]
                for t in inb[b]:
                    if ('t', t) not in par: par[('t', t)] = node; q.append(('t', t))
        if end is None: break
        node = end
        while par[node] is not None:
            p = par[node]
            if node[0] == 'b': flow.add((p[1], node[1])); inb[node[1]].add(p[1])
            else: flow.discard((node[1], p[1])); inb[p[1]].discard(node[1])
            node = p
        fs[node[1]] += 1; fb[end[1]] += 1
    return flow

def realise(ci, tries=40):
    bins = classes[CL[ci]]
    pool = defaultdict(list)
    for k in bins: pool[pat_of(k)].append(k)
    best = (10**9, None)
    for r in range(tries):
        pl = X[ci][:]; rng.shuffle(pl); pp = {p: v[:] for p, v in pool.items()}; assign = {}; rest = []
        for p in pl:
            if pp.get(p): assign[pp[p].pop()] = p
            else: rest.append(p)
        left = [k for v in pp.values() for k in v]; rng.shuffle(left)
        for k, p in zip(left, rest): assign[k] = p
        order = sorted(W, key=lambda w: -sum(Y[ci][t, ww] for (t, ww) in Y[ci] if ww == w)) if r == 0 else rng.sample(W, 5)
        used = {k: set() for k in bins}; res = []; miss = 0
        for w in order:
            sup = {t: c for (t, ww), c in Y[ci].items() if ww == w}
            if not sup: continue
            capb = {k: assign[k][W.index(w)] for k in bins if assign[k][W.index(w)]}
            fl = maxflow(sup, capb, lambda t, b: t not in used[b])
            for (t, b) in fl: used[b].add(t); res.append((b, t, w))
            miss += sum(sup.values()) - len(fl)
        if miss == 0: return res, 0
        if miss < best[0]: best = (miss, res)
    return best[1], best[0]
place = defaultdict(list); fails = []
for ci in range(len(CL)):
    res, nb = realise(ci)
    if nb: fails.append((ci, CL[ci][0], len(CL[ci][1]), nb)); print('partial', fails[-1], flush=True)
    for (k, t, w) in res: place[t, w].append(k)
print('fails', len(fails), 'unplaced', sum(f[3] for f in fails), flush=True)
byT = defaultdict(list)
for i, z in enumerate(m.roles): byT[z['time'], z['width']].append(i)
new = [dict(z) for z in m.roles]; unpl = []
used = Counter(); occ = defaultdict(set)
for tw, ks in place.items():
    hs = byT[tw]; assert len(hs) >= len(ks), tw
    rem = Counter(ks); free_h = []
    for i in hs:
        b = m.bin(i)
        if rem[b] > 0: rem[b] -= 1; used[b] += tw[1]; occ[tw[0]].add(m.fam[b])
        else: free_h.append(i)
    tgt = list(rem.elements())
    for i, k in zip(free_h, tgt): new[i] = lib.relocate(new[i], *k); new[i]['offset'] = 10**6; used[k] += tw[1]; occ[tw[0]].add(m.fam[k])
    unpl += free_h[len(tgt):]
for tw in byT:
    if tw not in place: unpl += byT[tw]
print('unplaced roles', len(unpl), flush=True)
unpl.sort(key=lambda i: -m.roles[i]['width'])
for i in unpl:
    t, w = m.roles[i]['time'], m.roles[i]['width']
    best = None
    for k in m.cap:
        f = m.cap[k] - used[k]
        if f >= w and t in m.allowed[k] and m.fam[k] not in occ[t]:
            d = lib.g(f - w) - lib.g(f)
            if best is None or d > best[0]: best = (d, k)
    k = best[1]; new[i] = lib.relocate(new[i], *k); new[i]['offset'] = 10**6; used[k] += w; occ[t].add(m.fam[k])
new = lib.compact(new)
au = lib.audit(new); pr = lib.price(au['profile'])
print('RESULT kappa', pr['kappa_decimal'], 'idle', au['idle'], flush=True)
open(out + '.OWNERS.json.gz', 'wb').write(gzip.compress(json.dumps(new).encode(), mtime=0))
