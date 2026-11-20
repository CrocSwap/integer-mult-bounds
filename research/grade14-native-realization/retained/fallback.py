"""Exact local-ring fallback; an abstract address program, not a tape compiler.

Ross Richardson with OpenAI Codex assistance. Apache-2.0.
The unit-pivot algorithm and conservative tariffs are retained source results.
"""

from math import gcd


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, modulus):
    n = len(a)
    out = [[0] * len(b[0]) for _ in range(n)]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    out[i][j] = (out[i][j] + x * y) % modulus
    return out


def compile_fallback(matrix, q, w):
    """Compile an even square matrix of determinant +/-1 over Z/q**w.

    The universal guarantee assumes prime q. A successful returned plan is an
    exact certificate also for other moduli; unit tests are gcd-based. The
    caller must separately establish primality for the universal claim.
    """
    require(type(q) is int and q >= 2 and type(w) is int and w >= 1,
            "invalid ring parameters")
    n = len(matrix)
    require(n >= 2 and n % 2 == 0 and all(len(row) == n for row in matrix),
            "expected even square matrix")
    require(all(type(x) is int for row in matrix for x in row),
            "matrix entries must be integers")
    modulus = q ** w
    a = [[x % modulus for x in row] for row in matrix]
    reductions, pivots = [], []
    for k in range(n):
        choices = [i for i in range(k, n) if gcd(a[i][k], modulus) == 1]
        require(bool(choices), "no unit pivot; outside the fallback domain")
        pivot = choices[0]
        pivots.append(pivot)
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            reductions.append(["swap", k, pivot])
        inv = pow(a[k][k], -1, modulus)
        for i in range(n):
            if i == k:
                continue
            c = (-a[i][k] * inv) % modulus
            # Keep all slots, including zeros, for a common template over
            # EVERY high lift in a low class. Arithmetic may skip a full-ring
            # zero, but the emitted slot and its conservative charge remain.
            if c:
                a[i] = [(x + c * y) % modulus for x, y in zip(a[i], a[k])]
            reductions.append(["add", i, k, c])
    require(all(a[i][j] == 0 for i in range(n) for j in range(n) if i != j),
            "reduction did not reach a diagonal")
    diagonal = [a[i][i] for i in range(n)]
    diagonal_sign = 1
    for x in diagonal:
        diagonal_sign = diagonal_sign * x % modulus
    require(diagonal_sign in {1, modulus - 1}, "determinant is not +/-1")

    # D first, then O_t^{-1}, ..., O_1^{-1}, where O_t ... O_1 M = D.
    operations = []
    for i, x in enumerate(diagonal[:-1]):
        # Keep identity pairs too: this is one common template for every
        # diagonal-conjugate atom column, whose unit coefficients may differ.
        operations.append(["pair", i, n - 1, x])
    if diagonal_sign != 1:
        operations.append(["sign", n - 1, -1])
    for op in reversed(reductions):
        operations.append(op[:] if op[0] == "swap" else
                          ["add", op[1], op[2], -op[3] % modulus])
    return {"q": q, "w": w, "N": n, "m": n // 2, "pivots": pivots,
            "reductions": reductions, "diagonal": diagonal,
            "diagonal_sign": diagonal_sign, "operations": operations,
            "lowered_operations": lower_operations(operations)}


def compile_weighted_block(matrix, weights_by_atom, q, w):
    """Emit one field word with vector coefficients for ancestor unit weights.

    Each coefficient is evaluated at full local-ring precision. The common
    topology is checked, rather than assuming low-pivot covariance suffices.
    This finite routine takes explicit weights; descriptor evaluation and tape
    movement are separate inherited obligations.
    """
    require(bool(weights_by_atom), "empty atom block")
    modulus = q ** w
    n = len(matrix)
    plans, matrices = [], []
    for weights in weights_by_atom:
        require(len(weights) == n and all(type(x) is int and gcd(x, modulus) == 1
                                        for x in weights), "invalid diagonal units")
        a = conjugate_diagonal(matrix, weights, modulus)
        matrices.append(a)
        plans.append(compile_fallback(a, q, w))
    template = plans[0]["lowered_operations"]
    combined = []
    for j, op in enumerate(template):
        if op[0] == "sign":
            require(all(p["lowered_operations"][j] == op for p in plans),
                    "column-dependent sign topology")
            combined.append(op[:])
        else:
            require(all(len(p["lowered_operations"]) == len(template) and
                        p["lowered_operations"][j][:3] == op[:3] for p in plans),
                    "column-dependent fallback topology")
            combined.append(op[:3] + [[p["lowered_operations"][j][3] for p in plans]])
    require(all(p["pivots"] == plans[0]["pivots"] for p in plans),
            "column-dependent pivot itinerary")
    return {"q": q, "w": w, "N": n, "atoms": len(plans),
            "pivots": plans[0]["pivots"], "plans": plans,
            "matrices_by_atom": matrices, "lowered_operations": combined}


