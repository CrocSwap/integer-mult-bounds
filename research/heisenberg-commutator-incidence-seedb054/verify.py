#!/usr/bin/env python3
"""Exact small-instance checks for the bipartite commutator tariff."""

from itertools import product


M = N = 2
GROUP_SIZE = 1 << (M + N + M * N)
UNIT = 1
ZERO = 0


def split(g):
    return g & 3, (g >> 2) & 3, (g >> 4) & 15


def outer(u, v):
    z = 0
    for i in range(2):
        for j in range(2):
            if ((u >> i) & 1) and ((v >> j) & 1):
                z ^= 1 << (2 * i + j)
    return z


def group_mul(g, h):
    u, v, z = split(g)
    u2, v2, z2 = split(h)
    return (u ^ u2) | ((v ^ v2) << 2) | ((z ^ z2 ^ outer(u, v2)) << 4)


def basis(g):
    return 1 << g


def ring_mul(a, b):
    out = 0
    aa = a
    while aa:
        xa = aa & -aa
        ga = xa.bit_length() - 1
        aa ^= xa
        bb = b
        while bb:
            xb = bb & -bb
            gb = xb.bit_length() - 1
            bb ^= xb
            out ^= basis(group_mul(ga, gb))
    return out


def matrix_mul(a, b):
    r = len(a)
    out = [[ZERO for _ in range(r)] for _ in range(r)]
    for i in range(r):
        for k in range(r):
            if a[i][k] == ZERO:
                continue
            for j in range(r):
                if b[k][j] != ZERO:
                    out[i][j] ^= ring_mul(a[i][k], b[k][j])
    return out


def identity_matrix(r):
    return [[UNIT if i == j else ZERO for j in range(r)] for i in range(r)]


def xgen(i):
    return 1 << i


def ygen(j):
    return 1 << (2 + j)


def zgen(i, j):
    return 1 << (4 + 2 * i + j)


def rho(g, i, j):
    u, v, z = split(g)
    return (
        (1, (u >> i) & 1, (z >> (2 * i + j)) & 1),
        (0, 1, (v >> j) & 1),
        (0, 0, 1),
    )


def dual_rho(g, i, j):
    u, v, z = split(g)
    a = (u >> i) & 1
    b = (v >> j) & 1
    c = (z >> (2 * i + j)) & 1
    return (
        (1, 0, 0),
        (a, 1, 0),
        (c ^ (a & b), b, 1),
    )


def mat3_mul(a, b):
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) & 1 for j in range(3))
        for i in range(3)
    )


def target_matrix(multiplicities, r=None):
    target_roles = sum(sum(row) for row in multiplicities)
    if r is None:
        r = target_roles
    assert r >= target_roles
    out = identity_matrix(r)
    role = 0
    for i in range(2):
        for j in range(2):
            for _ in range(multiplicities[i][j]):
                out[role][role] = basis(zgen(i, j))
                role += 1
    return out


def direct_word(multiplicities):
    factors = []
    role = 0
    for i in range(2):
        for j in range(2):
            for _ in range(multiplicities[i][j]):
                for g in (xgen(i), ygen(j), xgen(i), ygen(j)):
                    factors.append((g, role))
                role += 1
    return factors


def run_word(factors, r):
    result = identity_matrix(r)
    for g, role in factors:
        factor = identity_matrix(r)
        # D_{E_role,role}(g) has the basis element [g] in that diagonal slot.
        factor[role][role] = basis(g)
        result = matrix_mul(result, factor)
    return result


def check_group_and_quotients():
    groups = range(GROUP_SIZE)
    # The cocycle identity certifies associativity of the declared multiplication.
    for u, u1, u2, v1, v2 in product(range(4), repeat=5):
        left = outer(u, v1) ^ outer(u ^ u1, v2)
        right = outer(u1, v2) ^ outer(u, v1 ^ v2)
        assert left == right

    for g in groups:
        u, v, z = split(g)
        inv = u | (v << 2) | ((z ^ outer(u, v)) << 4)
        assert group_mul(g, inv) == 0
        assert group_mul(inv, g) == 0
        for i, j in product(range(2), repeat=2):
            central = zgen(i, j)
            assert group_mul(g, central) == group_mul(central, g)

    assert len({zgen(i, j) for i, j in product(range(2), repeat=2)}) == 4
    for i, k in product(range(2), repeat=2):
        assert group_mul(xgen(i), xgen(k)) == group_mul(xgen(k), xgen(i))
    for j, l in product(range(2), repeat=2):
        assert group_mul(ygen(j), ygen(l)) == group_mul(ygen(l), ygen(j))

    pairs_checked = 0
    for i, j in product(range(2), repeat=2):
        for g in groups:
            for h in groups:
                gh = group_mul(g, h)
                assert rho(gh, i, j) == mat3_mul(rho(g, i, j), rho(h, i, j))
                assert dual_rho(gh, i, j) == mat3_mul(dual_rho(g, i, j), dual_rho(h, i, j))
                pairs_checked += 1

        for k, l in product(range(2), repeat=2):
            expected = ((1, 0, 1), (0, 1, 0), (0, 0, 1)) if (i, j) == (k, l) else ((1, 0, 0), (0, 1, 0), (0, 0, 1))
            expected_dual = ((1, 0, 0), (0, 1, 0), (1, 0, 1)) if (i, j) == (k, l) else ((1, 0, 0), (0, 1, 0), (0, 0, 1))
            assert rho(zgen(k, l), i, j) == expected
            assert dual_rho(zgen(k, l), i, j) == expected_dual

    for i, j in product(range(2), repeat=2):
        x, y, z = xgen(i), ygen(j), zgen(i, j)
        assert group_mul(group_mul(group_mul(x, y), x), y) == z
        assert group_mul(x, x) == group_mul(y, y) == 0
    return pairs_checked


def main():
    pair_checks = check_group_and_quotients()

    grid = ((1, 1), (1, 1))
    factors = direct_word(grid)
    target = target_matrix(grid)
    assert len(factors) == 16
    assert run_word(factors, 4) == target
    assert run_word(factors, 5) == target_matrix(grid, 5)

    omission_controls = 0
    for k in range(len(factors)):
        shortened = factors[:k] + factors[k + 1 :]
        assert run_word(shortened, 4) != target
        omission_controls += 1

    wrong = list(factors)
    wrong[0] = (xgen(1), wrong[0][1])
    assert run_word(wrong, 4) != target

    weighted = ((2, 1), (0, 3))
    weighted_factors = direct_word(weighted)
    weighted_r = sum(sum(row) for row in weighted)
    assert len(weighted_factors) == 4 * weighted_r == 24
    assert run_word(weighted_factors, weighted_r + 2) == target_matrix(weighted, weighted_r + 2)

    print(
        "PASS_HEISENBERG_BIPARTITE_COMMUTATOR "
        f"group={GROUP_SIZE} edge_quotient_pairs={pair_checks} "
        f"K22_targets=4 calls=16 omission_controls={omission_controls} "
        "dirty_spectator=preserved weighted_targets=6 calls=24 "
        "wrong_label=rejected"
    )


if __name__ == "__main__":
    main()
