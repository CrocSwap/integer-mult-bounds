"""Exact three-frame shared-map counts. No predecessor imports."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SOURCE_NAMES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def gl_order(q, n):
    require(type(q) is int and 2 <= q <= 256, "field size outside arithmetic bound")
    require(type(n) is int and 0 <= n <= 64, "dimension outside arithmetic bound")
    value = 1
    for i in range(n):
        value *= q ** n - q ** i
    return value


def multiplicities(n, dims, pairs, common, total):
    """Return Boolean atoms in mask order, then the two-dimensional triangle."""
    require(len(dims) == len(pairs) == 3, "expected three dimensions and intersections")
    values = (n, *dims, *pairs, common, total)
    require(all(type(x) is int and 0 <= x <= 64 for x in values), "invalid dimension")
    d1, d2, d3 = dims
    p12, p13, p23 = pairs
    triangle = sum(dims) - sum(pairs) + common - total
    atoms = (n - total,
             d1 - p12 - p13 + common - triangle,
             d2 - p12 - p23 + common - triangle,
             p12 - common,
             d3 - p13 - p23 + common - triangle,
             p13 - common, p23 - common, common)
    require(min(*atoms, triangle) >= 0, "infeasible dimension data")
    require(sum(atoms) + 2 * triangle == n, "normal-form dimension mismatch")
    return atoms, triangle


def stabilizer(q, atoms, triangle):
    require(len(atoms) == 8, "expected eight Boolean atoms")
    require(all(type(x) is int and 0 <= x <= 64 for x in (*atoms, triangle)),
            "invalid multiplicity")
    n = sum(atoms) + 2 * triangle
    require(n <= 64, "normal form too large")
    end_dimension = sum(atoms[s] * atoms[t]
                        for s in range(8) for t in range(8) if s & t == s)
    end_dimension += triangle * (2 * atoms[0] + atoms[1] + atoms[2] + atoms[4]
                                 + atoms[3] + atoms[5] + atoms[6] + 2 * atoms[7])
    end_dimension += triangle ** 2
    free_entries = end_dimension - sum(x * x for x in atoms) - triangle ** 2
    require(free_entries >= 0, "negative off-diagonal dimension")
    value = q ** free_entries * gl_order(q, triangle)
    for m in atoms:
        value *= gl_order(q, m)
    require(gl_order(q, n) % value == 0, "stabilizer does not divide GL")
    return value


def add(x, y, q):
    return tuple((a + b) % q for a, b in zip(x, y, strict=True))


def span(vectors, q, n):
    require(q in (2, 3, 5) and 0 <= n <= 3 and q ** n <= 25,
            "literal experiment outside fixed domain")
    require(len(vectors) <= 3 * q ** n, "too many span generators")
    result = frozenset({(0,) * n})
    for v in vectors:
        multiples = [tuple(c * x % q for x in v) for c in range(q)]
        result = frozenset(add(x, y, q) for x in result for y in multiples)
    return result


def spaces(q, n):
    vectors = tuple(product(range(q), repeat=n))
    found = {frozenset({(0,) * n})}
    for _ in range(n):
        previous = tuple(found)
        for space in previous:
            for v in vectors:
                found.add(span((*space, v), q, n))
    return tuple(sorted(found, key=lambda x: (len(x), sorted(x)))), vectors


def dimension(space, q, n):
    candidates = [i for i in range(n + 1) if q ** i == len(space)]
    require(len(candidates) == 1, "set is not a subspace size")
    return candidates[0]


def signature(triple, q, n):
    dims = tuple(dimension(x, q, n) for x in triple)
    pairs = tuple(dimension(triple[i] & triple[j], q, n)
                  for i, j in combinations(range(3), 2))
    common = dimension(triple[0] & triple[1] & triple[2], q, n)
    total = dimension(span(tuple(set().union(*triple)), q, n), q, n)
    return multiplicities(n, dims, pairs, common, total)


def matrix_action(columns, v, q, n):
    return tuple(sum(columns[j][i] * v[j] for j in range(n)) % q
                 for i in range(n))


def permutations(q, n, subspaces, vectors):
    indices = {s: i for i, s in enumerate(subspaces)}
    result = []
    for columns in product(vectors[1:], repeat=n):
        if len(span(columns, q, n)) == q ** n:
            permutation = tuple(indices[frozenset(matrix_action(columns, v, q, n)
                                                  for v in s)] for s in subspaces)
            result.append(permutation)
    require(len(result) == gl_order(q, n), "literal GL enumeration incomplete")
    return result


def orbit_check(q, n):
    subspaces, vectors = spaces(q, n)
    actions = permutations(q, n, subspaces, vectors)
    signatures = {t: signature(tuple(subspaces[i] for i in t), q, n)
                  for t in product(range(len(subspaces)), repeat=3)}
    unseen = set(signatures)
    seen_signatures = set()
    histogram = Counter()
    digest = sha256()
    applications = 0
    # Each iteration removes at least one triple; the for loop is explicitly bounded.
    for representative in sorted(signatures):
        if representative not in unseen:
            continue
        images = Counter(tuple(p[i] for i in representative) for p in actions)
        applications += len(actions)
        key = signatures[representative]
        require(key not in seen_signatures, "same invariant in two GL orbits")
        seen_signatures.add(key)
        predicted = stabilizer(q, *key)
        require(images[representative] == predicted, "wrong literal stabilizer")
        require(len(images) * predicted == len(actions), "wrong orbit size")
        for image, count in sorted(images.items()):
            require(signatures[image] == key, "invariant changed under GL")
            require(count == predicted, "wrong realizing-map multiplicity")
            digest.update(repr((representative, image, count)).encode("ascii"))
        unseen.difference_update(images)
        histogram[predicted] += 1
    require(not unseen, "uncovered triples")
    expected_orbits = sum(comb(n - 2 * t + 7, 7) for t in range(n // 2 + 1))
    require(len(seen_signatures) == expected_orbits, "normal-form count mismatch")
    return {"q": q, "n": n, "subspaces": len(subspaces), "triples": len(signatures),
            "GL": len(actions), "orbits": expected_orbits,
            "matrix_triple_images": applications,
            "stabilizer_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "classification_sha256": digest.hexdigest()}


def controls():
    cases = [(lambda: multiplicities(2, (1, 1, 1), (0, 0, 0), 0, 4)),
             (lambda: multiplicities(2, (1, 1), (0, 0, 0), 0, 2)),
             (lambda: multiplicities(2, (True, 1, 1), (0, 0, 0), 0, 2)),
             (lambda: stabilizer(2, (0,) * 8, -1)),
             (lambda: gl_order(1, 2)), (lambda: gl_order(2, 65)),
             (lambda: span((), 7, 2))]
    for f in cases:
        try:
            f()
        except ValueError:
            continue
        raise ValueError("invalid input accepted")
    a = multiplicities(3, (1, 1, 1), (0, 0, 0), 0, 2)
    b = multiplicities(3, (1, 1, 1), (0, 0, 0), 0, 3)
    require(a != b and stabilizer(2, *a) == 4 and stabilizer(2, *b) == 1,
            "sum-dimension discrimination failed")
    c = multiplicities(3, (2, 2, 2), (1, 1, 1), 0, 3)
    d = multiplicities(3, (2, 2, 2), (1, 1, 1), 1, 3)
    require(c != d, "triple-intersection discrimination failed")
    return {"invalid_inputs_rejected": len(cases), "incomplete_invariants_rejected": 2}


def source_hashes():
    root = PACKAGE.parents[1]
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source drift: " + row["path"])
    return {name: sha256((PACKAGE / name).read_bytes()).hexdigest() for name in SOURCE_NAMES}


def nine_dimensional_types():
    """Enumerate normal-form tuples, never nine-dimensional subspace matrices."""
    count = 0
    digest = sha256()
    for triangle in range(5):
        total = 9 - 2 * triangle
        for bars in combinations(range(total + 7), 7):
            ends = (-1, *bars, total + 7)
            atoms = tuple(ends[i + 1] - ends[i] - 1 for i in range(8))
            dims = tuple(sum(atoms[s] for s in range(8) if s & (1 << i)) + triangle
                         for i in range(3))
            pairs = tuple(atoms[(1 << i) | (1 << j)] + atoms[7]
                          for i, j in combinations(range(3), 2))
            require(multiplicities(9, dims, pairs, atoms[7], 9 - atoms[0])
                    == (atoms, triangle), "normal-form tuple reconstruction failed")
            digest.update(repr((atoms, triangle)).encode("ascii"))
            count += 1
    require(count == sum(comb(9 - 2 * t + 7, 7) for t in range(5)) == 15792,
            "dimension-nine normal-form enumeration changed")
    return {"count": count, "tuple_sha256": digest.hexdigest()}


def certificate():
    cases = [orbit_check(q, n) for q, n in ((2, 0), (2, 1), (2, 2),
                                         (2, 3), (3, 2), (5, 2))]
    nine = nine_dimensional_types()
    return {"schema": "three-frame-shared-map/v1", "claim_type": "scoped proof",
            "source_sha256": source_hashes(), "literal_cases": cases,
            "dimension_nine_orbits": nine["count"],
            "dimension_nine_normal_forms": nine, "controls": controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a new receipt, never overwrite")
    args = parser.parse_args()
    result = certificate()
    if args.write is None:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "receipt differs from regenerated certificate")
    else:
        with args.write.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_THREE_FRAME_SHARED_MAP", json.dumps(
        {"triples": sum(c["triples"] for c in result["literal_cases"]),
         "orbits": sum(c["orbits"] for c in result["literal_cases"]),
         "dimension_nine_orbits": result["dimension_nine_orbits"]}, sort_keys=True))


if __name__ == "__main__":
    main()
