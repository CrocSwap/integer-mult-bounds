"""Build exact contact components, subspace bounds and rank invoices.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict, deque


def span(basis):
    out = {0}
    for x in basis:
        out |= {y ^ x for y in out}
    return frozenset(out)


def join(a, b):
    return frozenset(x ^ y for x in a for y in b)


def dimension(s):
    return len(s).bit_length()-1


def graph(w):
    parent, old = [], []

    def node(f):
        i = len(parent)
        parent.append(i)
        old.append(f)
        return i

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def unite(a, b):
        a, b = root(a), root(b)
        if old[a] != old[b]:
            raise ValueError('The source has an invalid scalar contact')
        parent[b] = a

    starts = [node(f) for f in w['initial']]
    current = starts+[None]*w['owned_fields']
    moves = []
    segments = []
    for i, e in enumerate(w['program']):
        op, r = e[:2]
        if op == 'INIT':
            current[r] = node(e[2])
        elif op == 'CLEAR':
            current[r] = None
        elif op == 'MOVE':
            a = current[r]
            b = node(e[3])
            moves.append((a, b, bool(e[4]), i))
            current[r] = b
        elif op in ('ADD', 'COPY'):
            unite(current[r], current[e[2]])
        segments.append(current[r])
    ends = current[:w['public']]
    roots = sorted({root(i) for i in range(len(parent))})
    index = {r:i for i,r in enumerate(roots)}
    label = lambda n: index[root(n)]
    return {
        'old': [old[r] for r in roots],
        'starts': list(map(label, starts)),
        'ends': list(map(label, ends)),
        'moves': [(label(a),label(b),p,i) for a,b,p,i in moves],
        'segments': [None if n is None else label(n) for n in segments],
    }


def bounds(w, g):
    full = frozenset(range(512))
    lo = [frozenset({0}) for _ in g['old']]
    hi = [full for _ in g['old']]
    forward, backward = defaultdict(set), defaultdict(set)
    for a,b,private,_ in g['moves']:
        if private:
            a,b = b,a
        forward[a].add(b)
        backward[b].add(a)
    main = set(w['live']) | {r+112 for r in w['live']}
    fixed = set()
    for r in main:
        for key, field in [('starts','initial'),('ends','final')]:
            i = g[key][r]
            s = span(w['frames'][w[field][r]])
            if i in fixed and lo[i] != s:
                raise ValueError('Inconsistent main boundary')
            lo[i] = hi[i] = s
            fixed.add(i)
    queue = deque(fixed)
    while queue:
        a = queue.popleft()
        for b in forward[a]:
            if not lo[a] <= lo[b]:
                lo[b] = join(lo[b], lo[a])
                queue.append(b)
    queue = deque(fixed)
    while queue:
        b = queue.popleft()
        for a in backward[b]:
            if not hi[a] <= hi[b]:
                hi[a] &= hi[b]
                queue.append(a)
    for i, f in enumerate(g['old']):
        if not lo[i] <= span(w['frames'][f]) <= hi[i]:
            raise ValueError('The source is outside the exact subspace bounds')
    return lo,hi


def invoice(w,g,spaces):
    dims = list(map(dimension, spaces))
    paid = Counter(abs(dims[a]-dims[b]) for a,b,_,_ in g['moves'])
    main = set(w['live']) | {r+112 for r in w['live']}
    helpers = Counter(dims[g['ends'][r]]-dims[g['starts'][r]]
                      for r in range(w['public']) if r not in main)
    paid.pop(0,None)
    zero = helpers.pop(0,0)
    return {'paid':dict(paid), 'helpers':dict(helpers), 'zero_helpers':zero,
            'owned_rank':sum(dims[a]-dims[b] for a,b,p,_ in g['moves'] if p)}
