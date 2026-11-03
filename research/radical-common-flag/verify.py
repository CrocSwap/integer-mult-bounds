#!/usr/bin/env python3
"""Exact finite corroboration. Produced by Nick Petalas. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return tuple(int(i == j) for i in range(n) for j in range(n))


def add(a, b, p):
    need(len(a) == len(b), "matrix size")
    return tuple((x+y) % p for x, y in zip(a, b, strict=True))


def mul(a, b, n, p):
    need(len(a) == len(b) == n*n, "matrix product size")
    return tuple(sum(a[i*n+k]*b[k*n+j] for k in range(n)) % p
                 for i in range(n) for j in range(n))


def mv(a, v, n, p):
    return tuple(sum(a[i*n+j]*v[j] for j in range(n)) % p for i in range(n))


def vm(v, a, n, p):
    return tuple(sum(v[i]*a[i*n+j] for i in range(n)) % p for j in range(n))


def reduce_matrix(a, n, p):
    rows = [list(a[i*n:(i+1)*n]) + list(eye(n)[i*n:(i+1)*n]) for i in range(n)]
    pivot = 0
    for j in range(n):
        choices = [i for i in range(pivot, n) if rows[i][j]]
        if not choices:
            continue
        i = choices[0]
        rows[pivot], rows[i] = rows[i], rows[pivot]
        scale = pow(rows[pivot][j], -1, p)
        rows[pivot] = [x*scale % p for x in rows[pivot]]
        for i in range(n):
            if i != pivot:
                scale = rows[i][j]
                rows[i] = [(x-scale*y) % p
                           for x, y in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    inverse = tuple(x for row in rows for x in row[n:]) if pivot == n else None
    if inverse is not None:
        need(mul(a, inverse, n, p) == eye(n), "inverse invariant")
    return pivot, inverse


def upper(a, n):
    return all(a[i*n+j] == 0 for i in range(n) for j in range(i))


def points(n, p):
    return tuple(v for v in itertools.product(range(p), repeat=n)
                 if next((x for x in v if x), None) == 1)


def multiple(v, w, p):
    return any(v == tuple(c*x % p for x in w) for c in range(p))


def flag_mask(a, flags, n, p):
    mask = 0
    for i, (v, w) in enumerate(flags):
        if multiple(mv(a, v, n, p), v, p):
            if w is None or multiple(vm(w, a, n, p), w, p):
                mask |= 1 << i
    return mask


def census(n, p):
    need((n, p) in ((2, 2), (2, 3), (3, 2)), "census capacity")
    matrices = tuple(itertools.product(range(p), repeat=n*n))
    lines = points(n, p)
    flags = (tuple((v, None) for v in lines) if n == 2 else
             tuple((v, w) for v in lines for w in lines
                   if sum(x*y for x, y in zip(v, w, strict=True)) % p == 0))
    bases = [(g, reduce_matrix(g, n, p)[1]) for g in matrices]
    bases = [(g, gi) for g, gi in bases if gi is not None]
    geometric = [flag_mask(a, flags, n, p) for a in matrices]
    triangular = []
    for a in matrices:
        mask = 0
        for i, (g, gi) in enumerate(bases):
            if upper(mul(mul(gi, a, n, p), g, n, p), n):
                mask |= 1 << i
        triangular.append(mask)
    histogram = {}
    for i in range(len(matrices)):
        for j in range(len(matrices)):
            common = geometric[i] & geometric[j]
            need(bool(common) == bool(triangular[i] & triangular[j]), "flag criteria")
            k = common.bit_count()
            histogram[k] = histogram.get(k, 0)+1
    visited = sum(histogram.values())
    need(visited == len(matrices)**2, "incomplete pair domain")
    return {"n": n, "q": p, "pairs": visited, "flags": len(flags),
            "bases": len(bases), "reachable": visited-histogram.get(0, 0),
            "common_flag_histogram": histogram}


def ring_identity(n, size):
    return (eye(n),) + ((0,)*(n*n),)*(size-1)


def ring_mul(a, b, n, p):
    need(2 <= len(a) == len(b) <= 4, "radical dimension")
    return (mul(a[0], b[0], n, p),) + tuple(
        add(mul(a[0], b[j], n, p), mul(a[j], b[0], n, p), p)
        for j in range(1, len(a)))


def word(coefficients, g, c0, n, p):
    need(1 <= n <= 4 and p in (2, 3, 5), "constructor capacity")
    need(1 <= len(coefficients) <= 3, "coefficient count")
    need(coefficients[0] == eye(n), "distinguished coefficient")
    need(all(upper(a, n) for a in coefficients), "supplied flag")
    gi = reduce_matrix(g, n, p)[1]
    need(gi is not None and reduce_matrix(c0, n, p)[1] is not None, "free maps")
    size = len(coefficients)+1
    factors = [(gi,) + ((0,)*(n*n),)*(size-1)]
    for j in range(n):
        scalar = list(eye(n))
        scalar[j*n+j] = 0
        columns = tuple(tuple(a[i*n+k] if k == j else 0
                              for i in range(n) for k in range(n))
                        for a in coefficients)
        factors.append((tuple(scalar),) + columns)
    left = mul(c0, g, n, p)
    factors.append((left,) + ((0,)*(n*n),)*(size-1))
    target = ((0,)*(n*n),) + tuple(
        mul(mul(left, a, n, p), gi, n, p) for a in coefficients)
    return factors, target


def endpoint(factors, n, p, size):
    result = ring_identity(n, size)
    for factor in factors:
        result = ring_mul(factor, result, n, p)
    return result


def literal(factors, data, n, p):
    state = [list(v) for v in data]
    for factor in factors:
        after = [[0]*n for _ in range(len(state))]
        for i in range(n):
            for j in range(n):
                after[0][i] += factor[0][i*n+j]*state[0][j]
                for k in range(1, len(state)):
                    after[k][i] += (factor[0][i*n+j]*state[k][j]
                                    + factor[k][i*n+j]*state[0][j])
        state = [[x % p for x in v] for v in after]
    return tuple(tuple(v) for v in state)


def literal_columns(factors, target, n, p):
    count = 0
    for k in range(len(target)):
        for i in range(n):
            data = tuple(tuple(int(j == i and h == k) for j in range(n))
                         for h in range(len(target)))
            need(literal(factors, data, n, p) == literal([target], data, n, p),
                 "arbitrary-input column")
            count += 1
    return count


def cuts(factors, target, n, p):
    need(target[0] == (0,)*(n*n), "scalar endpoint")
    xi = reduce_matrix(target[1], n, p)[1]
    need(xi is not None, "invertible distinguished coefficient")
    normalized = [mul(xi, a, n, p) for a in target[2:]]
    dimensions = []
    vectors = tuple(itertools.product(range(p), repeat=n))
    for cut in range(len(factors)+1):
        prefix = endpoint(factors[:cut], n, p, len(target))
        suffix = endpoint(factors[cut:], n, p, len(target))
        h, s = prefix[0], suffix[0]
        need(mul(s, h, n, p) == (0,)*(n*n), "scalar cut product")
        kernel = {v for v in vectors if mv(h, v, n, p) == (0,)*n}
        k = n-reduce_matrix(h, n, p)[0]
        need(reduce_matrix(s, n, p)[0] == k, "cut rank equality")
        need({mv(target[1], v, n, p) for v in kernel}
             == {mv(s, v, n, p) for v in vectors}, "cut image equality")
        for j in range(1, len(target)):
            need(target[j] == add(mul(s, prefix[j], n, p),
                                  mul(suffix[j], h, n, p), p), "cut coefficient")
        need(all(mv(a, v, n, p) in kernel for a in normalized for v in kernel),
             "cut invariance")
        dimensions.append(k)
    need(set(dimensions) == set(range(n+1)), "complete flag dimensions")
    need(all(0 <= b-a <= 1 for a, b in zip(dimensions, dimensions[1:])), "rank drop")
    return len(dimensions)


def constructions():
    count = columns = cut_count = 0
    for n, p in ((2, 2), (2, 3), (3, 2)):
        positions = [(i, j) for i in range(n) for j in range(i, n)]
        triangular = []
        for values in itertools.product(range(p), repeat=len(positions)):
            a = [0]*(n*n)
            for (i, j), value in zip(positions, values, strict=True):
                a[i*n+j] = value
            triangular.append(tuple(a))
        for a in triangular:
            for b in triangular:
                factors, target = word((eye(n), a, b), eye(n), eye(n), n, p)
                need(endpoint(factors, n, p, len(target)) == target, "attaining word")
                if count % 257 == 0:
                    columns += literal_columns(factors, target, n, p)
                    cut_count += cuts(factors, target, n, p)
                count += 1
    a, b = (0, 1, 0, 0, 0, 1, 0, 0, 0), (1, 0, 1, 0, 0, 0, 0, 0, 1)
    for g in itertools.product(range(2), repeat=9):
        if reduce_matrix(g, 3, 2)[1] is not None:
            factors, target = word((eye(3), a, b), g, g, 3, 2)
            need(endpoint(factors, 3, 2, len(target)) == target, "changed bases")
            columns += literal_columns(factors, target, 3, 2)
            cut_count += cuts(factors, target, 3, 2)
            count += 1
    for n, p in ((1, 2), (1, 5), (4, 3), (4, 5)):
        a = tuple((i+j+1) % p if i <= j else 0 for i in range(n) for j in range(n))
        factors, target = word((eye(n), a), eye(n), eye(n), n, p)
        need(endpoint(factors, n, p, len(target)) == target, "boundary sizes")
        columns += literal_columns(factors, target, n, p)
        cut_count += cuts(factors, target, n, p)
        count += 1
    factors, target = word((eye(1),), eye(1), eye(1), 1, 2)
    need(endpoint(factors, 1, 2, len(target)) == target, "vacuous tuple")
    columns += literal_columns(factors, target, 1, 2)
    cut_count += cuts(factors, target, 1, 2)
    count += 1
    return {"words": count, "dirty_basis_columns": columns, "cuts": cut_count}


def abstract_cuts():
    matrices = tuple(itertools.product(range(2), repeat=4))
    pair_count = coefficient_count = 0
    for h in matrices:
        kernel = {v for v in itertools.product(range(2), repeat=2)
                  if mv(h, v, 2, 2) == (0, 0)}
        for s in matrices:
            if mul(s, h, 2, 2) != (0,)*4:
                continue
            pair_count += 1
            image = {add(mul(s, d, 2, 2), mul(e, h, 2, 2), 2)
                     for d in matrices for e in matrices}
            for x in image:
                xi = reduce_matrix(x, 2, 2)[1]
                if xi is None:
                    continue
                need(reduce_matrix(s, 2, 2)[0] == 2-reduce_matrix(h, 2, 2)[0],
                     "abstract cut rank")
                for y in image:
                    a = mul(xi, y, 2, 2)
                    need(all(mv(a, v, 2, 2) in kernel for v in kernel), "abstract flag")
                    coefficient_count += 1
    return {"scalar_pairs": pair_count, "admissible_cut_cases": coefficient_count}


def strict_fixture():
    a = (0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0)
    b = (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0)
    common = [v for v in points(4, 3) if mv(a, v, 4, 3) == (0,)*4
              and mv(b, v, 4, 3) == (0,)*4]
    need(common == [(1, 0, 0, 0)], "forced first line")
    qa = tuple(a[i*4+j] for i in range(1, 4) for j in range(1, 4))
    qb = tuple(b[i*4+j] for i in range(1, 4) for j in range(1, 4))
    need(not any(mv(qa, v, 3, 3) == (0,)*3 and mv(qb, v, 3, 3) == (0,)*3
                 for v in points(3, 3)), "irreducible flag quotient")
    need(mul(mul(a, a, 4, 3), a, 4, 3) == (0,)*16
         and mul(mul(b, b, 4, 3), b, 4, 3) == (0,)*16, "nilpotent coefficients")
    return {"q": 3, "roles": 4, "common_lines": 1, "quotient_common_lines": 0}


def controls():
    count = 0
    invalid = [((eye(2), (0, 0, 1, 0)), eye(2), eye(2), 2, 2),
               ((eye(2),), (0,)*4, eye(2), 2, 2),
               ((eye(2),), eye(2), (0,)*4, 2, 2),
               ((eye(2),)*4, eye(2), eye(2), 2, 2),
               ((eye(2),), eye(2), eye(2), 2, 7),
               (((0,)*4,), eye(2), eye(2), 2, 2)]
    for args in invalid:
        try:
            word(*args)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid constructor accepted")
    a = (0, 1, 0, 0, 0, 1, 0, 0, 0)
    factors, target = word((eye(3), a), eye(3), eye(3), 3, 2)
    for i in range(1, 4):
        need(endpoint(factors[:i]+factors[i+1:], 3, 2, len(target)) != target,
             "omitted paid factor")
        count += 1
    need(endpoint(list(reversed(factors)), 3, 2, len(target)) != target, "chronology")
    count += 1
    h, s, y = (1, 0, 0, 0), eye(2), (0, 1, 0, 0)
    need(mul(s, h, 2, 2) != (0,)*4 and mv(y, (0, 1), 2, 2) == (1, 0),
         "missing scalar-endpoint countercontrol")
    count += 1
    try:
        cuts([target], ((0,)*9, (0,)*9, a), 3, 2)
    except ValueError:
        count += 1
    else:
        raise ValueError("singular coefficient accepted")
    return count


def main():
    result = {"status": "PASS_RADICAL_COMMON_FLAG",
              "claim_type": "scoped written proof with exact finite corroboration",
              "pair_censuses": [census(n, p) for n, p in ((2, 2), (2, 3), (3, 2))],
              "construction": constructions(), "cut_lemma": abstract_cuts(),
              "strict_obstruction": strict_fixture(), "controls": controls()}
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        with (package/name).open("rb") as source:
            content = source.read(131073)
        need(len(content) <= 131072, "file capacity")
        hashes[name] = hashlib.sha256(content).hexdigest()
    result["sha256"] = hashes
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
