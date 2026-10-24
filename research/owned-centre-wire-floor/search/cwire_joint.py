"""Stage B: joint frame retiming WITH a movable owned-C wire, on the #4470 native word.

Extends a joint frame-retiming search of the #4447/#4470 contact graph (which kept every C contact pinned) by #4534 lemma 3
(OWNED-C-RETIMING.md): every scalar contact that touches C becomes a variable, and the C wire of
each centre block gets its own chain.  Pricing:
  * L role edges: nested ascending climb, rank = dim b - dim a (else illegal)   [native.synthesize]
  * C wire edges: nested in either direction, rank = |dim b - dim a| (else not considered);
    the original centre is such an edge (8 -> 0 forward, 0 -> 8 backward).  After CLEAR the C chart
    is free, so a block's C chain starts at its first contact.
  * Objective: paid moment sum r^t, at t = 0.997 and 0.9999, in EACH orientation separately; a hit
    must gain in both orientations at both t (the verifier demands equal profiles in both).
Search: level 1 every unit, level 2 adjacent pairs, level 3 connected triples (exhaustive over
candidate frames), then simulated annealing.  Checkpoint: run/state.json; log: progress.log.
Run from the repository root:  python3.12 research/owned-centre-wire-floor/search/cwire_joint.py [--c-single] [--hours H]
(output directory: $CWIRE_OUT, default ./cwire-search-out).  Search evidence only; not part of verify.py.
Prepared by Matarener with Claude Code assistance.  Apache-2.0.
"""
import argparse, ctypes, json, math, os, random, sys, time
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'research/joint-helper-lattice'))
sys.path.insert(0, str(ROOT / 'research/fresh-helper-boundary'))
import native_joint as NJ  # noqa: E402
import native as F  # noqa: E402

OUT = Path(os.environ.get('CWIRE_OUT', 'cwire-search-out')).resolve()
RUN = OUT / 'run'
TS = (0.997, 0.9999)
EPS = 1e-9
POW = [[r ** t if r else 0.0 for r in range(10)] for t in TS]
DIRS = ('forward', 'backward')


def log(msg):
    line = f'{time.strftime("%Y-%m-%d %H:%M:%S")} cwireB {msg}'
    print(line, flush=True)
    with (OUT / 'progress.log').open('a', encoding='utf-8') as fh:
        fh.write(line + '\n')


def save(path, obj):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, indent=1), encoding='utf-8')
    os.replace(tmp, path)


def low_priority():
    if os.name == 'nt':
        try:
            h = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.kernel32.SetPriorityClass(h, 0x4000)  # BELOW_NORMAL
        except Exception:
            pass


def rref(vs):
    piv = {}
    for x in vs:
        for b, v in piv.items():
            if x >> b & 1:
                x ^= v
        if x:
            b = x.bit_length() - 1
            for k in list(piv):
                if piv[k] >> b & 1:
                    piv[k] ^= x
            piv[b] = x
    return tuple(sorted(piv.values()))


def points(s):
    p = {0}
    for x in s:
        p |= {v ^ x for v in tuple(p)}
    return frozenset(p)


def meet(a, b):
    return rref(points(a) & points(b))


def c_role(e):
    g = e[1]
    return any(isinstance(r, list) and r[0] == 'C' for r in g[1:3])


