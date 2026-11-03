"""Apply the retained-seed Gaussian map with exact integer operations."""


def center(sr, si):
    if (sr + si) % 2 == 0:
        return 0, 0
    if sr % 2:
        return (1 if sr > 0 else -1), 0
    return 0, (1 if si > 0 else -1)


def pair(x, y, seed, inverse=False):
    if seed not in (-1, 1):
        raise ValueError("seed must be -1 or 1")
    a, b = x
    c, d = y
    sr, si, dr, di = a + c, b + d, a - c, b - d
    cr, ci = center(sr, si)
    cr, ci = seed * cr, seed * ci
    dr, di = dr - cr, di - ci
    dr, di = (di, -dr) if inverse else (-di, dr)
    dr, di = dr + cr, di + ci
    numerators = (sr + dr, si + di, sr - dr, si - di)
    if any(v % 2 for v in numerators):
        raise ArithmeticError("pair output is not on the integer grid")
    a, b, c, d = (v // 2 for v in numerators)
    return (a, b), (c, d)


def phase(z, p):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[p % 4]


def route(recipe):
    n = len(recipe["matrix_rows"])
    mapping, phases = [], []
    for x in range(1 << n):
        y = sum(((row & x).bit_count() % 2) << j
                for j, row in enumerate(recipe["matrix_rows"])) ^ recipe["offset"]
        p = recipe["phase"]
        for j in range(n):
            if x >> j & 1:
                p += recipe["linear_Z4"][j]
                p += 2 * (((recipe["quadratic_rows"][j] >> (j + 1))
                          & (x >> (j + 1))).bit_count() % 2)
        mapping.append(y)
        phases.append(p % 4)
    if sorted(mapping) != list(range(1 << n)):
        raise ValueError("monomial route is not a permutation")
    return mapping, phases


def monomial(values, routing, axis, inverse=False):
    mapping, phases = routing
    radix = len(mapping)
    stride = radix ** axis
    out = [None] * len(values)
    for start in range(0, len(values), radix * stride):
        for digit, dest in enumerate(mapping):
            p = phases[digit]
            for low in range(stride):
                src, dst = start + digit * stride + low, start + dest * stride + low
                if inverse:
                    out[src] = phase(values[dst], -p)
                else:
                    out[dst] = phase(values[src], p)
    return out


def layer(values, seed, stride=1, inverse=False):
    out = [None] * len(values)
    for start in range(0, len(values), 2 * stride):
        for low in range(stride):
            a, b = start + low, start + stride + low
            out[a], out[b] = pair(values[a], values[b], seed, inverse)
    return out


def native(values, recipes, seeds, inverse=False):
    if not seeds or len(values) != 512 ** len(seeds):
        raise ValueError("native shape must be 512**len(seeds)")
    left, right = (route(recipes[key]) for key in ("left", "right"))
    out = list(values)
    axes = reversed(range(len(seeds))) if inverse else range(len(seeds))
    for axis in axes:
        if inverse:
            out = monomial(out, left, axis, True)
            out = layer(out, seeds[axis], 512 ** axis, True)
            out = monomial(out, right, axis, True)
        else:
            out = monomial(out, right, axis)
            out = layer(out, seeds[axis], 512 ** axis)
            out = monomial(out, left, axis)
    return out
