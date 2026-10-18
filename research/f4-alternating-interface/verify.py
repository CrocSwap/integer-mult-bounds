"""Exact, standard-library audit of the F4 trace / binary phase interface."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def mul(a, b):
    # F4 = F2[t]/(t^2+t+1), packed polynomial coefficients.
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return out


def conj(a):
    return mul(a, a)


def trace(a):
    return a ^ conj(a)


def dot(x, rows, y):
    return sum(((x >> i) & 1) * ((row & y).bit_count() & 1)
               for i, row in enumerate(rows)) & 1


def rank(rows):
    pivots = {}
    for x in rows:
        while x:
            k = x.bit_length() - 1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    return len(pivots)


def apply(rows, x):
    return sum(((row & x).bit_count() & 1) << i for i, row in enumerate(rows))


def hermitians(n):
    pairs = list(itertools.combinations(range(n), 2))
    for diagonal in itertools.product(range(2), repeat=n):
        for upper in itertools.product(range(4), repeat=len(pairs)):
            h = [[0] * n for _ in range(n)]
            for i, v in enumerate(diagonal):
                h[i][i] = v
            for (i, j), v in zip(pairs, upper):
                h[i][j], h[j][i] = v, conj(v)
            yield h


def trace_gram(h):
    n = len(h)
    # B(x,y) = Tr(sum conjugate(x_i) H_ij y_j), basis (1,t).
    return [sum(trace(mul(mul(conj(1 << (i % 2)), h[i // 2][j // 2]),
                              1 << (j % 2))) << j for j in range(2 * n))
            for i in range(2 * n)]


def alternate_forms(r):
    pairs = list(itertools.combinations(range(r), 2))
    for mask in range(1 << len(pairs)):
        rows = [0] * r
        for k, (i, j) in enumerate(pairs):
            if mask >> k & 1:
                rows[i] |= 1 << j
                rows[j] |= 1 << i
        yield rows


def q_values(rows, linear):
    r = len(rows)
    return [(2 * sum(((x >> i) & 1) * ((x >> j) & 1)
                     for i in range(r) for j in range(i + 1, r)
                     if rows[i] >> j & 1)
             + 2 * (x & linear).bit_count()) % 4 for x in range(1 << r)]


PHASE = ((1, 0), (0, 1), (-1, 0), (0, -1))


def times(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def phase_audit(rows, q, scalar_delta=0):
    r, size = len(rows), 1 << len(rows)
    require(rank(rows) == r, 'singular Gram matrix')
    for x in range(size):
        for y in range(size):
            require((q[x ^ y] - q[x] - q[y]) % 4 == 2 * dot(x, rows, y),
                    'wrong polarization')
    real = sum(PHASE[z][0] for z in q)
    imag = sum(PHASE[z][1] for z in q)
    require(real * real + imag * imag == size, 'wrong Gauss magnitude')
    # Exact unnormalized Fourier transform (Gaussian integer pairs).
    fourier = []
    for t in range(size):
        signs = [1 if (z & t).bit_count() % 2 == 0 else -1 for z in range(size)]
        fourier.append((sum(s * PHASE[q[z]][0] for z, s in enumerate(signs)),
                        sum(s * PHASE[q[z]][1] for z, s in enumerate(signs))))
    scalar = (real + scalar_delta, imag)
    for x in range(size):
        for y in range(size):
            # K=F^-1 diag(i^q) F; complete the square at t=G(x+y).
            predicted = times(scalar, PHASE[(-q[x] - q[y] + 2 * dot(x, rows, y)) % 4])
            require(fourier[apply(rows, x ^ y)] == predicted, 'kernel mismatch')
    # b=(1-i)/2: multiplying S_q b^r gives a fourth root, exactly.
    numerator = scalar
    for _ in range(r):
        numerator = times(numerator, (1, -1))
    require(numerator in [(size * a, size * b) for a, b in PHASE], 'nonunit normalization')
    return size * size


def rejects(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('negative control incorrectly accepted')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    census = {}
    for n in (1, 2, 3):
        counts = {}
        for h in hermitians(n):
            g = trace_gram(h)
            require(all((row >> i & 1) == 0 for i, row in enumerate(g)), 'not alternating')
            require(all((g[i] >> j & 1) == (g[j] >> i & 1)
                        for i in range(2*n) for j in range(2*n)), 'not symmetric')
            # Hermitian nullspace over F4, independently enumerate vectors.
            null = 0
            for x in itertools.product(range(4), repeat=n):
                products = [0] * n
                for i in range(n):
                    for j in range(n):
                        products[i] ^= mul(h[i][j], x[j])
                null += not any(products)
            require(null == 1 << (2*n - rank(g)), 'trace radical mismatch')
            counts[str(rank(g))] = counts.get(str(rank(g)), 0) + 1
        census[str(n)] = counts
    cases = entries = 0
    for r in (2, 4):
        for g in alternate_forms(r):
            if rank(g) != r:
                continue
            for linear in range(1 << r):
                entries += phase_audit(g, q_values(g, linear))
                cases += 1
    g = [2, 1]
    q = q_values(g, 0)
    bad = q.copy(); bad[1] = 1
    rejects(lambda: phase_audit(g, bad))
    rejects(lambda: phase_audit([0, 0], [0] * 4))
    rejects(lambda: phase_audit(g, q, scalar_delta=1))
    require(trace(mul(conj(2), 2)) == 0, 'Hermitian diagonal trace')
    rejects(lambda: require(trace(mul(2, 2)) == 0, 'missing conjugation'))
    # An actual even-weight embedding into the ordinary binary dot product.
    # V columns are 110 and 011; G=V^t V is the hyperbolic block.
    columns = [3, 6]
    embedded_q = []
    for x in range(4):
        v = 0
        for i, col in enumerate(columns):
            if x >> i & 1:
                v ^= col
        embedded_q.append(v.bit_count() % 4)
    phase_audit(g, embedded_q)
    require(embedded_q == [0, 2, 2, 2], 'embedding phase')
    # No nonzero odd-norm vector: cannot have an orthonormal basis.
    require(all(dot(x, g, x) == 0 for x in range(4)), 'odd norm control')
    result = {'hermitian_trace_rank_census': census, 'phase_cases': cases,
              'kernel_entries': entries, 'negative_controls': 4, 'embedded_hyperbolic_block': True,
              'scope': 'finite exact interface audit, not a multiplication theorem',
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if args.output:
        with args.output.open('x', encoding='utf-8') as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
