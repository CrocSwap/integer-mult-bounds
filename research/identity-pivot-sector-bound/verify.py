#!/usr/bin/env python3
"""Exact finite corroboration of the written sector theorem over F_2.

Prepared for ssafwann with substantial OpenAI Codex assistance. Apache-2.0.
Tuple-matrix helpers adapt ssafwann's PR4657 (b79f90bc8d839a4998a40b10bcb437e87baa8397).
Factorization: Nick Petalas, PR4597; identity specialization: PR4657.
No external inputs, predecessor executable, random search or third-party library.
"""
import itertools
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def zero(rows, cols):
    return tuple((0,) * cols for _ in range(rows))


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def add(a, b):
    require(len(a) == len(b) and all(len(x) == len(y) for x, y in zip(a, b)), "addition shape")
    return tuple(tuple(x ^ y for x, y in zip(ar, br)) for ar, br in zip(a, b))


def mul(a, b):
    require(bool(a) and bool(b) and len(a[0]) == len(b), "multiplication shape")
    cols = tuple(zip(*b))
    return tuple(tuple(sum(x * y for x, y in zip(row, col)) % 2
                       for col in cols) for row in a)


def rank(a):
    if not a:
        return 0
    rows = [sum(x << j for j, x in enumerate(row)) for row in a]
    pivot = 0
    for col in range(len(a[0])):
        hit = next((i for i in range(pivot, len(rows)) if rows[i] >> col & 1), None)
        if hit is not None:
            rows[pivot], rows[hit] = rows[hit], rows[pivot]
            for i in range(pivot + 1, len(rows)):
                if rows[i] >> col & 1:
                    rows[i] ^= rows[pivot]
            pivot += 1
    return pivot


def inverse(a):
    n = len(a)
    require(n > 0 and all(len(row) == n for row in a), "inverse shape")
    rows = [list(row) + list(unit) for row, unit in zip(a, eye(n))]
    for col in range(n):
        hit = next((i for i in range(col, n) if rows[i][col]), None)
        require(hit is not None, "singular matrix")
        rows[col], rows[hit] = rows[hit], rows[col]
        for i in range(n):
            if i != col and rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[col])]
    return tuple(tuple(row[n:]) for row in rows)


def block(a, r0, r1, c0, c1):
    return tuple(tuple(row[c0:c1]) for row in a[r0:r1])


def hcat(*parts):
    require(bool(parts) and len({len(p) for p in parts}) == 1, "horizontal shape")
    return tuple(sum(rows, ()) for rows in zip(*parts))


def columns(vectors, n):
    return tuple(tuple(v[i] for v in vectors) for i in range(n))


def grid(rows):
    return sum((hcat(*row) for row in rows), ())


def diagonal(blocks):
    sizes = [len(b) for b in blocks]
    return grid([[b if i == j else zero(sizes[i], sizes[j])
                  for j, b in enumerate(blocks)] for i in range(len(blocks))])


def image_and_complement(t):
    d = len(t)
    image = []
    for v in zip(*t):
        if rank(columns(image + [v], d)) > len(image):
            image.append(v)
    basis = image[:]
    for v in eye(d):
        if rank(columns(basis + [v], d)) > len(basis):
            basis.append(v)
    require(len(basis) == d, "basis extension")
    return image, basis[len(image):]


def factor(t, mode="full"):
    """X,Y with XY=T; full means X onto and Y one-to-one."""
    d = len(t)
    image, complement = image_and_complement(t)
    if mode == "full":
        return hcat(t, columns(complement, d)), eye(d) + zero(len(complement), d)
    if mode == "thin":
        change = columns(image + complement, d)
        coordinates = mul(inverse(change), t)
        return columns(image, d), coordinates[:len(image)]
    if mode == "only_injective":
        return t, eye(d)
    if mode == "only_surjective":
        return eye(d), t
    raise ValueError("unknown factor mode")