class Model:
    """Edges: (dir, kind, a, b) with a/b = ('k', key) variable contact or ('f', frame) fixed."""

    def __init__(self):
        c, programs, _, _, _ = NJ.construct()
        self.c = c
        self.frames, self.spans, self.dims, self.index, self.pts = [], [], [], {}, []
        for b in c['frames']:
            self.intern(rref(b))
        self.lab = {}
        self.edges = []            # (d, kind, u, v) kind 'L' or 'C'
        self.base_profile = {}
        for d in DIRS:
            prog = programs[d]
            Lkeys = F.gates(prog)
            inv = {i: k for k, i in Lkeys.items()}
            # C contacts: per block ordinal; forward copy <-> backward final add (L_src)
            blk, cnt, cinv = -1, 0, {}
            last_clear = False
            for i, e in enumerate(prog):
                if e[0] == 'scalar' and e[1][0] == 'clear':
                    if not last_clear:
                        blk += 1
                        cnt = 0
                    last_clear = True
                    continue
                if e[0] == 'scalar' and c_role(e):
                    last_clear = False
                    L = [r[1] for r in e[1][1:3] if r[0] == 'L'][0]
                    cinv[i] = ('C', blk, L)
                    cnt += 1
                elif e[0] == 'scalar':
                    last_clear = False
            # NB the clear-pairs: forward 'clear@0, clear@274' close/open; backward 'clear@254, clear@0'
            for i, k in list(inv.items()) + list(cinv.items()):
                f = prog[i][2]
                if k in self.lab:
                    assert self.lab[k] == f, ('orientation frame mismatch', k)
                self.lab[k] = f
            lch = defaultdict(list)
            cch = defaultdict(list)
            for r, f in enumerate(c['start']):
                lch[r].append(('f', f, f))
            for i, e in enumerate(prog):
                if e[0] == 'scalar':
                    g = e[1]
                    roles = g[1:3] if g[0] in ('add', 'copy') else g[1:2]
                    k = inv.get(i) or cinv.get(i)
                    for r in roles:
                        if r[0] == 'L':
                            lch[r[1]].append(('k', k, k) if k else ('f', e[2], e[2]))
                    if i in cinv:
                        cch[cinv[i][1]].append(('k', cinv[i], cinv[i]))
                elif e[0] == 'warp':
                    lch[e[1][1]].append(('f', e[3], e[4]))
            for r, f in enumerate(c['final']):
                lch[r].append(('f', f, f))
            for lst in lch.values():
                for x, y in zip(lst, lst[1:]):
                    self.edges.append((d, 'L', ('k', x[2]) if x[0] == 'k' else ('f', x[2]),
                                       ('k', y[1]) if y[0] == 'k' else ('f', y[1])))
            for lst in cch.values():
                for x, y in zip(lst, lst[1:]):
                    self.edges.append((d, 'C', ('k', x[1]), ('k', y[1])))
        self.keys = sorted(self.lab, key=str)
        self.inc = defaultdict(list)
        for n, (d, kind, u, v) in enumerate(self.edges):
            for w in (u, v):
                if w[0] == 'k':
                    self.inc[w[1]].append(n)
        self.base = dict(self.lab)
        self.rk = {}
        self.c_single = False

    def intern(self, s):
        lab = self.index.get(s)
        if lab is None:
            self.frames.append(list(s)); self.spans.append(s); self.dims.append(len(s))
            self.pts.append(points(s))
            lab = self.index[s] = len(self.frames) - 1
        return lab

    def rank(self, kind, a, b):
        if a == b:
            return 0
        key = (kind, a, b)
        r = self.rk.get(key)
        if r is None:
            pa, pb = self.pts[a], self.pts[b]
            if pa < pb:
                r = self.dims[b] - self.dims[a]
            elif kind == 'C' and pb < pa:
                r = self.dims[a] - self.dims[b]
            else:
                r = -1
            self.rk[key] = r
        return None if r < 0 else r

    def fr(self, w, ov):
        return w[1] if w[0] == 'f' else ov.get(w[1], self.lab[w[1]])

    def profile(self):
        prof = {d: Counter() for d in DIRS}
        for d, kind, u, v in self.edges:
            r = self.rank(kind, self.fr(u, {}), self.fr(v, {}))
            assert r is not None, ('illegal edge in baseline', d, kind, u, v)
            if r:
                prof[d][r] += 1
        return prof

    def delta(self, ov):
        """gain[d][t] of move ov {key: frame}; None if illegal."""
        es = set(n for k in ov for n in self.inc[k])
        gain = {d: [0.0, 0.0] for d in DIRS}
        prof = {d: Counter() for d in DIRS}
        for n in es:
            d, kind, u, v = self.edges[n]
            ro = self.rank(kind, self.fr(u, {}), self.fr(v, {}))
            rn = self.rank(kind, self.fr(u, ov), self.fr(v, ov))
            if rn is None:
                return None, None
            for t in (0, 1):
                gain[d][t] += POW[t][ro] - POW[t][rn]
            if ro:
                prof[d][ro] -= 1
            if rn:
                prof[d][rn] += 1
        return gain, {d: {k: v for k, v in p.items() if v} for d, p in prof.items()}

    # units: consecutive equal-frame variable contacts along L chains (C chains do not glue)
    def units(self):
        parent = {k: k for k in self.keys}

        def find(k):
            while parent[k] != k:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k
        for d, kind, u, v in self.edges:
            if kind == 'L' and u[0] == v[0] == 'k' and self.lab[u[1]] == self.lab[v[1]] \
                    and not (self.c_single and (u[1][0] == 'C' or v[1][0] == 'C')):
                a, b = find(u[1]), find(v[1])
                if a != b:
                    parent[a] = b
        g = defaultdict(list)
        for k in self.keys:
            g[find(k)].append(k)
        units = sorted(g.values(), key=lambda x: str(x[0]))
        uid = {k: i for i, u in enumerate(units) for k in u}
        adj = [set() for _ in units]
        for d, kind, u, v in self.edges:
            if u[0] == v[0] == 'k':
                x, y = uid[u[1]], uid[v[1]]
                if x != y:
                    adj[x].add(y); adj[y].add(x)
        return units, [sorted(s) for s in adj], uid


