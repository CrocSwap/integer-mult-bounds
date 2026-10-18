"""Independent integer endpoint checks, outside measured tape execution."""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(m):
    return [[int(i == j) for j in range(m)] for i in range(m)]


def product(a, b, modulus):
    return [[sum(x * row[j] for x, row in zip(left, b, strict=True)) % modulus
             for j in range(len(b[0]))] for left in a]


def projector_values(m, rank, modulus, kind):
    need(1 <= rank <= m <= 64, "fixed fixture dimensions")
    out = [[int(i == j and i < rank) for j in range(m)] for i in range(m)]
    if rank < m:
        # u=(1,1), v=(2,-1), v*u=1 over every stated ring.
        out[0][0], out[0][rank] = 2, modulus - 1
        out[rank][0], out[rank][rank] = 2, modulus - 1
        if kind == "fallback":
            # u=(1,-1), v=(2,1), again v*u=1.
            out[0][rank], out[rank][0] = 1, modulus - 2
    need(product(out, out, modulus) == out, "fixture is an exact projector")
    return out


def check_good(form, projector, rank, modulus):
    m = len(projector)
    need([word.inspect() for word in form.pivots] == [2] + [1] * (rank - 1),
         "literal good pivot values")
    rows = [(i, k, value.inspect()) for i, k, value in form.rows]
    columns = [(i, j, value.inspect()) for i, j, value in form.columns]
    need(rows == [(i, k, modulus - 1 if k == 0 and i == rank else 0)
                  for k in range(rank) for i in range(k + 1, m)], "literal good row coefficients")
    inv_two = pow(2, -1, modulus)
    need(columns == [(m - 1 - k, j, inv_two if k == 0 and j == m - 1 - rank else 0)
                     for k in range(rank) for j in range(m - 1 - k)],
         "literal good column coefficients")
    # Elementary inverses from the literal expected coefficients, independent
    # of the predecessor's matrix inversion and word-arithmetic routines.
    left, li, ri = identity(m), identity(m), identity(m)
    left[rank][0], li[rank][0] = modulus - 1, 1
    ri[m - 1][m - 1 - rank] = -inv_two % modulus
    a0 = product(product(left, projector, modulus)[:rank], li, modulus)
    b = product(ri, [row[:rank] for row in reversed(li)], modulus)
    expected = [[0] * m for _ in range(m)]
    for k in range(rank):
        inverse = inv_two if k == 0 else 1
        for i in range(m):
            expected[i][k] = (b[i][k] - (inverse if i == m - 1 - k else 0)) % modulus
        for j in range(rank, m):
            expected[m - 1 - k][j] = -inverse * a0[k][j] % modulus
    need([[word.inspect() for word in row] for row in form.cross] == expected,
         "complete independent good cross endpoint")


def check_fallback(form, projector, rank, modulus):
    m, size = len(projector), 2 * len(projector)
    rows = [[0] * size for _ in range(size)]
    for i in range(m):
        for j in range(m):
            rows[i][j] = rows[size - 1 - i][size - 1 - j] = (int(i == j) - projector[i][j]) % modulus
            rows[i][size - 1 - j] = rows[size - 1 - i][j] = projector[i][j]
    permutation, swaps = list(range(size)), 0
    for reduction in form.reductions:
        need(reduction.permutation == tuple(permutation), "chronological reduction permutation")
        i, j = reduction.target, reduction.source
        if reduction.kind == "swap":
            rows[i], rows[j] = rows[j], rows[i]
            permutation[i], permutation[j] = permutation[j], permutation[i]
            swaps += 1
        else:
            need(reduction.kind == "shear", "closed reduction alphabet")
            scalar = reduction.scalar.inspect()
            rows[i] = [(x + scalar * y) % modulus for x, y in zip(rows[i], rows[j], strict=True)]
    diagonal = [word.inspect() for word in form.diagonal]
    need(rows == [[diagonal[i] if i == j else 0 for j in range(size)] for i in range(size)],
         "complete fallback elimination endpoint")
    determinant = 1
    for value in diagonal:
        determinant = determinant * value % modulus
    need(determinant == pow(modulus - 1, rank + swaps, modulus), "independent determinant parity")
    need(form.permutation == tuple(permutation) and form.negative_sign == (determinant != 1),
         "fallback terminal labels and sign")


def check_form(form, kind, projector, rank, modulus):
    if kind == "good":
        check_good(form, projector, rank, modulus)
    else:
        check_fallback(form, projector, rank, modulus)
