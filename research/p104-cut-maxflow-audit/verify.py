#!/usr/bin/env python3
"""Independent max-flow audit of the frozen P104 rank-eight cut family.

The only mathematical input is the hash-pinned PR1972 frame-model witness.
No predecessor checker is imported, executed or adapted.  The method is a
time-expanded vertex-capacitated network, certified by weak duality (a
feasible integral flow and a separating vertex cut of equal size), plus a
union graph, a collapsed frame graph and an exact rational scalar replay.

Standard library only.  Prepared for Michael Yee with substantial Claude
(Anthropic) assistance.  Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from array import array
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WITNESS = 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
WITNESS_SHA256 = '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e'
RESULT = PACKAGE / 'RESULT.json'
STATUS = 'PASS_P104_CUT_MAXFLOW_AUDIT'
BITS = 9
INF = 1 << 30
FAMILIES = {'X': 104, 'Y': 104, 'G': 32, 'D': 32, 'Q': 8}
PRIVATE = 'C'
# Claims compared against this independent computation (author receipts, not inputs).
PR2090_CUT = 2429
PR2090_MINOR_PORTS = (0, 1, 2, 3, 7, 14, 22, 33)


class AuditError(Exception):
    """A source, legality or mathematical check failed."""


def require(condition, message):
    if not condition:
        raise AuditError(message)


# ---------------------------------------------------------------- GF(2) frames

def span_basis(vectors):
    """Unique fully reduced echelon basis of span(vectors) in GF(2)^9."""
    pivots = {}
    for v in vectors:
        require(type(v) is int and 0 <= v < 1 << BITS, f'bad frame vector {v!r}')
        for p, b in pivots.items():
            if v >> p & 1:
                v ^= b
        if v:
            p = v.bit_length() - 1
            for q in pivots:
                if pivots[q] >> p & 1:
                    pivots[q] ^= v
            pivots[p] = v
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def frame(vectors):
    require(isinstance(vectors, list), 'frame must be a list of vectors')
    return span_basis(vectors)


def contains(big, small):
    return span_basis(list(big) + list(small)) == big


# ---------------------------------------------------------------- source

def load_witness(path=None):
    path = Path(path) if path else ROOT / WITNESS
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == WITNESS_SHA256,
            'witness bytes differ from the PR1972 pin')
    return json.loads(data)


def family(name):
    return name.rstrip('0123456789')


def persistent_names():
    return [f'{f}{i}' for f, n in FAMILIES.items() for i in range(n)]


# ---------------------------------------------------------------- chronology

def chronology(w, drop_lifetimes=()):
    """Replay frames and liveness; private lifetimes become C#0..C#7.

    Returns a dict with the legality-checked layer structure.  A layer is a
    maximal run of cuts on which no frame or liveness changes.  Cut c is the
    state after events 0..c-1.  drop_lifetimes removes every event of the
    named private lifetimes (a semantic control, not a model change).
    """
    init, final, prog = w['initial_frames'], w['final_frames'], w['program']
    names = persistent_names()
    require(sorted(init) == sorted(names) and sorted(final) == sorted(names),
            'unexpected persistent register inventory')
    drop = set(drop_lifetimes)
    state = {n: frame(init[n]) for n in names}
    alias = {n: n for n in names}
    private_count = 0
    layers, layer_cuts = [dict(state)], [[0, None]]
    transports, events = [], Counter()
    frames_seen = set(state.values()) | {frame(final[n]) for n in names}
    kept = 0

    def lt(name):
        require(name in alias, f'register {name} is not live')
        return alias[name]

    def boundary(cut):
        layer_cuts[-1][1] = cut - 1
        layers.append(dict(state))
        layer_cuts.append([cut, None])

    for index, e in enumerate(prog):
        require(isinstance(e, list) and e, f'event {index} malformed')
        kind = e[0]
        if kind == 'zero':
            require(len(e) == 3 and e[1] == PRIVATE, f'event {index}: bad zero')
            require(PRIVATE not in alias, f'event {index}: private register already live')
            ident = f'{PRIVATE}#{private_count}'
            private_count += 1
            alias[PRIVATE] = ident
            if ident in drop:
                continue
            f = frame(e[2])
            frames_seen.add(f)
            state[ident] = f
        elif kind == 'erase':
            require(len(e) == 3 and e[1] == PRIVATE, f'event {index}: bad erase')
            ident = lt(PRIVATE)
            del alias[PRIVATE]
            if ident in drop:
                continue
            f = frame(e[2])
            frames_seen.add(f)
            require(state[ident] == f, f'event {index}: erase outside its chart')
            del state[ident]
        elif kind == 'transport':
            require(len(e) == 5, f'event {index}: bad transport')
            ident = lt(e[1])
            if ident in drop:
                continue
            a, b, rank = frame(e[2]), frame(e[3]), e[4]
            frames_seen.update((a, b))
            require(state[ident] == a, f'event {index}: transport source chart mismatch')
            require(contains(a, b) or contains(b, a), f'event {index}: transport not nested')
            require(type(rank) is int and rank == abs(len(a) - len(b)) > 0,
                    f'event {index}: transport rank mismatch')
            state[ident] = b
            transports.append({'event': index, 'lifetime': ident, 'from': a, 'to': b,
                               'rank': rank, 'up': len(b) > len(a)})
        elif kind in ('add', 'copy'):
            require(len(e) == (5 if kind == 'add' else 4), f'event {index}: bad {kind}')
            dst, src = lt(e[1]), lt(e[2])
            if dst in drop or src in drop:
                continue
            f = frame(e[-1])
            frames_seen.add(f)
            require(dst != src, f'event {index}: {kind} onto itself')
            require(state[dst] == f and state[src] == f,
                    f'event {index}: {kind} outside a common chart')
            if kind == 'add':
                require(Fraction(e[3]) != 0, f'event {index}: zero coefficient')
            events[kind] += 1
            kept += 1
            continue
        else:
            raise AuditError(f'event {index}: unknown kind {kind!r}')
        events[kind] += 1
        kept += 1
        boundary(index + 1)
    layer_cuts[-1][1] = len(prog)
    require(PRIVATE not in alias, 'private register live at the end')
    require(all(state[n] == frame(final[n]) for n in names), 'final frames differ')
    require(len(state) == len(names), 'unexpected live register at the end')
    return {'layers': layers, 'layer_cuts': [tuple(c) for c in layer_cuts],
            'transports': transports, 'events': events, 'kept_events': kept,
            'frames': frames_seen, 'private_lifetimes': private_count,
            'cuts': len(prog) + 1}


def layer_of_cut(chron, cut):
    for i, (a, b) in enumerate(chron['layer_cuts']):
        if a <= cut <= b:
            return i
    raise AuditError(f'cut {cut} outside the chronology')


# ---------------------------------------------------------------- flow network

class Network:
    """Forward-star residual network; arc a and a^1 are a forward/reverse pair."""

    def __init__(self):
        self.head = []
        self.to = array('i')
        self.cap = array('i')
        self.nxt = array('i')

    def node(self):
        self.head.append(-1)
        return len(self.head) - 1

    def arc(self, u, v, c):
        for tail, tip, cc in ((u, v, c), (v, u, 0)):
            self.to.append(tip)
            self.cap.append(cc)
            self.nxt.append(self.head[tail])
            self.head[tail] = len(self.to) - 1
        return len(self.to) - 2

    def reach(self, start, residual=True, blocked=()):
        """Nodes reachable from start using arcs of positive (residual) capacity."""
        blocked = set(blocked)
        seen = bytearray(len(self.head))
        seen[start] = 1
        dq = deque([start])
        head, to, cap, nxt = self.head, self.to, self.cap, self.nxt
        orig = self.orig if not residual else None
        while dq:
            u = dq.popleft()
            a = head[u]
            while a != -1:
                c = cap[a] if residual else orig[a]
                if c > 0 and a not in blocked:
                    v = to[a]
                    if not seen[v]:
                        seen[v] = 1
                        dq.append(v)
                a = nxt[a]
        return seen

    def coreach(self, target, residual=True):
        """Nodes with a positive-(residual) capacity path to target."""
        seen = bytearray(len(self.head))
        seen[target] = 1
        dq = deque([target])
        head, to, nxt = self.head, self.to, self.nxt
        cap = self.cap if residual else self.orig
        while dq:
            v = dq.popleft()
            b = head[v]
            while b != -1:
                u = to[b]
                if cap[b ^ 1] > 0 and not seen[u]:
                    seen[u] = 1
                    dq.append(u)
                b = nxt[b]
        return seen

    def augment(self, s, t):
        head, to, cap, nxt = self.head, self.to, self.cap, self.nxt
        parent = array('i', [-1]) * len(head)
        parent[s] = -2
        dq = deque([s])
        while dq and parent[t] == -1:
            u = dq.popleft()
            a = head[u]
            while a != -1:
                if cap[a] > 0:
                    v = to[a]
                    if parent[v] == -1:
                        parent[v] = a
                        dq.append(v)
                a = nxt[a]
        if parent[t] == -1:
            return 0
        bottleneck, v = INF, t
        while v != s:
            a = parent[v]
            bottleneck = min(bottleneck, cap[a])
            v = to[a ^ 1]
        v = t
        while v != s:
            a = parent[v]
            cap[a] -= bottleneck
            cap[a ^ 1] += bottleneck
            v = to[a ^ 1]
        return bottleneck

    def max_flow(self, s, t, limit=None):
        self.orig = array('i', self.cap)
        total = 0
        while limit is None or total < limit:
            pushed = self.augment(s, t)
            if not pushed:
                break
            total += pushed
        return total


def time_network(chron, contacts=(), nested_layers=()):
    """Frozen-chronology network with saturated equal-frame mixing.

    Node (r, l) is register lifetime r during layer l (capacity one array).
    Within a layer every equal-frame class mixes arbitrarily: a hub joins
    each member's out-node to each member's in-node in the next layer.  A
    final virtual layer lets each class also mix into the Y outputs after
    the last event.  contacts: extra (layer, r1, r2) cross-class contacts
    (bypass control).  nested_layers: layers where nested (not just equal)
    charts may mix (premise control).
    """
    layers = chron['layers']
    net = Network()
    s, t = net.node(), net.node()
    unit = {}
    hubs = []
    for li, live in enumerate(layers):
        classes = defaultdict(list)
        for r, f in live.items():
            classes[f].append(r)
        hub = {f: net.node() for f in classes}
        hubs.append((hub, classes))
        for r, f in live.items():
            vin, vout = net.node(), net.node()
            unit[(li, r)] = (vin, vout, net.arc(vin, vout, 1))
            net.arc(vout, hub[f], INF)
        if li:
            prev_hub, prev_classes = hubs[li - 1]
            for f, members in prev_classes.items():
                for r in members:
                    if r in live:
                        net.arc(prev_hub[f], unit[(li, r)][0], INF)
    for li, r1, r2 in contacts:
        hub, _ = hubs[li]
        f1, f2 = layers[li][r1], layers[li][r2]
        net.arc(unit[(li, r1)][1], hub[f2], INF)
        net.arc(unit[(li, r2)][1], hub[f1], INF)
    for li in nested_layers:
        hub, classes = hubs[li]
        fs = list(classes)
        for i, a in enumerate(fs):
            for b in fs[i + 1:]:
                if contains(a, b) or contains(b, a):
                    net.arc(hub[a], hub[b], INF)
                    net.arc(hub[b], hub[a], INF)
    last = len(layers) - 1
    for r in layers[0]:
        if family(r) == 'X':
            net.arc(s, unit[(0, r)][0], INF)
    final_hub, _ = hubs[last]
    for r, f in layers[last].items():
        if family(r) == 'Y':
            vin, vout = net.node(), net.node()
            unit[(last + 1, r)] = (vin, vout, net.arc(vin, vout, 1))
            net.arc(final_hub[f], vin, INF)
            net.arc(vout, t, INF)
    return net, s, t, unit


def certify_flow(net, s, t, unit):
    """Weak-duality certificate: feasible flow value == separating cut size."""
    flow = [net.orig[a] - net.cap[a] for a in range(0, len(net.to), 2)]
    excess = defaultdict(int)
    for k, f in enumerate(flow):
        a = 2 * k
        require(0 <= f <= net.orig[a], 'flow violates a capacity')
        if f:
            excess[net.to[a ^ 1]] -= f
            excess[net.to[a]] += f
    value = excess[t]
    require(value == -excess[s], 'flow value mismatch at the terminals')
    require(all(x == 0 for v, x in excess.items() if v not in (s, t)), 'flow not conserved')
    side = net.reach(s, residual=True)
    require(not side[t], 'residual path remains: flow is not maximum')
    near_t = net.coreach(t)
    cuts = []
    for inside, outside in ((side, None), (None, near_t)):
        if outside is None:
            cut = sorted(k for k, (vin, vout, a) in unit.items() if inside[vin] and not inside[vout])
        else:
            cut = sorted(k for k, (vin, vout, a) in unit.items() if outside[vout] and not outside[vin])
        require(len(cut) == value, 'cut size differs from flow value')
        blocked = {unit[key][2] for key in cut}
        require(not net.reach(s, residual=False, blocked=blocked)[t], 'cut does not separate')
        cuts.append(cut)
    return value, cuts[0], cuts[1], flow


def flow_paths(net, s, t, unit, flow):
    """Decompose the integral flow into source-to-target register itineraries."""
    owner = {}
    for (li, r), (vin, vout, a) in unit.items():
        owner[vin] = owner[vout] = (li, r)
    left = {2 * k: f for k, f in enumerate(flow) if f}
    out = defaultdict(list)
    for a in left:
        out[net.to[a ^ 1]].append(a)
    paths = []
    while True:
        u, path = s, []
        while u != t:
            arcs = [a for a in out[u] if left[a]]
            if not arcs:
                break
            a = arcs[0]
            left[a] -= 1
            u = net.to[a]
            if u in owner and (not path or path[-1] != owner[u]):
                path.append(owner[u])
        if u != t:
            break
        paths.append(path)
    return paths


# ---------------------------------------------------------------- static graphs

def intervals(chron, w):
    """Frame-path intervals per lifetime and the transports between them."""
    init = w['initial_frames']
    path = {n: [frame(init[n])] for n in persistent_names()}
    edges = []
    for k in range(chron['private_lifetimes']):
        path[f'{PRIVATE}#{k}'] = []
    zero_frames = [frame(e[2]) for e in w['program'] if e[0] == 'zero']
    for k, f in enumerate(zero_frames):
        path[f'{PRIVATE}#{k}'].append(f)
    for tr in chron['transports']:
        p = path[tr['lifetime']]
        require(p[-1] == tr['from'], 'interval chain broken')
        edges.append(((tr['lifetime'], len(p) - 1), (tr['lifetime'], len(p)), tr))
        p.append(tr['to'])
    return path, edges


def union_reach(path, edges, skip=()):
    """BFS in the union of all equal-frame contacts (time ignored)."""
    by_frame = defaultdict(list)
    for r, fs in path.items():
        for k, f in enumerate(fs):
            by_frame[f].append((r, k))
    nxt = defaultdict(list)
    for a, b, tr in edges:
        if tr['event'] not in skip:
            nxt[a].append(b)
    seen, used = set(), set()
    dq = deque((r, 0) for r in path if family(r) == 'X')
    seen.update(dq)
    while dq:
        u = dq.popleft()
        f = path[u[0]][u[1]]
        step = list(nxt[u])
        if f not in used:
            used.add(f)
            step += by_frame[f]
        for v in step:
            if v not in seen:
                seen.add(v)
                dq.append(v)
    return {r for r, fs in path.items() if family(r) == 'Y' and (r, len(fs) - 1) in seen}


def frame_partition(chron, w, skip):
    """Collapse every occurrence of a frame; reachability on transport arcs."""
    fwd, bwd = defaultdict(set), defaultdict(set)
    for tr in chron['transports']:
        if tr['event'] not in skip:
            fwd[tr['from']].add(tr['to'])
            bwd[tr['to']].add(tr['from'])

    def closure(start, arcs):
        seen, dq = set(start), deque(start)
        while dq:
            for v in arcs[dq.popleft()]:
                if v not in seen:
                    seen.add(v)
                    dq.append(v)
        return seen

    xs = {frame(w['initial_frames'][n]) for n in persistent_names() if family(n) == 'X'}
    ys = {frame(w['final_frames'][n]) for n in persistent_names() if family(n) == 'Y'}
    return closure(xs, fwd), closure(ys, bwd)


# ---------------------------------------------------------------- exact scalars

def scalar_replay(w):
    names = persistent_names()
    col = {n: i for i, n in enumerate(names)}
    rows = {n: {col[n]: Fraction(1)} for n in names}
    discarded_nonzero = 0
    for e in w['program']:
        kind = e[0]
        if kind == 'add':
            c = Fraction(e[3])
            dst, src = rows[e[1]], rows[e[2]]
            for k, v in list(src.items()):
                nv = dst.get(k, 0) + c * v
                if nv:
                    dst[k] = nv
                else:
                    dst.pop(k, None)
        elif kind == 'copy':
            require(not rows[e[1]], 'copy into a nonzero private register')
            rows[e[1]] = dict(rows[e[2]])
        elif kind == 'zero':
            rows[PRIVATE] = {}
        elif kind == 'erase':
            discarded_nonzero += bool(rows.pop(PRIVATE))
    for n in names:
        if family(n) != 'Y':
            require(rows[n] == {col[n]: 1}, f'{n} is not restored')
    xs = [n for n in names if family(n) == 'X']
    ys = [n for n in names if family(n) == 'Y']
    xcols = {col[n] for n in xs}
    m = []
    for y in ys:
        row = dict(rows[y])
        require(row.pop(col[y], 0) == 1, f'{y} lost its own input')
        require(set(row) <= xcols, f'{y} depends on a non-source input')
        m.append([row.get(col[x], Fraction(0)) for x in xs])
    return m, discarded_nonzero


def rank(mat):
    a = [list(r) for r in mat]
    r = 0
    for c in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        for i in range(r + 1, len(a)):
            if a[i][c]:
                f = a[i][c] / a[r][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[r])]
        r += 1
    return r


def det(mat):
    a = [list(r) for r in mat]
    n, d = len(a), Fraction(1)
    for c in range(n):
        p = next((i for i in range(c, n) if a[i][c]), None)
        if p is None:
            return Fraction(0)
        if p != c:
            a[c], a[p] = a[p], a[c]
            d = -d
        d *= a[c][c]
        for i in range(c + 1, n):
            f = a[i][c] / a[c][c]
            a[i] = [x - f * y for x, y in zip(a[i], a[c])]
    return d


def matmul(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(r, c) if x and y) for c in bt] for r in a]


def scalar_facts(m):
    n = len(m)
    eye = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    sq = matmul(m, m)
    resid = [[eye[i][j] - m[i][j] for j in range(n)] for i in range(n)]
    inv = [[eye[i][j] - m[i][j] / 12 for j in range(n)] for i in range(n)]
    minor = [[m[i][j] for j in PR2090_MINOR_PORTS] for i in PR2090_MINOR_PORTS]
    return {
        'block_rank': rank(m),
        'symmetric': all(m[i][j] == m[j][i] for i in range(n) for j in range(n)),
        'unit_diagonal': all(m[i][i] == 1 for i in range(n)),
        'square_is_13_block': sq == [[13 * x for x in r] for r in m],
        'residual_inverse_is_I_minus_block_over_12': matmul(resid, inv) == eye,
        'nonzero_offdiagonal_per_row': sorted({sum(1 for j in range(n) if j != i and m[i][j])
                                               for i in range(n)}),
        'pr2090_minor_det': str(det(minor)),
    }


# ---------------------------------------------------------------- audit

def name_cut(chron, cut):
    out = []
    for li, r in cut:
        if li == len(chron['layers']):
            a = b = chron['cuts'] - 1  # virtual post-mixing output layer
        else:
            a, b = chron['layer_cuts'][li]
        out.append({'register': r, 'layer': li, 'cuts': [a, b]})
    return out


def budget_line(w, profile):
    """Source-bound constants of the shared conditional budget line.

    The coverage contract (s=N=9, m=73, W=832, one unpaid coordinate per
    live family, unchanged idle requirement) is inherited from PR2082/2083
    and is NOT verified here; only its constants are re-derived from the
    witness instead of being copied from PR bodies.
    """
    init, final = w['initial_frames'], w['final_frames']
    boundary = sum(abs(len(frame(final[n])) - len(frame(init[n]))) for n in persistent_names())
    mass = sum(k * v for k, v in profile.items())
    copy = mass - boundary
    s, m, width = 9, 73, 832
    idle = (m - 1) * width - s * boundary
    capacity = m * width

    def moment(extra):
        return Fraction(s * (mass + extra) + idle, capacity)

    return {
        'contract': 'conditional paired-chain coverage, s=N=9, m=73, W=832 (inherited, unverified)',
        'boundary_coverage_from_frames': boundary,
        'private_descent_mass': copy,
        'idle_coverage': idle,
        'zero_saving_moment': {str(k): str(moment(k)) for k in (0, 96, 104, 208)},
        'slack_rank_per_call': str(Fraction(capacity - s * mass - idle, s)),
    }


def audit(w):
    chron = chronology(w)
    tr = chron['transports']
    profile = Counter(x['rank'] for x in tr)
    down = [x for x in tr if not x['up']]
    receipt = {
        'status': STATUS,
        'source': {'path': WITNESS, 'sha256': WITNESS_SHA256, 'pr': 1972,
                   'head': 'fd82d172f46933fd253c2c6de4bd5eaff5429cfd'},
        'counts': {
            'events': len(w['program']),
            'cuts': chron['cuts'],
            'event_kinds': dict(sorted(chron['events'].items())),
            'distinct_frames': len(chron['frames']),
            'layers': len(chron['layers']),
            'private_lifetimes': chron['private_lifetimes'],
            'transport_profile': {str(k): profile[k] for k in sorted(profile)},
            'rank_mass': sum(k * v for k, v in profile.items()),
            'upward_transports': len(tr) - len(down),
            'downward_transports': len(down),
        },
    }
    require(all(x['lifetime'].startswith(PRIVATE + '#') and x['rank'] == 7 for x in down),
            'a downward transport is not a private rank-seven descent')
    descents = [x['event'] for x in down]
    xs = [frame(w['initial_frames'][n]) for n in persistent_names() if family(n) == 'X']
    ys = [frame(w['final_frames'][n]) for n in persistent_names() if family(n) == 'Y']
    first_d = min(x['event'] for x in tr if family(x['lifetime']) == 'D')
    receipt['premises'] = {
        'distinct_source_lines': len(set(xs)) == 104 and all(len(f) == 1 for f in xs),
        'distinct_target_hyperplanes': len(set(ys)) == 104 and all(len(f) == 8 for f in ys),
        'first_D_transport_event': first_d,
    }
    require(receipt['premises']['distinct_source_lines'] and
            receipt['premises']['distinct_target_hyperplanes'], 'endpoint frames not distinct')

    # Common-frame contact multiplicities, for comparison with author receipts.
    per_cut = 0
    for (a, b), live in zip(chron['layer_cuts'], chron['layers']):
        sizes = Counter(live.values()).values()
        per_cut += (b - a + 1) * sum(k * (k - 1) for k in sizes)
    path, edges = intervals(chron, w)
    occ = Counter(f for fs in path.values() for f in fs)
    same = sum(k * (k - 1) for fs in path.values() for k in Counter(fs).values())
    receipt['counts'].update({
        'intervals': sum(len(fs) for fs in path.values()),
        'ordered_equal_frame_pairs_over_all_cuts': per_cut,
        'ordered_equal_frame_interval_pairs_cross_register':
            sum(k * (k - 1) for k in occ.values()) - same,
    })

    # 1. Frozen chronology: max-flow / min vertex cut.
    net, s, t, unit = time_network(chron)
    value = net.max_flow(s, t)
    value2, cut, cut_t, flow = certify_flow(net, s, t, unit)
    require(value == value2, 'flow bookkeeping mismatch')
    paths = flow_paths(net, s, t, unit, flow)
    require(len(paths) == value, 'path decomposition incomplete')
    crossings = sorted({k for p in paths for k in p if k in set(cut)})
    li2090 = layer_of_cut(chron, PR2090_CUT)
    live2090 = chron['layers'][li2090]
    queries = sorted((li2090, r) for r in live2090 if family(r) == 'Q')
    require(len(queries) == 8, 'expected eight live queries at the PR2090 cut')
    blocked = {unit[k][2] for k in queries}
    sep2090 = not net.reach(s, residual=False, blocked=blocked)[t]
    reopen = []
    for k in queries:
        reopen.append(bool(net.reach(s, residual=False, blocked=blocked - {unit[k][2]})[t]))
    ev = w['program'][PR2090_CUT]
    # Cones at the PR2090 cut: values entering the layer after event 2429.
    nxt_layer = li2090 + 1
    require(chron['layer_cuts'][nxt_layer][0] == PR2090_CUT + 1, 'PR2090 cut is not a layer end')
    fwd, bwd = net.reach(s, residual=False), net.coreach(t, residual=False)
    after = chron['layers'][nxt_layer]
    cone_f = sorted(r for r in after if fwd[unit[(nxt_layer, r)][0]])
    cone_b = sorted(r for r in after if bwd[unit[(nxt_layer, r)][0]])
    meet = sorted(set(cone_f) & set(cone_b))
    receipt['frozen_chronology'] = {
        'model': 'retained transports and lifetimes; every equal-frame class mixes arbitrarily at every cut',
        'max_flow_arrays': value,
        'min_vertex_cut_source_side': name_cut(chron, cut),
        'min_vertex_cut_target_side': name_cut(chron, cut_t),
        'paths': [{'source': p[0][1], 'target': p[-1][1], 'nodes': len(p)} for p in paths],
        'pr2090_cut': {
            'cut': PR2090_CUT, 'layer': li2090, 'next_event': ev[:2],
            'queries_separate': sep2090,
            'each_single_query_restored_reopens': reopen,
            'forward_cone_families': dict(sorted(Counter(map(family, cone_f)).items())),
            'backward_cone_families': dict(sorted(Counter(map(family, cone_b)).items())),
            'cone_intersection': meet,
        },
    }
    require(value == 8 and sep2090 and all(reopen), 'frozen-chronology cut differs from eight')
    require(meet == sorted(r for _, r in queries), 'PR2090 cones do not meet exactly in the queries')

    # 2. Union of all interleavings of the fixed frame paths (PR2113 model).
    union = {
        'intact_targets_reached': len(union_reach(path, edges)),
        'targets_reached_without_descents': len(union_reach(path, edges, set(descents))),
        'targets_reopened_by_each_descent': [
            len(union_reach(path, edges, set(descents) - {d})) for d in descents],
    }
    receipt['union_graph'] = union
    require(union['intact_targets_reached'] == 104 and union['targets_reached_without_descents'] == 0,
            'union-graph separation fails')

    # 3. Collapsed frame graph (PR2127 model).
    fx, fy = frame_partition(chron, w, set(descents))
    receipt['frame_graph'] = {
        'source_reachable_frames': len(fx), 'target_coreachable_frames': len(fy),
        'overlap': len(fx & fy), 'covers_all_frames': (fx | fy) == chron['frames'],
    }
    require(not fx & fy, 'frame partition overlaps')

    # 4. Exact rational replay: attainment and residual rank.
    m, nonzero_discards = scalar_replay(w)
    facts = scalar_facts(m)
    facts['nonzero_private_discards'] = nonzero_discards
    receipt['scalar_replay'] = facts
    require(facts['block_rank'] == value, 'replayed block rank differs from the cut')
    require(facts['symmetric'] and facts['unit_diagonal'] and facts['square_is_13_block'],
            'replayed block is not the expected G/2 shape')
    require(facts['residual_inverse_is_I_minus_block_over_12'], 'residual is not invertible')
    receipt['budget_line'] = budget_line(w, profile)

    # 5. Controls: each must change the answer in the stated direction.
    controls = {}
    li0 = 0
    x0 = next(r for r in chron['layers'][li0] if family(r) == 'X')
    y0 = next(r for r in chron['layers'][li0] if family(r) == 'Y')
    net_c, s_c, t_c, _ = time_network(chron, contacts=[(li0, x0, y0)])
    controls['one_cross_frame_contact_flow'] = net_c.max_flow(s_c, t_c, limit=value + 1)
    net_c, s_c, t_c, _ = time_network(chron, nested_layers=[li2090])
    controls['nested_chart_mixing_at_pr2090_cut_flow'] = net_c.max_flow(s_c, t_c, limit=value + 1)
    one_less = chronology(w, drop_lifetimes=[f'{PRIVATE}#0'])
    net_c, s_c, t_c, _ = time_network(one_less)
    controls['drop_private_lifetime_0_flow'] = net_c.max_flow(s_c, t_c)
    receipt['controls'] = controls
    require(controls['one_cross_frame_contact_flow'] == value + 1, 'bypass control did not open')
    require(controls['nested_chart_mixing_at_pr2090_cut_flow'] == value + 1,
            'nested-chart control did not open')
    require(controls['drop_private_lifetime_0_flow'] == value - 1, 'lifetime control did not close')
    receipt['crossing_nodes_on_paths'] = len(crossings)
    return receipt


def engine_fixtures():
    """Known small vertex-disjoint path counts; the flow code must agree."""
    cases = [((0, 1), (1, 2)), ((0, 1), (0, 2), (1, 3), (2, 3)),
             ((0, 1), (0, 2), (1, 3), (2, 3), (1, 2))]
    expected = [1, 2, 2]
    for edges, want in zip(cases, expected):
        net = Network()
        s, t = net.node(), net.node()
        nodes = {}
        for v in {v for e in edges for v in e}:
            vin, vout = net.node(), net.node()
            net.arc(vin, vout, 1 if v not in (0, 3) else INF)
            nodes[v] = (vin, vout)
        for a, b in edges:
            net.arc(nodes[a][1], nodes[b][0], INF)
        last = max(nodes)
        net.arc(s, nodes[0][0], INF)
        net.arc(nodes[last][1], t, INF)
        got = net.max_flow(s, t)
        require(got == want, f'flow fixture {edges}: {got} != {want}')


def canonical(obj):
    return json.dumps(obj, indent=1, sort_keys=True) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--witness', type=Path, help='alternate copy of the pinned witness')
    ap.add_argument('--write', type=Path, help='write the receipt to a new file')
    ap.add_argument('--result', type=Path, default=RESULT, help='stored receipt to compare')
    ap.add_argument('--premise-sensitivity', type=int, nargs='*', metavar='CUT',
                    help='uncapped max-flow when nested (not only equal) charts may mix at '
                         'one cut; checks the value 104 and prints it (default cut 2429)')
    args = ap.parse_args(argv)
    if args.premise_sensitivity is not None:
        chron = chronology(load_witness(args.witness))
        for cut in args.premise_sensitivity or [PR2090_CUT]:
            li = layer_of_cut(chron, cut)
            net, s, t, _ = time_network(chron, nested_layers=[li])
            value = net.max_flow(s, t)
            require(value == 104, f'nested-chart relaxation at cut {cut} gives {value}, not 104')
            print(f'PASS_P104_NESTED_CHART_RELAXATION cut={cut} layer={li} max_flow={value}')
        return 0
    engine_fixtures()
    receipt = audit(load_witness(args.witness))
    text = canonical(receipt)
    if args.write:
        require(not args.write.exists(), f'refusing to overwrite {args.write}')
        args.write.write_text(text, encoding='utf-8', newline='\n')
    else:
        require(args.result.is_file(), 'missing stored receipt; regenerate with --write to a new path')
        require(args.result.read_text(encoding='utf-8') == text, 'stored receipt differs from this replay')
    print(f"{STATUS} max_flow={receipt['frozen_chronology']['max_flow_arrays']} "
          f"rank={receipt['scalar_replay']['block_rank']} "
          f"frames={receipt['counts']['distinct_frames']} "
          f"union_reopen={sorted(set(receipt['union_graph']['targets_reopened_by_each_descent']))} "
          f"partition={receipt['frame_graph']['source_reachable_frames']}/"
          f"{receipt['frame_graph']['target_coreachable_frames']}")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except AuditError as exc:
        print(f'FAIL {exc}', file=sys.stderr)
        sys.exit(1)
