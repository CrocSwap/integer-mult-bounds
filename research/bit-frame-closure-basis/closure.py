"""Exact modular closure with one echelon basis per input mask.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
The closure contract and Hadamard guard follow Seth Burkart's PR886 as
refined during maintainer integration. See README.md for scope and credit.
"""

PRIME = 2147483647


def require(condition, message):
    if not condition:
        raise ValueError(message)


def echelon(rows, width):
    """An increasing-pivot, unit-pivot basis over the fixed prime field."""
    basis = []
    for source in rows:
        row = [x % PRIME for x in source]
        for pivot, vector in basis:
            factor = row[pivot]
            if factor:
                for j in range(pivot, width):
                    row[j] = (row[j] - factor * vector[j]) % PRIME
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            inverse = pow(row[pivot], -1, PRIME)
            row = tuple(x * inverse % PRIME for x in row)
            basis.append((pivot, row))
            basis.sort(key=lambda item: item[0])
    return basis


def contains(source, basis, width):
    row = [x % PRIME for x in source]
    for pivot, vector in basis:
        factor = row[pivot]
        if factor:
            for j in range(pivot, width):
                row[j] = (row[j] - factor * vector[j]) % PRIME
    return not any(row)


def make_close(lines, count, cache):
    """Return the PR886 close(mask) contract on this immutable line table.

    The table and cache are private to one checker execution. No result is
    reused between words or processes. Check the guard even if the caller
    disabled assertions; rational equivalence needs this domain restriction.
    """
    require(type(count) is int and count > 0 and count == len(lines),
            "line count")
    vectors = tuple(tuple(row) for row in lines)
    width = len(vectors[0])
    require(width > 0 and all(len(row) == width for row in vectors),
            "rectangular nonempty coordinates")
    require(all(type(x) is int for row in vectors for x in row),
            "integer coordinates")
    norm = max(sum(x*x for x in row) for row in vectors)
    require(norm ** width < PRIME ** 2, "Hadamard guard")
    require(not cache, "fresh per-word cache")
    full = (1 << count) - 1

    def close(mask):
        # This is the same input-mask cache boundary as the frozen checker.
        if mask not in cache:
            require(type(mask) is int and 0 <= mask <= full, "line mask")
            if mask == 0:
                # Preserve the reference's explicit empty-selection convention.
                answer = (0, 0)
            else:
                basis = echelon((row for i, row in enumerate(vectors)
                                 if mask >> i & 1), width)
                rank = len(basis)
                if rank == width:
                    closed = full
                else:
                    closed = mask
                    for i, row in enumerate(vectors):
                        if not (mask >> i & 1) and contains(row, basis, width):
                            closed |= 1 << i
                answer = (closed, rank)
            cache[mask] = answer
        return cache[mask]

    return close
