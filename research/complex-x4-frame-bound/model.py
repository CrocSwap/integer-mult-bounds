"""Complete frame-assignment model of a fixed native complex word (standard library only).

The frame contract is the one checked by research/gauge44-frames-x/independent/audit_local.py:

* every register has a fixed start frame and a fixed end frame;
* an A, B or tail gate has one frame, shared by its registers, and frames are monotone
  (nested) along every register's event sequence;
* centre registers equal their centre frame, and targets their target level, at the start of B;
* for every low-end helper q, every register k in q's inverse-row or dirt-column cone has its
  end-of-B frame inside q's end frame;
* each strict climb of dimension d along a register pays one child of rank d, and the eight
  centre descents are fixed.

The scalar program (gate list, order, registers, coefficients, cut, precondition, cleanup) is
fixed. Only the frames of A, B and early-cleanup (tail) gates vary. A climb into a centre or
target pin at the start of B is admitted and charged; the contract requires it to be zero, so
this only enlarges the feasible set.
"""
import gzip
import json
from collections import defaultdict
from fractions import Fraction as F

H = 9
FULL = tuple(1 << i for i in range(H - 1, -1, -1))


def basis(vs):
    piv = {}
    for a in vs:
        while a:
            bit = a.bit_length() - 1
            if bit in piv:
                a ^= piv[bit]
            else:
                piv[bit] = a
                break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1:
                piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def contained(a, b):
    return basis(list(a) + list(b)) == tuple(b)


def join(frames):
    return basis([x for f in frames for x in f])


def meet(a, b):
    """Zassenhaus intersection of two subspaces of F_2^H."""
    rows = [(u << H) | u for u in a] + [x << H for x in b]
    return basis([r for r in basis(rows) if r >> H == 0])


def interval(lo, hi):
    """Every subspace F with lo <= F <= hi, by closure over the quotient hi/lo."""
    assert contained(lo, hi), (lo, hi)
    comp, cur = [], list(lo)
    for x in hi:
        if len(basis(cur + [x])) > len(basis(cur)):
            comp.append(x)
            cur.append(x)
    k = len(comp)
    assert k <= 4, 'quotient dimension above 4 is not enumerated'
    vectors = list(range(1, 1 << k))
    out = []
    for mask in range(1 << len(vectors)):
        chosen = {vectors[i] for i in range(len(vectors)) if mask >> i & 1}
        if all((a ^ b) in chosen for a in chosen for b in chosen if a != b):
            lifted = []
            for a in chosen:
                x = 0
                for i in range(k):
                    if a >> i & 1:
                        x ^= comp[i]
                lifted.append(x)
            out.append(basis(list(lo) + lifted))
    assert len(set(out)) == len(out)
    return sorted(out, key=lambda f: (len(f), f))


def registers(e):
    return tuple(e[1:3]) if e[0] == 'add' else tuple(e[1:2])


def apply(e, rows, dual=False):
    if e[0] == 'add':
        t, s = e[1:3]
        q = F(e[3], e[4])
        if dual:
            t, s, q = s, t, -q
        dst = rows[t]
        for k, x in list(rows[s].items()):
            a = dst.get(k, F(0)) + q * x
            if a:
                dst[k] = a
            else:
                dst.pop(k, None)
    elif e[0] == 'scale':
        t = e[1]
        q = F(e[2], e[3])
        if dual:
            q = 1 / q
        rows[t] = {k: q * x for k, x in rows[t].items()}
    else:
        raise RuntimeError('unknown scalar primitive')


def invert(e):
    r = list(e)
    if r[0] == 'add':
        r[3] = -r[3]
    else:
        r[2], r[3] = r[3], r[2]
    return r


