#!/usr/bin/env python3
"""Independent compiler for round-seven-style bit side programs (lifted frames with M_n = U_n, late copies,
B-defer readouts, V leaves) and their one-child histogram under PR #104's rule (as in PR #117's bit_profile).
Written from Swapnil Jain's round-seven note (notes/deferred-readout.tex) and the slot semantics of
check_lifted.py; no code imported from the round-seven package.

Frames live in Q^h with G = I - J/9. Root covectors: output T: 9 t_T - 3*1 (frame t_T^perp); retained c: 1 - 3 e_c.
A node's gate frame is U_n = common kernel of the root covectors reachable from n through its slots.
"""
import gzip, json, sys, time
from collections import Counter, defaultdict
from itertools import combinations
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from linalg_p import Span, span_of, kernel, gram_rank, P


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


T0 = time.time()


class Program:
    def __init__(self, h, args, leafT, outputs, retained):
        self.h = h
        self.trip = list(combinations(range(h), 3))
        self.v = len(self.trip)
        self.tid = {T: i for i, T in enumerate(self.trip)}
        self.args = args                      # node -> (a, b) or None
        self.leafT = leafT                    # leaf node -> triple
        self.outputs = outputs                # (c, T) -> node
        self.retained = retained              # c -> node
        roots = list(outputs.values()) + list(retained.values())
        act, st = set(), list(roots)
        while st:
            x = st.pop()
            if x not in act:
                act.add(x)
                if args[x]:
                    st.extend(args[x])
        self.act = sorted(act)
        self.tvec = {n: [int(q in T) for q in range(h)] for n, T in leafT.items()}
        # exact span dims of the supports (independent triple subsets)
        self.bas, self.dn = {}, {}
        for n in self.act:
            if args[n] is None:
                self.bas[n] = (n,)
                self.dn[n] = 1
                continue
            a, b = args[n]
            S, keep = Span(h), []
            for x in self.bas[a] + self.bas[b]:
                if len(S) == h:
                    break
                if S.insert(self.tvec[x]):
                    keep.append(x)
            self.bas[n] = tuple(keep)
            self.dn[n] = len(keep)
        self.key = lambda n: (self.dn[n], n)
        self.order = sorted(self.act, key=self.key)
        self.gpos = {n: i for i, n in enumerate(self.order)}
        users = {n: [] for n in self.act}
        for n in self.order:
            if args[n]:
                for pos, x in enumerate(args[n]):
                    users[x].append(('gate', n, pos))
        for (c, T), n in sorted(outputs.items()):
            users[n].append(('out', (c, T)))
        for c, n in sorted(retained.items()):
            users[n].append(('ret', c))
        self.users = users
        self.wout = {T: [9 * int(q in T) - 3 for q in range(h)] for T in self.trip}
        self.wret = {c: [1 - 3 * int(q == c) for q in range(h)] for c in range(h)}


def load_witness(path):
    W = json.load(gzip.open(path, 'rt'))
    h = W['h']
    args = {int(k): (tuple(a) if a else None) for k, a in W['args'].items()}
    leafT = {int(k): tuple(t) for k, t in W['leaf'].items()}
    outputs = {(c, tuple(T)): n for c, T, n in W['outputs']}
    retained = {c: n for c, n in W['retained']}
    links = {x: (y, k) for x, y, k in W['links']}
    late = {int(n): (list(e), list(l)) for n, (e, l) in W['late'].items()}
    return Program(h, args, leafT, outputs, retained), links, late


# ------------------------------------------------------------------------------------ frames
def use_K(pr, Kn, u):
    if u[0] == 'gate':
        return Kn[u[1]]
    if u[0] == 'out':
        return span_of(pr.h, [pr.wout[u[1][1]]])
    return span_of(pr.h, [pr.wret[u[1]]])


def node_frames(pr, links):
    """K(n) = span of root covectors reachable from n (gates, root reads, the donor's linked use)."""
    Kn = {}
    for n in reversed(pr.order):
        K = Span(pr.h)
        for u in pr.users[n]:
            K.add_span(use_K(pr, Kn, u))
        if n in links:
            y, k = links[n]
            K.add_span(use_K(pr, Kn, pr.users[y][k]))
        Kn[n] = K
    return Kn


def node_dim(pr, Kn, n, lifted=None):
    if pr.args[n] is None:
        return 1
    if lifted is not None and n not in lifted:
        return pr.dn[n]
    return pr.h - len(Kn[n])


