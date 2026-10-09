#!/usr/bin/env python3
"""Optimized physical gate frames on the immutable PR117 complex DAG.

After saturated deferral, each mixer gate frame is optimized within its two
role chains. Maximal nondegenerate extensions and minimal nondegenerate hulls
are accepted only when they improve the local moment objective; every actual
source, mixer, copied-center and root incidence is checked exactly.
Physical-frame optimization prepared with OpenAI Codex assistance.
Compensated birth-cut reuse follows jamesyc PR124; this composition regenerates
all pairings, replays arbitrary aliased scratch, and retains every scalar charge.
Arbitrary source gauges are then optimized by exact chain insertion and joint
equal-frame plateau moves under PR130, preserving the selected reuse mapping.
The changed deferred readout and injection chronology is replayed in full.

PR117 credits its searched DAG to eumemic with Anthropic Claude assistance;
this experiment imports and replays that witness unchanged. PR110/PR114
saturation and exact finite checks are applied to the resulting graph.
Logical readout macros are realized as signed numerator/42 chunks of magnitude
at most one. The literal audit expands and charges those same-frame shears,
checks exact reconstruction, and reverses the chunks under reflection.
Inherited Avi Eisenberg, Rohan Arun, icekylinx and Swapnil Jain credits retained.
This integration prepared with OpenAI Codex assistance. Apache-2.0.
"""
import array
import json
import random
import struct
import sys
import tempfile
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from reuse import select_reuse, check_pairs, check_compensation, mutation_controls
from arbitrary_frames import optimize as optimize_arbitrary_frames, general_frame
from gauge_frames import optimize as optimize_gauge_frames

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(HERE))
import importlib.util
producer_path = HERE / 'producer.py'
spec = importlib.util.spec_from_file_location('replayed_producer_wrapper', producer_path)
producer = importlib.util.module_from_spec(spec); spec.loader.exec_module(producer)
build = producer.build

P = (1 << 61) - 1


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def load(prefix):
    def rd(fh, typ, cnt):
        a = array.array(typ); a.fromfile(fh, cnt); return a
    with open(str(prefix) + '.bin', 'rb') as f:
        h, v, n, q = struct.unpack('<4I', f.read(16))
        flat = rd(f, 'I', 2 * n); core = rd(f, 'Q', n); cover = rd(f, 'Q', n)
        roots = rd(f, 'I', q); kind = rd(f, 'I', q); active = rd(f, 'B', n)
    with open(str(prefix) + '.labels', 'rb') as f:
        ranks = rd(f, 'I', n); types = rd(f, 'B', n)
    args = [(flat[2 * i], flat[2 * i + 1]) for i in range(n)]
    return h, v, n, q, args, core, cover, roots, kind, active, ranks, types


# ---------------------------------------------------------------- F2 linear algebra on bit vectors
def dot(a, b): return bin(a & b).count('1') & 1


def reduce(basis):
    rows = []; piv = []
    for vec in basis:
        for p, r in zip(piv, rows):
            if vec >> p & 1: vec ^= r
        if vec:
            p = vec.bit_length() - 1
            for i in range(len(rows)):
                if rows[i] >> p & 1: rows[i] ^= vec
            rows.append(vec); piv.append(p)
    return rows


def kernel(funcs, h):
    K = reduce(funcs); piv = [r.bit_length() - 1 for r in K]
    out = []
    for c in (i for i in range(h) if i not in piv):
        vec = 1 << c
        for r, p in zip(K, piv):
            if r >> c & 1: vec |= 1 << p
        out.append(vec)
    return out


def restrict(basis, funcs):
    B = reduce(basis)
    for f in funcs:
        if not B: break
        vals = [dot(b, f) for b in B]
        if not any(vals): continue
        k = vals.index(1); pv = B[k]
        B = [b ^ pv if val else b for b, val in zip(B, vals)]; B.pop(k)
    return reduce(B)


def contains(A, B):
    RB = reduce(B)
    return len(reduce(RB + list(A))) == len(RB)


def cap(A, B):
    A = reduce(A); B = reduce(B)
    if not A or not B: return []
    ker = []; red = []
    for i, vec in enumerate(A + B):
        tag = 1 << i
        for rv, rt in red:
            if vec >> (rv.bit_length() - 1) & 1: vec ^= rv; tag ^= rt
        if vec: red.append((vec, tag))
        else:
            comb_ = 0
            for k in range(len(A)):
                if tag >> k & 1: comb_ ^= A[k]
            ker.append(comb_)
    return reduce(ker)