def cone_ceilings(w, n, v, low_ends):
    """End-of-B ceilings implied by the low-end cone conditions of audit_local.py."""
    ident = lambda: [{k: F(1)} for k in range(n)]
    main = w['A'] + w['cut'] + w['B']
    raw = ident()
    for e in main:
        apply(e, raw)
    dirt = [{} for _ in range(n)]
    for y in range(v, 2 * v):
        dirt[y] = {k: a for k, a in raw[y].items() if k >= 2 * v}
    for e in w['precondition']:
        apply(e, dirt)
    compensation = [['add', y, k, -a.numerator, a.denominator, []]
                    for y in range(v, 2 * v) for k, a in sorted(dirt[y].items())]
    prefix = w['precondition'] + compensation + main
    p, pinv = ident(), ident()
    for e in prefix:
        apply(e, p)
    for e in reversed(prefix):
        apply(invert(e), pinv)
    holders = defaultdict(set)
    for k in range(n):
        for j in p[k]:
            holders[j].add(k)
    ceil = {}
    for q, U in low_ends.items():
        for k in set(pinv[q]) | holders[q]:
            if k != q:
                ceil[k] = meet(ceil.get(k, FULL), U)
    return ceil


class Model:
    """Event graph, complete domains and components of a native complex word."""

    def __init__(self, w):
        rep = w['report']
        self.v, self.R = v, R = rep['v'], rep['R']
        assert rep['h'] == H
        self.n = n = 2 * v + R
        end = [FULL] * v + [basis([x for x in range(1, 1 << H) if (x & p).bit_count() % 2 == 0])
                             for p in w['ports']] + [FULL] * R
        low = {int(q): basis(U) for q, U in w.get('helper_final', {}).items()}
        for q, U in low.items():
            assert 2 * v <= q < n
            end[q] = U
        start = [(p,) for p in w['ports']] + [()] * (v + R)
        for q, U in w.get('start_extra', {}).items():
            assert 2 * v <= int(q) < n
            start[int(q)] = basis(U)
        early = w.get('early_cleanup', [])
        assert len({i for i, _ in early}) == len(early)
        tail = [w['cleanup'][i][:-1] + [U] for i, U in early]
        lev = {int(t): basis(U) for t, U in w.get('target_levels', {}).items()}
        pins = {q: basis(U) for q, U in zip(w['centers'], w['center_frames'])}
        assert len(pins) == 8
        for t in range(v):
            assert v + t not in pins
            pins[v + t] = lev.get(t, ())
        self.ceil = cone_ceilings(w, n, v, low)
        # centre descents: fixed children, recorded separately (audit_local.py rule)
        self.centre_children = []
        for q, U in zip(w['centers'], w['center_frames']):
            U = basis(U)
            served = {lev.get(e[1] - v, ()) for e in w['cut'] if e[2] == q}
            for T in sorted(served, key=lambda x: -len(x)):
                assert contained(T, U)
                if T != U:
                    self.centre_children.append(len(U) - len(T))
                U = T
        # nodes: ('S',q) start, ('G',i) gate, ('P',q) start-of-B pin, ('E',q) end
        gates = [('A', e) for e in w['A']] + [('B', e) for e in w['B']] + [('T', e) for e in tail]
        self.gates = gates
        self.given = [basis(e[-1]) for _, e in gates]
        self.regs = [registers(e) for _, e in gates]
        for rs in self.regs:
            assert len(set(rs)) == len(rs) and all(0 <= q < n for q in rs)
        nA, nB = len(w['A']), len(w['B'])
        self.nA, self.nB = nA, nB
        fixed = {}
        for q in range(n):
            fixed[('S', q)] = start[q]
            fixed[('E', q)] = end[q]
        for q, U in pins.items():
            fixed[('P', q)] = U
        chains = defaultdict(list)
        for q in range(n):
            chains[q].append(('S', q))
        boundary = {}   # register -> index in its chain of the last pre-tail node
        for i, rs in enumerate(self.regs):
            if i == nA:
                for q in pins:
                    chains[q].append(('P', q))
            if i == nA + nB:
                for q in range(n):
                    boundary[q] = len(chains[q]) - 1
            for q in rs:
                chains[q].append(('G', i))
        if len(gates) == nA:
            for q in pins:
                chains[q].append(('P', q))
        if len(gates) <= nA + nB:
            for q in range(n):
                boundary[q] = len(chains[q]) - 1
        for q in range(n):
            chains[q].append(('E', q))
        self.chains = chains
        self.fixed_frames = fixed
        # forward joins and backward meets
        order = [('S', q) for q in range(n)]
        for i in range(len(gates)):
            if i == nA:
                order += [('P', q) for q in pins]
            order.append(('G', i))
        if len(gates) == nA:
            order += [('P', q) for q in pins]
        order += [('E', q) for q in range(n)]
        position = {node: k for k, node in enumerate(order)}
        pred = defaultdict(list)
        succ = defaultdict(list)
        for q, ch in chains.items():
            for a, b in zip(ch, ch[1:]):
                assert position[a] < position[b]
                succ[a].append((q, b))
                pred[b].append((q, a))
        lo, hi = {}, {}
        for node in order:
            if node in fixed:
                lo[node] = fixed[node]
                for q, a in pred[node]:
                    assert contained(lo[a], fixed[node]), ('fixed frame below forward join', node)
            else:
                lo[node] = join(lo[a] for q, a in pred[node])
        ceil_at = defaultdict(list)    # node -> ceilings applying to that node
        for q, k in boundary.items():
            if q in self.ceil:
                ceil_at[chains[q][k]].append(self.ceil[q])
        for node in reversed(order):
            if node in fixed:
                hi[node] = fixed[node]
            else:
                U = FULL
                for q, b in succ[node]:
                    U = meet(U, hi[b])
                for C in ceil_at[node]:
                    U = meet(U, C)
                hi[node] = U
            assert contained(lo[node], hi[node]), ('empty domain', node)
        for node, Cs in ceil_at.items():
            if node in fixed:
                assert all(contained(fixed[node], C) for C in Cs), ('fixed frame above a cone ceiling', node)
        self.lo, self.hi = lo, hi
        self.domain = {}
        for i in range(len(gates)):
            node = ('G', i)
            if lo[node] != hi[node]:
                self.domain[node] = interval(lo[node], hi[node])
                assert self.given[i] in self.domain[node]
            else:
                assert self.given[i] == lo[node], ('given frame differs from forced frame', i)
        # edges, merged by endpoint pair, with integer multiplicity
        mult = defaultdict(int)
        for q, ch in chains.items():
            for a, b in zip(ch, ch[1:]):
                mult[(a, b)] += 1
        self.edges = dict(mult)

    def frame_of(self, node, assignment):
        if node in self.fixed_frames:
            return self.fixed_frames[node]
        if node in self.domain:
            return assignment[node]
        return self.lo[node]

    def baseline(self):
        return {('G', i): self.given[i] for i in range(len(self.gates)) if ('G', i) in self.domain}

    def profile(self, assignment):
        """Paid children of an assignment (graph climbs plus fixed centre descents)."""
        count = defaultdict(int)
        for (a, b), m in self.edges.items():
            A, B = self.frame_of(a, assignment), self.frame_of(b, assignment)
            if not contained(A, B):
                raise ValueError(('non-monotone', a, b))
            d = len(B) - len(A)
            if d:
                count[d] += m
        for d in self.centre_children:
            count[d] += 1
        return dict(sorted(count.items()))

    def components(self):
        parent = {node: node for node in self.domain}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for (a, b) in self.edges:
            if a in self.domain and b in self.domain:
                parent[find(a)] = find(b)
        groups = defaultdict(list)
        for node in self.domain:
            groups[find(node)].append(node)
        comps = [sorted(g, key=lambda x: x[1]) for g in groups.values()]
        return sorted(comps, key=lambda c: c[0][1])

    def component_problem(self, comp):
        """Unary and pairwise rank-count potentials of one component.

        Costs are integer vectors c[0..H]; c[d] counts children of rank d.
        Returns (labels, unary, pairs): unary[node][F] collects the edges from the node
        to fixed or forced neighbours, and pairs[(a,b)][(F,G)] the merged edges between
        two members (only nested pairs F <= G appear). Edges with no free endpoint
        belong to no component; fixed_profile() counts them.
        """
        members = set(comp)
        labels = {node: self.domain[node] for node in comp}
        zero = lambda: [0] * (H + 1)
        unary = {node: {Fr: zero() for Fr in labels[node]} for node in comp}
        pairs = {}
        for (a, b), m in self.edges.items():
            ina, inb = a in members, b in members
            if not (ina or inb):
                continue
            if ina and inb:
                table = {}
                for Fa in labels[a]:
                    for Fb in labels[b]:
                        if contained(Fa, Fb):
                            c = zero()
                            d = len(Fb) - len(Fa)
                            if d:
                                c[d] += m
                            table[(Fa, Fb)] = c
                pairs[(a, b)] = table
            elif ina:
                Fb = self.frame_of(b, None)
                for Fa in labels[a]:
                    assert contained(Fa, Fb)
                    d = len(Fb) - len(Fa)
                    if d:
                        unary[a][Fa][d] += m
            else:
                Fa = self.frame_of(a, None)
                for Fb in labels[b]:
                    assert contained(Fa, Fb)
                    d = len(Fb) - len(Fa)
                    if d:
                        unary[b][Fb][d] += m
        return labels, unary, pairs

    def fixed_profile(self):
        """Children on edges between two fixed or forced nodes, plus centre descents."""
        count = defaultdict(int)
        for (a, b), m in self.edges.items():
            if a in self.domain or b in self.domain:
                continue
            A, B = self.frame_of(a, None), self.frame_of(b, None)
            assert contained(A, B)
            d = len(B) - len(A)
            if d:
                count[d] += m
        for d in self.centre_children:
            count[d] += 1
        return count