def ann(h, vecs):
    """annihilator (Span of covectors) of span(vecs)."""
    return span_of(h, kernel(span_of(h, vecs)))


class Frames:
    """frames as annihilators: frame = ker(K). Node frames: U_n (lifted) or span(n) (plain); leaves <t_S>."""
    def __init__(self, pr, Kn, lifted):
        self.pr, self.Kn, self.lifted = pr, Kn, lifted
        self.cache = {}

    def K(self, key):
        if key in self.cache:
            return self.cache[key]
        pr, h = self.pr, self.pr.h
        kind = key[0]
        if kind == 'n':
            n = key[1]
            if pr.args[n] is None:
                K = ann(h, [pr.tvec[n]])
            elif self.lifted is None or n in self.lifted:
                K = self.Kn[n]
            else:
                K = ann(h, [pr.tvec[x] for x in pr.bas[n]])
        elif kind == 'c':
            n, suffix = key[1], key[2]
            K = Span(h)
            for k in suffix:
                K.add_span(self.K(self.ukey(n, k)))
        elif kind == 'out':
            K = span_of(h, [pr.wout[key[2]]])
        elif kind == 'ret':
            K = span_of(h, [pr.wret[key[1]]])
        elif kind == '0':
            K = span_of(h, [[int(i == j) for i in range(h)] for j in range(h)])
        elif kind == 'F':
            K = Span(h)
        else:
            raise KeyError(key)
        self.cache[key] = K
        return K

    def ukey(self, n, k):
        u = self.pr.users[n][k]
        return ('n', u[1]) if u[0] == 'gate' else ('out',) + u[1] if u[0] == 'out' else ('ret', u[1])

    def dim(self, key):
        return self.pr.h - len(self.K(key))


# ------------------------------------------------------------------------------------ slots
def compile_slots(pr, links, late):
    """slot structure: chains of frame keys per slot, start info, hold lists, ops (without copy placement)."""
    linked = {r: x for x, r in links.items()}
    chains, start, hold = [], [], []
    edge = {}
    ops = []

    def new(first, st, n):
        chains.append(list(first))
        start.append(st)
        hold.append([n])
        return len(chains) - 1

    def assign(s, n, k):
        u = pr.users[n][k]
        if u[0] == 'gate':
            edge[u[1], u[2]] = s
        else:
            chains[s] += [('out',) + u[1] if u[0] == 'out' else ('ret', u[1]), ('F',)]

    def ufr(n, k):
        u = pr.users[n][k]
        return ('n', u[1]) if u[0] == 'gate' else ('out',) + u[1] if u[0] == 'out' else ('ret', u[1])
    lateinfo = {}
    early_copies, late_copies, pivslot, addop = [], [], {}, {}
    for n in pr.order:
        if pr.args[n] is None:
            piv = new([('0',), ('n', n)], ('src', n), n)
            ops.append(('src', piv, n))
        else:
            a, b = pr.args[n]
            sa, sb = edge.pop((n, 0)), edge.pop((n, 1))
            if n in links and links[n][0] == a:
                sa, sb = sb, sa
            piv, oth = sa, sb
            chains[piv].append(('n', n))
            chains[oth].append(('n', n))
            hold[piv].append(n)
            hold[oth].append(n)
            ops.append(('add', piv, oth, n))
            addop[n] = ('add', piv, oth, n)
            if n in links:
                y, k = links[n]
                assign(oth, y, k)
            else:
                chains[oth].append(('F',))
        ks = [k for k in range(len(pr.users[n])) if (n, k) not in linked]
        if n in late:
            early, lt = late[n]
            assert sorted(early + lt) == ks, ('bad late decision', n)
        else:
            early, lt = ks[1:], [ks[0]]
        pivslot[n] = piv
        for k in early:
            f = new([('0',), ('n', n)], ('fresh', n, k), n)
            ops.append(('copy', piv, f, n))
            early_copies.append((n, f))
            assign(f, n, k)
        for i, k in enumerate(lt):
            Ck = ufr(n, k) if i == len(lt) - 1 else ('c', n, tuple(lt[i:]))
            chains[piv].append(Ck)
            if i < len(lt) - 1:
                f = new([('0',), Ck], ('fresh', n, k), n)
                ops.append(('copy', piv, f, n))
                late_copies.append((n, i, f, k, lt[-1]))
                assign(f, n, k)
        if len(lt) > 1:
            lateinfo[n] = lt
        k = lt[-1]
        if pr.users[n][k][0] == 'gate':
            edge[pr.users[n][k][1], pr.users[n][k][2]] = piv
        else:
            assign(piv, n, k)
    assert not edge
    adds = sum(1 for n in pr.act if pr.args[n])
    R = len(chains)
    assert R == adds + len(pr.outputs) + len(pr.retained) - len(links), 'role count'
    return dict(chains=chains, start=start, hold=hold, ops=ops, R=R, lateinfo=lateinfo, early_copies=early_copies,
                late_copies=late_copies, pivslot=pivslot, addop=addop)


