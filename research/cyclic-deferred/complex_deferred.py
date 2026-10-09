#!/usr/bin/env python3
"""Saturated deferred readouts on the immutable PR117 complex DAG.

PR117 credits its searched DAG to eumemic with Anthropic Claude assistance;
this experiment imports and replays that witness unchanged. PR110/PR114
saturation and exact finite checks are applied to the resulting graph.
Logical readout macros are realized as signed numerator/42 chunks of magnitude
at most one. The literal audit expands and charges those same-frame shears,
checks exact reconstruction, and reverses the chunks under reflection.
Inherited Avi Eisenberg, Rohan Arun, icekylinx, Swapnil Jain and eumemic
credits retained. Extended with radical-complement frame lifting, phase-aware
role compilation, lazy effective-target placement, and exact-moment frame and
placement optimization by Thomas Marchand with Google Antigravity assistance.
Apache-2.0.
"""
import array
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import heapq
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import random
import struct
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(HERE))
from partial_swap_network import log_upper

producer_path = HERE / 'producer.py'
spec = importlib.util.spec_from_file_location('replayed_producer_wrapper', producer_path)
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)
build = producer.build

P = (1 << 61) - 1


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def load(prefix):
    def rd(fh, typ, cnt):
        a = array.array(typ)
        a.fromfile(fh, cnt)
        return a
    with open(str(prefix) + '.bin', 'rb') as f:
        h, v, n, q = struct.unpack('<4I', f.read(16))
        flat = rd(f, 'I', 2 * n)
        core = rd(f, 'Q', n)
        cover = rd(f, 'Q', n)
        roots = rd(f, 'I', q)
        kind = rd(f, 'I', q)
        active = rd(f, 'B', n)
    with open(str(prefix) + '.labels', 'rb') as f:
        ranks = rd(f, 'I', n)
        types = rd(f, 'B', n)
    args = [(flat[2 * i], flat[2 * i + 1]) for i in range(n)]
    return h, v, n, q, args, core, cover, roots, kind, active, ranks, types


# ---------------------------------------------------------------- F2 linear algebra on bit vectors
def dot(a, b):
    return (a & b).bit_count() & 1


def reduce(basis):
    return list(sat_basis(basis))


def kernel(funcs, h):
    K = sat_basis(funcs)
    piv = [r.bit_length() - 1 for r in K]
    out = []
    for c in (i for i in range(h) if i not in piv):
        vec = 1 << c
        for r, p in zip(K, piv):
            if r >> c & 1:
                vec |= 1 << p
        out.append(vec)
    return out


def restrict(basis, funcs):
    B = list(sat_basis(basis))
    for f in funcs:
        if not B:
            break
        vals = [(b & f).bit_count() & 1 for b in B]
        if not any(vals):
            continue
        k = vals.index(1)
        pv = B[k]
        B = [b ^ pv if val else b for b, val in zip(B, vals)]
        B.pop(k)
    return sat_basis(B)


def contains(A, B):
    return sat_contained(sat_basis(A), sat_basis(B))


def cap(A, B):
    return list(sat_cap(sat_basis(A), sat_basis(B)))


def nondeg(B):
    return sat_nondeg(sat_basis(B))


def hopcroft_karp(left, adj):
    """maximum bipartite matching; adj[x] = sorted list of right vertices."""
    INF = 1 << 60
    mate_l = {x: None for x in left}
    mate_r = {}
    while True:
        dist = {}
        queue = []
        for x in left:
            if mate_l[x] is None:
                dist[x] = 0
                queue.append(x)
            else:
                dist[x] = INF
        found = INF
        head = 0
        while head < len(queue):
            x = queue[head]
            head += 1
            if dist[x] >= found:
                continue
            for r in adj[x]:
                y = mate_r.get(r)
                if y is None:
                    found = min(found, dist[x] + 1)
                elif dist[y] == INF:
                    dist[y] = dist[x] + 1
                    queue.append(y)
        if found == INF:
            break
        gained = 0
        for x0 in left:
            if mate_l[x0] is not None:
                continue
            stack = [(x0, iter(adj[x0]))]
            path = []
            while stack:
                x, it = stack[-1]
                advanced = False
                for r in it:
                    y = mate_r.get(r)
                    if (y is None and dist[x] + 1 == found) or (y is not None and dist[y] == dist[x] + 1):
                        path.append((x, r))
                        if y is None:
                            for xx, rr in path:
                                mate_l[xx] = rr
                                mate_r[rr] = xx
                            gained += 1
                            stack = []
                            break
                        stack.append((y, iter(adj[y])))
                        advanced = True
                        break
                else:
                    dist[x] = INF
                    stack.pop()
                    if path:
                        path.pop()
                    continue
                if not advanced:
                    break
        if not gained:
            break
    return mate_l


def sat_basis(vectors):
    piv = {}
    for x in vectors:
        for p in sorted(piv, reverse=True):
            if x >> p & 1:
                x ^= piv[p]
        if x:
            p = x.bit_length() - 1
            for q in piv:
                if piv[q] >> p & 1:
                    piv[q] ^= x
            piv[p] = x
    return tuple((piv[p] for p in sorted(piv, reverse=True)))


def sat_dot(a, b):
    return (a & b).bit_count() & 1


@lru_cache(None)
def sat_contained(A, B):
    for x in A:
        for r in B:
            if x >> r.bit_length() - 1 & 1:
                x ^= r
        if x:
            return False
    return True