def lp(labels, unary, pairs):
    """Local-polytope LP of one component: min c.z, A z = rhs, z >= 0.

    Rows: ('N', node) normalisation (rhs 1); ('M', a, b, side, frame) marginal of the
    merged edge (a, b) at endpoint side 0 (a) or 1 (b) (rhs 0).
    Columns: ('x', node, frame) and ('y', a, b, frame_a, frame_b) with F_a <= F_b.
    Every literal legal assignment gives a 0/1 feasible point.
    """
    rows = [('N', node) for node in sorted(labels)]
    for (a, b) in sorted(pairs):
        rows += [('M', a, b, 0, Fa) for Fa in labels[a]]
        rows += [('M', a, b, 1, Fb) for Fb in labels[b]]
    index = {r: i for i, r in enumerate(rows)}
    rhs = [1 if r[0] == 'N' else 0 for r in rows]
    touching = defaultdict(list)
    for (a, b) in sorted(pairs):
        touching[a].append((a, b, 0))
        touching[b].append((a, b, 1))
    cols = []
    for node in sorted(labels):
        for Fr in labels[node]:
            entries = [(index[('N', node)], 1)]
            entries += [(index[('M', a, b, side, Fr)], -1) for a, b, side in touching[node]]
            cols.append((('x', node, Fr), unary[node][Fr], entries))
    for (a, b) in sorted(pairs):
        for (Fa, Fb), c in sorted(pairs[(a, b)].items()):
            cols.append((('y', a, b, Fa, Fb), c,
                         [(index[('M', a, b, 0, Fa)], 1), (index[('M', a, b, 1, Fb)], 1)]))
    return rows, rhs, cols


def assignment_cost(labels, unary, pairs, assignment):
    c = [0] * (H + 1)
    for node in labels:
        for d, x in enumerate(unary[node][assignment[node]]):
            c[d] += x
    for (a, b), table in pairs.items():
        for d, x in enumerate(table[(assignment[a], assignment[b])]):
            c[d] += x
    return c


def load_word(raw_gz):
    return json.loads(gzip.decompress(raw_gz))
