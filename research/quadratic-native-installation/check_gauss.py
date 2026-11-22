"""Cross-check every entry in random small Clifford circuits and arbitrary binary quadratic sums."""

from fractions import Fraction as F
from random import Random
import clifford_exact as c
from gauss_phase import matrix_element, Quadratic

rng = Random(761125)


def value(raw):
    if raw is None:
        return (0, 0)
    s, k = raw
    assert s % 2 == k % 2
    a, b = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)][k]
    power = F(2) ** (s // 2)
    return a * power, b * power


def enumerated(q, n):
    out = [0, 0]
    for x in range(1 << n):
        p = q.constant
        p += sum(q.linear[i] for i in range(n) if x >> i & 1)
        p += 2 * sum(
            ((q.edges[i] & x) >> (i + 1)).bit_count() for i in range(n) if x >> i & 1
        )
        v = [(1, 0), (0, 1), (-1, 0), (0, -1)][p % 4]
        out = [a + b for a, b in zip(out, v)]
    return tuple(out)


forms = entries = 0
for n in range(1, 8):
    for sample in range(30):
        q = Quadratic(n)
        for j in range(2 * n):
            a, b = (rng.randrange(2 << n) for _ in range(2))
            q.add_cross(a, b)
            q.add_linear(a, rng.randrange(4))
        expected = enumerated(q, n)
        assert value(q.sum()) == expected
        forms += 1
for n in range(1, 6):
    for trial in range(12):
        op = c.ident(n)
        for layer in range(9):
            typ = rng.randrange(4)
            if typ == 0:
                gate = c.cgate(n, rng.randrange(1, 1 << n), rng.choice([-1, 1]))
            elif typ == 1:
                rows = [0] * n
                for i in range(n):
                    for j in range(i + 1):
                        if rng.randrange(2):
                            rows[i] |= 1 << j
                            rows[j] |= 1 << i
                gate = c.diag(n, rows)
            elif typ == 2:
                basis = list(range(n))
                rng.shuffle(basis)
                gate = c.perm(n, tuple(1 << j for j in basis))
            else:
                gate = c.xgate(n, rng.randrange(1 << n))
            op = op.then(gate)
        for col in range(1 << n):
            vec, den = op.zero_state(col)
            for row, (a, b) in enumerate(vec):
                expected = F(a, 2**den), F(b, 2**den)
                assert value(matrix_element(op.circuit, n, col, row)) == expected
                entries += 1
print(f"PASS quadratic_forms={forms} exact_matrix_entries={entries}")