def place_ops(pr, sl):
    """time order of L (adds and copies of additions; leaf copies become V gates outside L), with every
    non-final late copy placed as late as possible (before its user's gate and the pivot's last late user's gate,
    and before the next copy), and early copies right after their node."""
    INF = len(pr.order)
    gpos = pr.gpos
    ins = defaultdict(list)
    early_after = defaultdict(list)
    for (n, i, f, k, kl) in sl['late_copies']:
        pass
    byn = defaultdict(list)
    for item in sl['late_copies']:
        byn[item[0]].append(item)
    for n, lst in byn.items():
        lst.sort(key=lambda z: z[1])
        Dd = []
        for (_, i, f, k, kl) in lst:
            u, ul = pr.users[n][k], pr.users[n][kl]
            Dd.append(min(gpos[u[1]] if u[0] == 'gate' else INF, gpos[ul[1]] if ul[0] == 'gate' else INF))
        for t in range(len(Dd) - 2, -1, -1):
            Dd[t] = min(Dd[t], Dd[t + 1])
        for (_, i, f, k, kl), d in zip(lst, Dd):
            ins[d].append((gpos[n], i, n, f))
    for (n, f) in sl['early_copies']:
        early_after[n].append(f)
    pivslot = sl['pivslot']
    L = []
    for n in pr.order:
        for (_, i, m, f) in sorted(ins.get(gpos[n], [])):
            if pr.args[m] is not None:
                L.append(('copy', pivslot[m], f, m))
        if pr.args[n] is not None:
            a = sl['addop'][n]
            L.append(a)
            for f in early_after[n]:
                L.append(('copy', pivslot[n], f, n))
    for d in sorted(x for x in ins if x >= INF):
        for (_, i, m, f) in sorted(ins[d]):
            if pr.args[m] is not None:
                L.append(('copy', pivslot[m], f, m))
    return L