def kernel(a):
    """Columns form a basis of ker(a); a must have independent rows."""
    rows = [list(row) for row in a]
    m, n = len(rows), len(rows[0])
    pivots = []
    for col in range(n):
        hit = next((i for i in range(len(pivots), m) if rows[i][col]), None)
        if hit is None:
            continue
        p = len(pivots)
        rows[p], rows[hit] = rows[hit], rows[p]
        for i in range(m):
            if i != p and rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[p])]
        pivots.append(col)
    require(len(pivots) == m, "kernel input full row rank")
    vectors = []
    for free in range(n):
        if free not in pivots:
            v = [0] * n
            v[free] = 1
            for row, pivot in enumerate(pivots):
                v[pivot] = rows[row][free]
            vectors.append(tuple(v))
    return columns(vectors, n)


def construct(h, alteration=None):
    d = len(h)
    require(d > 0 and all(len(row) == d for row in h), "H square")
    w = add(eye(d), h)
    factors = [factor(w, "thin"), factor(w), factor(w), factor(h)]
    if alteration is not None:
        sector, mode = alteration
        require(sector in (1, 2, 3), "active sector index")
        factors[sector] = factor(h if sector == 3 else w, mode)
    pi = hcat(*(x for x, _ in factors))
    inclusion = sum((y for _, y in factors), ())
    require(mul(pi, inclusion) == eye(d), "split inclusion")
    change = hcat(inclusion, kernel(pi))
    back = inverse(change)
    sizes = [len(y) for _, y in factors]
    p0 = diagonal([zero(sizes[0], sizes[0]), eye(sizes[1]),
                   zero(sizes[2], sizes[2]), eye(sizes[3])])
    q0 = diagonal([zero(sizes[0], sizes[0]), zero(sizes[1], sizes[1]),
                   eye(sizes[2]), eye(sizes[3])])
    return mul(mul(back, p0), change), mul(mul(back, q0), change)


def inspect_pair(p, q, d):
    n = len(p)
    require(0 < d < n <= 65 and len(q) == n, "pair dimensions")
    require(all(len(row) == n for a in (p, q) for row in a), "square pair")
    require(all(type(x) is int and x in (0, 1)
                for a in (p, q) for row in a for x in row), "binary entries")
    require(block(p, 0, d, 0, d) == eye(d) and
            block(q, 0, d, 0, d) == eye(d), "identity pivots")
    require(mul(p, p) == p and mul(q, q) == q, "idempotence")
    pq = mul(p, q)
    require(pq == mul(q, p), "commutation")
    r, c, dd = block(p, 0, d, d, n), block(p, d, n, 0, d), block(p, d, n, d, n)
    l, e, f = block(q, 0, d, d, n), block(q, d, n, 0, d), block(q, d, n, d, n)
    s, z = add(dd, mul(c, r)), add(f, mul(e, l))
    k = add(mul(s, z), mul(z, s))
    h = block(pq, 0, d, 0, d)
    w = add(eye(d), h)
    a, b = d - rank(h), d - rank(w)
    t = d - rank(add(h, mul(h, h)))
    require(t == a + b, "coprime kernel sum")
    left = hcat(mul(z, c), add(c, e))
    right = add(r, l) + mul(r, z)
    require(mul(left, right) == k, "Schur factorization")
    # Recompute factors in the ambient space, without Schur blocks.
    qi = block(q, 0, n, 0, d)
    pqi = block(pq, 0, n, 0, d)
    ambient_a = hcat(add(pqi, mul(qi, h)), block(add(p, q), 0, n, 0, d))
    ambient_b = block(add(p, q), 0, d, 0, n) + add(
        block(pq, 0, d, 0, n), mul(h, block(q, 0, d, 0, n)))
    require(block(ambient_a, 0, d, 0, 2 * d) == zero(d, 2 * d), "A lands in ker pi")
    require(block(ambient_b, 0, 2 * d, 0, d) == zero(2 * d, d), "B kills inclusion")
    require(block(ambient_a, d, n, 0, 2 * d) == left, "ambient A")
    require(block(ambient_b, 0, 2 * d, d, n) == right, "restricted B")
    sectors = [add(add(eye(n), p), add(q, pq)), add(p, pq), add(q, pq), pq]
    expected_a = [zero(d, 2 * d), hcat(zero(d, d), eye(d)),
                  hcat(h, eye(d)), hcat(w, zero(d, d))]
    expected_b = [zero(2 * d, d), eye(d) + zero(d, d),
                  eye(d) + h, zero(d, d) + w]
    sizes, maps = [], []
    for j, sector in enumerate(sectors):
        require(mul(sector, sector) == sector, "joint projector")
        require(block(sector, 0, d, 0, d) == (h if j == 3 else w), "compression")
        for other in sectors[:j]:
            require(mul(sector, other) == zero(n, n), "joint annihilation")
        y, x = block(sector, 0, n, 0, d), block(sector, 0, d, 0, n)
        require(mul(sector, ambient_a) == mul(y, expected_a[j]), "sector A")
        require(mul(ambient_b, sector) == mul(expected_b[j], x), "sector B")
        sizes.append(rank(sector))
        if j:
            maps.append([rank(y), rank(x)])
    require(sum(sizes) == n, "direct sector dimensions")
    sharp = rank(k) == 2 * d
    require(rank(k) <= 2 * d, "rank ceiling")
    require(sharp == all(y == x == d for y, x in maps), "six-map equivalence")
    if sharp:
        require(rank(left) == rank(right) == 2 * d, "full factor ranks")
        floors = [d - b, d + b, d + b, d + a]
        require(all(rj >= floor for rj, floor in zip(sizes, floors)), "sector floors")
        require(n >= 4 * d + t, "fixed-H dimension bound")
    return {"d": d, "n": n, "H": h, "nullities": [a, b, t],
            "commutator_rank": rank(k), "sector_dimensions": sizes,
            "active_map_ranks_Y_X": maps}


