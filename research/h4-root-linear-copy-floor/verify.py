"""Exact H4 finite premises. Standard library, no solver or external inputs."""
from collections import Counter
from functools import reduce
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from operator import xor

ZERO = (0, 0)
ALL = (1 << 60) - 1
CLIQUES = [
    [8, 9, 14, 23, 24, 26, 27, 28, 35, 39, 40, 43, 44],
    [2, 8, 11, 22, 24, 26, 28, 33, 35, 39, 44, 48, 51],
    [7, 9, 10, 12, 14, 18, 23, 27, 40, 42, 43, 44, 52],
    [0, 2, 5, 11, 12, 19, 22, 33, 39, 45, 48, 51, 55],
    [0, 5, 7, 10, 12, 18, 19, 22, 23, 42, 45, 52, 55],
]
ODD = [12, 22, 23, 39, 44]
PARTITION = [
    [0, 1, 14, 59], [2, 18, 34, 41], [4, 19, 38, 44],
    [5, 17, 31, 40], [6, 26, 32, 45], [3, 22, 37, 43],
    [9, 25, 33, 46], [7, 20, 35, 58], [8, 21, 36, 55],
    [10, 24, 29, 49], [11, 16, 27, 57], [12, 15, 28, 56],
    [13, 23, 30, 48], [39, 50, 52, 54], [42, 47, 51, 53],
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def mul(x, y):
    a, b = x
    c, d = y
    return a * c + b * d, a * d + b * c + b * d


def dot(x, y):
    terms = [mul(a, b) for a, b in zip(x, y)]
    return sum(a for a, _ in terms), sum(b for _, b in terms)


def negate(vector):
    return tuple((-a, -b) for a, b in vector)


def mask(indices):
    return sum(1 << i for i in indices)


def geometry():
    vectors = []
    for i in range(4):
        for sign in (-1, 1):
            v = [ZERO] * 4
            v[i] = (2 * sign, 0)
            vectors.append(tuple(v))
    vectors.extend(tuple((s, 0) for s in signs)
                   for signs in product((-1, 1), repeat=4))
    base = (ZERO, (1, 0), (0, 1), (-1, 1))
    for order in permutations(range(4)):
        if sum(order[i] > order[j] for i in range(4) for j in range(i + 1, 4)) % 2:
            continue
        for signs in product((-1, 1), repeat=3):
            v = [ZERO] + [(a * s, b * s) for (a, b), s in zip(base[1:], signs)]
            vectors.append(tuple(v[i] for i in order))
    need(len(vectors) == len(set(vectors)) == 120, "root count")
    roots = sorted({max(v, negate(v)) for v in vectors})
    need(len(roots) == 60, "line count")
    need(all(dot(r, r) == (4, 0) for r in roots), "root norm")
    orth = [mask(j for j, y in enumerate(roots) if i != j and dot(x, y) == ZERO)
            for i, x in enumerate(roots)]
    need(all(x.bit_count() == 15 for x in orth), "orthogonal degree")
    return roots, orth


def rank2(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)


def check_clique(roots, clique, allowed, size):
    need(len(clique) == len(set(clique)) == size, "clique size")
    need(all(0 <= i < 60 and (allowed >> i) & 1 for i in clique), "clique support")
    need(all(dot(roots[i], roots[j]) != ZERO for i, j in combinations(clique, 2)),
         "clique has an orthogonal pair")


def check_syndrome(roots, cliques, odd):
    need(len(cliques) == 5, "five cliques required")
    for clique in cliques:
        check_clique(roots, clique, ALL, 13)
    check_clique(roots, odd, ALL, 5)
    need(reduce(xor, map(mask, cliques)) == mask(odd), "odd incidence")


def check_partition(roots, partition):
    need(sorted(i for block in partition for i in block) == list(range(60)), "partition")
    need(len(partition) == 15 and all(len(block) == 4 for block in partition), "tetrads")
    need(all(dot(roots[i], roots[j]) == ZERO
             for block in partition for i, j in combinations(block, 2)), "orthogonal tetrad")
    rows = [next(mask(block) for block in partition if i in block) for i in range(60)]
    need(rank2(rows) == 15, "partition fitting rank")


def determinant(rows):
    out = [0, 0]
    for p in permutations(range(len(rows))):
        sign = (-1) ** sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p)))
        term = (1, 0)
        for i, j in enumerate(p):
            term = mul(term, rows[i][j])
        out[0] += sign * term[0]
        out[1] += sign * term[1]
    return tuple(out)


def normal(rows):
    return tuple(tuple((-1) ** col * x for x in determinant(
        [row[:col] + row[col + 1:] for row in rows])) for col in range(4))


def hyperplanes(roots):
    flats = {}
    for indices in combinations(range(60), 3):
        rows = [roots[i] for i in indices]
        n = normal(rows)
        if all(x == ZERO for x in n):
            continue
        need(all(dot(n, row) == ZERO for row in rows), "cofactor annihilation")
        flat = mask(i for i, root in enumerate(roots) if dot(n, root) == ZERO)
        flats.setdefault(flat, n)
    need(Counter(x.bit_count() for x in flats) == {4: 600, 6: 660, 15: 60}, "flat census")
    return flats


