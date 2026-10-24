"""Explicit matrix-product operator constructors, not a physical-cost compiler.

Apache-2.0; substantial OpenAI Codex assistance.
"""
from dataclasses import dataclass
from exact import G, encode, need, scalar, zeros


def identity(n):
    return [[G(i == j) for j in range(n)] for i in range(n)]


def kron_vector(a, b):
    return [x*y for x in a for y in b]


def kron(a, b):
    n, m = len(a), len(b)
    c = zeros(n*m, n*m)
    for i in range(n):
        for j in range(n):
            if a[i][j]:
                for k in range(m):
                    for h in range(m):
                        if b[k][h]:
                            c[i*m+k][j*m+h] = a[i][j]*b[k][h]
    return c


@dataclass
class MPO:
    d: int
    left: list
    right: list
    transitions: dict

    @property
    def n(self):
        return len(self.left)

    def problem(self):
        return {'local_dimension': self.d, 'states': self.n, 'outputs': 1, 'inputs': 1,
                'left': encode([self.left]), 'right': encode([[x] for x in self.right]),
                'transitions': {f'{y},{x}': encode(a)
                                for (y, x), a in sorted(self.transitions.items())}}


def local(d, entries):
    return MPO(d, [G(1)], [G(1)],
               {key: [[G(value)]] for key, value in entries.items() if value})


def unit(d):
    return local(d, {(i, i): G(1) for i in range(d)})


def zero(d):
    return MPO(d, [G()], [G(1)], {})


def scale(a, c):
    if not c:
        return zero(a.d)
    return MPO(a.d, [c*x for x in a.left], a.right, a.transitions)


def add(a, b):
    need(a.d == b.d, 'sum local dimension')
    if not any(a.left) or not a.transitions:
        return b
    if not any(b.left) or not b.transitions:
        return a
    n, m = a.n, b.n
    trans = {}
    for key in set(a.transitions) | set(b.transitions):
        c = zeros(n+m, n+m)
        for offset, size, t in ((0, n, a.transitions.get(key)), (n, m, b.transitions.get(key))):
            if t is not None:
                for i in range(size):
                    for j in range(size):
                        c[offset+i][offset+j] = t[i][j]
        trans[key] = c
    return MPO(a.d, a.left+b.left, a.right+b.right, trans)


def difference(a, b):
    return add(a, scale(b, G(-1)))


def compose(a, b):
    """a after b; contract the same intermediate physical column entry."""
    need(a.d == b.d, 'composition local dimension')
    if not any(a.left) or not any(b.left) or not a.transitions or not b.transitions:
        return zero(a.d)
    by_input, by_output = {}, {}
    for (y, z), t in a.transitions.items():
        by_input.setdefault(z, []).append((y, t))
    for (z, x), t in b.transitions.items():
        by_output.setdefault(z, []).append((x, t))
    trans = {}
    size = a.n*b.n
    for z in by_input.keys() & by_output.keys():
        for y, at in by_input[z]:
            for x, bt in by_output[z]:
                term = kron(at, bt)
                if (y, x) not in trans:
                    trans[y, x] = term
                else:
                    old = trans[y, x]
                    trans[y, x] = [[u+v for u, v in zip(row, addrow)]
                                    for row, addrow in zip(old, term)]
    return MPO(a.d, kron_vector(a.left, b.left), kron_vector(a.right, b.right), trans)


def transpose(a):
    return MPO(a.d, a.left, a.right, {(x, y): t for (y, x), t in a.transitions.items()})


def recurrence(a, transition, left, right):
    """Multiply the width-f operator by left * transition^f * right."""
    return MPO(a.d, kron_vector(a.left, left), kron_vector(a.right, right),
               {s: kron(t, transition) for s, t in a.transitions.items()})


def prefix_xor(d=2, bit=0):
    need(d > 1 and d & (d-1) == 0 and 0 <= bit < d.bit_length()-1, 'binary column space')
    trans = {}
    for x in range(d):
        for previous in range(2):
            y = x ^ (previous << bit)
            t = zeros(2, 2)
            t[previous][(y >> bit) & 1] = G(1)
            trans[y, x] = t
    return MPO(d, [G(1), G()], [G(1), G(1)], trans)


def cyclic_delay(n, d=1):
    t = zeros(n, n)
    for i in range(n):
        t[i][(i+1) % n] = G(1)
    return MPO(d, [G(i == 0) for i in range(n)], [G(i == 0) for i in range(n)],
               {(i, i): t for i in range(d)})


def native_entries(recipe, n):
    """Literal source convention: upper quadratic entries, phase at input."""
    entries = {}
    phases = (G(1), G(0, 1), G(-1), G(0, -1))
    for x in range(1 << n):
        y = recipe['offset']
        for j, row in enumerate(recipe['matrix_rows']):
            y ^= ((row & x).bit_count() & 1) << j
        exponent = recipe['phase']
        for i in range(n):
            if x >> i & 1:
                exponent += recipe['linear_Z4'][i]
                exponent += 2*sum(1 for j in range(i+1, n)
                                  if x >> j & 1 and recipe['quadratic_rows'][i] >> j & 1)
        entries[y, x] = phases[exponent % 4]
    need(len({y for y, _ in entries}) == 1 << n, 'source permutation must be invertible')
    return entries


def native_frontend(data):
    """Compile every owner/input block of the supplied finite literal word.

    Local products are composed before tensor lifting only when both operands
    have one virtual state; exterior register coefficients stay in boundaries.
    """
    n, roles = data['axes'], data['roles']
    d = 1 << n
    operators = {}
    for name, recipe in data['generators'].items():
        entries = native_entries(recipe, n)
        operators[name, False] = local(d, entries)
        operators[name, True] = local(d, {(x, y): G(1)/v for (y, x), v in entries.items()})

    def compile_word(word):
        state = [[unit(d) if i == j else zero(d) for j in range(roles)] for i in range(roles)]
        for op in word:
            kind, dst = op['op'], op['dst']
            need(kind in ('apply', 'add', 'query', 'scale', 'swap'), 'unsupported source instruction')
            if kind == 'apply':
                a = operators[op['generator'], op.get('inverse', False)]
                state[dst] = [compose(a, v) for v in state[dst]]
            elif kind == 'scale':
                c = scalar(op['coefficient'])
                state[dst] = [scale(v, c) for v in state[dst]]
            elif kind == 'swap':
                src = op['src']
                state[dst], state[src] = state[src], state[dst]
            else:
                src = op['src']
                before_src, before_dst = list(state[src]), list(state[dst])
                c = scalar(op.get('coefficient', 1))
                a = operators[op['generator'], op.get('inverse', False)] if kind == 'query' else None
                state[dst] = [add(v, scale(compose(a, u) if a else u, c))
                              for v, u in zip(before_dst, before_src)]
        return state
    actual, expected = compile_word(data['program']), compile_word(data['reference'])
    return [[difference(actual[i][j], expected[i][j]) for j in range(roles)] for i in range(roles)]
