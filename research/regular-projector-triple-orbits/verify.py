#!/usr/bin/env python3
"""Exact corroboration of regular rank-one triple orbits.

Produced by Nick Petalas. Apache-2.0. The written proof supplies all fields.
"""

import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """Only five admitted fields; F4 uses t^2+t+1."""

    def __init__(self, order):
        require(type(order) is int and order in (2, 3, 4, 5, 7), "field order")
        self.q = order
        self.add = tuple(tuple((a ^ b) if order == 4 else (a+b) % order
                               for b in range(order)) for a in range(order))
        self.neg = tuple(a if order == 4 else (-a) % order
                         for a in range(order))
        rows = []
        for a in range(order):
            row = []
            for b in range(order):
                if order == 4:
                    value = (a & 1)*b ^ ((a >> 1)*b << 1)
                    if value & 4:
                        value ^= 7
                else:
                    value = a*b % order
                row.append(value)
            rows.append(tuple(row))
        self.mul = tuple(rows)
        self.inv = (0,) + tuple(next(b for b in range(1, order)
                                    if self.mul[a][b] == 1)
                                for a in range(1, order))


def validate_matrix(a, f, maximum=5):
    require(isinstance(a, tuple) and 1 <= len(a) <= maximum, "matrix size")
    require(all(isinstance(row, tuple) and len(row) == len(a) for row in a),
            "matrix shape")
    require(all(type(x) is int and 0 <= x < f.q for row in a for x in row),
            "field entry")


def product(a, b, f):
    n = len(a)
    out = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                out[i][j] = f.add[out[i][j]][f.mul[a[i][k]][b[k][j]]]
    return tuple(tuple(row) for row in out)