@lru_cache(None)
def sat_cap(A, B):
    if not A or not B:
        return ()
    red = {}
    out = []
    for i, x in enumerate(A + B):
        tag = 1 << i
        for p in sorted(red, reverse=True):
            if x >> p & 1:
                r, t = red[p]
                x ^= r
                tag ^= t
        if x:
            red[x.bit_length() - 1] = (x, tag)
        else:
            y = 0
            for j, r in enumerate(A):
                if tag >> j & 1:
                    y ^= r
            if y:
                out.append(y)
    return sat_basis(out)


@lru_cache(None)
def sat_nondeg(B):
    return len(sat_basis((sum((sat_dot(a, b) << j for j, b in enumerate(B))) for a in B))) == len(B)


@lru_cache(None)
def sat_nonsingular_part(B):
    rows = list(B)
    out = []
    while rows:
        i = next((i for i, x in enumerate(rows) if sat_dot(x, x)), None)
        if i is not None:
            a = rows.pop(i)
            out.append(a)
            rows = [x ^ a if sat_dot(x, a) else x for x in rows]
            continue
        pair = next(((i, j) for i in range(len(rows)) for j in range(i + 1, len(rows)) if sat_dot(rows[i], rows[j])), None)
        if pair is None:
            break
        i, j = pair
        a, b = (rows[i], rows[j])
        out.extend((a, b))
        rows = [x ^ (a if sat_dot(x, b) else 0) ^ (b if sat_dot(x, a) else 0) for k, x in enumerate(rows) if k not in (i, j)]
    return sat_basis(out)


def max_nondeg_between(L, W):
    perp = restrict(W, L)
    return sat_basis(L + sat_nonsingular_part(perp))


def min_nondeg_between(L, W):
    B = L
    while not sat_nondeg(B):
        k = len(B)
        gram = [sum(sat_dot(B[i], B[j]) << j for j in range(k)) for i in range(k)]
        rad = []
        red = []
        for i, row in enumerate(gram):
            tag = 1 << i
            for rv, rt in red:
                if row >> (rv.bit_length() - 1) & 1:
                    row ^= rv
                    tag ^= rt
            if row:
                red.append((row, tag))
            else:
                v_rad = 0
                for j in range(k):
                    if tag >> j & 1:
                        v_rad ^= B[j]
                rad.append(v_rad)
        r0 = rad[0]
        cand_v = [u for u in W if sat_dot(u, r0) and not sat_contained((u,), B)]
        if not cand_v:
            return W if sat_nondeg(W) else (max_nondeg_between(L, W) if sat_nondeg(L) else None)
        B = sat_basis(B + (cand_v[0],))
    return B


def reduce_against(X, t_list, byT, placed, skip_s=None):
    changed = True
    while changed and X:
        changed = False
        for t in t_list:
            for w in byT[t]:
                if w == skip_s or w not in placed:
                    continue
                B = placed[w]
                if (len(B) >= len(X) and not sat_contained(X, B)) or (len(B) < len(X) and not sat_contained(B, X)):
                    X = sat_cap(X, B)
                    changed = True
                if not X:
                    break
            if not X:
                break
        if X and not sat_nondeg(X):
            before = X
            X = sat_nonsingular_part(X)
            assert sat_contained(X, before) and sat_nondeg(X)
            assert len(X) < len(before)
            changed = True
    return X


def lazy_saturated_placement(cand, t_lists):
    cur = {s: sat_basis(B) for s, B in cand.items()}
    byT = defaultdict(list)
    byT_set = defaultdict(set)
    placed = {}
    prio_fn = lambda s, d, r, r_eff: (Fraction(-(1 << d), max(1, r * r_eff)), -d, r, s)
    heap = [(prio_fn(s, len(B), len(t_lists[s]), len(t_lists[s])), len(B), len(t_lists[s]), s) for s, B in cur.items()]
    heapq.heapify(heap)
    while heap:
        _, old_d, old_reff, s = heapq.heappop(heap)
        X = reduce_against(cur[s], t_lists[s], byT, placed)
        if not X:
            continue
        r_eff = sum(1 for t in t_lists[s] if X not in byT_set[t])
        if len(X) < old_d or r_eff < old_reff:
            cur[s] = X
            heapq.heappush(heap, (prio_fn(s, len(X), len(t_lists[s]), r_eff), len(X), r_eff, s))
            continue
        assert sat_nondeg(X) and sat_contained(X, cand[s])
        placed[s] = X
        for t in t_lists[s]:
            byT[t].append(s)
            byT_set[t].add(X)
    for t, ss in byT.items():
        ss.sort(key=lambda s: (len(placed[s]), s))
        assert all(sat_contained(placed[a], placed[b]) for a, b in zip(ss, ss[1:]))
    return placed


