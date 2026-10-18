"""Small integer fixture oracle, independent of the binary source arithmetic."""
from types import SimpleNamespace


def need(condition, message):
    if not condition:
        raise ValueError(message)


def headers(kind, rank, modulus):
    need(kind in ("good", "fallback") and rank in (1, 42), "fixture alphabet")
    low = [[int(i == j) for j in range(64)] for i in range(64)]
    p = [[int(i == j and i < rank) for j in range(64)] for i in range(64)]
    low[0][rank] = 1
    if kind == "good":
        low[rank][0], low[rank][rank] = 1, 2
        p[0][0], p[0][rank], p[rank][0], p[rank][rank] = 2, modulus - 1, 2, modulus - 1
    else:
        low[rank][0] = 2
        p[0][0], p[0][rank], p[rank][0], p[rank][rank] = modulus - 1, 1, modulus - 2, 2
    return low, p


def fallback(projector, modulus):
    rows = [[0] * 128 for _ in range(128)]
    for i in range(64):
        for j in range(64):
            rows[i][j] = rows[127 - i][127 - j] = (int(i == j) - projector[i][j]) % modulus
            rows[i][127 - j] = rows[127 - i][j] = projector[i][j]
    permutation, reductions, scalars = list(range(128)), [], []
    for j in range(128):
        pivot = next(i for i in range(j, 128) if rows[i][j] % 3)
        inverse = pow(rows[pivot][j], -1, modulus)
        if pivot != j:
            reductions.append(("swap", j, pivot, tuple(permutation)))
            scalars.append(None)
            rows[j], rows[pivot] = rows[pivot], rows[j]
            permutation[j], permutation[pivot] = permutation[pivot], permutation[j]
        for i in range(128):
            if i != j:
                scalar = -rows[i][j] * inverse % modulus
                reductions.append(("shear", i, j, tuple(permutation)))
                scalars.append(scalar)
                if scalar:
                    rows[i] = [(a + scalar * b) % modulus for a, b in zip(rows[i], rows[j], strict=True)]
    diagonal = [rows[i][i] for i in range(128)]
    need(all(rows[i][j] == (diagonal[i] if i == j else 0)
             for i in range(128) for j in range(128)), "oracle diagonal endpoint")
    determinant = 1
    for value in diagonal:
        determinant = determinant * value % modulus
    need(determinant in (1, modulus - 1), "oracle determinant")
    plan = SimpleNamespace(good=False, dimension=64, rank=1, reductions=tuple(reductions),
                           permutation=tuple(permutation), negative_sign=determinant != 1)
    return plan, scalars


def reference(kind, rank, modulus, branch, reverse=False):
    low, p = headers(kind, rank, modulus)
    if kind == "good":
        plan = SimpleNamespace(good=True, dimension=64, rank=rank)
        values = {"head": (rank - 1, rank, 0, modulus - 1),
                  "tail": (63 - rank, 63, 63 - rank, pow(2, -1, modulus)),
                  "zero": (62, 63, 0, 0)}
        index, first, second, scalar = values[branch]
        ref = SimpleNamespace(kind="head" if branch == "zero" else branch, index=index,
                              first=first, second=second, sign=1)
    else:
        plan, scalars = fallback(p, modulus)
        index = next(i for i, value in enumerate(scalars) if value is not None and bool(value) == (branch != "zero"))
        _, first, second, permutation = plan.reductions[index]
        scalar = scalars[index]
        ref = SimpleNamespace(kind="shear", index=index, first=first, second=second,
                              permutation=permutation, sign=1)
    return low, plan, ref, scalar, reverse