def nondeg(B):
    B = reduce(B); k = len(B)
    if not k: return True
    M = [sum(dot(B[i], B[j]) << j for j in range(k)) for i in range(k)]
    return len(reduce(M)) == k


def hopcroft_karp(left, adj):
    """maximum bipartite matching; adj[x] = sorted list of right vertices."""
    INF = 1 << 60
    mate_l = {x: None for x in left}; mate_r = {}
    while True:
        dist = {}; queue = []
        for x in left:
            if mate_l[x] is None: dist[x] = 0; queue.append(x)
            else: dist[x] = INF
        found = INF; head = 0
        while head < len(queue):
            x = queue[head]; head += 1
            if dist[x] >= found: continue
            for r in adj[x]:
                y = mate_r.get(r)
                if y is None: found = min(found, dist[x] + 1)
                elif dist[y] == INF: dist[y] = dist[x] + 1; queue.append(y)
        if found == INF: break
        gained = 0
        for x0 in left:
            if mate_l[x0] is not None: continue
            stack = [(x0, iter(adj[x0]))]; path = []
            while stack:
                x, it = stack[-1]
                advanced = False
                for r in it:
                    y = mate_r.get(r)
                    if (y is None and dist[x] + 1 == found) or (y is not None and dist[y] == dist[x] + 1):
                        path.append((x, r))
                        if y is None:
                            for xx, rr in path: mate_l[xx] = rr; mate_r[rr] = xx
                            gained += 1; stack = []; break
                        stack.append((y, iter(adj[y]))); advanced = True; break
                else:
                    dist[x] = INF; stack.pop()
                    if path: path.pop()
                    continue
                if not advanced: break
        if not gained: break
    return mate_l


from functools import lru_cache
from fractions import Fraction

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

def saturated_placement(cand, reach):
    # Each extracted block is orthogonal to previously selected blocks.
    # A diagonal-one pivot contributes a nondegenerate line; when all
    # remaining diagonals vanish, a dot-one pair contributes a hyperbolic
    # plane. The residual radical is discarded, not counted as a frame.
    cand = {s: sat_basis(B) for s, B in cand.items()}
    order = sorted(cand, key=lambda s: (Fraction(-(1 << len(cand[s])), max(1, len(reach[s]))**2), -len(cand[s]), s))
    byT = defaultdict(list); placed = {}
    for s in order:
        X = cand[s]; changed = True
        while changed and X:
            changed = False
            for t in sorted(reach[s]):
                for w in byT[t]:
                    B = placed[w]
                    if (len(B) >= len(X) and not sat_contained(X, B)) or (len(B) < len(X) and not sat_contained(B, X)):
                        X = sat_cap(X, B); changed = True
                    if not X: break
                if not X: break
            if X and not sat_nondeg(X):
                before = X; X = sat_nonsingular_part(X)
                assert sat_contained(X, before) and sat_nondeg(X)
                assert len(X) < len(before)
                changed = True  # Extraction can break containment of a smaller target frame.
        if X:
            assert sat_nondeg(X) and sat_contained(X, cand[s])
            placed[s] = X
            for t in reach[s]: byT[t].append(s)
    for t, ss in byT.items():
        ss.sort(key=lambda s: (len(placed[s]), s))
        assert all(sat_contained(placed[a], placed[b]) for a, b in zip(ss, ss[1:]))
    return placed

def frame_restrict(A,B):return sat_basis(restrict(A,B))

@lru_cache(None)
def frame_protected_part(X, L):
    Q = sat_nonsingular_part(X)
    rad = frame_restrict(X, Q)
    if not L:
        return Q
    red = {}
    for q, r in [(q, 0) for q in Q] + [(0, r) for r in rad]:
        x = q ^ r
        for p in sorted(red, reverse=True):
            if x >> p & 1:
                y, a, b = red[p]
                x ^= y
                q ^= a
                r ^= b
        assert x
        red[x.bit_length() - 1] = (x, q, r)
    lin = {}
    for x in L:
        q = r = 0
        for p in sorted(red, reverse=True):
            if x >> p & 1:
                y, a, b = red[p]
                x ^= y
                q ^= a
                r ^= b
        if x:
            return ()
        for p in sorted(lin, reverse=True):
            if q >> p & 1:
                a, b = lin[p]
                q ^= a
                r ^= b
        if not q:
            if r:
                return ()
        else:
            lin[q.bit_length() - 1] = (q, r)
    out = []
    for x in Q:
        q = x
        r = 0
        for p in sorted(lin, reverse=True):
            if q >> p & 1:
                a, b = lin[p]
                q ^= a
                r ^= b
        out.append(x ^ r)
    out = sat_basis(out)
    assert sat_nondeg(out) and sat_contained(out, X) and sat_contained(L, out)
    return out

