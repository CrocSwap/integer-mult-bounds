"""Independent zero-column support witness for the forbidden target end."""


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def full_column():
    # Product of the nine C=(1+i)I/2+(1-i)X/2 factors, without reduction.
    out = []
    for y in range(512):
        z = (1, 0)
        for bit in range(9):
            z = mul(z, (1, -1) if y >> bit & 1 else (1, 1))
        out.append(z)
    return out


def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in tuple(out)}
    return out


def witness(port):
    # A canonical rank-eight frame is monomial-conjugate to C on eight axes.
    # Its zero-column support is its frame subspace, here perp(port).
    space = {x for x in range(512) if (x & port).bit_count() % 2 == 0}
    outside = next(1 << j for j in range(9) if port >> j & 1)
    numerator = full_column()[outside]
    if len(space) != 256 or outside in space or numerator == (0, 0):
        raise ValueError('native support witness')
    return {'port': port, 'column': 0, 'row': outside,
            'required_support': len(space), 'overridden_support': 512,
            'required_coefficient': [0, 0], 'overridden_numerator': list(numerator),
            'denominator': 512}