def reflection_orbits(roots, flats):
    index = {r: i for i, r in enumerate(roots)}
    generators = []
    for root in roots:
        permutation = []
        for source in roots:
            products = [mul(dot(source, root), x) for x in root]
            need(all(a % 2 == b % 2 == 0 for a, b in products), "reflection integral")
            target = tuple((a - c // 2, b - d // 2)
                           for (a, b), (c, d) in zip(source, products))
            permutation.append(index[max(target, negate(target))])
        need(sorted(permutation) == list(range(60)), "reflection permutation")
        need(all(permutation[permutation[i]] == i for i in range(60)), "reflection involution")
        generators.append(permutation)
    def transport(flat, permutation):
        return mask(permutation[i] for i in range(60) if flat >> i & 1)
    remaining = set(flats)
    orbits = []
    while remaining:
        representative = min(remaining)
        orbit, queue = {representative}, [representative]
        for flat in queue:
            for permutation in generators:
                target = transport(flat, permutation)
                need(target in flats, "reflection hyperplane closure")
                if target not in orbit:
                    orbit.add(target)
                    queue.append(target)
        need(orbit <= remaining, "disjoint orbits")
        remaining -= orbit
        orbits.append((representative, len(orbit)))
    need(sorted((f.bit_count(), n) for f, n in orbits)
         == [(4, 600), (6, 300), (6, 360), (15, 60)], "orbit census")
    return orbits


def clique_witness(adjacency, allowed, size):
    # Search only produces witnesses; check_clique separately validates each.
    def search(candidates, chosen):
        if len(chosen) == size:
            return chosen
        order, colors, remaining, color = [], [], candidates, 0
        while remaining:
            color += 1
            available = remaining
            while available:
                low = available & -available
                v = low.bit_length() - 1
                order.append(v)
                colors.append(color)
                remaining ^= low
                available &= ~low & ~adjacency[v]
        for j in range(len(order) - 1, -1, -1):
            if len(chosen) + colors[j] < size:
                return None
            v = order[j]
            answer = search(candidates & adjacency[v], chosen + [v])
            if answer is not None:
                return answer
            candidates &= ~(1 << v)
        return None
    answer = search(allowed, [])
    need(answer is not None, "support witness absent")
    return answer


def budget(denominator=2900):
    # 60(14s+1)(s-1) - denominator(8s-60) is positive for all real s.
    a, b, c = 840, -780 - 8 * denominator, -60 + 60 * denominator
    need(a > 0 and b * b - 4 * a * c < 0, "uniform deficit bound")
    need(2 * 2899 ** 2000 > 2900 ** 2000, "exact a=1/1000 rejection")
    return b * b - 4 * a * c


def main():
    need(mul((0, 1), (0, 1)) == (1, 1), "golden field arithmetic")
    roots, orth = geometry()
    check_syndrome(roots, CLIQUES, ODD)
    check_partition(roots, PARTITION)
    need(determinant([roots[i] for i in [0, 1, 14, 59]]) != ZERO, "rank four")
    flats = hyperplanes(roots)
    orbits = reflection_orbits(roots, flats)
    adjacency = [ALL ^ x ^ (1 << i) for i, x in enumerate(orth)]
    receipt, counts = [], Counter()
    for left, orbit_size in orbits:
        for right in sorted(flats):
            nonorthogonal = dot(flats[left], flats[right]) != ZERO
            size = 13 if nonorthogonal else 10
            allowed = ALL & ~(left | right)
            clique = clique_witness(adjacency, allowed, size)
            check_clique(roots, clique, allowed, size)
            receipt.append([left, right, size, clique])
            counts[size] += orbit_size
    need(counts == {10: 82920, 13: 1659480}, "support pair census")
    discriminant = budget()
    rejected = 0
    def reject(function):
        nonlocal rejected
        try:
            function()
        except ValueError:
            rejected += 1
        else:
            raise ValueError("corruption was accepted")
    reject(lambda: check_clique(roots, CLIQUES[0][:-1] + [CLIQUES[0][0]], ALL, 13))
    reject(lambda: check_clique(roots, CLIQUES[0], ALL ^ (1 << CLIQUES[0][0]), 13))
    reject(lambda: check_clique(roots, PARTITION[0], ALL, 4))
    reject(lambda: check_syndrome(roots, CLIQUES[:-1] + [CLIQUES[0]], ODD))
    reject(lambda: check_syndrome(roots, CLIQUES, ODD[:-1]))
    reject(lambda: check_partition(roots, PARTITION[:-1] + [PARTITION[0]]))
    reject(lambda: check_partition(roots, [CLIQUES[0][:4]] + PARTITION[1:]))
    reject(lambda: budget(3000))
    need(rejected == 8, "negative controls")
    print(json.dumps({
        "status": "PASS_H4_ROOT_LINEAR_COPY_FLOOR",
        "roots": 120, "lines": 60, "characteristic_two_block_minrank": "15k",
        "hyperplanes": len(flats), "ordered_support_pairs": dict(counts),
        "verified_representative_pairs": len(receipt), "root_linear_copy_floor": 52,
        "primitive_ceiling": "a < 1/1000 under the stated template",
        "budget_discriminant": discriminant, "negative_controls": rejected,
        "support_receipt_sha256": sha256(json.dumps(receipt, separators=(",", ":")).encode()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