def lower_operations(operations):
    """Lower to later-target adds, ordinary weighted swaps and a fixed sign."""
    out = []
    for op in operations:
        kind, i = op[:2]
        if kind == "sign":
            out.append(op[:])
            continue
        j = op[2]
        require(i != j, "aliased operation")
        if kind == "swap":
            out.append(["weighted_swap", i, j, 1])
        elif kind == "pair":
            # J_a J_1 as an operator: chronological J_1 then J_a.
            out.extend([["weighted_swap", i, j, 1],
                        ["weighted_swap", i, j, op[3]]])
        elif kind == "add" and i > j:
            out.append(["lower", i, j, op[3]])
        elif kind == "add":
            out.extend([["weighted_swap", i, j, 1],
                        ["lower", j, i, op[3]],
                        ["weighted_swap", i, j, 1]])
        else:
            raise ContractError("unknown operation")
    return out


def execute_rows(operations, rows, modulus):
    """Chronological symbolic-row semantics; every input column is retained."""
    a = [list(row) for row in rows]
    for op in operations:
        kind, i = op[:2]
        if kind in {"add", "lower"}:
            j, c = op[2:]
            if kind == "lower":
                require(i > j, "non-ordered lower adapter")
            if not c % modulus:
                continue
            a[i] = [(x + c * y) % modulus for x, y in zip(a[i], a[j])]
        elif kind == "swap":
            j = op[2]
            a[i], a[j] = a[j], a[i]
        elif kind == "weighted_swap":
            j, c = op[2:]
            ci = pow(c, -1, modulus)
            a[i], a[j] = ([c * x % modulus for x in a[j]],
                          [ci * x % modulus for x in a[i]])
        elif kind == "pair":
            j, c = op[2:]
            ci = pow(c, -1, modulus)
            a[i] = [c * x % modulus for x in a[i]]
            a[j] = [ci * x % modulus for x in a[j]]
        elif kind == "sign":
            a[i] = [op[2] * x % modulus for x in a[i]]
        else:
            raise ContractError("unknown operation")
    return a


def charge(plan, f):
    require(type(f) is int and f >= 1, "invalid block width")
    low = lower_operations(plan["operations"])
    swaps = sum(op[0] == "weighted_swap" for op in low)
    n = plan["N"]
    maximum = 6 * n * (n - 1) + 3 * n + 6 * (n - 1)
    hist = {f: swaps}
    if f // 2:
        hist[f // 2] = hist.get(f // 2, 0) + 2 * swaps
    return {"f": f, "weighted_swaps": swaps,
            "lower_adapters": sum(op[0] == "lower" for op in low),
            "fixed_signs": sum(op[0] == "sign" for op in low),
            "reversed_child_histogram": dict(sorted(hist.items())),
            "children": sum(hist.values()),
            "child_rank_mass": sum(r * c for r, c in hist.items()),
            "source_allowance": maximum,
            "selected_round_allowance": 32 * (n // 2) ** 2}


def bad_projector(m, rank, q, modulus):
    """Explicit split rank-r chart; NOT a selected emitted residual ID.

    On axes 0,r, u=(q,1), v=(1,1-q), v*u=1. All other active
    axes 1..r-1 have identity projector entries.
    """
    require(1 <= rank < m, "bad-chart rank must lie between 1 and m-1")
    p = [[0] * m for _ in range(m)]
    p[0][0], p[0][rank] = q % modulus, (q * (1 - q)) % modulus
    p[rank][0], p[rank][rank] = 1, (1 - q) % modulus
    for i in range(1, rank):
        p[i][i] = 1
    return p


def residual(projector, modulus):
    """D_P with coarse tail reversal, exactly the pinned source formula."""
    p, m = projector, len(projector)
    a = identity(2 * m)
    for i in range(m):
        for j in range(m):
            a[i][j] = (int(i == j) - p[i][j]) % modulus
            a[i][m + j] = p[i][m - 1 - j] % modulus
            a[m + i][j] = p[m - 1 - i][j] % modulus
            a[m + i][m + j] = (int(i == j) - p[m - 1 - i][m - 1 - j]) % modulus
    return a


def conjugate_diagonal(matrix, units, modulus):
    inv = [pow(x, -1, modulus) for x in units]
    return [[units[i] * x * inv[j] % modulus for j, x in enumerate(row)]
            for i, row in enumerate(matrix)]