def bdefer(pr, sl, fr, log=print):
    """B-defer word facts: phase one, adjoint supports, V-leaf starts, deferral frames, orders; returns the slot
    dims needed by the one-child histogram."""
    h, v, R = pr.h, pr.v, sl['R']
    chains, hold = sl['chains'], sl['hold']
    L = place_ops(pr, sl)
    touch = lambda o: (o[1], o[2])
    # phase one: closure of the retained totals' last operations under per-slot precedence
    prev = {}
    pred = defaultdict(list)
    last = {}
    for i, o in enumerate(L):
        for s in touch(o):
            if s in prev:
                pred[i].append(prev[s])
            prev[s] = i
            last[s] = i
    ret_slots = [s for s in range(R) if chains[s][-2][0] == 'ret']
    assert len(ret_slots) == h
    phase1, st = set(), [last[s] for s in ret_slots]
    while st:
        i = st.pop()
        if i not in phase1:
            phase1.add(i)
            st.extend(pred[i])
    touched = set()
    for i in phase1:
        touched.update(touch(L[i]))
    # adjoint supports (targets reached by each slot's start value), bitmasks over targets
    cov = [0] * R
    tid = pr.tid
    for s in range(R):
        k = chains[s][-2]
        if k[0] == 'out':
            cov[s] = 1 << tid[k[2]]
        elif k[0] == 'ret':
            cov[s] = sum(1 << t for t, T in enumerate(pr.trip) if k[1] in T)
    for o in reversed(L):
        if o[0] == 'add':
            cov[o[2]] |= cov[o[1]]
        else:
            cov[o[1]] |= cov[o[2]]
    # V-leaf starts: per leaf, its use slots in time order; s_i = intersection of the first frames of uses i, i+1, ..
    leaf_slots = defaultdict(list)
    for s in range(R):
        if pr.args[hold[s][0]] is None:
            leaf_slots[hold[s][0]].append(s)
    vK, vdim = {}, {}
    nfall = 0
    for n, ss in leaf_slots.items():
        ss.sort(key=lambda s: (pr.gpos.get(hold[s][1], 10 ** 9) if len(hold[s]) > 1 else 10 ** 9, s))
        acc = Span(h)
        for s in reversed(ss):
            acc = acc.copy().add_span(fr.K(chains[s][2]))
            B = kernel(acc)
            if gram_rank(B) == len(B):
                vK[s], vdim[s] = acc, len(B)
            else:
                vK[s], vdim[s] = fr.K(('n', n)), 1
                nfall += 1
    log('V leaves: %d use slots, %d fall back to <t_S>' % (len(vdim), nfall))

    def startK(s):
        return vK[s] if s in vK else fr.K(chains[s][1])

    def startdim(s):
        return vdim[s] if s in vdim else fr.dim(chains[s][1])
    # deferral candidates: start frame cut by every reached target's t_T^perp, nondegenerate (PR #110's rule)
    cand = {}
    nd_deg = 0
    targets_of = {}
    for s in range(R):
        if s in touched or not cov[s]:
            continue
        K = startK(s).copy()
        ts = []
        m = cov[s]
        while m:
            b = m & -m
            t = b.bit_length() - 1
            ts.append(t)
            if len(K) < h:
                K.insert(pr.wout[pr.trip[t]])
            m ^= b
        if len(K) == h:
            continue
        B = kernel(K)
        if gram_rank(B) < len(B):
            nd_deg += 1
            continue
        cand[s] = K
        targets_of[s] = ts
    # placement: on every target the placed frames form a chain (by dimension); a candidate is cut by its
    # neighbours in each chain until it fits, and placed if still nonzero and nondegenerate
    chainT = defaultdict(dict)                         # target -> {dim: annihilator}
    placed = {}

    def sup_of(KA, KB):                                # frame(A) contains frame(B)  <=>  ann(A) <= ann(B)
        return all(KB.contains(r) for r in KA.vectors())
    for s in sorted(cand, key=lambda s: (len(cand[s]), s)):          # largest frames first
        K = cand[s]
        changed = True
        while changed and len(K) < h:
            changed = False
            d = h - len(K)
            for t in targets_of[s]:
                ch = chainT[t]
                if not ch:
                    continue
                lower = max((e for e in ch if e < d), default=None)
                upper = min((e for e in ch if e >= d), default=None)
                for e, need in ((lower, 'X>=B'), (upper, 'X<=B')):
                    if e is None:
                        continue
                    KB = ch[e]
                    ok = sup_of(K, KB) if need == 'X>=B' else sup_of(KB, K)
                    if not ok:
                        K = K.copy().add_span(KB)
                        changed = True
                        break
                if changed or len(K) == h:
                    break
        if len(K) == h:
            continue
        B = kernel(K)
        if gram_rank(B) < len(B):
            continue
        placed[s] = K
        for t in targets_of[s]:
            chainT[t][h - len(K)] = K
    # X_S chains: early V frames, then deferred V frames, must be nested; the V-leaf starts are nested in use
    # order, so a deferred leaf slot must not start below any early slot of its leaf: un-defer violators
    undef = 0
    changed = True
    while changed:
        changed = False
        for n, ss in leaf_slots.items():
            early_max = max((vdim[s] for s in ss if s not in placed), default=0)
            for s in ss:
                if s in placed and vdim[s] < early_max:
                    del placed[s]
                    undef += 1
                    changed = True
    if undef:
        log('un-deferred %d leaf slots to keep X_S chains nested' % undef)
    f = [0] * R
    for s, K in placed.items():
        f[s] = h - len(K)
    dset = [s for s in range(R) if f[s]]
    log('phase one: %d ops of %d; untouched slots %d; deferred %d (degenerate intersections %d)' % (
        len(phase1), len(L), R - len(touched), len(dset), nd_deg))
    # orders and levels
    lev = defaultdict(set)
    for s in dset:
        m = cov[s]
        while m:
            b = m & -m
            lev[b.bit_length() - 1].add(f[s])
            m ^= b
    ylev = {t: sorted(lev[t]) for t in range(v)}
    xdata = []
    for n, ss in leaf_slots.items():
        early = sorted(startdim(s) for s in ss if not f[s])
        late_ = sorted(startdim(s) for s in ss if f[s])
        ds = [1] + early + late_ + [h]
        ds = [d for i, d in enumerate(ds) if i == 0 or d != ds[i - 1]]
        xdata.append([b - a for a, b in zip(ds, ds[1:])])
    # slot chain dims
    chain_dims = []
    for s in range(R):
        ds = [f[s], startdim(s)] + [fr.dim(k) for k in chains[s][2:]]
        chain_dims.append(ds)
    return dict(f=f, ylev=ylev, xdata=xdata, chain_dims=chain_dims, deferred=len(dset), phase1=len(phase1),
                cov=cov, vdim=vdim)


