#!/usr/bin/env python3
"""Construct and certify the dyadic multiplicity operator for the pinned A1 W.

New construction produced by Nick Petalas. Apache-2.0.
No predecessor executable or characteristic-polynomial computation is run.
"""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
EVIDENCE = "research/a1-joint-216-charpoly/evidence/"
QUERY = ("research/centre-polynomial-cache-limits/frozen/work/"
         "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json")
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
R_INV = (0, 1, 6, 7, 3, 2, 5, 4)
R_EPS = (-1, 1, 1, 1, 1, 1, 1, -1)
U_INV = (0, 1, 2, 3, 7, 6, 5, 4)
CHARACTER = (2, 1, -1, -2, -1, 1)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_json(path):
    raw = path.read_bytes()
    need(len(raw) <= 2_000_000, "JSON capacity")
    return json.loads(raw), raw


def inputs():
    sources, _ = bounded_json(PACKAGE / "SOURCES.json")
    loaded = {}
    hashes = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            obj, raw = bounded_json(ROOT / row["path"])
            digest = hashlib.sha256(raw).hexdigest()
            need(digest == row["sha256"], "input hash: " + row["path"])
            loaded[row["path"]] = obj
            hashes[row["path"]] = digest
    vectors = [dict(v) for v in loaded[EVIDENCE + "basis.json"]["vectors"]]
    matrix = loaded[EVIDENCE + "matrix.json"]["rows"]
    query = loaded[QUERY]
    ports = list(map(int, query["ports"]))
    columns = [tuple(int(query["R"][i].get(str(j), 0)) for i in range(8))
               for j in range(112)]
    need(len(vectors) == len(matrix) == 216, "216-space input dimension")
    need(all(len(row) == 216 for row in matrix), "square input matrix")
    need(all(type(x) is int and -28 <= x <= 28 for row in matrix for x in row),
         "input matrix entry range")
    need(len(ports) == len(set(ports)) == 112, "query ports")
    need(all(0 < p < 512 for p in ports), "nine-bit port")
    need(all(v and all(0 <= i < 4096 and c in (-1, 1) for i, c in v.items())
             for v in vectors), "signed orbit basis entries")
    need(sum(len(v) for v in vectors) == len({i for v in vectors for i in v}),
         "disjoint orbit supports")
    return vectors, matrix, ports, columns, hashes


def normalize(vector):
    need(len(vector) == 8 and any(vector), "nonzero root")
    first = next(x for x in vector if x)
    need(first in (-1, 1), "root sign")
    return tuple(first * x for x in vector)


def label_action(inv, eps, ports, columns):
    need(sorted(inv) == list(range(8)) and len(eps) == 8, "coordinate permutation")
    need(all(s in (-1, 1) for s in eps), "coordinate signs")
    lookup = {normalize(c): p for c, p in zip(columns, ports, strict=True)}
    mapping = {}
    for c, p in zip(columns, ports, strict=True):
        image = normalize(tuple(eps[i] * c[inv[i]] for i in range(8)))
        need(image in lookup, "root leaves query")
        mapping[p] = lookup[image]
    linear = {0: 0}
    for p in ports:
        if p not in linear:
            linear.update({a ^ p: b ^ mapping[p] for a, b in list(linear.items())})
        need(len(linear) <= 512, "label-map capacity")
    need(len(linear) == len(set(linear.values())) == 512, "label automorphism")
    need(all(linear[a] == b for a, b in mapping.items()), "linear label agreement")
    return linear