def main():
    with tempfile.TemporaryDirectory(prefix='deferred-stopped-') as work:
        prefix = Path(work) / 'complex'
        build(24, prefix, central_disjoint=24)
        h, v, n, q, args, core, cover, roots, kind, active, ranks, types = load(prefix)
    trip = list(combinations(range(h), 3))
    require(len(trip) == v, 'triple count')
    m = h * h
    N = v * v
    FULL = (1 << h) - 1
    tmask = [sum(1 << p for p in T) for T in trip]
    tid = {T: i for i, T in enumerate(trip)}

    # ------------------------------------------------------------ uses and matching (inherited adjacency)
    degree = [0] * n
    uses = defaultdict(list)
    c_add = 0
    for x in range(1, n):
        if active[x] and args[x][0]:
            c_add += 1
            for pos, y in enumerate(args[x]):
                degree[y] += 1
                uses[y].append(('gate', x, pos))
    for j, x in enumerate(roots):
        degree[x] += 1
        uses[x].append(('root', j))
    def unode(u):
        return roots[u[1]] if u[0] == 'root' else u[1]
    def before(x, u):
        y = unode(u)
        return (ranks[x], x) < (ranks[y], (n + u[1]) if u[0] == 'root' else y)
    def incl(x, y):
        tx, ty = types[x], types[y]
        if tx == 1 and ty == 1:
            return not (core[y] & ~core[x]) and not (cover[x] & ~cover[y])
        if tx in (1, 2) and ty == 2:
            return not (cover[x] & ~cover[y])
        if tx == 1 and ty == 3:
            return bool(core[x] & core[y])
        if tx == 2 and ty == 3:
            return not (cover[x] & ~core[y])
        if tx == 3 and ty == 2:
            return cover[y] == FULL
        if tx == 3 and ty == 3:
            return core[x] == core[y]
        return False
    left = []
    adj = {}
    for x in range(1, n):
        if not (active[x] and args[x][0]):
            continue
        rs = sorted({(y, k) for y in args[x] for k, u in enumerate(uses[y]) if before(x, u) and incl(x, unode(u))})
        if rs:
            left.append(x)
            adj[x] = rs
    mate = hopcroft_karp(left, adj)
    links = {x: r for x, r in mate.items() if r is not None}
    R = c_add + q - len(links)
    require((c_add, q, len(links), R) == (91770, 8120, 71185, 28705), 'selected PR117 graph')
    print('PR117 graph matched', c_add, q, len(links), R, flush=True)
    linked_use = {(y, k): x for x, (y, k) in links.items()}

    # ------------------------------------------------------------ root targets, read coefficients, root functionals
    target = [None] * q
    for j in range(v):
        target[j] = j
    idx = v
    for a, b in combinations(range(h), 2):
        others = [i for i in range(h) if i not in (a, b)]
        for i in others:
            target[idx] = tid[tuple(sorted((a, b, i)))]
            idx += 1
    centre_of = {}
    for j in range(q):
        if kind[j]:
            miss = FULL & ~cover[roots[j]]
            require(bin(miss).count('1') == 1, 'centre cover')
            centre_of[j] = miss.bit_length() - 1
    require(idx + len(centre_of) == q, 'root order')
    rootfun = [(1 << centre_of[j]) if kind[j] else tmask[target[j]] for j in range(q)]

    # ------------------------------------------------------------ lifted binary frames, radical-complement saturation
    succ = defaultdict(set)
    droot = defaultdict(set)
    for x in range(1, n):
        if not active[x]:
            continue
        for k, u in enumerate(uses[x]):
            if (x, k) in linked_use:
                continue
            (succ[x].add(u[1]) if u[0] == 'gate' else droot[x].add(u[1]))
    for x, (y, k) in links.items():
        u = uses[y][k]
        (succ[x].add(u[1]) if u[0] == 'gate' else droot[x].add(u[1]))
    order_desc = sorted((x for x in range(1, n) if active[x]), key=lambda x: (ranks[x], x), reverse=True)
    order = list(reversed(order_desc))
    K = {}
    for x in order_desc:
        rows = [rootfun[j] for j in droot[x]]
        for t in succ[x]:
            rows += K[t]
        K[x] = sat_basis(rows)

    def envelope(x):
        if not args[x][0]:
            return sat_basis([tmask[x - 1]])
        if types[x] == 2:
            return sat_basis([1 << i for i in range(h) if cover[x] >> i & 1])
        require(types[x] == 1, 'only ordinary and common-pair labels occur')
        ks = [i for i in range(h) if (cover[x] & ~core[x]) >> i & 1]
        require(len(ks) == ranks[x], 'common-pair support')
        return sat_basis([core[x] | (1 << k) for k in ks])

    env_map = {x: envelope(x) for x in order}
    K_ker = {x: sat_basis(kernel(K[x], h)) for x in order_desc if args[x][0]}
    U = {}
    for x in order_desc:
        if not args[x][0]:
            U[x] = env_map[x]
            continue
        W = K_ker[x]
        require(sat_contained(env_map[x], W), 'label outside lifted frame')
        for t in succ[x]:
            if not sat_contained(W, U[t]):
                W = sat_cap(W, U[t])
        if not sat_nondeg(W):
            W = max_nondeg_between(env_map[x], W)
        U[x] = W

    # ------------------------------------------------------------ explicit phase-aware role compile
    node_in_anc = {}
    for x in order_desc:
        node_in_anc[x] = any(kind[j] for j in droot[x]) or any(node_in_anc[t] for t in succ[x])

    def use_in_anc(x, k):
        u = uses[x][k]
        return bool(kind[u[1]]) if u[0] == 'root' else node_in_anc[u[1]]

    gate_in_reach = {}
    gate_in_all = {}
    def u_reach(u):
        if u[0] == 'root':
            j = u[1]
            return (set(), True) if kind[j] else ({target[j]}, False)
        return gate_in_reach[(u[1], u[2])], gate_in_all[(u[1], u[2])]

    for y in order_desc:
        if not args[y][0]:
            continue
        free_y = [k for k in range(len(uses[y])) if (y, k) not in linked_use]
        fr_set = set()
        fr_all = False
        for k in free_y:
            rs, ra = u_reach(uses[y][k])
            fr_set |= rs
            fr_all = fr_all or ra
        a, b = args[y]
        oth_pos = 0 if (y in links and links[y][0] == a) else 1
        piv_pos = 1 - oth_pos
        gate_in_reach[(y, piv_pos)] = fr_set
        gate_in_all[(y, piv_pos)] = fr_all
        oth_set = set(fr_set)
        oth_all = fr_all
        if y in links:
            ly, lk = links[y]
            rs, ra = u_reach(uses[ly][lk])
            oth_set |= rs
            oth_all = oth_all or ra
        gate_in_reach[(y, oth_pos)] = oth_set
        gate_in_all[(y, oth_pos)] = oth_all

    holds = []
    first_node = []
    ops = []
    edge_key = {}
    role_root = {}
    def new_role(node):
        holds.append([node])
        first_node.append(node)
        return len(holds) - 1
    def serve(s, y, k):
        u = uses[y][k]
        if u[0] == 'gate':
            edge_key[(y, k)] = s
        else:
            role_root[s] = u[1]
    for x in order:
        free = [k for k in range(len(uses[x])) if (x, k) not in linked_use]
        if not args[x][0]:
            for k in free:
                s = new_role(x)
                ops.append(('src', s, x))
                serve(s, x, k)
            continue
        a, b = args[x]
        ka = next(k for k, u in enumerate(uses[a]) if u == ('gate', x, 0))
        kb = next(k for k, u in enumerate(uses[b]) if u == ('gate', x, 1))
        sa, sb = edge_key.pop((a, ka)), edge_key.pop((b, kb))
        if x in links and links[x][0] == a:
            sa, sb = sb, sa
        piv, oth = sa, sb
        ops.append(('add', piv, oth, x))
        holds[piv].append(x)
        holds[oth].append(x)
        if x in links:
            serve(oth, *links[x])
        require(free, 'every use linked at node %d' % x)
        if len(free) > 1:
            non_c = [k for k in free if not use_in_anc(x, k)]
            yes_c = [k for k in free if use_in_anc(x, k)]
            if non_c:
                if len(non_c) > 1:
                    non_c.sort(key=lambda k: (-int(u_reach(uses[x][k])[1]), -len(u_reach(uses[x][k])[0]), k))
                free = [non_c[0]] + yes_c + non_c[1:]
        serve(piv, x, free[0])
        for k in free[1:]:
            f = new_role(x)
            ops.append(('copy', piv, f, x))
            serve(f, x, k)
    require(not edge_key and len(holds) == R, 'compile')
    Rr = R

    # ------------------------------------------------------------ B. the word computes every root value
    rng = random.Random(20261008)
    xs = [rng.randrange(P) for _ in range(v)]
    val = [0] * n
    for i in range(v):
        val[i + 1] = xs[i]
    for x in order:
        if args[x][0]:
            val[x] = (val[args[x][0]] + val[args[x][1]]) % P
    leaf_of = {s: first_node[s] for s in range(Rr) if not args[first_node[s]][0]}
    a_ = [0] * Rr
    for s, leaf in leaf_of.items():
        a_[s] = xs[leaf - 1]
    for o in ops:
        if o[0] == 'add':
            a_[o[1]] = (a_[o[1]] + a_[o[2]]) % P
        elif o[0] == 'copy':
            a_[o[2]] = (a_[o[2]] + a_[o[1]]) % P
    require(all(a_[s] == val[roots[j]] for s, j in role_root.items()), 'root values')

    # ------------------------------------------------------------ phase one and garbage reach
    def touch(o):
        return [o[1], o[2]] if o[0] in ('add', 'copy') else []
    prev = {}
    pred = defaultdict(list)
    last = {}
    for i, o in enumerate(ops):
        for s in touch(o):
            if s in prev:
                pred[i].append(prev[s])
            prev[s] = i
            last[s] = i
    centre_roles = [s for s, j in role_root.items() if kind[j]]
    Anc = set()
    st = [last[s] for s in centre_roles]
    while st:
        i = st.pop()
        if i not in Anc:
            Anc.add(i)
            st.extend(pred[i])
    touched = set(centre_roles)
    for i in Anc:
        touched.update(touch(ops[i]))
    require(all(last[s] in Anc for s in centre_roles), 'centres complete in phase one')
    reach = [set() for _ in range(Rr)]
    reach_all = [False] * Rr
    for s, j in role_root.items():
        if kind[j]:
            reach_all[s] = True
        else:
            reach[s].add(target[j])
    for o in reversed(ops):
        if o[0] == 'add':
            reach[o[2]] |= reach[o[1]]
            reach_all[o[2]] = reach_all[o[2]] or reach_all[o[1]]
        elif o[0] == 'copy':
            reach[o[1]] |= reach[o[2]]
            reach_all[o[1]] = reach_all[o[1]] or reach_all[o[2]]

    # ------------------------------------------------------------ deferral frames, insertion nesting, and joint optimization
    root_frame = {}
    for s, j in role_root.items():
        root_frame[s] = sat_basis([1 << i for i in range(h) if i != centre_of[j]] if kind[j] else kernel([tmask[target[j]]], h))
    FULLB = sat_basis([1 << i for i in range(h)])

    cand = {}
    for s in range(Rr):
        if s in touched or reach_all[s] or first_node[s] <= v:
            continue
        S_ = restrict(U[first_node[s]], [tmask[t] for t in reach[s]])
        if S_ and not sat_nondeg(S_):
            S_ = sat_nonsingular_part(S_)
        if S_ and sat_nondeg(S_):
            cand[s] = S_
    t_lists = {s: sorted(reach[s]) for s in cand}
    print('PR117 candidates', len(cand), flush=True)
    placed = lazy_saturated_placement(cand, t_lists)

    SAV = 1.115e-4
    W_T = [0.0] * m
    for t in range(1, m):
        ell = float(log_upper(Fraction(m, t)))
        u = SAV * ell
        W_T[t] = t * (u + u * u / (2.0 * (1.0 - u / 3.0)))
    g = lambda t: 0.0 if t <= 0 else W_T[t]

    roles_of = defaultdict(list)
    for s, hs in enumerate(holds):
        for x in hs:
            roles_of[x].append(s)
    preds = defaultdict(list)
    for y, ts in succ.items():
        for t in ts:
            preds[t].append(y)

    def role_chain_cost(s, U_map, placed_map):
        seq = [placed_map.get(s, ()), U_map[first_node[s]]] + [U_map[x] for x in holds[s][1:]]
        if s in root_frame:
            seq.append(root_frame[s])
        seq.append(FULLB)
        ds = [len(B) for B in seq]
        cost = 0.0
        for a, b in zip(ds[:-1], ds[1:-1]):
            if b > a:
                cost += g(b - a)
        lastd = ds[-2]
        cost += g(h - lastd)
        return cost

    def optimize_U_for_placed(U_init, placed_map, n_sweeps=4, dirty_init=None):
        U_map = dict(U_init)
        starts = defaultdict(list)
        for s, X in placed_map.items():
            starts[first_node[s]].append(X)
        dirty = set(order_desc) if dirty_init is None else set(dirty_init)
        for sweep in range(n_sweeps):
            top_down = (sweep % 2 == 1)
            nodes_iter = order_desc if top_down else order
            next_dirty = set()
            visit_all = (sweep < 2 and dirty_init is None)
            for x in nodes_iter:
                if not args[x][0]:
                    continue
                if not visit_all and x not in dirty:
                    continue
                vecs = list(env_map[x])
                for X in starts[x]:
                    vecs.extend(X)
                for y in preds[x]:
                    vecs.extend(U_map[y])
                L_x = sat_basis(vecs)
                W_x = K_ker[x]
                for t in succ[x]:
                    if not sat_contained(W_x, U_map[t]):
                        W_x = sat_cap(W_x, U_map[t])
                if len(L_x) == len(W_x):
                    if U_map[x] != L_x:
                        U_map[x] = L_x
                        next_dirty.update(preds[x])
                        next_dirty.update(succ[x])
                        for s in roles_of[x]:
                            next_dirty.update(holds[s])
                    continue
                cands_B = [U_map[x]]
                if sat_nondeg(L_x):
                    cands_B.append(L_x)
                    if not sat_nondeg(W_x):
                        cands_B.append(max_nondeg_between(L_x, W_x))
                else:
                    B_min = min_nondeg_between(L_x, W_x)
                    if B_min is not None and sat_nondeg(B_min):
                        cands_B.append(B_min)
                        if not sat_nondeg(W_x):
                            cands_B.append(max_nondeg_between(B_min, W_x))
                if sat_nondeg(W_x):
                    cands_B.append(W_x)
                for s in roles_of[x]:
                    for z_node in holds[s]:
                        cands_B.append(U_map[z_node])
                    if s in root_frame:
                        cands_B.append(root_frame[s])
                uniq_B = []
                for B in cands_B:
                    if B not in uniq_B and sat_nondeg(B) and sat_contained(L_x, B) and sat_contained(B, W_x):
                        uniq_B.append(B)
                if len(uniq_B) <= 1:
                    continue
                cur_B = U_map[x]
                best_B = cur_B
                best_c = sum(role_chain_cost(s, U_map, placed_map) for s in roles_of[x])
                for B in uniq_B:
                    if B == cur_B:
                        continue
                    U_map[x] = B
                    c = sum(role_chain_cost(s, U_map, placed_map) for s in roles_of[x])
                    if c < best_c - 1e-12 or (abs(c - best_c) <= 1e-12 and ((top_down and len(B) > len(best_B)) or (not top_down and len(B) < len(best_B)))):
                        best_c = c
                        best_B = B
                U_map[x] = best_B
                if best_B != cur_B:
                    dirty.update(preds[x])
                    dirty.update(succ[x])
                    for s in roles_of[x]:
                        dirty.update(holds[s])
                    next_dirty.update(preds[x])
                    next_dirty.update(succ[x])
                    for s in roles_of[x]:
                        next_dirty.update(holds[s])
            if not visit_all and not next_dirty:
                break
            if sweep >= 1:
                dirty = next_dirty
        return U_map

    U = optimize_U_for_placed(U, placed, n_sweeps=4)

    for _outer in range(3):
        d1_map = {s: len(U[first_node[s]]) for s in cand}
        def role_benefit(s, d):
            if d <= 0:
                return 0.0
            d1 = max(d, d1_map[s])
            return g(d1) - g(d1 - d) - (g(m - h + d) - g(m - h))

        pruned = dict(placed)
        level_counts = [Counter() for _ in range(v)]
        byT = defaultdict(set)
        for s, X in pruned.items():
            d = len(X)
            for t in t_lists[s]:
                level_counts[t][d] += 1
                byT[t].add(s)

        def target_cost(ds_set):
            ds = sorted(ds_set)
            return sum(g(b - a) for a, b in zip(ds, ds[1:]))

        target_cur_cost = [target_cost(set(level_counts[t].keys()) | {0, h - 1}) for t in range(v)]

        def eval_group_move(group_moves):
            ben_delta = 0.0
            affected_t = set()
            for s, B_new in group_moves.items():
                d_old = len(pruned[s]) if s in pruned else 0
                d_new = 0 if B_new is None else len(B_new)
                ben_delta += role_benefit(s, d_new) - role_benefit(s, d_old)
                affected_t.update(t_lists[s])
            for s, B_new in group_moves.items():
                d_old = len(pruned[s]) if s in pruned else 0
                d_new = 0 if B_new is None else len(B_new)
                for t in t_lists[s]:
                    if d_old > 0:
                        level_counts[t][d_old] -= 1
                    if d_new > 0:
                        level_counts[t][d_new] += 1
            t_cost_delta = 0.0
            for t in affected_t:
                ds_set = {d for d, c in level_counts[t].items() if c > 0} | {0, h - 1}
                t_cost_delta += target_cost(ds_set) - target_cur_cost[t]
            for s, B_new in group_moves.items():
                d_old = len(pruned[s]) if s in pruned else 0
                d_new = 0 if B_new is None else len(B_new)
                for t in t_lists[s]:
                    if d_new > 0:
                        level_counts[t][d_new] -= 1
                        if level_counts[t][d_new] == 0:
                            del level_counts[t][d_new]
                    if d_old > 0:
                        level_counts[t][d_old] += 1
            return ben_delta - t_cost_delta

        changed_roles_in_outer = set()
        def apply_group_move(group_moves):
            affected_t = set()
            for s, B_new in group_moves.items():
                changed_roles_in_outer.add(s)
                d_old = len(pruned[s]) if s in pruned else 0
                for t in t_lists[s]:
                    if d_old > 0:
                        level_counts[t][d_old] -= 1
                        if level_counts[t][d_old] == 0:
                            del level_counts[t][d_old]
                    affected_t.add(t)
                if B_new is None:
                    if s in pruned:
                        del pruned[s]
                        for t in t_lists[s]:
                            byT[t].discard(s)
                else:
                    if s not in pruned:
                        for t in t_lists[s]:
                            byT[t].add(s)
                    pruned[s] = B_new
                    d_new = len(B_new)
                    for t in t_lists[s]:
                        level_counts[t][d_new] += 1
            for t in affected_t:
                target_cur_cost[t] = target_cost(set(level_counts[t].keys()) | {0, h - 1})
            return affected_t

        def valid_lower_frames(s, exclude_set=()):
            d = len(pruned[s])
            cands_B = {}
            for t in t_lists[s]:
                for w in byT[t]:
                    if w != s and w not in exclude_set and w in pruned and len(pruned[w]) < d:
                        cands_B[len(pruned[w])] = pruned[w]
            out = [None]
            for d_low, B_low in sorted(cands_B.items(), reverse=True):
                ok = True
                for t in t_lists[s]:
                    for w in byT[t]:
                        if w == s or w in exclude_set or w not in pruned:
                            continue
                        Bw = pruned[w]
                        if (len(Bw) >= d_low and not sat_contained(B_low, Bw)) or (len(Bw) < d_low and not sat_contained(Bw, B_low)):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    out.append(B_low)
            return out

        role_best = {}
        def compute_role_best(s):
            best_g = 1e-12
            best_B = None
            found = False
            for B_new in valid_lower_frames(s):
                gv = eval_group_move({s: B_new})
                if gv > best_g:
                    best_g = gv
                    best_B = B_new
                    found = True
            if found:
                role_best[s] = (best_g, best_B)
            else:
                role_best.pop(s, None)

        for s in list(pruned.keys()):
            compute_role_best(s)

        while True:
            if role_best:
                best_s = max(role_best, key=lambda s: role_best[s][0])
                _, best_B = role_best[best_s]
                aff_t = apply_group_move({best_s: best_B})
                role_best.pop(best_s, None)
                aff_roles = {w for t in aff_t for w in byT[t]}
                if best_s in pruned:
                    aff_roles.add(best_s)
                for w in aff_roles:
                    compute_role_best(w)
                continue
            best_move = None
            best_gain = 1e-12
            checked_groups = set()
            for t in range(v):
                for d, cnt in list(level_counts[t].items()):
                    if 2 <= cnt <= 20:
                        grp = tuple(sorted(w for w in byT[t] if w in pruned and len(pruned[w]) == d))
                        if len(grp) == cnt and grp not in checked_groups:
                            checked_groups.add(grp)
                            grp_set = set(grp)
                            gain_rem = eval_group_move({w: None for w in grp})
                            if gain_rem > best_gain:
                                best_gain = gain_rem
                                best_move = {w: None for w in grp}
                            snap_map = {}
                            for w in grp:
                                lows = [B for B in valid_lower_frames(w, grp_set) if B is not None]
                                snap_map[w] = lows[0] if lows else None
                            vals = [B for B in snap_map.values() if B is not None]
                            if len(set(vals)) <= 1:
                                gain_snap = eval_group_move(snap_map)
                                if gain_snap > best_gain:
                                    best_gain = gain_snap
                                    best_move = snap_map
            if best_move is not None:
                aff_t = apply_group_move(best_move)
                for w in best_move:
                    role_best.pop(w, None)
                aff_roles = {w for t in aff_t for w in byT[t]}
                for w in aff_roles:
                    compute_role_best(w)
                continue
            break

        for s in sorted(cand, key=lambda s: (-len(cand[s]), len(t_lists[s]), s)):
            d_cur = len(pruned[s]) if s in pruned else 0
            cand_s_cur = restrict(U[first_node[s]], [tmask[t] for t in reach[s]])
            if cand_s_cur and not sat_nondeg(cand_s_cur):
                cand_s_cur = sat_nonsingular_part(cand_s_cur)
            if not cand_s_cur or len(cand_s_cur) <= d_cur:
                continue
            X_up = reduce_against(cand_s_cur, t_lists[s], byT, pruned, skip_s=s)
            if len(X_up) > d_cur and eval_group_move({s: X_up}) > 1e-12:
                apply_group_move({s: X_up})

        placed = pruned
        dirty_nodes = set()
        for s in changed_roles_in_outer:
            x0 = first_node[s]
            dirty_nodes.add(x0)
            dirty_nodes.update(preds[x0])
            dirty_nodes.update(succ[x0])
            dirty_nodes.update(holds[s])
        U = optimize_U_for_placed(U, placed, n_sweeps=4, dirty_init=dirty_nodes)

    # Connected plateau-peeling block sweep on U
    starts = defaultdict(list)
    for s, X in placed.items():
        starts[first_node[s]].append(X)
    subspace_nodes = defaultdict(list)
    for x in order:
        if args[x][0]:
            subspace_nodes[U[x]].append(x)
    for B, nodes_B in list(subspace_nodes.items()):
        if len(nodes_B) <= 1:
            continue
        rem = set(nodes_B)
        while rem:
            root_x = rem.pop()
            comp = {root_x}
            q_c = [root_x]
            while q_c:
                curr = q_c.pop()
                for nb in list(preds[curr]) + list(succ[curr]):
                    if nb in rem:
                        rem.remove(nb)
                        comp.add(nb)
                        q_c.append(nb)
            if len(comp) <= 1:
                continue
            W_c = FULLB
            vecs_flat = []
            for x in comp:
                vecs_flat.extend(env_map[x])
                for X in starts[x]:
                    vecs_flat.extend(X)
                for y in preds[x]:
                    if y not in comp:
                        vecs_flat.extend(U[y])
                W_c = sat_cap(W_c, K_ker[x])
                for t in succ[x]:
                    if t not in comp and not sat_contained(W_c, U[t]):
                        W_c = sat_cap(W_c, U[t])
            L_c = sat_basis(vecs_flat)
            if not sat_contained(L_c, W_c):
                continue
            cands_c = []
            if sat_nondeg(L_c):
                cands_c.append(L_c)
                if not sat_nondeg(W_c):
                    cands_c.append(max_nondeg_between(L_c, W_c))
            else:
                B_min = min_nondeg_between(L_c, W_c)
                if B_min is not None and sat_nondeg(B_min) and sat_contained(L_c, B_min) and sat_contained(B_min, W_c):
                    cands_c.append(B_min)
                    if not sat_nondeg(W_c):
                        cands_c.append(max_nondeg_between(B_min, W_c))
            if sat_nondeg(W_c):
                cands_c.append(W_c)
            if not cands_c:
                continue
            aff_r = {s for x in comp for s in roles_of[x]}
            best_Bc = B
            best_cc = sum(role_chain_cost(s, U, placed) for s in aff_r)
            for Bc in cands_c:
                if Bc == B or not (sat_nondeg(Bc) and sat_contained(L_c, Bc) and sat_contained(Bc, W_c)):
                    continue
                for x in comp:
                    U[x] = Bc
                cc = sum(role_chain_cost(s, U, placed) for s in aff_r)
                if cc < best_cc - 1e-12 or (abs(cc - best_cc) <= 1e-12 and len(Bc) < len(best_Bc)):
                    best_cc = cc
                    best_Bc = Bc
            for x in comp:
                U[x] = best_Bc

    dimU = {x: len(U[x]) for x in U}
    print('PR117 frames lifted', sum(dimU[x] > ranks[x] for x in U), flush=True)
    print('PR117 placed', len(placed), flush=True)
    deferred = sorted(placed, key=lambda s: (len(placed[s]), s))
    dset = set(deferred)
    def F0(s):
        return U[first_node[s]]

    # ------------------------------------------------------------ C. replay with arbitrary scratch and data
    inv = lambda a: pow(a % P, P - 2, P)
    HALF = inv(2)
    I21 = inv(21)
    cvec = [None] * Rr
    dpart = [dict() for _ in range(Rr)]
    for s, j in role_root.items():
        if kind[j]:
            c = [0] * h
            c[centre_of[j]] = 1
            cvec[s] = c
        else:
            dpart[s][target[j]] = (P - HALF) if j >= v else HALF
    seed_c = {s: (None if cvec[s] is None else list(cvec[s])) for s in role_root}
    seed_d = {s: dict(dpart[s]) for s in role_root}
    def addc(dst, src):
        if cvec[src] is not None:
            cvec[dst] = list(cvec[src]) if cvec[dst] is None else [(p + q_) % P for p, q_ in zip(cvec[dst], cvec[src])]
        for t, c in dpart[src].items():
            dpart[dst][t] = (dpart[dst].get(t, 0) + c) % P
    for o in reversed(ops):
        if o[0] == 'add':
            addc(o[2], o[1])
        elif o[0] == 'copy':
            addc(o[1], o[2])
    scatter = [[(I21 - (HALF if i in trip[t] else 0)) % P for t in range(v)] for i in range(h)]
    def readout(y, s, value, sign, seed=False):
        cv = seed_c[s] if seed else cvec[s]
        dp = seed_d[s] if seed else dpart[s]
        if cv is not None:
            for i, ci in enumerate(cv):
                if ci:
                    f = sign * ci * value % P
                    row = scatter[i]
                    for t in range(v):
                        y[t] = (y[t] + f * row[t]) % P
        for t, c in dp.items():
            y[t] = (y[t] + sign * c * value) % P
    phase1 = sorted(Anc)
    rest = [i for i in range(len(ops)) if i not in Anc]
    def replay(seed):
        rng = random.Random(seed)
        x = [rng.randrange(P) for _ in range(v)]
        z = [rng.randrange(P) for _ in range(Rr)]
        y0 = [rng.randrange(P) for _ in range(v)]
        a = list(z)
        y = list(y0)
        for s in range(Rr):
            if s not in dset:
                readout(y, s, a[s], -1)
        for s, leaf in leaf_of.items():
            if s not in dset:
                a[s] = (a[s] + x[leaf - 1]) % P
        def run(i, sign=1):
            o = ops[i]
            if o[0] == 'add':
                a[o[1]] = (a[o[1]] + sign * a[o[2]]) % P
            elif o[0] == 'copy':
                a[o[2]] = (a[o[2]] + sign * a[o[1]]) % P
        for i in phase1:
            run(i)
        for s in centre_roles:
            readout(y, s, a[s], +1, True)
        for s in deferred:
            readout(y, s, a[s], -1)
        for s in deferred:
            if s in leaf_of:
                a[s] = (a[s] + x[leaf_of[s] - 1]) % P
        for i in rest:
            run(i)
        for s, j in role_root.items():
            if not kind[j]:
                readout(y, s, a[s], +1, True)
        for i in reversed(range(len(ops))):
            run(i, -1)
        for s, leaf in leaf_of.items():
            a[s] = (a[s] - x[leaf - 1]) % P
        return a == z, all((y[t] - y0[t] - x[t]) % P == 0 for t in range(v))
    rep = [replay(seed) for seed in (1, 2)]
    require(all(r == (True, True) for r in rep), 'replay %s' % rep)

    # ------------------------------------------------------------ D. exact F2 frame facts
    chain_dims = []
    for s in range(Rr):
        seq = [placed.get(s, ()), F0(s)] + [U[x] for x in holds[s][1:]]
        if s in root_frame:
            seq.append(root_frame[s])
        seq.append(FULLB)
        require(all(sat_contained(A, B) for A, B in zip(seq, seq[1:])), 'role chain nesting %d' % s)
        require(all(sat_nondeg(B) for B in seq[1:-1] if B), 'degenerate frame on role %d' % s)
        chain_dims.append([len(B) for B in seq])
    for s, X in placed.items():
        require(sat_contained(X, F0(s)) and sat_nondeg(X), 'deferral frame %d' % s)
        require(all(not any(sat_dot(xv, tmask[t]) for xv in X) for t in reach[s]), 'target frame %d' % s)
    byT2 = defaultdict(list)
    for s in deferred:
        for t in reach[s]:
            byT2[t].append(s)
    for t, ss in byT2.items():
        ss.sort(key=lambda s: (len(placed[s]), s))
        require(all(sat_contained(placed[p], placed[q_]) for p, q_ in zip(ss, ss[1:])), 'target chain %d' % t)

    # ------------------------------------------------------------ E. one-child histogram
    z = Counter()
    for s in range(Rr):
        ds = chain_dims[s]
        for a, b in zip(ds[:-1], ds[1:-1]):
            if b > a:
                z[b - a] += 2 * v
        lastd = ds[-2]
        if s in role_root and kind[role_root[s]]:
            z[h - 1] += 2 * v           # copied centre transform
        z[h - lastd] += 2 * v                                                  # final growth to F
        z[m - h + ds[0]] += 2 * v                                              # exterior, gauged by sigma
    levels = defaultdict(set)
    for s in deferred:
        for t in reach[s]:
            levels[t].add(len(placed[s]))
    for t in range(v):
        ds = sorted(levels[t] | {0, h - 1})
        for a, b in zip(ds, ds[1:]):
            z[b - a] += 2 * v                                                  # target fronts
    z[h - 1] += 2 * N                                                          # data-wire fronts
    z[(h - 1) ** 2] += 2 * N                                                   # data macros
    z[1] += N                                                                  # endpoint copies
    z.pop(0, None)
    W = 2 * N + 2 * v * R
    L = 2 * v * h * (h - 1)
    s_ = W * m - N + L
    require(sum(t * c for t, c in z.items()) == s_, 'complex rank mass')
    require(all(0 < t < m for t in z), 'children below m')
    out = dict(h=h, v=v, additions=c_add, roots=q, links=len(links), R=R, m=m, N=N, W=W, L=L, total_rank=s_,
               deficit=N - L, maxchild=max(z), phase_one_ops=len(Anc), phase_one_roles=len(touched),
               deferred_roles=len(deferred),
               deferred_dims=dict(sorted(Counter(len(X) for X in placed.values()).items())),
               lifted_additions=sum(1 for x in U if args[x][0] and dimU[x] > ranks[x]),
               replay=dict(seeds=[1, 2], scratch_restored=True, y_plus_x=True, field='Z/(2^61-1)'),
               child_multiplicities=dict(sorted(z.items())))
    (HERE / 'complex-profile.json').write_text(json.dumps(out, indent=2) + '\n')
    print('PASS complex: R=%d, deferred roles %d, maxchild %d, rank mass %d' % (R, len(deferred), max(z), s_))


if __name__ == '__main__':
    main()
