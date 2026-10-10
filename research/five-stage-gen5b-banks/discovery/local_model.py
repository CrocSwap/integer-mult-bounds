"""Per-cube local-channel model: exact replica of the generator's compile_word arc feasibility restricted to one cube.
Nodes: sources (8), additions created by a node list in creation order. Each addition = unordered pair of existing nodes
with disjoint supports. Plane nodes get preann PA[plane] (from a full compile); inner nodes inherit joins of successors.
"""
import sys, pickle
from itertools import combinations, product
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
P = (1 << 127) - 1

def rref(rows, h):
    piv = {}
    for r in rows:
        x = [a % P for a in r]
        for c, y in piv.items():
            if x[c]:
                f = x[c]; x = [(a - f * b) % P for a, b in zip(x, y)]
        nz = next((j for j in range(h) if x[j]), None)
        if nz is None: continue
        inv = pow(x[nz], P - 2, P); x = [(a * inv) % P for a in x]
        for c in list(piv):
            y = piv[c]
            if y[nz]:
                f = y[nz]; piv[c] = [(a - f * b) % P for a, b in zip(y, x)]
        piv[nz] = x
    return tuple(tuple(piv[c]) for c in sorted(piv))

class Table:
    def __init__(self, h):
        self.h = h; self.rows = [()]; self.index = {(): 0}; self.jc = {}
    def intern(self, rows):
        S = rref(rows, self.h); i = self.index.get(S)
        if i is None:
            i = len(self.rows); self.rows.append(S); self.index[S] = i
        return i
    def dim(self, i): return len(self.rows[i])
    def join(self, i, j):
        if i == j or j == 0: return i
        if i == 0: return j
        if i > j: i, j = j, i
        k = self.jc.get((i, j))
        if k is None:
            A, B = self.rows[i], self.rows[j]
            k = i if len(A) == self.h else j if len(B) == self.h else self.intern(A + B); self.jc[(i, j)] = k
        return k
    def join_many(self, ids):
        k = 0
        for i in ids: k = self.join(k, i)
        return k
    def contained(self, i, j): return self.join(i, j) == j

ALLB = list(product(range(2), repeat=3))
PLANES = [('A', i, a) for i in range(3) for a in range(2)] + [('G', j, k, m) for j, k in combinations(range(3), 2) for m in range(2)]
def members(key):
    if key[0] == 'A': return frozenset(b for b in ALLB if b[key[1]] == key[2])
    return frozenset(b for b in ALLB if b[key[1]] ^ b[key[2]] == key[3])
MEMBERS = {k: members(k) for k in PLANES}
PLANE_OF = {}  # frozenset of 4 -> key
for k, m in MEMBERS.items(): PLANE_OF[m] = k

