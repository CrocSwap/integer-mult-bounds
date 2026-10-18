"""Exact signed dot-product rows for the historical Leech minors.

CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
See README.md for the no-carry argument and predecessor credit.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def lane_rows(sample, indices, shift):
    """Return C[i,j] = (i == j or dot(sample[i], sample[j]) == shift).

    Each coordinate lies in [-4, 4]. Each selected row has l1 norm <= 31,
    so every accumulated base-256 digit is at most 8*31 < 256. This holds
    for every signed Leech vector (actual l1 norms: 8, 16, 26).
    """
    require(sample and sample[0], 'Empty sample')
    dimension = len(sample[0])
    require(all(len(v) == dimension and
                all(type(x) is int and -4 <= x <= 4 for x in v)
                for v in sample), 'Invalid byte-lane coordinates')
    require(indices and len(set(indices)) == len(indices) and
            all(type(i) is int and 0 <= i < len(sample) for i in indices),
            'Invalid selected rows')
    require(type(shift) is int, 'Integer shift required')
    require(all(sum(abs(x) for x in sample[i]) <= 31 for i in indices),
            'Byte-lane carry bound exceeded')

    plus = [int.from_bytes(bytes(v[k] + 4 for v in sample), 'little')
            for k in range(dimension)]
    minus = [int.from_bytes(bytes(4 - v[k] for v in sample), 'little')
             for k in range(dimension)]
    rows = []
    for i in indices:
        u = sample[i]
        offset = 4 * sum(abs(x) for x in u)
        packed = sum(x * plus[k] if x > 0 else -x * minus[k]
                     for k, x in enumerate(u) if x)
        values = packed.to_bytes(len(sample), 'little')
        rows.append(sum(1 << j for j, value in enumerate(values)
                        if i == j or value == shift + offset))
    return rows
