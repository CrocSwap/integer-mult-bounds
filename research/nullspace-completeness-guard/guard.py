"""Exact admission of integer rational-nullspace bases; ywz65, Apache-2.0.

Prepared with OpenAI Codex assistance. See PROOF.md for the rank sandwich.
This certifies the row space, not a canonical normalization or row order.
"""
from fractions import Fraction

PRIMES = (2147483647, 1000000007)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rows(matrix, n):
    try:
        result = tuple(tuple(row) for row in matrix)
    except TypeError as exc:
        raise ValueError("matrix must contain iterable rows") from exc
    require(all(len(row) == n and all(type(x) is int for x in row)
                for row in result), "integer rectangular matrices required")
    return result


def rank_mod(matrix, prime, goal):
    """A lower bound on rational rank, stopped at the requested witness size."""
    if goal == 0:
        return 0
    work = [[x % prime for x in row] for row in matrix]
    rank = 0
    for col in range(len(work[0]) if work else 0):
        pivot = next((i for i in range(rank, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][col], -1, prime)
        tail = [x * inverse % prime for x in work[rank][col:]]
        for i in range(rank + 1, len(work)):
            factor = work[i][col]
            if factor:
                work[i][col:] = [(x - factor * y) % prime
                                for x, y in zip(work[i][col:], tail)]
        rank += 1
        if rank == goal:
            return rank
    return rank


def rank_exact(matrix):
    """Exact fallback: unlucky primes must not reject a valid rational basis."""
    work = [[Fraction(x) for x in row] for row in matrix]
    rank = 0
    for col in range(len(work[0]) if work else 0):
        pivot = next((i for i in range(rank, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        divisor = work[rank][col]
        tail = [x / divisor for x in work[rank][col:]]
        for i in range(rank + 1, len(work)):
            factor = work[i][col]
            if factor:
                work[i][col:] = [x - factor * y
                                for x, y in zip(work[i][col:], tail)]
        rank += 1
    return rank


def certify(matrix, n, basis):
    """Return witness routes or raise ValueError; no assert-dependent guards."""
    require(type(n) is int and n >= 0, "invalid ambient dimension")
    a, b = rows(matrix, n), rows(basis, n)
    k = len(b)
    require(k <= n, "too many basis rows")
    require(all(sum(x * y for x, y in zip(arow, brow)) == 0
                for arow in a for brow in b), "annihilation failed")
    # One column supported on each distinct row supplies a nonzero diagonal minor.
    witnessed = set()
    for col in range(n):
        nonzero = [i for i, row in enumerate(b) if row[col]]
        if len(nonzero) == 1:
            witnessed.add(nonzero[0])
    if len(witnessed) == k:
        basis_route = "diagonal"
    elif any(rank_mod(b, p, k) == k for p in PRIMES):
        basis_route = "modular"
    else:
        require(rank_exact(b) == k, "dependent nullspace rows")
        basis_route = "exact"
    target = n - k
    if any(rank_mod(a, p, target) == target for p in PRIMES):
        input_route = "modular"
    else:
        require(rank_exact(a) == target, "incomplete nullspace")
        input_route = "exact"
    return {"basis": basis_route, "input": input_route}


def guarded_kernel(candidate):
    """Keep an immutable input copy even if the candidate mutates its argument."""
    def checked(matrix, n):
        require(type(n) is int and n >= 0, "invalid ambient dimension")
        original = rows(matrix, n)
        output = candidate([list(row) for row in original], n)
        output = rows(output, n)
        certify(original, n, output)
        return [list(row) for row in output]
    return checked
