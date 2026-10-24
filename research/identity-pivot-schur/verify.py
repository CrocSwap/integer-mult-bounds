#!/usr/bin/env python3
"""Exact binary matrix corroboration; ssafwann with OpenAI Codex, Apache-2.0.

No predecessor executable, external input, numerical library or random search.
The all-d claims are proved in README.md, not inferred from these finite checks.
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
    require(len(a) == len(b) and len(a[0]) == len(b[0]), "addition shape")
    return tuple(tuple(x ^ y for x, y in zip(ar, br)) for ar, br in zip(a, b))


def mul(a, b):
    require(len(a[0]) == len(b), "multiplication shape")
    cols = tuple(zip(*b))
    return tuple(tuple(sum(x * y for x, y in zip(row, col)) % 2
                       for col in cols) for row in a)


def rank(a):
    rows = [sum(x << j for j, x in enumerate(row)) for row in a]
    pivot = 0
    for col in range(len(a[0])):
        hit = next((i for i in range(pivot, len(rows)) if rows[i] >> col & 1), None)
        if hit is None:
            continue
        rows[pivot], rows[hit] = rows[hit], rows[pivot]
        for i in range(pivot + 1, len(rows)):
            if rows[i] >> col & 1:
                rows[i] ^= rows[pivot]
        pivot += 1
    return pivot


def inverse(a):
    n = len(a)
    require(all(len(row) == n for row in a), "inverse shape")
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


def hcat(a, b):
    require(len(a) == len(b), "horizontal shape")
    return tuple(x + y for x, y in zip(a, b))


def grid(rows):
    result = ()
    for row in rows:
        line = row[0]
        for part in row[1:]:
            line = hcat(line, part)
        result += line
    return result


def diagonal(blocks):
    sizes = [len(b) for b in blocks]
    return grid([[b if i == j else zero(sizes[i], sizes[j])
                  for j, b in enumerate(blocks)] for i in range(len(blocks))])


def validate_pair(p, q, d):
    n = len(p)
    require(0 < d < n <= 52 and len(q) == n, "matrix capacity or split")
    require(all(len(row) == n for a in (p, q) for row in a), "square pair")
    require(all(type(x) is int and x in (0, 1)
                for a in (p, q) for row in a for x in row), "binary entries")
    require(block(p, 0, d, 0, d) == eye(d), "P identity pivot")
    require(block(q, 0, d, 0, d) == eye(d), "Q identity pivot")
    require(mul(p, p) == p and mul(q, q) == q, "idempotence")
    require(mul(p, q) == mul(q, p), "commutation")


def dimension_lower_bound(d):
    return min(max(3 * d + 2 * t, 4 * d - 3 * t) for t in range(d + 1))


def inspect_pair(p, q, d):
    validate_pair(p, q, d)
    n, k = len(p), len(p) - d
    r, c, a = block(p, 0, d, d, n), block(p, d, n, 0, d), block(p, d, n, d, n)
    l, e, b = block(q, 0, d, d, n), block(q, d, n, 0, d), block(q, d, n, d, n)
    s, z = add(a, mul(c, r)), add(b, mul(e, l))
    comm = add(mul(s, z), mul(z, s))
    require(mul(s, s) == s and mul(z, z) == z, "Schur idempotence")
    require(rank(p) == d + rank(s) and rank(q) == d + rank(z), "Schur ranks")
    h = block(mul(p, q), 0, d, 0, d)
    j = add(h, mul(h, h))
    u, v = add(c, e), add(r, l)
    left = hcat(mul(z, c), u)
    right = v + mul(r, z)
    require(mul(left, right) == comm, "ordered commutator factorization")
    reverse = grid([[j, zero(d, d)], [j, j]])
    require(mul(right, left) == reverse, "reverse-product identity")
    pq = mul(p, q)
    sectors = [pq, add(p, pq), add(q, pq), add(add(eye(n), p), add(q, pq))]
    tops = [h] + [add(eye(d), h)] * 3
    for i, sector in enumerate(sectors):
        require(mul(sector, sector) == sector, "joint sector idempotence")
        require(block(sector, 0, d, 0, d) == tops[i], "joint compression")
        for other in sectors[:i]:
            require(mul(sector, other) == zero(n, n), "joint orthogonality")
    require(sum(map(rank, sectors)) == n, "joint direct-sum dimensions")
    rk = rank(comm)
    defect = d - rank(j)
    a, b = d - rank(h), d - rank(add(eye(d), h))
    require(a + b == defect, "coprime-factor kernel dimensions")
    require(rank(mul(right, left)) == 2 * rank(j), "reverse-product rank")
    require(rk <= min(2 * d, k), "universal rank bound")
    if n == 3 * d:
        require(rk < 2 * d, "identity-pivot 3d obstruction")
    if rank(j) == d:
        require(rk == 2 * d, "invertible reverse product implies sharpness")
        require(all(rank(t) >= d for t in sectors), "four-sector lower bound")
        require(n >= 4 * d, "invertible-J dimension bound")
    if rk == 2 * d:
        require(rank(left) == rank(right) == 2 * d, "sharp factor ranks")
        require(n >= 3 * d + 2 * defect, "Sylvester lower bound")
        require(n >= 4 * d - a - 3 * b, "joint-sector lower bound")
        require(n >= dimension_lower_bound(d), "integer dimension bound")
        require(5 * n >= 17 * d, "17d/5 lower bound")
    return {"n": n, "d": d, "commutator_rank": rk, "J_rank": rank(j),
            "J_nullity": defect, "dimension_lower_bound": dimension_lower_bound(d),
            "sector_ranks": list(map(rank, sectors))}, (left, right, comm, reverse)


H2 = ((0, 1), (1, 1))
H3 = ((0, 0, 1), (1, 0, 1), (0, 1, 0))

# Literal new witness, also printed in README.md.
P8 = tuple(tuple(map(int, row)) for row in (
    "10110011", "01100010", "10110011", "01100010",
    "00111011", "00100110", "10110011", "01100010"))
Q8 = tuple(tuple(map(int, row)) for row in (
    "10111100", "01101000", "10111100", "01101000",
    "10111100", "01101000", "00111110", "00101001"))

# Ryanson Jonathan's PR4609 witness, transcribed from PR4617 verify.py
# at 96c01a2124e234d798e9e97643c20fb5b430840d (Apache-2.0).
# It prevents extending the square-factor argument to rectangular factors.
P5 = ((1, 1, 0, 0, 0), (0, 0, 0, 0, 0), (1, 0, 1, 1, 1),
      (0, 0, 0, 1, 0), (1, 1, 0, 1, 0))
Q5 = ((1, 1, 1, 0, 0), (1, 0, 0, 1, 1), (1, 0, 0, 1, 1),
      (1, 0, 1, 0, 1), (1, 1, 0, 1, 0))


def seed(d):
    require(d >= 2, "seed dimension at least two")
    return diagonal(([H3] if d % 2 else []) + [H2] * ((d - (3 if d % 2 else 0)) // 2))


def construct(h):
    d = len(h)
    ident, blank = eye(d), zero(d, d)
    require(rank(h) == d and rank(add(h, ident)) == d, "H and I+H invertible")
    w = mul(inverse(h), add(ident, h))
    change = grid([[ident, ident, blank, blank], [ident, blank, ident, blank],
                   [ident, blank, blank, ident], [ident, w, w, w]])
    back = inverse(change)
    p0 = diagonal([blank, ident, blank, ident])
    q0 = diagonal([blank, blank, ident, ident])
    return mul(mul(back, p0), change), mul(mul(back, q0), change)


def exhaustive_pairs(n, d):
    """All binary matrices, then all ordered admissible idempotent pairs."""
    candidates = []
    for bits in range(1 << (n * n)):
        a = tuple(tuple(bits >> (i * n + j) & 1 for j in range(n)) for i in range(n))
        if block(a, 0, d, 0, d) == eye(d) and mul(a, a) == a:
            candidates.append(a)
    counts = {}
    for p, q in itertools.product(candidates, repeat=2):
        if mul(p, q) != mul(q, p):
            continue
        receipt, _ = inspect_pair(p, q, d)
        rk = receipt["commutator_rank"]
        counts[str(rk)] = counts.get(str(rk), 0) + 1
    return {"n": n, "d": d, "idempotents_with_identity_pivot": len(candidates),
            "ordered_commuting_pair_rank_histogram": counts}


def rejects(label, thunk):
    try:
        thunk()
    except ValueError:
        return label
    raise ValueError("control was accepted: " + label)


def toggle(a, i, j):
    rows = [list(row) for row in a]
    rows[i][j] ^= 1
    return tuple(map(tuple, rows))


def check_controls(p, q, factors):
    left, right, comm, reverse = factors
    bad_q = None
    for i, j in itertools.combinations(range(2, 8), 2):
        perm = list(range(8))
        perm[i], perm[j] = perm[j], perm[i]
        candidate = tuple(tuple(q[a][b] for b in perm) for a in perm)
        if mul(p, candidate) != mul(candidate, p):
            bad_q = candidate
            break
    require(bad_q is not None, "noncommuting fixture exists")
    require(mul(bad_q, bad_q) == bad_q and block(bad_q, 0, 2, 0, 2) == eye(2),
            "noncommuting control preserves its other premises")
    return [
        rejects("nonidentity pivot", lambda: inspect_pair(toggle(p, 0, 1), q, 2)),
        rejects("broken idempotence", lambda: inspect_pair(toggle(p, 2, 2), q, 2)),
        rejects("commutation with both projectors and pivots preserved",
                lambda: inspect_pair(p, bad_q, 2)),
        rejects("singular H", lambda: construct(zero(2, 2))),
        rejects("singular I+H", lambda: construct(eye(2))),
        rejects("nonzero singular H", lambda: construct(((1, 0), (0, 0)))),
        rejects("nonbinary entry", lambda: inspect_pair(((2,) + p[0][1:],) + p[1:], q, 2)),
        rejects("omitted first commutator factor", lambda: require(
            mul(hcat(zero(6, 2), block(left, 0, 6, 2, 4)), right) == comm,
            "omitting ZC changes commutator")),
        rejects("omitted lower-left J", lambda: require(
            mul(right, left) == grid([[block(reverse, 0, 2, 0, 2), zero(2, 2)],
                                     [zero(2, 2), block(reverse, 2, 4, 2, 4)]]),
            "lower-left J is necessary")),
        rejects("zero commutator claimed sharp", lambda: require(
            inspect_pair(p, p, 2)[0]["commutator_rank"] == 4, "sharpness")),
    ]


def main():
    families = []
    for d in range(2, 13):
        p, q = construct(seed(d))
        receipt, _ = inspect_pair(p, q, d)
        require(receipt["commutator_rank"] == 2 * d and receipt["J_rank"] == d,
                "constructed family sharpness")
        require(receipt["sector_ranks"] == [d] * 4, "constructed sector dimensions")
        families.append(receipt)
    seed_counts = {}
    for d in (2, 3):
        count = 0
        for bits in range(1 << (d * d)):
            h = tuple(tuple(bits >> (i * d + j) & 1 for j in range(d)) for i in range(d))
            if rank(h) == d and rank(add(h, eye(d))) == d:
                p, q = construct(h)
                require(inspect_pair(p, q, d)[0]["commutator_rank"] == 2 * d,
                        "admissible seed sharpness")
                count += 1
        require(count == {2: 2, 3: 48}[d], "admissible seed census")
        seed_counts[str(d)] = count
    p, q = construct(H2)
    require((p, q) == (P8, Q8), "literal eight-dimensional witness")
    receipt, factors = inspect_pair(p, q, 2)
    padded = inspect_pair(diagonal([p, zero(3, 3)]), diagonal([q, zero(3, 3)]), 2)[0]
    require(padded["commutator_rank"] == 4, "padding retains sharpness")
    controls = check_controls(p, q, factors)
    predecessor, _ = inspect_pair(P5, Q5, 1)
    require(predecessor["commutator_rank"] == 2 and predecessor["J_rank"] == 0,
            "predecessor rectangular-factor boundary")
    controls.append(rejects("sharpness does not imply invertible J for rectangular factors",
                           lambda: require(predecessor["J_rank"] == 1, "J may be singular")))
    # Direct sum with the pivot coordinates moved first: a singular-J case at d=3.
    order = [0, 5, 6] + list(range(1, 5)) + list(range(7, 13))
    mixed_p, mixed_q = diagonal([P5, P8]), diagonal([Q5, Q8])
    mixed_p = tuple(tuple(mixed_p[i][j] for j in order) for i in order)
    mixed_q = tuple(tuple(mixed_q[i][j] for j in order) for i in order)
    mixed, _ = inspect_pair(mixed_p, mixed_q, 3)
    require(mixed["commutator_rank"] == 6 and mixed["J_nullity"] == 1,
            "nonzero-J singular reverse product")
    require(dimension_lower_bound(2) == 8 and dimension_lower_bound(3) == 11,
            "small integer dimension bounds")
    report = {"scope": "finite corroboration of README proof; no new kappa",
              "family": families, "all_admissible_seeds": seed_counts,
              "exhaustive_pairs": [exhaustive_pairs(3, 1), exhaustive_pairs(4, 2)],
              "padded": padded, "controls_rejected": controls,
              "credited_PR4617_boundary_control": predecessor,
              "mixed_singular_J_fixture": mixed,
              "literal_d2": {"P": ["".join(map(str, row)) for row in p],
                             "Q": ["".join(map(str, row)) for row in q]}}
    print(json.dumps(report, indent=2, sort_keys=True))
    print("PASS_IDENTITY_PIVOT_SCHUR")


if __name__ == "__main__":
    main()
