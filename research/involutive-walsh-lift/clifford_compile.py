"""Small exact Gaussian-dyadic Clifford compiler, independent of gx internals.
Paulis use i^p X^x Z^z. State vectors use integer Gaussian numerators / 2^d.
The tableau is supplemented by a literal circuit, so global phases are kept.
"""
from dataclasses import dataclass

def parity(x):
    return x.bit_count() & 1

def rank(rows):
    p = {}
    for x in rows:
        while x:
            b = x.bit_length() - 1
            if b not in p:
                p[b] = x
                break
            x ^= p[b]
    return len(p)

def transpose(rows, n):
    return tuple((sum(((rows[j] >> i & 1) << j for j in range(n))) for i in range(n)))

def mv(rows, x):
    return sum((parity(r & x) << i for i, r in enumerate(rows)))

def inv(rows, n):
    a = [r | 1 << n + i for i, r in enumerate(rows)]
    for j in range(n):
        k = next((i for i in range(j, n) if a[i] >> j & 1))
        a[j], a[k] = (a[k], a[j])
        for i in range(n):
            if i != j and a[i] >> j & 1:
                a[i] ^= a[j]
    assert [r & (1 << n) - 1 for r in a] == [1 << i for i in range(n)]
    return tuple((r >> n for r in a))

def basis_extend(cols, n):
    out = []
    for x in list(cols) + [1 << i for i in range(n)]:
        if rank(out + [x]) > len(out):
            out.append(x)
    assert len(out) == n
    return tuple(out)

def pmul(a, b):
    x, z, p = a
    y, w, q = b
    return (x ^ y, z ^ w, (p + q + 2 * parity(z & y)) % 4)

def identity(n):
    return tuple([(1 << i, 0, 0) for i in range(n)] + [(0, 1 << i, 0) for i in range(n)])

def apply(T, p):
    n = len(T) // 2
    x, z, ph = p
    out = (0, 0, ph)
    for i in range(n):
        if x >> i & 1:
            out = pmul(out, T[i])
    for i in range(n):
        if z >> i & 1:
            out = pmul(out, T[n + i])
    return out

def compose(A, B):
    return tuple((apply(A, p) for p in B))

def inverse(T):
    n = len(T) // 2
    cols = [x | z << n for x, z, p in T]
    rows = transpose(cols, 2 * n)
    cols_inv = transpose(inv(rows, 2 * n), 2 * n)
    out = []
    for j, w in enumerate(cols_inv):
        x = w & (1 << n) - 1
        z = w >> n
        u, v, p = apply(T, (x, z, 0))
        assert (u, v) == identity(n)[j][:2]
        out.append((x, z, -p % 4))
    return tuple(out)

def qvalue(Q, alpha, x, n):
    return (sum((alpha[i] for i in range(n) if x >> i & 1)) + 2 * sum((parity(Q[i] >> i + 1 & x >> i + 1) for i in range(n) if x >> i & 1))) % 4

def mul_i(a, p):
    x, y = a
    p %= 4
    return [(x, y), (-y, x), (-x, -y), (y, -x)][p]

