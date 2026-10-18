"""Dense faithful-regular census; no primary-engine imports. Apache-2.0."""
from itertools import product


def address_matrix(label):
    return (1, label & 1, (label >> 2) & 1, 0, 1, (label >> 1) & 1, 0, 0, 1)


def address_product(left, right):
    return tuple(sum(left[i * 3 + k] * right[k * 3 + j] for k in range(3)) % 2
                 for i in range(3) for j in range(3))


ADDRESSES = [address_matrix(i) for i in range(8)]
PRODUCT = [[ADDRESSES.index(address_product(g, h)) for h in ADDRESSES] for g in ADDRESSES]


def multiply_labels(g, h):
    return PRODUCT[g][h]


def natural_sum():
    return tuple(sum(g[i] for g in ADDRESSES) % 2 for i in range(9))


def binary_product(left, right):
    out = []
    for row in left:
        result = 0
        while row:
            bit = row & -row
            result ^= right[bit.bit_length() - 1]
            row ^= bit
        out.append(result)
    return tuple(out)


def scalar_projectors(r):
    result = []
    for rows in product(range(1 << r), repeat=r):
        if len(set(rows) - {0}) == 1 and binary_product(rows, rows) == rows:
            result.append(rows)
    return result


def regular_from_formal(state, r):
    result = []
    for i in range(r):
        for h in range(8):
            row = 0
            for j in range(r):
                p = state[i * r + j]
                for g in range(8):
                    if (p >> g) & 1:
                        row ^= 1 << (8 * j + PRODUCT[h][g])
            result.append(row)
    return tuple(result)


def decode(matrix, r):
    formal = tuple((matrix[8 * i] >> (8 * j)) & 255 for i in range(r) for j in range(r))
    if regular_from_formal(formal, r) != matrix:
        raise ValueError("regular matrix left the group-algebra image")
    return formal


def generator(rows, g):
    r = len(rows)
    answer = []
    for i in range(r):
        for h in range(8):
            row = 1 << (8 * i + h)
            for j in range(r):
                if (rows[i] >> j) & 1:
                    row ^= (1 << (8 * j + h)) ^ (1 << (8 * j + PRODUCT[h][g]))
            answer.append(row)
    return tuple(answer)


BALLS = {}


def census(r):
    scalar = scalar_projectors(r)
    generators = [generator(rows, g) for rows in scalar for g in (1, 2)]
    start = tuple(1 << i for i in range(8 * r))
    seen = {start: 0}
    frontier = {start}
    attempts = 0
    for depth in range(1, 4):
        following = set()
        for matrix in frontier:
            for gate in generators:
                attempts += 1
                result = binary_product(matrix, gate)
                if result not in seen:
                    following.add(result)
        seen.update((m, depth) for m in following)
        frontier = following
    BALLS[r] = seen
    decoded = {decode(m, r): d for m, d in seen.items()}
    if len(decoded) != len(seen):
        raise ValueError("faithful decoding collision")
    ids = {sum(row << (i * r) for i, row in enumerate(rows)) for rows in scalar}
    return decoded, attempts, ids


def meet_distance(r, copies):
    formal = tuple((16 if i < copies else 1) if i == j else 0
                   for i in range(r) for j in range(r))
    wanted = regular_from_formal(formal, r)
    seen = BALLS[r]
    values = []
    for matrix, depth in seen.items():
        other = binary_product(wanted, matrix)
        if other in seen:
            values.append(depth + seen[other])
    return min(values) if values else None