def rank(a, f):
    rows = [list(row) for row in a]
    n, pivot = len(a), 0
    for col in range(n):
        found = next((i for i in range(pivot, n) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = f.inv[rows[pivot][col]]
        rows[pivot] = [f.mul[scale][x] for x in rows[pivot]]
        for i in range(n):
            if i != pivot:
                factor = f.neg[rows[i][col]]
                rows[i] = [f.add[x][f.mul[factor][y]]
                           for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def inverse(a, f):
    n = len(a)
    rows = [list(a[i])+[int(i == j) for j in range(n)] for i in range(n)]
    for col in range(n):
        found = next((i for i in range(col, n) if rows[i][col]), None)
        require(found is not None, "singular conjugator")
        rows[col], rows[found] = rows[found], rows[col]
        scale = f.inv[rows[col][col]]
        rows[col] = [f.mul[scale][x] for x in rows[col]]
        for i in range(n):
            if i != col:
                factor = f.neg[rows[i][col]]
                rows[i] = [f.add[x][f.mul[factor][y]]
                           for x, y in zip(rows[i], rows[col])]
    return tuple(tuple(row[n:]) for row in rows)


def determinant(a, f):
    """Six Leibniz terms, separate from row reduction."""
    total = 0
    for perm in itertools.permutations(range(3)):
        term = 1
        for i in range(3):
            term = f.mul[term][a[i][perm[i]]]
        inversions = sum(perm[i] > perm[j] for i in range(3)
                         for j in range(i+1, 3))
        total = f.add[total][f.neg[term] if inversions % 2 else term]
    return total


def trace(a, f):
    out = 0
    for i in range(len(a)):
        out = f.add[out][a[i][i]]
    return out


def gram_key(g, f):
    validate_matrix(g, f, 3)
    require(len(g) == 3 and all(g[i][i] == 1 for i in range(3)),
            "unit diagonal")
    require(all(g[i][j] != 0 for i in range(3) for j in range(3)),
            "fully coupled")
    require(determinant(g, f) != 0, "regular active summand")
    p = f.mul[g[0][1]][g[1][0]]
    q = f.mul[g[0][2]][g[2][0]]
    r = f.mul[g[1][2]][g[2][1]]
    u = f.mul[f.mul[g[0][1]][g[1][2]]][g[2][0]]
    return p, q, r, u


def representative(key, f):
    require(isinstance(key, tuple) and len(key) == 4, "four invariants")
    require(all(type(x) is int and 0 < x < f.q for x in key),
            "nonzero invariant")
    p, q, r, u = key
    g = ((1, 1, 1), (p, 1, f.mul[u][f.inv[q]]),
         (q, f.mul[f.mul[r][q]][f.inv[u]], 1))
    require(gram_key(g, f) == key, "admissible invariant")
    return g


def diagonal_conjugate(g, scales, f):
    return tuple(tuple(f.mul[f.mul[f.inv[scales[i]]][g[i][j]]][scales[j]]
                       for j in range(3)) for i in range(3))


def projectors(g, ambient=3):
    require(3 <= ambient <= 5, "ambient dimension")
    return tuple(tuple(tuple(g[i][j] if row == i and j < 3 else 0
                             for j in range(ambient))
                       for row in range(ambient)) for i in range(3))


def triple_key(ps, f):
    require(isinstance(ps, tuple) and len(ps) == 3, "three projectors")
    for p in ps:
        validate_matrix(p, f)
        require(len(p) == len(ps[0]), "common ambient dimension")
        require(rank(p, f) == 1 and product(p, p, f) == p, "rank-one idempotent")
    n = len(ps[0])
    s = tuple(tuple(f.add[f.add[ps[0][i][j]][ps[1][i][j]]][ps[2][i][j]]
                    for j in range(n)) for i in range(n))
    require(rank(s, f) == rank(product(s, s, f), f) == 3,
            "regular active summand")
    pairs = tuple(trace(product(ps[i], ps[j], f), f)
                  for i, j in ((0, 1), (0, 2), (1, 2)))
    u = trace(product(product(ps[0], ps[1], f), ps[2], f), f)
    require(all(x != 0 for x in pairs), "fully coupled")
    return pairs+(u,)


def census(f):
    """All six-entry Grams, compared with separately expanded orbits."""
    raw, classes, singular = set(), {}, 0
    positions = ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))
    for values in itertools.product(range(1, f.q), repeat=6):
        g = [[int(i == j) for j in range(3)] for i in range(3)]
        for (i, j), value in zip(positions, values):
            g[i][j] = value
        g = tuple(tuple(row) for row in g)
        if determinant(g, f) == 0:
            singular += 1
            continue
        key = gram_key(g, f)
        normalized = diagonal_conjugate(g, (1, f.inv[g[0][1]],
                                            f.inv[g[0][2]]), f)
        require(normalized == representative(key, f), "normal form")
        raw.add(g)
        classes[key] = classes.get(key, 0)+1
    expanded, accepted = set(), 0
    for key in itertools.product(range(1, f.q), repeat=4):
        p, q, r, u = key
        v = f.mul[f.mul[f.mul[p][q]][r]][f.inv[u]]
        delta = f.add[f.add[f.add[f.add[f.add[1][f.neg[p]]][f.neg[q]]]
                                    [f.neg[r]]][u]][v]
        if not delta:
            continue
        g = representative(key, f)
        require(rank(g, f) == 3, "row-reduction invertibility")
        require(triple_key(projectors(g), f) == key, "matrix trace invariant")
        for a, b in itertools.product(range(1, f.q), repeat=2):
            expanded.add(diagonal_conjugate(g, (1, a, b), f))
        accepted += 1
    expected = f.q**4-5*f.q**3+9*f.q**2-9*f.q+6
    require(raw == expanded, "complete diagonal-orbit partition")
    require(len(classes) == accepted == expected, "closed orbit count")
    require(all(count == (f.q-1)**2 for count in classes.values()), "free gauge orbit")
    require(len(raw)+singular == (f.q-1)**6, "complete six-entry domain")
    return {"field_order": f.q, "raw_grams": (f.q-1)**6,
            "regular_grams": len(raw), "classes": accepted,
            "singular_grams": singular}


def conjugacy_checks():
    """All GL3(F3) basis changes for the six canonical ternary triples."""
    f, seeds = Field(3), []
    for key in itertools.product(range(1, 3), repeat=4):
        try:
            seeds.append((key, projectors(representative(key, f))))
        except ValueError as exc:
            require(str(exc) == "regular active summand", "known rejection")
    require(len(seeds) == 6, "six ternary seeds")
    endpoints, group = set(), 0
    for entries in itertools.product(range(3), repeat=9):
        a = tuple(tuple(entries[3*i:3*i+3]) for i in range(3))
        if determinant(a, f) == 0:
            continue
        ai = inverse(a, f)
        for key, ps in seeds:
            changed = tuple(product(product(a, p, f), ai, f) for p in ps)
            require(triple_key(changed, f) == key, "full GL trace invariance")
            endpoints.add(changed)
        group += 1
    require(group == (27-1)*(27-3)*(27-9), "full GL3 enumeration")
    require(len(endpoints) == 6*group//2, "scalar centralizer")
    return {"group_order": group, "distinct_ordered_triples": len(endpoints),
            "conjugated_triples_checked": 6*group}


def controls():
    f = Field(5)
    g, h = (representative((1, 1, 1, u), f) for u in (2, 3))
    require(gram_key(g, f)[:3] == gram_key(h, f)[:3], "same pair data")
    require(gram_key(g, f) != gram_key(h, f), "oriented trace distinction")
    for n in (3, 4, 5):
        require(triple_key(projectors(g, n), f) == (1, 1, 1, 2), "zero spectators")
    invalid = [((1, 1, 1), (1, 1, 1), (1, 1, 1)),
               ((1, 0, 1), (1, 1, 1), (1, 1, 1)),
               ((2, 1, 1), (1, 1, 1), (1, 1, 1)),
               ((1, 1), (1, 1)), ((1, 1, 1), (1, 1, 1), (1, 1, 5))]
    rejections = 0
    for bad in invalid:
        try:
            gram_key(bad, f)
        except ValueError:
            rejections += 1
    for key in ((0, 1, 1, 2), (1, 1, 1, 1), (1, 1, 2), (1, 1, 1, 5)):
        try:
            representative(key, f)
        except ValueError:
            rejections += 1
    require(rejections == len(invalid)+4, "all invalid Grams and keys rejected")
    bad_ps = list(projectors(g))
    bad_ps[0] = tuple(tuple(0 for _ in range(3)) for _ in range(3))
    try:
        triple_key(tuple(bad_ps), f)
    except ValueError as exc:
        require(str(exc) == "rank-one idempotent", "rank rejection")
        rejections += 1
    require(rejections == 10, "all ten domain rejections")
    require(Field(4).add[1][1] == 0 and Field(4).mul[2][2] == 3,
            "extension field differs from modular four")
    return {"domain_rejections": rejections, "pair_trace_ambiguity_field": 5,
            "spectator_dimensions": [0, 1, 2]}


def source_hashes():
    package = Path(__file__).resolve().parent
    out = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py"):
        with (package/name).open("rb") as handle:
            data = handle.read(1024*1024+1)
        require(len(data) <= 1024*1024, "package-file bound")
        out[name] = hashlib.sha256(data).hexdigest()
    return out


def main():
    report = {"claim_type": "scoped written proof with exact finite corroboration",
              "censuses": [census(Field(q)) for q in (2, 3, 4, 5, 7)],
              "full_conjugation": conjugacy_checks(),
              "controls": controls(), "sha256": source_hashes()}
    print(json.dumps(report, sort_keys=True, indent=2))
    print("PASS_REGULAR_PROJECTOR_TRIPLE_ORBITS")


if __name__ == "__main__":
    main()
