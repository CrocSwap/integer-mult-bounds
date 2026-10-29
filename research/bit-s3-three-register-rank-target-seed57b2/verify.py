#!/usr/bin/env python3
"""Exact algebra checks for a representation-rank lower bound in F2[S3]."""

from itertools import permutations


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(matrix):
    a = [list(row) for row in matrix]
    rows = len(a)
    cols = len(a[0]) if rows else 0
    pivot_row = 0
    for col in range(cols):
        pivot = next((i for i in range(pivot_row, rows) if a[i][col] & 1), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        for i in range(rows):
            if i != pivot_row and (a[i][col] & 1):
                a[i] = [x ^ y for x, y in zip(a[i], a[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def mul2(a, b):
    return tuple(tuple((sum(a[i][k] * b[k][j] for k in range(2))) & 1
                       for j in range(2)) for i in range(2))


def compose(p, q):
    """Permutation composition p after q."""
    return tuple(p[q[i]] for i in range(3))


def scalar_idempotents():
    found = set()
    for x in range(1, 8):
        for y in range(1, 8):
            if (x & y).bit_count() & 1:
                found.add(tuple(tuple(((x >> i) & 1) * ((y >> j) & 1)
                                      for j in range(3)) for i in range(3)))
    return sorted(found)


def mul3(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) & 1
                        for j in range(3)) for i in range(3))


def six_by_six_delta(address_delta, n):
    return tuple(tuple(n[i][j] * address_delta[a][b]
                       for j in range(3) for b in range(2))
                 for i in range(3) for a in range(2))


def zero_alg_matrix():
    return [[0 for _ in range(3)] for _ in range(3)]


def identity_alg_matrix(identity_index):
    out = zero_alg_matrix()
    for i in range(3):
        out[i][i] = 1 << identity_index
    return out


def ga_mul(x, y, group_table):
    out = 0
    for a in range(6):
        if (x >> a) & 1:
            for b in range(6):
                if (y >> b) & 1:
                    out ^= 1 << group_table[a][b]
    return out


def alg_matrix_mul(a, b, group_table):
    out = zero_alg_matrix()
    for i in range(3):
        for j in range(3):
            value = 0
            for k in range(3):
                value ^= ga_mul(a[i][k], b[k][j], group_table)
            out[i][j] = value
    return out


def paid_factor(g_index, n, identity_index):
    out = identity_alg_matrix(identity_index)
    delta = (1 << g_index) ^ (1 << identity_index)
    for i in range(3):
        for j in range(3):
            if n[i][j]:
                out[i][j] ^= delta
    return out


def diagonal_target(labels):
    out = zero_alg_matrix()
    for i, label_index in enumerate(labels):
        out[i][i] = 1 << label_index
    return out


def product(word, group_table, identity_index):
    out = identity_alg_matrix(identity_index)
    for g_index, n in word:
        out = alg_matrix_mul(out, paid_factor(g_index, n, identity_index), group_table)
    return out


def main():
    group = sorted(permutations(range(3)))
    group_index = {g: i for i, g in enumerate(group)}
    e = (0, 1, 2)
    s = (1, 0, 2)  # (12)
    t = (0, 2, 1)  # (23)
    st = compose(s, t)
    need(len(group) == 6 and len(group_index) == 6, "S3 must have six elements")

    group_table = [[group_index[compose(a, b)] for b in group] for a in group]
    e_i = group_index[e]
    s_i, t_i, st_i = group_index[s], group_index[t], group_index[st]
    need(group_table[s_i][s_i] == e_i and group_table[t_i][t_i] == e_i,
         "the paid labels must be involutions")
    need(group_table[s_i][t_i] == st_i and group_table[st_i][st_i] != e_i,
         "the endpoint st must be the order-three product")
    need(group_table[group_table[st_i][st_i]][st_i] == e_i,
         "st must have order three")

    identity2 = ((1, 0), (0, 1))
    rho_s = ((1, 1), (0, 1))
    rho_t = ((1, 0), (1, 1))
    rho = {e: identity2}
    todo = [e]
    while todo:
        g = todo.pop()
        for generator, matrix in ((s, rho_s), (t, rho_t)):
            h = compose(g, generator)
            candidate = mul2(rho[g], matrix)
            if h in rho:
                need(rho[h] == candidate, "representation assignment is inconsistent")
            else:
                rho[h] = candidate
                todo.append(h)
    need(len(rho) == 6 and len(set(rho.values())) == 6,
         "the two-dimensional representation must be faithful on S3")
    for a in group:
        for b in group:
            need(rho[compose(a, b)] == mul2(rho[a], rho[b]),
                 "rho must preserve every S3 product")

    def plus_identity(a):
        return tuple(tuple(a[i][j] ^ identity2[i][j] for j in range(2))
                     for i in range(2))

    need(rank(plus_identity(rho[s])) == 1, "rho(s)+I must have rank one")
    need(rank(plus_identity(rho[t])) == 1, "rho(t)+I must have rank one")
    need(rank(plus_identity(rho[st])) == 2, "rho(st)+I must have rank two")

    idempotents = scalar_idempotents()
    need(len(idempotents) == 28, "expected all 28 rank-one idempotents")
    for n in idempotents:
        need(mul3(n, n) == n and rank(n) == 1,
             "enumerated scalar must be a rank-one idempotent")
        for g in (s, t):
            delta = plus_identity(rho[g])
            need(rank(six_by_six_delta(delta, n)) == 1,
                 "every paid factor must have represented update rank one")

    blocks = (rho[s], rho[t], rho[st])
    target_delta = tuple(
        tuple((blocks[i][a][b] ^ identity2[a][b]) if i == j else 0
              for j in range(3) for b in range(2))
        for i in range(3) for a in range(2))
    need(rank(target_delta) == 4, "represented target-minus-identity rank must be four")

    # Exact full F2[S3] witness: the three coordinate projectors are legal N.
    e11 = ((1, 0, 0), (0, 0, 0), (0, 0, 0))
    e22 = ((0, 0, 0), (0, 1, 0), (0, 0, 0))
    e33 = ((0, 0, 0), (0, 0, 0), (0, 0, 1))
    word = [(s_i, e11), (t_i, e22), (s_i, e33), (t_i, e33)]
    target = diagonal_target((s_i, t_i, st_i))
    need(product(word, group_table, e_i) == target,
         "four-call word must equal the full group-algebra target")
    for omitted in range(len(word)):
        shortened = word[:omitted] + word[omitted + 1:]
        need(product(shortened, group_table, e_i) != target,
             "each single-factor omission must fail the target")

    print("PASS_S3_THREE_REGISTER_RANK_BOUND q_lower=4 direct=4 "
          "target_rank=4 paid_delta_rank=1 idempotents=28 omissions=4")


if __name__ == "__main__":
    main()
