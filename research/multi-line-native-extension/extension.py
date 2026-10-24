"""Finite prime-field reference implementation of the native extension lemma.

Prepared for JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
from math import prod


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(x, y, coefficient, q):
    return tuple((a + coefficient * b) % q for a, b in zip(x, y))


def basis(rows, q):
    """Canonical reduced row basis; vectors are tuples over the prime field."""
    out = []
    for row in rows:
        row = tuple(row)
        for pivot, old in out:
            row = add(row, old, -row[pivot], q)
        if not any(row):
            continue
        pivot = next(i for i, value in enumerate(row) if value)
        row = tuple(value * pow(row[pivot], -1, q) % q for value in row)
        out = [(i, add(old, row, -old[pivot], q)) for i, old in out]
        out.append((pivot, row))
        out.sort()
    return tuple(row for _, row in out)


def contains(rows, vector, q):
    return len(basis((*rows, vector), q)) == len(rows)


def graph(pairs, n, q):
    """Reduce simultaneous prescribed equations; reject inconsistency/kernel."""
    out = []
    for source, target in pairs:
        source, target = tuple(source), tuple(target)
        for pivot, old, image in out:
            coefficient = -source[pivot]
            source = add(source, old, coefficient, q)
            target = add(target, image, coefficient, q)
        if not any(source):
            if any(target):
                return None
            continue
        pivot = next(i for i, value in enumerate(source) if value)
        scale = pow(source[pivot], -1, q)
        source = tuple(value * scale % q for value in source)
        target = tuple(value * scale % q for value in target)
        reduced = []
        for i, old, image in out:
            coefficient = -old[pivot]
            reduced.append((i, add(old, source, coefficient, q),
                            add(image, target, coefficient, q)))
        out = sorted((*reduced, (pivot, source, target)))
    if len(basis([image for _, _, image in out], q)) != len(out):
        return None
    return out


def image(reduced, vector, q):
    result = (0,) * len(vector)
    for pivot, source, target in reduced:
        coefficient = vector[pivot]
        vector = add(vector, source, -coefficient, q)
        result = add(result, target, coefficient, q)
    return None if any(vector) else result


def intersection(left, right, n, q):
    """Intersection by relations among a left basis followed by a right basis."""
    reduced, found = [], []
    width = len(left) + len(right)
    for j, vector in enumerate((*left, *right)):
        relation = tuple(int(i == j) for i in range(width))
        for pivot, old, coefficients in reduced:
            factor = -vector[pivot]
            vector = add(vector, old, factor, q)
            relation = add(relation, coefficients, factor, q)
        if any(vector):
            pivot = next(i for i, value in enumerate(vector) if value)
            scale = pow(vector[pivot], -1, q)
            vector = tuple(v * scale % q for v in vector)
            relation = tuple(v * scale % q for v in relation)
            reduced = [(i, add(old, vector, -old[pivot], q),
                        add(coefficients, relation, -old[pivot], q))
                       for i, old, coefficients in reduced]
            reduced = sorted((*reduced, (pivot, vector, relation)))
        else:
            value = (0,) * n
            for factor, row in zip(relation[:len(left)], left):
                value = add(value, row, factor, q)
            found.append(value)
    return basis(found, q)


def validate(n, q, source, capacity, pairs):
    need(type(n) is int and 0 <= n <= 12, "reference dimension must be 0..12")
    need(type(q) is int and 2 <= q <= 31 and
         all(q % p for p in range(2, int(q ** .5) + 1)), "prime q required")
    need(all(len(pair) == 2 for pair in pairs), "prescribed pairs have two vectors")
    rows = [*source, *capacity, *(v for pair in pairs for v in pair)]
    need(all(len(row) == n and all(type(v) is int and 0 <= v < q for v in row)
             for row in rows), "malformed vector")


def extend(n, q, source, capacity, pairs):
    """Return exact completion count and one matrix (columns), or count zero."""
    validate(n, q, source, capacity, pairs)
    prescribed = graph(pairs, n, q)
    if prescribed is None:
        return {"count": 0, "columns": None, "reason": "inconsistent-or-noninjective"}
    a, c = basis(source, q), basis(capacity, q)
    u = tuple(row for _, row, _ in prescribed)
    up = tuple(row for _, _, row in prescribed)
    meet = intersection(a, u, n, q)
    if any(not contains(c, image(prescribed, v, q), q) for v in meet):
        return {"count": 0, "columns": None, "reason": "prescribed-intersection"}
    k = len(a) - len(meet)
    c0 = len(intersection(c, basis(up, q), n, q))
    dimensions = {"n": n, "u": len(u), "a": len(a), "c": len(c),
                  "d": len(meet), "k": k, "c0": c0}
    if k > len(c) - c0:
        return {"count": 0, "columns": None, "reason": "quotient-capacity",
                "dimensions": dimensions}
    ab, bb = list(u), list(up)
    for v in a:
        if not contains(basis(ab, q), v, q):
            ab.append(v)
    for v in c:
        if len(bb) == len(ab):
            break
        if not contains(basis(bb, q), v, q):
            bb.append(v)
    standard = [tuple(int(i == j) for i in range(n)) for j in range(n)]
    for rows in (ab, bb):
        for v in standard:
            if not contains(basis(rows, q), v, q):
                rows.append(v)
    completed = graph(list(zip(ab, bb)), n, q)
    need(completed is not None and len(completed) == n, "completion invariant")
    count = (q ** (c0 * k) * prod(q ** (len(c) - c0) - q ** i for i in range(k))
             * prod(q ** n - q ** i for i in range(len(u) + k, n)))
    return {"count": count, "columns": [image(completed, e, q) for e in standard],
            "dimensions": dimensions, "reason": "compatible"}
