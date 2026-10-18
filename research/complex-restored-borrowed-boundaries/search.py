"""Exact dyadic boundary obstruction through the GL(n,3) quotient.

Ross Richardson, with substantial OpenAI Codex assistance; Apache-2.0.
Adapted from Ross Richardson / Codex PR1145; see NOTICE.md.
"""
from collections import Counter
from hashlib import sha256
import struct

SEED = 33
RADIUS = 4
PERMUTATIONS = {3: (1, 0, 2), 4: (1, 2, 0, 3), 6: (1, 0, 3, 4, 2, 5)}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def generators(n):
    require(n in PERMUTATIONS, "unsupported dimension")
    ops = [(t, s, sign) for t in range(n) for s in range(n)
           for sign in (-1, 1) if t != s or sign == -1]
    cut = SEED % len(ops)
    return ops[cut:] + ops[:cut]


def row_tables(n):
    size = 3 ** n
    digits = [tuple((a // 3 ** j) % 3 for j in range(n)) for a in range(size)]
    encode = lambda row: sum(x * 3 ** j for j, x in enumerate(row))
    plus = [[encode([(x + y) % 3 for x, y in zip(a, b)]) for b in digits]
            for a in digits]
    minus = [[encode([(x - y) % 3 for x, y in zip(a, b)]) for b in digits]
             for a in digits]
    return plus, minus


def ball(n, radius=RADIUS, ops=None):
    """Rows are base-three integers; BFS keeps exact minimum distances."""
    require(type(n) is int and n in PERMUTATIONS, "unsupported dimension")
    require(type(radius) is int and 0 <= radius <= RADIUS, "radius outside closed domain")
    plus, minus = row_tables(n)
    ops = generators(n) if ops is None else ops
    identity = tuple(3 ** j for j in range(n))
    distance = {identity: 0}
    level = [identity]
    for depth in range(1, radius + 1):
        following = []
        for matrix in level:
            for target, source, sign in ops:
                value = (minus[0][matrix[target]] if target == source else
                         (plus if sign == 1 else minus)[matrix[target]][matrix[source]])
                other = matrix[:target] + (value,) + matrix[target + 1:]
                if other not in distance:
                    distance[other] = depth
                    following.append(other)
        level = following
    return distance


def encode_matrix(matrix):
    size = 3 ** len(matrix)
    return sum(row * size ** i for i, row in enumerate(matrix))


def ball_bytes(distance):
    return b"".join(struct.pack("<QB", key, depth) for key, depth in
                    sorted((encode_matrix(m), d) for m, d in distance.items()))


def right_permute(matrix, permutation):
    """M P, where row i of P is e_{permutation[i]}."""
    n = len(matrix)
    require(sorted(permutation) == list(range(n)), "invalid permutation")
    return tuple(sum(((row // 3 ** j) % 3) * 3 ** permutation[j]
                     for j in range(n)) for row in matrix)


def meeting(distance, permutation):
    require(sorted(permutation) == list(range(len(permutation))), "invalid permutation")
    # Precompute only row permutations; every matrix is still visited.
    n = len(permutation)
    table = [sum(((row // 3 ** j) % 3) * 3 ** permutation[j]
                 for j in range(n)) for row in range(3 ** n)]
    best = None
    meetings = Counter()
    for matrix, depth in distance.items():
        other = distance.get(tuple(table[row] for row in matrix))
        if other is not None:
            total = depth + other
            meetings[total] += 1
            best = total if best is None else min(best, total)
    return best, {str(k): v for k, v in sorted(meetings.items())}


def certificate(n, distance):
    minimum, meetings = meeting(distance, PERMUTATIONS[n])
    raw = ball_bytes(distance)
    return {"dimension": n, "radius": RADIUS, "generators": len(generators(n)),
            "target": list(PERMUTATIONS[n]), "states": len(distance),
            "layers": [sum(d == k for d in distance.values()) for k in range(RADIUS + 1)],
            "ball_format": "sorted little-endian uint64 ternary matrix, uint8 distance",
            "ball_sha256": sha256(raw).hexdigest(), "meetings_by_total_length": meetings,
            "minimum_if_at_most_eight": minimum,
            "lower_bound": minimum if minimum is not None else 9}