class Search:
    def __init__(self, M):
        self.M = M
        self.units, self.adj, self.uid = M.units()
        self.ulab = [M.lab[u[0]] for u in self.units]
        # boundary summary per unit: (neighbour unit or -1, fixed frame or -1, out?, kind, dir, mult)
        nb = [Counter() for _ in self.units]
        for d, kind, u, v in M.edges:
            x = self.uid[u[1]] if u[0] == 'k' else None
            y = self.uid[v[1]] if v[0] == 'k' else None
            if x is not None and x == y:
                continue
            if x is not None:
                nb[x][(-1 if y is None else y, v[1] if y is None else -1, 1, kind, d)] += 1
            if y is not None:
                nb[y][(-1 if x is None else x, u[1] if x is None else -1, 0, kind, d)] += 1
        self.nb = [[k + (m,) for k, m in c.items()] for c in nb]
        self.di = {d: i for i, d in enumerate(DIRS)}

    def cands(self, i, S, cap):
        M = self.M
        lo, hi = set(), set()
        for j, f, out, kind, d, m in self.nb[i]:
            if j in S:
                continue
            lab = f if j < 0 else self.ulab[j]
            if kind == 'C':
                lo.add(lab); hi.add(lab)
            else:
                (hi if out else lo).add(lab)
        lo_l = sorted(f for f in lo)
        res = [self.ulab[i]]
        lower = rref([x for f in lo_l for x in M.spans[f]])
        res.append(M.intern(lower))
        upper = None
        for f in sorted(hi):
            upper = M.spans[f] if upper is None else meet(upper, M.spans[f])
        if upper is not None:
            res.append(M.intern(upper))
            g = lower
            for x in upper:
                h = rref(g + (x,))
                if len(h) > len(g) and points(h) <= points(upper):
                    g = h
                    res.append(M.intern(g))
        res += sorted(lo | hi)
        return list(dict.fromkeys(res))[:cap]

    def gain_of(self, assign):
        """Exact gain per (dir, t) of moving units {i: frame}; None if illegal."""
        M = self.M
        g = [[0.0, 0.0], [0.0, 0.0]]
        for i, fnew in assign.items():
            for j, f, out, kind, d, m in self.nb[i]:
                if j in assign and j < i:
                    continue
                o = f if j < 0 else self.ulab[j]
                n = f if j < 0 else assign.get(j, o)
                a0, b0 = (self.ulab[i], o) if out else (o, self.ulab[i])
                a1, b1 = (fnew, n) if out else (n, fnew)
                ro, rn = M.rank(kind, a0, b0), M.rank(kind, a1, b1)
                if rn is None:
                    return None
                di = self.di[d]
                for t in (0, 1):
                    g[di][t] += m * (POW[t][ro] - POW[t][rn])
        return g

    def best(self, idx, cap):
        S = set(idx)
        cl = []
        for i in idx:
            cs = list(self.cands(i, S, cap))
            if len(idx) > 1:
                cs += [f for f in self.cands(i, {i}, cap) if f not in cs]
            cl.append([f for f in cs if f != self.ulab[i]][:cap])
        if len(idx) == 2:
            for a in (0, 1):
                cl[a] += [f for f in cl[1 - a] if f not in cl[a] and f != self.ulab[idx[a]]]
        bestv, besta = EPS, None
        for combo in product(*cl):
            assign = dict(zip(idx, combo))
            g = self.gain_of(assign)
            if g is None:
                continue
            if min(g[0][0], g[0][1], g[1][0], g[1][1]) > EPS and g[0][0] + g[1][0] > bestv:
                bestv, besta = g[0][0] + g[1][0], (assign, g)
        return besta

    def apply(self, assign):
        for i, f in assign.items():
            self.ulab[i] = f
            for k in self.units[i]:
                self.M.lab[k] = f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=float, default=1.0)
    ap.add_argument('--cap', type=int, default=12)
    ap.add_argument('--c-single', action='store_true', help='C contacts are their own units')
    args = ap.parse_args()
    low_priority()
    global RUN
    if args.c_single:
        RUN = OUT / 'run-csingle'
    OUT.mkdir(exist_ok=True)
    RUN.mkdir(exist_ok=True)
    st_path = RUN / 'state.json'
    st = json.loads(st_path.read_text(encoding='utf-8')) if st_path.exists() else {'level': 1, 'pos': 0, 'hits': [], 'sa_step': 0}
    log(f'stage B: launch (resume level {st["level"]} pos {st["pos"]}, {len(st["hits"])} hits)')
    M = Model()
    prof = M.profile()
    log(f'stage B: baseline profile forward {dict(sorted(prof["forward"].items()))}')
    log(f'stage B: baseline profile backward {dict(sorted(prof["backward"].items()))}')
    want = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}
    ok = all(dict(prof[d]) == want for d in DIRS)
    log(f'stage B: self-test vs #4470 RESULT local_paid {want}: {"PASS" if ok else "FAIL"}')
    if not ok:
        sys.exit(1)
    M.c_single = args.c_single
    S = Search(M)
    ncu = sum(1 for u in S.units if any(k[0] == 'C' for k in u))
    sizes = Counter(len(u) for u in S.units)
    log(f'stage B: {len(S.units)} units ({ncu} contain C contacts), largest {max(sizes)}, C-wire edges {sum(1 for e in M.edges if e[1]=="C")}')
    deadline = time.time() + args.hours * 3600
    for level in (1, 2, 3):
        if st['level'] > level:
            continue
        if level == 1:
            items = [(i,) for i in range(len(S.units))]
        elif level == 2:
            items = [(x, y) for x in range(len(S.units)) for y in S.adj[x] if x < y]
        else:
            items = []
            for y in range(len(S.units)):
                for x, z in combinations(S.adj[y], 2):
                    tri = tuple(sorted((x, y, z)))
                    if z in S.adj[x] and y != tri[0]:
                        continue
                    items.append(tri)
        cap = args.cap if level < 3 else max(6, args.cap // 2)
        log(f'stage B: level {level}: {len(items)} items, cap {cap}')
        t_log = time.time()
        for n in range(st['pos'], len(items)):
            h = S.best(list(items[n]), cap)
            if h:
                assign, g = h
                rec = {'level': level, 'units': list(items[n]), 'sizes': [len(S.units[i]) for i in items[n]],
                       'has_C': [any(k[0] == 'C' for k in S.units[i]) for i in items[n]],
                       'frames': [[S.ulab[i], M.dims[S.ulab[i]], f, M.dims[f]] for i, f in assign.items()],
                       'gain': g}
                st['hits'].append(rec)
                log(f'stage B: MODEL HIT level {level} {rec}')
            if time.time() - t_log > 60:
                st['level'], st['pos'] = level, n
                save(st_path, st)
                log(f'stage B:   level {level}: {n}/{len(items)} ({100*n/len(items):.1f}%), hits {len(st["hits"])}')
                t_log = time.time()
            if time.time() > deadline:
                st['level'], st['pos'] = level, n
                save(st_path, st)
                log('stage B: time budget used, state saved; rerun to continue')
                return
        st['level'], st['pos'] = level + 1, 0
        save(st_path, st)
        log(f'stage B: level {level} done, hits so far {len(st["hits"])}')
    # simulated annealing on unit moves (single / adjacent pair)
    rng = random.Random(7 + st['sa_step'])
    n = len(S.units)
    gain = 0.0
    best_g = 0.0
    step0 = st['sa_step']
    t_log = time.time()
    log('stage B: annealing start')
    while time.time() < deadline:
        st['sa_step'] += 1
        T = 1.0 * (0.02 / 1.0) ** (((st['sa_step'] - step0) % 200000) / 200000)
        x = rng.randrange(n)
        idx = [x] if rng.random() < 0.6 or not S.adj[x] else [x, rng.choice(S.adj[x])]
        assign = {}
        for i in idx:
            f = rng.choice(S.cands(i, set(idx), 16))
            if f != S.ulab[i]:
                assign[i] = f
        if not assign:
            continue
        g = S.gain_of(assign)
        if g is None:
            continue
        w = min(g[0][0], g[1][0])
        if w >= 0 or rng.random() < math.exp(w / T):
            S.apply(assign)
            gain += w
            if gain > best_g + EPS:
                best_g = gain
                pr = M.profile()
                if all(sum(v * r ** t for r, v in pr[d].items()) < sum(v * r ** t for r, v in want.items()) - EPS
                       for d in DIRS for t in TS):
                    st['hits'].append({'level': 'anneal', 'step': st['sa_step'], 'profile': {d: dict(pr[d]) for d in DIRS},
                                       'changed': {str(k): M.lab[k] for k in M.keys if M.lab[k] != M.base[k]}})
                    log(f'stage B: ANNEAL MODEL HIT gain {gain:+.4f}, profiles {[dict(sorted(pr[d].items())) for d in DIRS]}')
        if time.time() - t_log > 300:
            log(f'stage B: anneal step {st["sa_step"]}, T {T:.3f}, gain {gain:+.4f}, best {best_g:+.4f}, hits {len(st["hits"])}')
            save(st_path, st)
            t_log = time.time()
    save(st_path, st)
    log(f'stage B: finished; total model hits {len(st["hits"])}')


if __name__ == '__main__':
    main()