@lru_cache(None)
def frame_smallest_hull(L, ambient):
    L = sat_basis(L)
    while not sat_nondeg(L):
        radical = frame_restrict(L, L)
        assert radical
        r = radical[0]
        partner = next((x for x in ambient if sat_dot(r, x)))
        L = sat_basis(L + (partner,))
    assert sat_contained(L, ambient)
    return L

def main():
    with tempfile.TemporaryDirectory(prefix='deferred-stopped-') as work:
        prefix = Path(work) / 'complex'
        build(24, prefix, central_disjoint=24)
        h, v, n, q, args, core, cover, roots, kind, active, ranks, types = load(prefix)
    trip = list(combinations(range(h), 3)); require(len(trip) == v, 'triple count')
    m = h * h; N = v * v; FULL = (1 << h) - 1
    tmask = [sum(1 << p for p in T) for T in trip]
    tid = {T: i for i, T in enumerate(trip)}

    # ------------------------------------------------------------ uses and matching (inherited adjacency)
    degree = [0] * n; uses = defaultdict(list); c_add = 0
    for x in range(1, n):
        if active[x] and args[x][0]:
            c_add += 1
            for pos, y in enumerate(args[x]): degree[y] += 1; uses[y].append(('gate', x, pos))
    for j, x in enumerate(roots): degree[x] += 1; uses[x].append(('root', j))
    def unode(u): return roots[u[1]] if u[0] == 'root' else u[1]
    def before(x, u):
        y = unode(u)
        return (ranks[x], x) < (ranks[y], (n + u[1]) if u[0] == 'root' else y)
    def incl(x, y):
        tx, ty = types[x], types[y]
        if tx == 1 and ty == 1: return not (core[y] & ~core[x]) and not (cover[x] & ~cover[y])
        if tx in (1, 2) and ty == 2: return not (cover[x] & ~cover[y])
        if tx == 1 and ty == 3: return bool(core[x] & core[y])
        if tx == 2 and ty == 3: return not (cover[x] & ~core[y])
        if tx == 3 and ty == 2: return cover[y] == FULL
        if tx == 3 and ty == 3: return core[x] == core[y]
        return False
    left = []; adj = {}
    for x in range(1, n):
        if not (active[x] and args[x][0]): continue
        rs = sorted({(y, k) for y in args[x] for k, u in enumerate(uses[y]) if before(x, u) and incl(x, unode(u))})
        if rs: left.append(x); adj[x] = rs
    mate = hopcroft_karp(left, adj)
    links = {x: r for x, r in mate.items() if r is not None}
    R = c_add + q - len(links)
    require((c_add,q,len(links),R)==(91770,8120,71185,28705),'selected PR117 graph')
    print('PR117 graph matched', c_add, q, len(links), R, flush=True)
    linked_use = {(y, k): x for x, (y, k) in links.items()}

    # ------------------------------------------------------------ root targets, read coefficients, root functionals
    target = [None] * q
    for j in range(v): target[j] = j
    idx = v
    # PR117 witness stores pair-star roots in natural excluded-point order.
    for a, b in combinations(range(h), 2):
        others = [i for i in range(h) if i not in (a, b)]
        for i in others: target[idx] = tid[tuple(sorted((a, b, i)))]; idx += 1
    centre_of = {}
    for j in range(q):
        if kind[j]:
            miss = FULL & ~cover[roots[j]]; require(bin(miss).count('1') == 1, 'centre cover')
            centre_of[j] = miss.bit_length() - 1
    require(idx + len(centre_of) == q, 'root order')
    rootfun = [(1 << centre_of[j]) if kind[j] else tmask[target[j]] for j in range(q)]

    # ------------------------------------------------------------ lifted binary frames, monotone
    succ = defaultdict(set); droot = defaultdict(set)
    for x in range(1, n):
        if not active[x]: continue
        for k, u in enumerate(uses[x]):
            if (x, k) in linked_use: continue
            (succ[x].add(u[1]) if u[0] == 'gate' else droot[x].add(u[1]))
    for x, (y, k) in links.items():
        u = uses[y][k]; (succ[x].add(u[1]) if u[0] == 'gate' else droot[x].add(u[1]))
    order_desc = sorted((x for x in range(1, n) if active[x]), key=lambda x: (ranks[x], x), reverse=True)
    K = {}
    for x in order_desc:
        rows = [rootfun[j] for j in droot[x]]
        for t in succ[x]: rows += K[t]
        K[x] = reduce(rows)
    def envelope(x):
        if not args[x][0]: return [tmask[x - 1]]
        if types[x] == 2: return [1 << i for i in range(h) if cover[x] >> i & 1]
        require(types[x] == 1, 'only ordinary and common-pair labels occur')
        ks = [i for i in range(h) if (cover[x] & ~core[x]) >> i & 1]
        require(len(ks) == ranks[x], 'common-pair support')
        return [core[x] | (1 << k) for k in ks]
    U = {}
    for x in range(1, n):
        if not active[x]: continue
        if not args[x][0]: U[x] = envelope(x); continue
        B = kernel(K[x], h)
        require(contains(envelope(x), B), 'label outside lifted frame')
        U[x] = B if nondeg(B) else envelope(x)
    changed = True
    while changed:
        changed = False
        for x in order_desc:
            if args[x][0] and any(not contains(U[x], U[t]) for t in succ[x]):
                env = envelope(x)
                if len(reduce(U[x])) != len(reduce(env)) or not contains(U[x], env): U[x] = env; changed = True
    dimU = {x: len(reduce(B)) for x, B in U.items()}
    print('PR117 frames lifted',sum(dimU[x]>ranks[x] for x in U),flush=True)

    # ------------------------------------------------------------ explicit role compile
    order = sorted((x for x in range(1, n) if active[x]), key=lambda x: (ranks[x], x))
    holds = []; first_node = []; ops = []; edge_key = {}; role_root = {}
    def new_role(node): holds.append([node]); first_node.append(node); return len(holds) - 1
    def serve(s, y, k):
        u = uses[y][k]
        if u[0] == 'gate': edge_key[(y, k)] = s
        else: role_root[s] = u[1]
    for x in order:
        free = [k for k in range(len(uses[x])) if (x, k) not in linked_use]
        if not args[x][0]:
            for k in free:
                s = new_role(x); ops.append(('src', s, x)); serve(s, x, k)
            continue
        a, b = args[x]
        ka = next(k for k, u in enumerate(uses[a]) if u == ('gate', x, 0))
        kb = next(k for k, u in enumerate(uses[b]) if u == ('gate', x, 1))
        sa, sb = edge_key.pop((a, ka)), edge_key.pop((b, kb))
        if x in links and links[x][0] == a: sa, sb = sb, sa
        piv, oth = sa, sb
        ops.append(('add', piv, oth, x)); holds[piv].append(x); holds[oth].append(x)
        if x in links: serve(oth, *links[x])
        require(free, 'every use linked at node %d' % x)
        serve(piv, x, free[0])
        for k in free[1:]:
            f = new_role(x); ops.append(('copy', piv, f, x)); serve(f, x, k)
    require(not edge_key and len(holds) == R, 'compile')
    Rr = R

    # ------------------------------------------------------------ B. the word computes every root value
    rng = random.Random(20261008)
    xs = [rng.randrange(P) for _ in range(v)]
    val = [0] * n
    for i in range(v): val[i + 1] = xs[i]
    for x in order:
        if args[x][0]: val[x] = (val[args[x][0]] + val[args[x][1]]) % P
    leaf_of = {s: first_node[s] for s in range(Rr) if not args[first_node[s]][0]}
    a_ = [0] * Rr
    for s, leaf in leaf_of.items(): a_[s] = xs[leaf - 1]
    for o in ops:
        if o[0] == 'add': a_[o[1]] = (a_[o[1]] + a_[o[2]]) % P
        elif o[0] == 'copy': a_[o[2]] = (a_[o[2]] + a_[o[1]]) % P
    require(all(a_[s] == val[roots[j]] for s, j in role_root.items()), 'root values')

    # ------------------------------------------------------------ phase one and garbage reach
    def touch(o): return [o[1], o[2]] if o[0] in ('add', 'copy') else []
    prev = {}; pred = defaultdict(list); last = {}
    for i, o in enumerate(ops):
        for s in touch(o):
            if s in prev: pred[i].append(prev[s])
            prev[s] = i; last[s] = i
    centre_roles = [s for s, j in role_root.items() if kind[j]]
    Anc = set(); st = [last[s] for s in centre_roles]
    while st:
        i = st.pop()
        if i not in Anc: Anc.add(i); st.extend(pred[i])
    touched = set(centre_roles)
    for i in Anc: touched.update(touch(ops[i]))
    require(all(last[s] in Anc for s in centre_roles), 'centres complete in phase one')
    reach = [set() for _ in range(Rr)]; reach_all = [False] * Rr
    for s, j in role_root.items():
        if kind[j]: reach_all[s] = True
        else: reach[s].add(target[j])
    for o in reversed(ops):
        if o[0] == 'add': reach[o[2]] |= reach[o[1]]; reach_all[o[2]] = reach_all[o[2]] or reach_all[o[1]]
        elif o[0] == 'copy': reach[o[1]] |= reach[o[2]]; reach_all[o[1]] = reach_all[o[1]] or reach_all[o[2]]

    # ------------------------------------------------------------ deferral frames, insertion nesting
    def F0(s): return U[first_node[s]]
    cand = {}
    for s in range(Rr):
        if s in touched or reach_all[s]: continue
        S_ = restrict(F0(s), [tmask[t] for t in reach[s]])
        if S_ and nondeg(S_): cand[s] = S_
    print('PR117 candidates',len(cand),flush=True)
    placed = saturated_placement(cand, reach)
    print('PR117 placed',len(placed),flush=True)
    deferred = sorted(placed, key=lambda s: (len(placed[s]), s)); dset = set(deferred)

    # Optimize the actual mixer word. Source injection and root frames stay fixed.
    # Floating objective values choose legal finite frames only; the complete
    # child profile and its contraction are certified independently and exactly.
    root_frame={s:([1<<i for i in range(h)if i!=centre_of[j]] if kind[j] else kernel([tmask[target[j]]],h)) for s,j in role_root.items()}
    frame_U={x:sat_basis(B)for x,B in U.items()}
    FULL=sat_basis(1<<i for i in range(h))
    sigma={s:sat_basis(B)for s,B in placed.items()}
    role_events=defaultdict(list);frames={};birth={};lifted=Counter()
    for i,o in enumerate(ops):
     if o[0]=='src':
      frames[i]=frame_U[o[2]];role_events[o[1]].append(i)
     else:
      frames[i]=frame_U[o[3]]
      for s in o[1:3]:role_events[s].append(i)
    prev={};after={};end={s:sat_basis(root_frame[s])if s in root_frame else FULL for s in range(R)}
    for s,events in role_events.items():
     for j,i in enumerate(events):prev[i,s]=events[j-1]if j else None;after[i,s]=events[j+1]if j+1<len(events)else None
    # Frozen IEEE-754 search weights remove platform libm variation.
    vals=[float.fromhex(x) for x in ['0x0.0p+0', '0x1.0000000000000p+0', '0x1.fff611fabad2cp+0', '0x1.7ff4324fbceecp+1', '0x1.ffec2426c27bdp+1', '0x1.3ff197310b8c8p+2', '0x1.7fecc00663620p+2', '0x1.bfe79c1e23586p+2', '0x1.ffe2368416067p+2', '0x1.1fee4bbd449aep+3', '0x1.3feb62b54ad1bp+3', '0x1.5fe862b99e2f4p+3', '0x1.7fe54de202531p+3', '0x1.9fe225ec96cafp+3', '0x1.bfdeec529ef76p+3', '0x1.dfdba257523b3p+3', '0x1.ffd84912b47dep+3', '0x1.0fea70bcdaf4fp+4', '0x1.1fe8b63233d76p+4', '0x1.2fe6f54967551p+4', '0x1.3fe52e5858b9ap+4', '0x1.4fe361ac5190ep+4', '0x1.5fe18f8b3cb6dp+4', '0x1.6fdfb834a8020p+4', '0x1.7fdddbe2990a6p+4']]
    for turn in range(5):
     changes=0;delta=0
     for i in (reversed(range(len(ops)))if turn%2==0 else range(len(ops))):
      o=ops[i]
      if o[0]=='src':continue
      _,a,b,x=o;old=frames[i];ends=[frames[after[i,s]]if after[i,s]is not None else end[s]for s in (a,b)]
      starts=[frames[prev[i,s]]if prev[i,s]is not None else sigma.get(s,())for s in (a,b)]
      cap=sat_cap(*ends);lower=sat_basis(starts[0]+starts[1])
      options=[frame_protected_part(cap,old),frame_smallest_hull(lower,old)]
      best=old;bestdelta=-1e-10
      for F in options:
       assert sat_nondeg(F)and all(sat_contained(P,F)and sat_contained(F,N)for P,N in zip(starts,ends))
       df=sum(vals[len(F)-len(P)]+vals[len(N)-len(F)]-vals[len(old)-len(P)]-vals[len(N)-len(old)]for P,N in zip(starts,ends))
       if df<bestdelta:best=F;bestdelta=df
      if best!=old:frames[i]=best;changes+=1;delta+=bestdelta
     print('Physical frame descent',turn,changes,delta,flush=True)
     if not changes:break
    for i,o in enumerate(ops):
     if o[0]=='src':birth[o[1]]=frames[i]
     elif o[0]=='copy':birth[o[2]]=frames[i]
     if o[0]!='src':lifted[len(frame_U[o[3]]),len(frames[i])]+=1
    assert len(birth)==R
    op_frames=frames
    role_frames={s:[]for s in range(R)}
    for i,o in enumerate(ops):
        if o[0]=='src':role_frames[o[1]].append(op_frames[i])
        else:
            for s in o[1:3]:role_frames[s].append(op_frames[i])
    def F0(s):return birth[s]
    reuse_pairs = select_reuse(locals())
    merge = check_pairs(locals(), reuse_pairs)
    reuse_rejected_controls = mutation_controls(locals(), reuse_pairs)
    op_frames, arbitrary_frame_stats = optimize_arbitrary_frames(locals())
    placed, op_frames, gauge_frame_stats = optimize_gauge_frames(locals())
    sigma = placed
    deferred = sorted(placed, key=lambda s: (len(placed[s]), s)); dset = set(deferred)
    for pair in reuse_pairs:
        A = op_frames[last[pair['donor']]]; F = placed[pair['recipient']]
        pair.update(donor_frame=A, birth_frame=F, e=len(A), s=len(F))
    frames = op_frames
    role_frames = {s: [] for s in range(R)}
    for i, o in enumerate(ops):
        if o[0] == 'src':
            role_frames[o[1]].append(op_frames[i]); birth[o[1]] = op_frames[i]
        else:
            for s in o[1:3]: role_frames[s].append(op_frames[i])
            if o[0] == 'copy': birth[o[2]] = op_frames[i]
    merge = check_pairs(locals(), reuse_pairs)
    live = [s for s in range(Rr) if s not in merge]
    physical_id = {s: i for i, s in enumerate(live)}
    def alias(s): return physical_id[merge.get(s, s)]
    print('Compensated birth reuse', len(reuse_pairs), 'physical roles', len(live), flush=True)

    # ------------------------------------------------------------ C. replay with arbitrary scratch and data
    inv = lambda a: pow(a % P, P - 2, P); HALF = inv(2); I21 = inv(21)
    cvec = [None] * Rr; dpart = [dict() for _ in range(Rr)]
    for s, j in role_root.items():
        if kind[j]: c = [0] * h; c[centre_of[j]] = 1; cvec[s] = c
        else: dpart[s][target[j]] = (P - HALF) if j >= v else HALF
    seed_c = {s: (None if cvec[s] is None else list(cvec[s])) for s in role_root}
    seed_d = {s: dict(dpart[s]) for s in role_root}
    def addc(dst, src):
        if cvec[src] is not None:
            cvec[dst] = list(cvec[src]) if cvec[dst] is None else [(p + q_) % P for p, q_ in zip(cvec[dst], cvec[src])]
        for t, c in dpart[src].items(): dpart[dst][t] = (dpart[dst].get(t, 0) + c) % P
    for o in reversed(ops):
        if o[0] == 'add': addc(o[2], o[1])
        elif o[0] == 'copy': addc(o[1], o[2])
    scatter = [[(I21 - (HALF if i in trip[t] else 0)) % P for t in range(v)] for i in range(h)]
    def readout(y, s, value, sign, seed=False):
        # Logical readout macro: the literal audit combines its exact rational
        # target coefficients and expands each numerator/42 into bounded shears.
        cv = seed_c[s] if seed else cvec[s]; dp = seed_d[s] if seed else dpart[s]
        if cv is not None:
            for i, ci in enumerate(cv):
                if ci:
                    f = sign * ci * value % P; row = scatter[i]
                    for t in range(v): y[t] = (y[t] + f * row[t]) % P
        for t, c in dp.items(): y[t] = (y[t] + sign * c * value) % P
    phase1 = sorted(Anc); rest = [i for i in range(len(ops)) if i not in Anc]
    def replay(seed, omit_compensation=None):
        rng = random.Random(seed)
        x = [rng.randrange(P) for _ in range(v)]
        z = [rng.randrange(P) for _ in live]
        y0 = [rng.randrange(P) for _ in range(v)]; a = list(z); y = list(y0)
        chronology = []
        def inject(s, leaf):
            dst = alias(s)
            a[dst] = (a[dst] + x[leaf - 1]) % P
            chronology.append(('src', dst, leaf - 1))
        def run(i):
            o = ops[i]
            if o[0] == 'src': return
            dst, src = (o[1], o[2]) if o[0] == 'add' else (o[2], o[1])
            dst, src = alias(dst), alias(src)
            require(dst != src, 'aliased gate ports')
            a[dst] = (a[dst] + a[src]) % P
            chronology.append(('work', dst, src))
        for s in range(Rr):
            if s not in dset: readout(y, s, a[alias(s)], -1)
        for s, leaf in leaf_of.items():
            if s not in dset: inject(s, leaf)
        for i in phase1: run(i)
        for s in centre_roles: readout(y, s, a[alias(s)], +1, True)
        compensated = []
        for s in deferred:
            if s != omit_compensation:
                readout(y, s, a[alias(s)], -1)
                compensated.append(s)
        if omit_compensation is None: check_compensation(merge, compensated)
        for s in deferred:
            if s in leaf_of: inject(s, leaf_of[s])
        for i in rest: run(i)
        for s, j in role_root.items():
            if not kind[j]: readout(y, s, a[alias(s)], +1, True)
        # Aliased births require reversal of the actual source/workspace
        # chronology, including delayed source injections.
        for kind_, dst, src in reversed(chronology):
            value = x[src] if kind_ == 'src' else a[src]
            a[dst] = (a[dst] - value) % P
        return a == z, all((y[t] - y0[t] - x[t]) % P == 0 for t in range(v))
    rep = [replay(seed) for seed in (1, 2)]
    require(all(r == (True, True) for r in rep), 'aliased replay %s' % rep)
    missing_compensation = replay(3, omit_compensation=reuse_pairs[0]['recipient'])
    require(missing_compensation == (True, False), 'omitted compensation unexpectedly accepted')
    compensated_births = sorted(merge)

    # ------------------------------------------------------------ D. exact F2 frame facts
    root_frame = {}
    for s, j in role_root.items():
        root_frame[s] = [1 << i for i in range(h) if i != centre_of[j]] if kind[j] else kernel([tmask[target[j]]], h)
    FULLB = [1 << i for i in range(h)]
    chain_dims = []
    for s in range(Rr):
        seq = [placed.get(s, [])] + role_frames[s]
        if s in root_frame: seq.append(root_frame[s])
        seq.append(FULLB)
        require(all(contains(A, B) for A, B in zip(seq, seq[1:])), 'role chain nesting %d' % s)
        require(all(general_frame(sat_basis(B), h) for B in seq[1:-1]), 'invalid generalized frame on role %d' % s)
        chain_dims.append([len(reduce(B)) for B in seq])
    for s, X in placed.items():
        require(contains(X, F0(s)) and general_frame(sat_basis(X), h), 'deferral frame %d' % s)
        require(all(not any(dot(xv, tmask[t]) for xv in X) for t in reach[s]), 'target frame %d' % s)
    byT2 = defaultdict(list)
    for s in deferred:
        for t in reach[s]: byT2[t].append(s)
    for t, ss in byT2.items():
        ss.sort(key=lambda s: (len(placed[s]), s))
        require(all(contains(placed[p], placed[q_]) for p, q_ in zip(ss, ss[1:])), 'target chain %d' % t)

    # ------------------------------------------------------------ E. one-child histogram
    z = Counter()
    for s in range(Rr):
        ds = chain_dims[s]
        for a, b in zip(ds[:-1], ds[1:-1]):
            if b > a: z[b - a] += 2 * v
        lastd = ds[-2]
        if s in role_root and kind[role_root[s]]: z[h - 1] += 2 * v           # copied centre transform
        z[h - lastd] += 2 * v                                                  # final growth to F
        z[m - h + ds[0]] += 2 * v                                              # exterior, gauged by sigma
    levels = defaultdict(set)
    for s in deferred:
        for t in reach[s]: levels[t].add(len(placed[s]))
    for t in range(v):
        ds = sorted(levels[t] | {0, h - 1})
        for a, b in zip(ds, ds[1:]): z[b - a] += 2 * v                       # target fronts
    z[h - 1] += 2 * N                                                          # data-wire fronts
    z[(h - 1) ** 2] += 2 * N                                                   # data macros
    z[1] += N                                                                  # endpoint copies
    z.pop(0, None)
    virtual_R = R
    for pair in reuse_pairs:
        e, f = pair['e'], pair['s']
        z[h - e] -= 2 * v
        z[m - h + f] -= 2 * v
        if f > e: z[f - e] += 2 * v
    require(all(count >= 0 for count in z.values()), 'reuse histogram subtraction')
    z = Counter({width: count for width, count in z.items() if count})
    physical_R = len(live)
    # Canonical inventory of actual physical source gauges. Recipients have
    # disappeared; every reused donor remains a separate zero-gauge slot.
    source_counts = Counter(sat_basis(placed.get(s, ())) for s in live)
    physical_auxiliary_source_frames = [dict(basis=list(F), count=count)
        for F, count in sorted(source_counts.items(), key=lambda item: (len(item[0]), item[0]))]
    require(sum(source_counts.values()) == physical_R, 'physical source inventory')
    require(all(not placed.get(a) for a in merge.values()), 'reused donor source gauge')
    W = 2 * N + 2 * v * physical_R; L = 2 * v * h * (h - 1); s_ = W * m - N + L
    require(sum(t * c for t, c in z.items()) == s_, 'complex rank mass')
    require(all(0 < t < m for t in z), 'children below m')
    out = dict(h=h, v=v, additions=c_add, roots=q, links=len(links), R=physical_R, virtual_R=virtual_R, reused_roles=len(reuse_pairs), m=m, N=N, W=W, L=L, total_rank=s_,
               deficit=N - L, maxchild=max(z), phase_one_ops=len(Anc), phase_one_roles=len(touched),
               physical_auxiliary_source_frames=physical_auxiliary_source_frames,
               generalized_lagrangian_frames=True, arbitrary_frame_stats=arbitrary_frame_stats,
               generalized_source_gauges=True, gauge_frame_stats=gauge_frame_stats,
               deferred_roles=len(deferred),
               deferred_dims=dict(sorted(Counter(len(X) for X in placed.values()).items())),
               lifted_additions=sum(1 for i,o in enumerate(ops) if o[0]=='add' and len(op_frames[i])>ranks[o[3]]),
               physical_gate_frame_changes=sum(op_frames[i]!=frame_U[o[3]] for i,o in enumerate(ops) if o[0]!='src'),
               replay=dict(seeds=[1, 2], scratch_restored=True, y_plus_x=True, field='Z/(2^61-1)',
                           physically_aliased=True, inverse_order='true source/workspace chronology',
                           omitted_compensation_rejected=True),
               reuse_rejected_controls=reuse_rejected_controls,
               child_multiplicities=dict(sorted(z.items())))
    (HERE / 'complex-profile.json').write_text(json.dumps(out, indent=1) + '\n')
    (HERE / 'reuse-pairs.json').write_text(json.dumps(reuse_pairs, indent=1) + '\n')
    print('PASS complex: R=%d, deferred roles %d, maxchild %d, rank mass %d' % (physical_R, len(deferred), max(z), s_))


if __name__ == '__main__':
    main()
