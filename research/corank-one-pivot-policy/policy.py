"""Three-swap corank-one pivot plans. Produced by Nick Petalas, Apache-2.0."""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(u, v, q):
    require(type(q) is int and 2 <= q <= 31, "prime field bound")
    require(all(q % d for d in range(2, q)), "prime field")
    require(isinstance(u, (tuple, list)) and isinstance(v, (tuple, list)), "vectors")
    require(2 <= len(u) == len(v) <= 64, "dimension bound")
    require(all(type(x) is int and 0 <= x < q for x in (*u, *v)), "field entries")
    require(sum(x * y for x, y in zip(u, v, strict=True)) % q == 1, "v u = 1")


def bad_prefixes(a, q):
    """Indices k where the leading (k+1)-minor of I-u v is zero."""
    total, bad = 0, []
    for k in range(len(a) - 1):
        total = (total + a[k]) % q
        if total == 1:
            bad.append(k)
    return bad


def pivot_plan(u, v, q):
    """Return current row/column indices for m-1 same-head pivot stages.

    Rows k and i and columns k and j are swapped at stage (k,i,j).
    Separate nontrivial row and column swaps each cost one. The proof
    covers all fields; this bounded executable supports prime q<=31.
    """
    validate(u, v, q)
    m = len(u)
    a = [x * y % q for x, y in zip(u, v, strict=True)]
    plan = [(k, k) for k in range(m - 1)]
    bad = bad_prefixes(a, q)
    if not bad:
        return plan
    if a[-1] == 0:
        first = bad[0]
        plan[first] = (m - 1, m - 1)
        a[first], a[-1] = a[-1], a[first]
        bad = bad_prefixes(a, q)
        require(not bad or bad[0] > first, "preparatory pivot clears first failure")
    if bad:
        first, last = bad[0], bad[-1]
        require(last + 1 < m - 1 and a[first] * a[last + 1] % q, "bridge anchors")
        plan[first] = (first, last + 1)
    require(sum((i != k) + (j != k) for k, (i, j) in enumerate(plan)) <= 3,
            "three paid swaps")
    return plan
