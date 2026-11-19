"""Test actual n=5,6 coset observations using exact monomial Clifford matrices."""
from itertools import combinations
from functools import reduce
from operator import xor


def require(test, why):
    if not test:
        raise ValueError(why)


def compose(a, b):
    return tuple((a[j][0], (t + a[j][1]) % 4) for j, t in b)


def inverse(a):
    b = [None] * len(a)
    for i, (j, t) in enumerate(a):
        b[j] = (i, -t % 4)
    return tuple(b)


def conjugate(a):
    return tuple((j, -t % 4) for j, t in a)


def weyl(n, label):
    x, z = label & ((1 << n) - 1), label >> n
    return tuple((v ^ x, 2 * ((v & z).bit_count() % 2)) for v in range(1 << n))


def recognize(a, n):
    x, phase = a[0]
    z = sum(1 << j for j in range(n) if a[1 << j][1] != phase)
    label = (z << n) | x
    require(all(j == r and (t - p) % 4 == phase for (j, t), (r, p) in zip(a, weyl(n, label))),
            "operator must be a phased Weyl matrix")
    return label, phase


def tuple_action(u, source, n):
    transposed = conjugate(inverse(u))
    ordinary_inverse = inverse(u)

    def act(label, right):
        return recognize(compose(compose(u, weyl(n, label)), right), n)

    blocks = [act(label, transposed) for label in source]
    labels = tuple(label for label, _ in blocks)
    beta = sum(t for _, t in blocks) % 4
    w = reduce(xor, source)
    odd = len(source) % 2
    wp, t = act(w, transposed if odd else ordinary_inverse)
    require(wp == reduce(xor, labels), "affine output sum")
    return labels, beta, (beta + t if odd else beta - t) % 4


def add_monomial(acc, u, coefficient, phase):
    real, imag = coefficient
    rotations = ((real, imag), (-imag, real), (-real, -imag), (imag, -real))
    for j, (i, t) in enumerate(u):
        a, b = rotations[(phase + t) % 4]
        k = (i, j)
        x, y = acc.get(k, (0, 0))
        acc[k] = x + a, y + b


def evaluate(n):
    s = n // 2 + 1
    d = 1 << n
    source = (0, *(1 << (n+j) for j in range(n)), *(1 << j for j in range(s, n)))
    basis = list(combinations(range(s), 2))
    cnot = tuple((v ^ (((v >> 1) & 1) << 2), 0) for v in range(d))
    phase0 = tuple((v, v & 1) for v in range(d))
    phase1 = tuple((v, (v >> 1) & 1) for v in range(d))
    g = compose(cnot, phase0)
    h = compose(phase1, cnot)
    miss = compose(phase1, g)
    i, _, ji = tuple_action(h, source, n)
    j, _, jj = tuple_action(g, source, n)
    w, wp = reduce(xor, i), reduce(xor, j)
    odd = len(source) % 2
    left = inverse(weyl(n, wp)) if odd else weyl(n, wp)
    right = weyl(n, w) if odd else inverse(weyl(n, w))
    actual, expected = {}, {}
    accepted = skipped = 0
    for pattern in range(1 << len(basis)):
        edges = [(1 << a) | (1 << b) for t, (a, b) in enumerate(basis) if (pattern >> t) & 1]
        c = tuple((v, 2 * (sum((v & e) == e for e in edges) % 2)) for v in range(d))
        stabilizes, beta, sigma = tuple_action(c, source, n)
        require((stabilizes, beta, sigma) == (source, 0, 0), "seed stabilizer phases")
        for hit, lft in [(True, g), (False, miss)]:
            lift = compose(compose(lft, c), inverse(h))
            for j_pauli, p in enumerate((0, 1, 2 << n, 3 | (2 << n))):
                u0 = compose(weyl(n, p), lift)
                scalar = (j_pauli + pattern) % 4
                u = tuple((row, (a + scalar) % 4) for row, a in u0)
                out, beta, sigma = tuple_action(u, i, n)
                require((out == j) == hit, "literal block membership vs planted coset")
                if not hit:
                    skipped += 1
                    continue
                require(sigma == (jj - ji) % 4, "transporter phase")
                c_input = (2 - pattern, pattern + j_pauli + 1)
                add_monomial(actual, compose(compose(left, u), right), c_input, beta + ji - jj)
                add_monomial(expected, conjugate(u) if odd else u, c_input, 0)
                accepted += 1
    require(actual == expected and any(a or b for a, b in actual.values()), "coset sum")
    return len(source), accepted, skipped


if __name__ == "__main__":
    for n in (5, 6):
        k, hits, misses = evaluate(n)
        print(f"PASS n={n} f={2*k+1} pairs={k} accepted={hits} excluded={misses}")
