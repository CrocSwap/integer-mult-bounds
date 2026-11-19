"""Check the radical Fourier identity on every Levi element in symplectic ranks 1, 2, 3."""
from collections import deque


def pairing(v, w, half):
    mask = (1 << half) - 1
    return (((v >> half) & w & mask) ^ ((w >> half) & v & mask)).bit_count() % 2


def symplectic_actions(half):
    n = 1 << (2 * half)
    identity = tuple(range(n))
    generators = [tuple(v ^ (a if pairing(a, v, half) else 0) for v in identity)
                  for a in range(1, n)]
    seen = {identity}
    queue = deque([identity])
    while queue:
        current = queue.popleft()
        yield current
        for generator in generators:
            product = tuple(generator[y] for y in current)
            if product not in seen:
                seen.add(product)
                queue.append(product)


def nullity(columns):
    pivots = {}
    for v in columns:
        while v.bit_length() in pivots:
            v ^= pivots[v.bit_length()]
        if v:
            pivots[v.bit_length()] = v
    return len(columns) - len(pivots)


def check_rank(m):
    half = m - 1
    dim = 2 * half
    count = 1 << dim
    q0 = tuple(((v >> half) & v & ((1 << half)-1)).bit_count() % 2 for v in range(count))
    characters = []
    for z in range(count):
        linear = tuple(pairing(v, z, half) for v in range(count))
        quadratic = tuple(l ^ q for l, q in zip(linear, q0, strict=True))
        characters.extend([(linear, False, "linear" if z else "trivial"),
                           (quadratic, True, "quadratic")])
    tested = groups = 0
    for s in symplectic_actions(half):
        groups += 1
        differences = [s[1 << i] ^ (1 << i) for i in range(dim)]
        d = nullity(differences)
        # Coordinates are e (bit zero), W, then f. These are columns of u(c,b)s - I.
        terms = []
        for c in range(count):
            middle = [(v << 1) | pairing(c, s[1 << i], half) for i, v in enumerate(differences)]
            for b in range(2):
                terms.append((c, b, nullity([0, *middle, (c << 1) | b])))
        for phase, odd, kind in characters:
            if any(phase[v] != phase[s[v]] for v in range(count)):
                continue
            actual = [0] * (2*m+1)
            for c, b, k in terms:
                actual[k] += (-1 if phase[c] ^ (odd and b) else 1) * (1 << k)
            expected = [0] * len(actual)
            expected[d+2] = 4*count
            expected[d+1] = (-2 if odd else 2)*count
            if not odd:
                expected[d] = count * ((2 << d) - 2 if kind == "trivial" else -2)
            if actual != expected:
                raise ValueError((m, s, kind, actual, expected))
            tested += 1
    if groups != (1, 6, 720)[m-1]:
        raise ValueError(("incomplete Levi group", m, groups))
    return groups, tested


if __name__ == "__main__":
    totals = [check_rank(m) for m in (1, 2, 3)]
    print("PASS radical fixed-space Fourier polynomials on all 727 small Levi elements;",
          sum(n for _, n in totals), "invariant character tests", totals)