def one_child(pr, R, bd):
    """PR #117's bit_profile list: both stages, all invocations."""
    h, v = pr.h, pr.v
    m, N = h * h, v * v
    z = Counter()
    bad = 0
    for _ in range(2):
        for s in range(R):
            z[m - (h - bd['f'][s])] += v
            ds = bd['chain_dims'][s]
            if any(b < a for a, b in zip(ds, ds[1:])):
                bad += 1
            for a, b in zip(ds, ds[1:]):
                if b > a:
                    z[b - a] += v
        z[h - 1] += v * h
        for t in range(v):
            ds = sorted(set([0] + bd['ylev'][t] + [h - 1]))
            for a, b in zip(ds, ds[1:]):
                z[b - a] += v
        for xs in bd['xdata']:
            for x in xs:
                if x <= 0:
                    bad += 2
                z[x] += v
    z[(h - 1) ** 2] += 2 * N
    z[1] += N
    Wb, L = 2 * N + 2 * v * R, 2 * v * h * (h - 1)
    s = Wb * m - N + L
    return dict(z=dict(sorted(z.items())), W=Wb, L=L, s=s, m=m, N=N, rank=sum(t * n for t, n in z.items()),
                decreasing_chains=bad // 2)


def load_dump(path):
    """the autoresearch kit's DAG dump (run_producer.py)."""
    d = json.load(open(path))
    h = d['h']
    trip = list(combinations(range(h), 3))
    v = len(trip)
    args = {i + 1: None for i in range(v)}
    for k, (a, b) in enumerate(d['args']):
        args[v + 1 + k] = (a, b)
    leafT = {i + 1: T for i, T in enumerate(trip)}
    outputs = {(c, tuple(T)): x for c, T, x in d['out']}
    retained = {c: x for c, x in enumerate(d['ret'])}
    return Program(h, args, leafT, outputs, retained)


def auto_links(pr, log=print):
    """maximum lifted-admissible matching (as the kit's evaluator), then validated with reach through links."""
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import maximum_bipartite_matching
    h, v = pr.h, pr.v
    star = [0] * h
    for i, S in enumerate(pr.trip):
        for a in S:
            star[a] |= 1 << i
    sup = {}
    for n in pr.order:
        sup[n] = (1 << pr.tid[pr.leafT[n]]) if pr.args[n] is None else sup[pr.args[n][0]] | sup[pr.args[n][1]]
    good = {}
    for T in pr.trip:
        a, b, c = (star[x] for x in T)
        good[T] = (a ^ b ^ c) & ~((a & b) | (a & c) | (b & c))
    full = (1 << v) - 1
    allowed = {}
    for n in reversed(pr.order):
        m = full
        for u in pr.users[n]:
            m &= allowed[u[1]] if u[0] == 'gate' else good[u[1][1]] if u[0] == 'out' else star[u[1]]
        allowed[n] = m
    adds = [n for n in pr.order if pr.args[n]]
    rows, cols, colid = [], [], {}
    for di, x in enumerate(adds):
        for y in pr.args[x]:
            for k, u in enumerate(pr.users[y]):
                if u[0] == 'gate':
                    if u[1] == x or not pr.key(x) < pr.key(u[1]) or sup[x] & ~allowed[u[1]]:
                        continue
                elif sup[x] & ~(good[u[1][1]] if u[0] == 'out' else star[u[1]]):
                    continue
                colid.setdefault((y, k), len(colid))
                rows.append(di)
                cols.append(colid[(y, k)])
    G = csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(len(adds), len(colid)))
    match = maximum_bipartite_matching(G, perm_type='column')
    inv = {c: key for key, c in colid.items()}
    links = {adds[i]: inv[int(c)] for i, c in enumerate(match) if c >= 0}
    log('matching: %d links' % len(links))
    for it in range(30):
        Kn = node_frames(pr, links)
        bad = []
        for x, (y, k) in links.items():
            K = use_K(pr, Kn, pr.users[y][k])
            if any(any(sum(a * b for a, b in zip(r, pr.tvec[t])) % P for t in pr.bas[x]) for r in K.vectors()):
                bad.append(x)
        if not bad:
            break
        for x in bad:
            del links[x]
        log('  dropped %d links violating reach through links' % len(bad))
    return links, Kn