class Cube:
    def __init__(self, cd, h, labels):
        self.h = h; self.T = Table(h)
        self.I = cd['I']; self.sources = cd['sources']  # b -> global source id
        self.src_label = {b: labels[cd['sources'][b]] for b in ALLB}
        self.coord = [self.T.intern([[1 if k == j else 0 for k in range(h)]]) for j in range(h)]
        self.PA = {k: self.T.intern(list(v['preann_rows'])) for k, v in cd['planes'].items()}
        self.partner = {}  # source b -> rann id of the partner root reading it
        inv = {v: b for b, v in cd['sources'].items()}
        for node, v in cd['partner'].items():
            self.partner[inv[node]] = self.T.intern(list(v['rows']))
        assert len(self.partner) == 8
        self.cover_cache = {}
    def cover_pad(self, sup):  # join of coordinate vectors not covered by the labels of sup (frozenset of b)
        if sup not in self.cover_cache:
            cov = set()
            for b in sup: cov.update(self.src_label[b])
            self.cover_cache[sup] = self.T.join_many(self.coord[j] for j in range(self.h) if j not in cov)
        return self.cover_cache[sup]

    def evaluate(self, nodes, want=False):
        """nodes: list of (a, b) in creation order where a, b are node refs: a 3-bit tuple (source) or an int index
        into `nodes` (earlier addition). Interning by unordered pair is applied (duplicates collapse). Every plane must
        appear exactly once (support = plane members). Returns (adds, arcs, debt[, details])."""
        h = self.h
        sup = []; args = []; intern = {}; keyof = {}  # addition index -> support
        remap = {}
        def ref(r):
            return ('s', r) if isinstance(r, tuple) else ('n', remap[r])
        def supof(r):
            return frozenset([r[1]]) if r[0] == 's' else sup[r[1]]
        for idx, (a, b) in enumerate(nodes):
            ra, rb = ref(a), ref(b)
            if ra > rb: ra, rb = rb, ra
            if (ra, rb) in intern:
                remap[idx] = intern[ra, rb]; continue
            sa, sb = supof(ra), supof(rb)
            assert not (sa & sb), 'support-disjoint'
            intern[ra, rb] = len(args); remap[idx] = len(args)
            args.append((ra, rb)); sup.append(sa | sb)
        n = len(args)
        planes_at = {}
        for x in range(n):
            if sup[x] in PLANE_OF:
                assert sup[x] not in planes_at.values() or True
                k = PLANE_OF[sup[x]]; assert k not in planes_at, 'plane twice'; planes_at[k] = x
        assert len(planes_at) == 12, 'all planes'
        # users
        users = defaultdict(list)  # ref -> list of (x, j)
        for x in range(n):
            for j, r in enumerate(args[x]): users[r].append((x, j))
        # every addition must be used (plane or operand)
        for x in range(n):
            assert users[('n', x)] or sup[x] in PLANE_OF, 'unused node %d' % x
        preann = [0] * n
        for x in range(n - 1, -1, -1):
            ids = [preann[y] for y, j in users[('n', x)]]
            if sup[x] in PLANE_OF: ids.append(self.PA[PLANE_OF[sup[x]]])
            preann[x] = self.T.join_many(ids)
        initial = [self.T.join(preann[x], self.cover_pad(sup[x])) for x in range(n)]
        order = sorted(range(n), key=lambda x: (h - self.T.dim(initial[x]), x))
        pos = {x: i for i, x in enumerate(order)}
        # uses: list of (value ref, target, useann); target = ('op', x) or ('root', b)
        uses = []
        for x in order:
            for j, r in enumerate(args[x]): uses.append((r, ('op', x), initial[x]))
        for b in ALLB: uses.append((('s', b), ('root', b), self.partner[b]))
        # feasible arcs
        adj = defaultdict(list)
        for x in range(n):
            for r in args[x]:
                for u, (val, t, ann) in enumerate(uses):
                    if val != r or t == ('op', x): continue
                    if t[0] == 'op' and pos[t[1]] <= pos[x]: continue
                    if self.T.contained(ann, initial[x]): adj[x].append(u)
        # max matching (simple augmenting paths)
        mR = {}; mL = {}
        def try_(x, seen):
            for u in adj[x]:
                if u in seen: continue
                seen.add(u)
                if u not in mR or try_(mR[u], seen):
                    mR[u] = x; mL[x] = u; return True
            return False
        for x in range(n): try_(x, set())
        arcs = len(mL)
        if not want: return n, arcs, n - arcs
        det = dict(args=args, sup=sup, initial=initial, preann=preann, order=order, uses=uses, adj=dict(adj), match=mL,
                   planes_at=planes_at)
        return n, arcs, n - arcs, det

def design_to_nodes(design):
    """generator's design list -> node list in creation order (same as BitGraph.local_design)."""
    nodes = []
    def build(t):
        if isinstance(t[0], int): return tuple(t)
        a = build(t[0]); b = build(t[1]); nodes.append((a, b)); return len(nodes) - 1
    for key, tree in design: build(tree)
    return nodes

def load_cubes(path):
    d = pickle.load(open(path, 'rb'))
    return [Cube(cd, d['h'], d['labels']) for cd in d['cube_data']]

if __name__ == '__main__':
    import json
    cubes = load_cubes(sys.argv[1])
    design = json.loads(Path(sys.argv[2]).read_text())['design']
    nodes = design_to_nodes(design)
    res = [c.evaluate(nodes) for c in cubes]
    from collections import Counter
    print(Counter(res))
    n, arcs, debt, det = cubes[0].evaluate(nodes, want=True)
    T = cubes[0].T
    for x in det['order']:
        a, b = det['args'][x]
        print(x, sorted(''.join(map(str, s)) for s in det['sup'][x]), 'codim', 24 - T.dim(det['initial'][x]), 'preann', T.dim(det['preann'][x]),
              'arc->', (det['uses'][det['match'][x]][1], det['uses'][det['match'][x]][0]) if x in det['match'] else None, 'feasible', len(det['adj'].get(x, [])))
