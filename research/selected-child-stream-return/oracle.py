"""Independent integer Gaussian model; imports no predecessor implementation."""


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def phase(a, n):
    for _ in range(n % 4):
        a = (-a[1], a[0])
    return a


def monomial(recipe, x):
    coords = [(x // (2 ** i)) % 2 for i in range(9)]
    y = recipe['offset']
    for i, row in enumerate(recipe['matrix_rows']):
        y ^= (sum(coords[j] * ((row // (2 ** j)) % 2) for j in range(9)) % 2) << i
    exponent = recipe['phase'] + sum(coords[i] * recipe['linear_Z4'][i] for i in range(9))
    exponent += 2 * sum(coords[i] * coords[j] * ((recipe['quadratic_rows'][i] // (2 ** j)) % 2)
                        for i in range(9) for j in range(i + 1, 9))
    return y, exponent % 4


def canonical_columns(frame):
    # Independent complete-span construction of the pinned canonical_frame
    # definition, using lookup inversion instead of binary elimination.
    basis, span = [], {0}
    for vector in list(frame) + [1 << j for j in range(9)]:
        if vector not in span:
            basis.append(vector)
            span |= {x ^ vector for x in tuple(span)}
    if len(basis) != 9:
        raise ValueError('complete canonical basis')
    mapping = []
    for x in range(512):
        y = 0
        for j, q in enumerate(basis):
            if (x >> j) & 1:
                y ^= q
        mapping.append(y)
    inverse = {y: x for x, y in enumerate(mapping)}
    cols = [inverse[1 << j] for j in range(9)]
    Q = [[int(i == j) ^ ((cols[i] & cols[j]).bit_count() % 2) for j in range(9)] for i in range(9)]
    def phase_at(x):
        bits = [(x >> i) & 1 for i in range(9)]
        return (sum(bits[i] * Q[i][i] for i in range(9)) +
                2 * sum(bits[i] * bits[j] * Q[i][j] for i in range(9) for j in range(i + 1, 9))) % 4
    phases = [phase_at(x) for x in range(512)]
    result = []
    for x in range(512):
        first = inverse[x]
        column = {}
        for mask in range(256):
            middle = first ^ mask
            y = mapping[middle]
            numerator = (1, 0)
            for j in range(8):
                numerator = mul(numerator, (1, 1) if mask >> j & 1 else (1, -1))
            column[y] = phase(numerator, phases[y] - phases[x])
        result.append(column)
    return result


def apply_columns(values, columns, outer_rows, spectators, coefficients, adjoint=False):
    out = [(0, 0)] * len(values)
    for row in range(outer_rows * spectators):
        for x, column in enumerate(columns):
            for y, numerator in column.items():
                src, dst = (y, x) if adjoint else (x, y)
                if adjoint:
                    numerator = numerator[0], -numerator[1]
                for k in range(coefficients):
                    i = (row * 512 + reverse9(src)) * coefficients + k
                    j = (row * 512 + reverse9(dst)) * coefficients + k
                    out[j] = add(out[j], mul(numerator, values[i]))
    if any(component % 256 for value in out for component in value):
        raise ValueError('full canonical operator exact division')
    return [tuple(component // 256 for component in value) for value in out]


def circuit_column(recipe, x, axes=tuple(range(8))):
    right, rp = monomial(recipe['right'], x)
    out = {}
    for mask in range(1 << len(axes)):
        z = right
        numerator = (1, 0)
        for j, axis in enumerate(axes):
            flipped = (mask >> j) & 1
            z ^= flipped << axis
            numerator = mul(numerator, (1, -1) if flipped else (1, 1))
        y, lp = monomial(recipe['left'], z)
        out[y] = add(out.get(y, (0, 0)), phase(numerator, rp + lp))
    return out


def reverse9(x):
    return sum(((x >> i) & 1) << (8 - i) for i in range(9))