def greedy_links(pr, log=print):
    """valid links by one pass in decreasing schedule order: when donor x is reached, every later node's reach
    (and so its frame) is final. x takes a free use (y, k) of one of its operands whose consumer frame contains
    span(x), preferring the one that enlarges x's reach least. Returns links and the reach spans K."""
    h = pr.h
    Kn = {}
    taken = set()
    links = {}

    def perp(K, x):
        return all(not (sum(a * b for a, b in zip(r, pr.tvec[t])) % P) for r in K.vectors() for t in pr.bas[x])
    for x in reversed(pr.order):
        K0 = Span(h)
        for u in pr.users[x]:
            K0.add_span(use_K(pr, Kn, u))
        if pr.args[x] is not None:
            best = None
            for y in pr.args[x]:
                for k, u in enumerate(pr.users[y]):
                    if (y, k) in taken or (u[0] == 'gate' and (u[1] == x or not pr.key(x) < pr.key(u[1]))):
                        continue
                    Ku = use_K(pr, Kn, u)
                    if not perp(Ku, x):
                        continue
                    grow = sum(1 for r in Ku.vectors() if not K0.contains(r))
                    cand = (grow, -(pr.key(u[1]) if u[0] == 'gate' else (10 ** 9, 0))[0], y, k)
                    if best is None or cand[:2] < best[0][:2]:
                        best = (cand, Ku)
            if best is not None:
                (_, _, y, k), Ku = best
                links[x] = (y, k)
                taken.add((y, k))
                K0 = K0.copy().add_span(Ku)
        Kn[x] = K0
    log('greedy links: %d' % len(links))
    return links, Kn


def auto_late(pr, Kn, links, fr):
    """late copies for every addition with >= 2 free uses (users in schedule order), when every intersection
    frame is nondegenerate; otherwise early copies."""
    linked = {r: x for x, r in links.items()}
    late = {}
    for n in pr.order:
        if pr.args[n] is None:
            continue
        ks = [k for k in range(len(pr.users[n])) if (n, k) not in linked]
        if len(ks) < 2:
            continue
        ok = True
        for i in range(len(ks) - 1):
            B = kernel(fr.K(('c', n, tuple(ks[i:]))))
            if not B or gram_rank(B) < len(B):
                ok = False
                break
        if ok:
            late[n] = ([], ks)
    return late


def auto_lifted(pr, Kn, links):
    """lift (frame U_n) every addition whose U_n is nondegenerate, keeping the plain set (frame span(n)) closed
    under slot predecessors; returns lifted set and the number of degenerate plain frames."""
    plain = set()
    for n in pr.order:
        if pr.args[n] is None:
            continue
        B = kernel(Kn[n])
        if gram_rank(B) < len(B):
            plain.add(n)
    preds = defaultdict(list)
    for n in pr.order:
        if pr.args[n]:
            for x in pr.args[n]:
                preds[n].append(x)
    for x, (y, k) in links.items():
        u = pr.users[y][k]
        if u[0] == 'gate':
            preds[u[1]].append(x)
    st = list(plain)
    while st:
        t = st.pop()
        for x in preds[t]:
            if pr.args[x] is not None and x not in plain:
                plain.add(x)
                st.append(x)
    bad = 0
    for n in plain:
        B = [pr.tvec[t] for t in pr.bas[n]]
        if gram_rank(B) < len(B):
            bad += 1
    lifted = {n for n in pr.order if pr.args[n] is not None and n not in plain}
    return lifted, len(plain), bad