@dataclass
class Op:
    n: int
    tab: tuple
    circuit: list

    def then(self, b):
        assert self.n == b.n
        return Op(self.n, compose(b.tab, self.tab), self.circuit + b.circuit)

    def adjoint(self):
        circ = []
        for e in reversed(self.circuit):
            if e[0] == 'P':
                circ.append(('P', inv(e[1], self.n)))
            elif e[0] == 'D':
                circ.append(('D', e[1], tuple((-x % 4 for x in e[2]))))
            elif e[0] == 'C':
                circ.append(('C', e[1], -e[2]))
            elif e[0] == 'phase':
                circ.append(('phase', -e[1] % 4))
            else:
                circ.append(e)
        return Op(self.n, inverse(self.tab), circ)

    def zero_state(self, basis=0):
        N = 1 << self.n
        vec = [(0, 0)] * N
        vec[basis] = (1, 0)
        den = 0
        for e in self.circuit:
            if e[0] == 'P':
                v = [(0, 0)] * N
                for x, a in enumerate(vec):
                    v[mv(e[1], x)] = a
                vec = v
            elif e[0] == 'X':
                vec = [vec[x ^ e[1]] for x in range(N)]
            elif e[0] == 'D':
                vec = [mul_i(a, qvalue(e[1], e[2], x, self.n)) for x, a in enumerate(vec)]
            elif e[0] == 'phase':
                vec = [mul_i(a, e[1]) for a in vec]
            elif e[0] == 'C':
                q, sgn = e[1:]
                v = []
                for x, (a, b) in enumerate(vec):
                    c, d = vec[x ^ q]
                    v.append((a - sgn * b + c + sgn * d, b + sgn * a + d - sgn * c))
                vec = v
                den += 1
            else:
                raise AssertionError(e)
            while den and all((a & 1 == b & 1 == 0 for a, b in vec)):
                vec = [(a // 2, b // 2) for a, b in vec]
                den -= 1
        return (vec, den)

def ident(n):
    return Op(n, identity(n), [])

def perm(n, G):
    cols = transpose(G, n)
    gi = inv(G, n)
    return Op(n, tuple([(a, 0, 0) for a in cols] + [(0, a, 0) for a in gi]), [('P', tuple(G))])

def diag(n, Q, alpha=None):
    Q = tuple(Q)
    assert transpose(Q, n) == Q
    alpha = tuple(alpha) if alpha is not None else tuple((Q[i] >> i & 1 for i in range(n)))
    assert all((alpha[i] % 2 == Q[i] >> i & 1 for i in range(n)))
    return Op(n, tuple([(1 << i, Q[i], alpha[i]) for i in range(n)] + [(0, 1 << i, 0) for i in range(n)]), [('D', Q, alpha)])

def cgate(n, q, sgn=1):
    return Op(n, tuple([(1 << i, 0, 0) for i in range(n)] + [(q if q >> i & 1 else 0, 1 << i, 3 * sgn % 4 if q >> i & 1 else 0) for i in range(n)]), [('C', q, sgn)])

def xgate(n, b):
    return Op(n, tuple([(1 << i, 0, 0) for i in range(n)] + [(0, 1 << i, 2 * (b >> i & 1)) for i in range(n)]), [('X', b)])

def fourier(n, axes=None):
    out = ident(n)
    for i in range(n) if axes is None else axes:
        out = out.then(cgate(n, 1 << i))
    return out

def hadamard(n, axes):
    axes = list(axes)
    Q = tuple((1 << i if i in axes else 0 for i in range(n)))
    S = diag(n, Q)
    return S.then(fourier(n, axes)).then(S)

def canonical_frame(n, U):
    r = len(U)
    if r == 0:
        return ident(n)
    if r == n:
        return fourier(n)
    G = transpose(basis_extend(U, n), n)
    gi = inv(G, n)
    Q = tuple((1 << i ^ sum((parity(gi_i & gi_j) << j for j, gi_j in enumerate(transpose(gi, n)))) for i, gi_i in enumerate(transpose(gi, n))))
    K = perm(n, G).then(diag(n, Q))
    return K.adjoint().then(fourier(n, range(r))).then(K)

def monomial(op):
    n = op.n
    table = op.tab
    if any((x != 0 or phase % 2 for x, z, phase in table[n:])):
        raise ValueError('The operator is not monomial')
    matrix = transpose([x for x, z, phase in table[:n]], n)
    offset = mv(matrix, sum((phase // 2 << i for i, (x, z, phase) in enumerate(table[n:]))))
    transposed = transpose(matrix, n)
    quadratic = transpose([mv(transposed, z) for x, z, phase in table[:n]], n)
    linear = [(phase - 2 * parity(offset & z)) % 4 for x, z, phase in table[:n]]
    if all((gate[0] in ('P', 'D', 'X', 'phase') for gate in op.circuit)):
        address, scalar_phase = (0, 0)
        for gate in op.circuit:
            if gate[0] == 'P':
                address = mv(gate[1], address)
            elif gate[0] == 'D':
                scalar_phase += qvalue(gate[1], gate[2], address, n)
            elif gate[0] == 'X':
                address ^= gate[1]
            else:
                scalar_phase += gate[1]
        if address != offset:
            raise ValueError('The monomial offset does not match its circuit')
        scalar_phase %= 4
    else:
        vector, denominator = op.zero_state()
        if denominator or any((value != (0, 0) for j, value in enumerate(vector) if j != offset)):
            raise ValueError('The monomial basis image is not a Gaussian unit')
        scalar_phase = [(1, 0), (0, 1), (-1, 0), (0, -1)].index(vector[offset])
    result = diag(n, quadratic, linear).then(perm(n, matrix)).then(xgate(n, offset))
    result = result.then(Op(n, identity(n), [('phase', scalar_phase)]))
    if result.tab != table:
        raise ValueError('The compiled monomial has the wrong Pauli action')
    return (result, dict(matrix_rows=matrix, offset=offset, quadratic_rows=quadratic, linear_Z4=linear, phase=scalar_phase))