def orbit_action(inv, eps, ports, columns, vectors):
    linear = label_action(inv, eps, ports, columns)
    sigma = [inv.index(i) for i in range(8)]
    owners = {i: (j, c) for j, v in enumerate(vectors) for i, c in v.items()}
    result = []
    for v in vectors:
        image = {sigma[i // 512] * 512 + linear[i % 512]: c * eps[sigma[i // 512]]
                 for i, c in v.items()}
        pivot = min(image)
        need(pivot in owners, "actor leaves pinned space")
        j, s = owners[pivot]
        s *= image[pivot]
        need(image == {i: s * c for i, c in vectors[j].items()}, "orbit action")
        result.append((j, s))
    need(len({j for j, _ in result}) == 216, "signed permutation on E")
    return result


def add(left, right, scale=1):
    need(len(left) <= 216 and len(right) <= 216, "sparse vector capacity")
    out = dict(left)
    for i, c in right.items():
        out[i] = out.get(i, 0) + scale * c
    return {i: c for i, c in out.items() if c}


def act(actor, vector):
    out = {}
    for j, c in vector.items():
        i, sign = actor[j]
        out[i] = out.get(i, 0) + sign * c
    return {i: c for i, c in out.items() if c}


def image(matrix, vector):
    out = {}
    for i, row in enumerate(matrix):
        c = sum(row[j] * value for j, value in vector.items())
        if c:
            out[i] = c
    return out


def projector(rotation):
    cols = []
    for j in range(216):
        v, total = {j: 1}, {}
        for c in CHARACTER:
            total = add(total, v, c)
            v = act(rotation, v)
        need(v == {j: 1}, "rotation order divides six")
        cols.append(total)
    return cols


def apply_columns(columns, vector):
    result = {}
    for j, c in vector.items():
        result = add(result, columns[j], c)
    return result


def elimination(columns):
    """Keep original columns and coordinate expressions for normalized pivots."""
    need(len(columns) <= 216, "column bound")
    rows, selected, indices = {}, [], []
    for index, column in enumerate(columns):
        v = {i: Fraction(c) for i, c in column.items()}
        coeff = {len(selected): Fraction(1)}
        for pivot, (row, coordinates) in rows.items():
            if pivot in v:
                scalar = -v[pivot]
                v = add(v, row, scalar)
                coeff = add(coeff, coordinates, scalar)
        if not v:
            continue
        pivot = min(v)
        scale = v[pivot]
        rows[pivot] = ({i: c / scale for i, c in v.items()},
                       {i: c / scale for i, c in coeff.items()})
        selected.append(column)
        indices.append(index)
    return selected, indices, rows


def coordinates(vector, rows):
    v = {i: Fraction(c) for i, c in vector.items()}
    result = {}
    for pivot, (row, coeff) in rows.items():
        if pivot in v:
            scalar = v[pivot]
            v = add(v, row, -scalar)
            result = add(result, coeff, scalar)
    need(not v, "image outside multiplicity space")
    return result


def modular_rank(columns, prime=1_000_003):
    """Independent dense row elimination; no rational construction is used."""
    need(len(columns) <= 216, "rank input capacity")
    rows = [[int(v.get(i, 0)) % prime for v in columns] for i in range(216)]
    rank = 0
    for col in range(len(columns)):
        pivot = next((i for i in range(rank, 216) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, prime)
        rows[rank] = [(x * inv) % prime for x in rows[rank]]
        for i in range(rank + 1, 216):
            scalar = rows[i][col]
            if scalar:
                rows[i] = [(a - scalar * b) % prime
                           for a, b in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


def intertwines(matrix, basis, k):
    if len(basis) != 64 or len(k) != 64 or any(len(row) != 64 for row in k):
        return False
    for j, vector in enumerate(basis):
        target = {i: k[i][j] for i in range(64) if k[i][j]}
        if image(matrix, vector) != apply_columns(basis, target):
            return False
    return True


def dense_certificate(matrix, basis, partners, k):
    """Check the rectangular integer identity using dense dot products."""
    ccols = [[v.get(i, 0) for i in range(216)] for v in basis + partners]
    crows = [list(row) for row in zip(*ccols, strict=True)]
    for j in range(128):
        block = j // 64
        column = j % 64
        for i in range(216):
            left = 2 * sum(a * b for a, b in zip(matrix[i], ccols[j], strict=True))
            right = sum(crows[i][block * 64 + t] * k[t][column] for t in range(64))
            need(left == right, "dense integer intertwiner")
    return 216 * 128


def construct(vectors, matrix, ports, columns):
    rotation = orbit_action(R_INV, R_EPS, ports, columns, vectors)
    reflection = orbit_action(U_INV, (1,) * 8, ports, columns, vectors)
    p = projector(rotation)
    need(sum(p[i].get(i, 0) for i in range(216)) == 768, "projector trace")
    for j, column in enumerate(p):
        need(apply_columns(p, column) == {i: 6 * c for i, c in column.items()},
             "scaled idempotent")
        need(act(reflection, act(reflection, {j: 1})) == {j: 1}, "reflection square")
    candidates = [add(v, act(reflection, v)) for v in p]
    basis, selected, rows = elimination(candidates)
    need(len(basis) == 64, "multiplicity dimension")
    tcols = [coordinates(image(matrix, v), rows) for v in basis]
    k = [[2 * tcols[j].get(i, 0) for j in range(64)] for i in range(64)]
    need(all(c.denominator == 1 for row in k for c in row), "8T integral")
    k = [[int(c) for c in row] for row in k]
    partners = [act(rotation, v) for v in basis]
    for v, rv in zip(basis, partners, strict=True):
        need(act(reflection, v) == v, "reflection-positive basis")
        need(act(rotation, rv) == add(rv, v, -1), "standard rotation block")
        need(act(reflection, rv) == add(v, rv, -1), "standard reflection block")
        need(apply_columns(p, v) == {i: 6 * c for i, c in v.items()}, "inside W")
    twice_b = [[2 * c for c in row] for row in matrix]
    need(intertwines(twice_b, basis, k), "first operator block")
    need(intertwines(twice_b, partners, k), "second operator block")
    need(modular_rank(basis + partners) == 128, "independent doubled basis")
    return basis, partners, selected, k, p, twice_b


def controls(basis, partners, k, p, twice_b):
    outcomes = []
    bad = [list(row) for row in k]
    bad[0][0] += 1
    outcomes.append(not intertwines(twice_b, basis, bad))
    outcomes.append(not intertwines(twice_b, partners, bad))
    outcomes.append(not intertwines(twice_b, basis, [[2 * c for c in row] for row in k]))
    outcomes.append(not intertwines(twice_b, basis[:-1], k))
    doubled = basis + partners
    outcomes.append(modular_rank(doubled[:-1]) == 127)
    outcomes.append(modular_rank(doubled[:-1] + [doubled[0]]) == 127)
    outcomes.append(modular_rank(basis) == 64)
    outcomes.append(any(apply_columns(p, {i: 1}) != {i: 6} for i in range(216)))
    # A nonidentity relabeling of the domain changes the represented operator.
    swapped = [dict(v) for v in basis]
    pair = next((j for j in range(1, 64) if k[j] != k[0]), None)
    need(pair is not None, "nonconstant matrix control")
    swapped[0], swapped[pair] = swapped[pair], swapped[0]
    outcomes.append(not intertwines(twice_b, swapped, k))
    need(all(outcomes), "semantic control failed")
    return len(outcomes)


def certificate(basis, selected, k):
    return {"convention": "T=K/8; C=[V,RV]; 2 B C=C diag(K,K)",
            "selected_projector_columns": selected,
            "V_columns": [sorted(v.items()) for v in basis], "K_rows": k}


def run():
    vectors, matrix, ports, columns, hashes = inputs()
    basis, partners, selected, k, p, twice_b = construct(vectors, matrix, ports, columns)
    count = controls(basis, partners, k, p, twice_b)
    dense_entries = dense_certificate(matrix, basis, partners, k)
    cert = certificate(basis, selected, k)
    supports = sorted({len(v) for v in basis})
    return cert, {"marker": "PASS_A1_DIHEDRAL_MULTIPLICITY_MATRIX",
                  "multiplicity_dimension": 64, "doubled_rank": 128,
                  "K_nonzero_entries": sum(c != 0 for row in k for c in row),
                  "K_min": min(map(min, k)), "K_max": max(map(max, k)),
                  "V_support_sizes": supports,
                  "T_common_denominator": math.lcm(*(Fraction(c, 8).denominator
                                                      for row in k for c in row)),
                  "dense_integer_equalities": dense_entries,
                  "controls": count, "input_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="create a new receipt outside the checkout")
    parser.add_argument("--matrix", action="store_true", help="include the complete new matrix and basis")
    args = parser.parse_args()
    if args.emit is not None:
        dest = args.emit.expanduser().resolve()
        need(not dest.is_relative_to(ROOT), "receipt must be outside checkout")
        need(not dest.exists(), "receipt already exists")
    cert, result = run()
    result["certificate_sha256"] = hashlib.sha256(
        json.dumps(cert, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result["package_sha256"] = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                                for name in FILES}
    result["python"] = sys.version
    if args.matrix:
        result["certificate"] = cert
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit is not None:
        with dest.open("x", encoding="utf-8") as stream:
            need(stream.write(output) == len(output), "complete receipt write")
    print(output, end="")


if __name__ == "__main__":
    main()