def compile_program(pr, links=None, late=None, lifted=None, log=print):
    """full pipeline -> one-child list and statistics."""
    if links is None:
        links, Kn = greedy_links(pr, log)
    else:
        Kn = node_frames(pr, links)
    if lifted is None:
        lifted, nplain, nbad = auto_lifted(pr, Kn, links)
        log('lifted %d additions, plain %d (degenerate plain frames %d)' % (len(lifted), nplain, nbad))
    fr = Frames(pr, Kn, lifted)
    if late is None:
        late = auto_late(pr, Kn, links, fr)
        log('late decisions: %d nodes' % len(late))
    sl = compile_slots(pr, links, late)
    log('R = %d (%.4f v)' % (sl['R'], sl['R'] / pr.v))
    bd = bdefer(pr, sl, fr, log)
    oc = one_child(pr, sl['R'], bd)
    log('one-child list: %d children, rank %d vs s %d, decreasing chains %d' % (
        sum(oc['z'].values()), oc['rank'], oc['s'], oc['decreasing_chains']))
    return dict(R=sl['R'], links=len(links), late=len(late), lifted=len(lifted), deferred=bd['deferred'],
                profile=dict(h=pr.h, m=oc['m'], W=oc['W'], N=oc['N'], L=oc['L'], total_rank=oc['s'],
                             child_multiplicities={str(t): n for t, n in oc['z'].items()}),
                ok=oc['rank'] == oc['s'] and not oc['decreasing_chains'])


def late_K(pr, Kn, n, suffix):
    K = Span(pr.h)
    for k in suffix:
        K.add_span(use_K(pr, Kn, pr.users[n][k]))
    return K


if __name__ == '__main__':
    wpath, dpath = sys.argv[1], sys.argv[2]
    pr, links, late = load_witness(wpath)
    log('program: %d active nodes, %d additions, %d links, %d late' % (
        len(pr.act), sum(1 for n in pr.act if pr.args[n]), len(links), len(late)))
    D = json.load(gzip.open(dpath, 'rt'))
    Kn = node_frames(pr, links)
    log('frames computed')
    W = json.load(gzip.open(wpath, 'rt'))
    lifted = {int(k) for k in W['j']}
    nd = dict((n, d) for n, d in D['node_dims'])
    mism = [(n, node_dim(pr, Kn, n, lifted), nd.get(n)) for n in pr.act if node_dim(pr, Kn, n, lifted) != nd.get(n)]
    log('node dims: %d mismatches of %d' % (len(mism), len(pr.act)), mism[:5])
    sl = compile_slots(pr, links, late)
    log('compiled R = %d (round seven %d)' % (sl['R'], D['R']))
    ld = {(n, tuple(lt)): d for n, lt, d in D['late_dims']}
    lm = 0
    cnt = 0
    for n, lt in sl['lateinfo'].items():
        for i in range(len(lt) - 1):
            key = (n, tuple(lt[i:]))
            d = pr.h - len(late_K(pr, Kn, n, lt[i:]))
            cnt += 1
            if ld.get(key) != d:
                lm += 1
    log('late dims: %d mismatches of %d (round seven lists %d)' % (lm, cnt, len(ld)))
    hold_ok = sum(1 for a, b in zip(sl['hold'], D['hold']) if a == b)
    log('hold lists equal: %d of %d' % (hold_ok, len(D['hold'])))
    fr = Frames(pr, Kn, lifted)
    bd = bdefer(pr, sl, fr, log)
    sig = dict(zip(D['readout_order'], (len(B) for B in D['sigma'])))
    mine = {s: bd['f'][s] for s in range(sl['R']) if bd['f'][s]}
    log('deferred: mine %d, round seven %d, common %d, equal dims on common %d' % (
        len(mine), len(sig), len(set(mine) & set(sig)), sum(1 for s in set(mine) & set(sig) if mine[s] == sig[s])))
    vs = dict(zip(D['vleaf_slots'], (len(B) for B in D['vleaf_start'])))
    log('V-leaf starts: equal dims %d of %d' % (sum(1 for s, d in vs.items() if bd['vdim'].get(s) == d), len(vs)))
    oc = one_child(pr, sl['R'], bd)
    log('one-child list: %d children, rank %d vs s %d, decreasing chains %d' % (
        sum(oc['z'].values()), oc['rank'], oc['s'], oc['decreasing_chains']))
    json.dump(dict(h=pr.h, m=oc['m'], W=oc['W'], N=oc['N'], L=oc['L'], total_rank=oc['s'],
                   child_multiplicities={str(t): n for t, n in oc['z'].items()}), open(sys.argv[3], 'w'))