def check_construction(h):
    d = len(h)
    p, q = construct(h)
    receipt = inspect_pair(p, q, d)
    a, b, t = receipt["nullities"]
    require(receipt["H"] == h, "prescribed product compression")
    require(receipt["commutator_rank"] == 2 * d, "attainment")
    require(receipt["sector_dimensions"] == [d - b, d + b, d + b, d + a], "minimal sectors")
    require(receipt["n"] == 4 * d + t, "exact fixed-H minimum")
    require(rank(p) == rank(q) == 2 * d + t, "minimal projector ranks")
    return receipt


def all_binary(d):
    for bits in range(1 << (d * d)):
        yield tuple(tuple(bits >> (i * d + j) & 1 for j in range(d)) for i in range(d))


def exhaustive_small_pairs(n, d):
    candidates = [a for a in all_binary(n)
                  if block(a, 0, d, 0, d) == eye(d) and mul(a, a) == a]
    counts = {}
    for p, q in itertools.product(candidates, repeat=2):
        if mul(p, q) == mul(q, p):
            receipt = inspect_pair(p, q, d)
            key = str(receipt["commutator_rank"])
            counts[key] = counts.get(key, 0) + 1
    return {"n": n, "d": d, "idempotents": len(candidates), "rank_histogram": counts}


def rejects(label, call):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("control did not reject: " + label)


# lee-phys's PR4634 seeds, also reused in PR4657.
H2 = ((0, 1), (1, 1))
H3 = ((0, 0, 1), (1, 0, 1), (0, 1, 0))
JORDAN3 = ((0, 1, 0), (0, 0, 1), (0, 0, 0))

# Literal singular-product witness, also printed in README.md.
P13 = tuple(tuple(map(int, row)) for row in (
    "1001100000100", "0100110000010", "0010010000001",
    "0000100000100", "0000010000010", "0000000000001",
    "1001100000100", "0100110000010", "0010010000001",
    "0001100001100", "0000110000110", "0000010000011", "0000000000001"))
Q13 = tuple(tuple(map(int, row)) for row in (
    "1000001100100", "0100000110010", "0010000010001",
    "1000001100100", "0100000110010", "0010000010001",
    "0000000100100", "0000000010010", "0000000000001",
    "0000001101100", "0000000110110", "0000000010011", "0000000000001"))


def main():
    distributions = {}
    for d in (1, 2, 3):
        counts = {}
        for h in all_binary(d):
            r = check_construction(h)
            key = str(r["n"])
            counts[key] = counts.get(key, 0) + 1
        distributions[str(d)] = counts
    require(sum(distributions["3"].values()) == 512, "complete seed domain")
    family = []
    for d in range(2, 13):
        h = diagonal(([H3] if d % 2 else []) + [H2] * ((d - 3 * (d % 2)) // 2))
        r = check_construction(h)
        require(r["n"] == 4 * d, "identity-pivot minimum")
        family.append([d, r["n"]])
    singular = check_construction(JORDAN3)
    p, q = construct(JORDAN3)
    require((p, q) == (P13, Q13), "literal witness agrees with constructor")
    require(inspect_pair(P13, Q13, 3) == singular, "literal witness direct check")
    padded = inspect_pair(diagonal([p, zero(2, 2)]), diagonal([q, zero(2, 2)]), 3)
    require(padded["commutator_rank"] == 6 and padded["n"] == 15, "padding")
    controls = []
    for sector in (1, 2, 3):
        h = zero(1, 1) if sector == 3 else eye(1)
        for mode in ("only_injective", "only_surjective"):
            rp, rq = construct(h, (sector, mode))
            r = inspect_pair(rp, rq, 1)
            deficient = 1 if mode == "only_injective" else 0
            require(r["active_map_ranks_Y_X"][sector - 1][deficient] == 0, "intended deficiency")
            require(sum(v < 1 for pair in r["active_map_ranks_Y_X"] for v in pair) == 1,
                    "exactly one missing map condition")
            controls.append(rejects(f"sector-{sector}-{mode}", lambda r=r: require(
                r["commutator_rank"] == 2, "false sharpness")))
    p8, q8 = construct(H2)
    controls.append(rejects("nonbinary", lambda: inspect_pair(
        ((2,) + p8[0][1:],) + p8[1:], q8, 2)))
    controls.append(rejects("false-universal-4d-attainment", lambda: require(
        singular["n"] == 12, "singular surcharge")))
    controls.append(rejects("false-singular-H-exclusion", lambda: require(
        singular["nullities"][2] == 0, "singular H is admissible with extra space")))
    # PR4634 formula: invertible nonidentity pivots permit n=3d.
    w = add(eye(2), H2)
    p6 = grid([[w, w, H2], [H2, H2, H2], [zero(2, 2), zero(2, 2), eye(2)]])
    q6 = grid([[w, H2, w], [zero(2, 2), eye(2), zero(2, 2)], [H2, H2, H2]])
    require(mul(p6, p6) == p6 and mul(q6, q6) == q6 and mul(p6, q6) == mul(q6, p6),
            "nonidentity control: valid commuting idempotents")
    require(rank(w) == 2 and w != eye(2), "nonidentity invertible control")
    controls.append(rejects("identity-pivot-premise", lambda: inspect_pair(p6, q6, 2)))
    pairs = [exhaustive_small_pairs(3, 1), exhaustive_small_pairs(4, 2)]
    require(pairs[0]["rank_histogram"] == {"0": 241, "1": 12}, "pair count 3,1")
    require(pairs[1]["rank_histogram"] == {"0": 1147, "1": 72}, "pair count 4,2")
    print(json.dumps({"all_H_dimension_distributions": distributions,
                      "optimal_family": family, "nilpotent_3_by_3": singular,
                      "small_pairs": pairs, "rejection_controls": controls}, sort_keys=True))
    print("PASS_IDENTITY_PIVOT_SECTOR_BOUND")


if __name__ == "__main__":
    main()
