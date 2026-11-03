"""Independent bounded vector-set/GL corroboration of PROOF.md.

The census uses literal vector permutations, not the reference eliminator.
It writes no files. Redirect its generated JSON receipt outside the checkout.
"""

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("nested_capacity_reference",
                                             PACKAGE / "extension.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("reference module unavailable")
REFERENCE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = REFERENCE
SPEC.loader.exec_module(REFERENCE)


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def indices(mask, size):
    return tuple(i for i in range(size) if mask & (1 << i))


def vector_sum(a, b, q):
    return tuple((x + y) % q for x, y in zip(a, b))


def literal_span(rows, vectors, lookup, q):
    values = {vectors[0]}
    for row in rows:
        values = {vector_sum(v, tuple(t * x % q for x in row), q)
                  for v in values for t in range(q)}
    return sum(1 << lookup[v] for v in values)


def geometry(q, n):
    check((q, n) in ((2, 0), (2, 1), (2, 2), (3, 2), (5, 2), (2, 3)),
          "unbudgeted literal census")
    vectors = tuple(itertools.product(range(q), repeat=n))
    lookup = {v: i for i, v in enumerate(vectors)}
    spaces = {1}
    for _ in range(n):
        additions = set()
        for mask in spaces:
            for vector in vectors:
                rows = tuple(vectors[i] for i in indices(mask, len(vectors)))
                # A space has at most eight vectors in the n=3 domain.
                additions.add(literal_span(rows + (vector,), vectors, lookup, q))
        spaces |= additions
    spaces = tuple(sorted(spaces, key=lambda x: (x.bit_count(), x)))
    bases, dimensions = [], []
    for mask in spaces:
        basis, current = [], 1
        for i in indices(mask, len(vectors)):
            if not current & (1 << i):
                basis.append(vectors[i])
                current = literal_span(tuple(basis), vectors, lookup, q)
        check(current == mask and q ** len(basis) == mask.bit_count(), "space basis")
        bases.append(tuple(basis))
        dimensions.append(len(basis))
    return vectors, lookup, spaces, tuple(bases), tuple(dimensions)


def literal_groups(q, n, vectors, lookup, spaces):
    permutations, matrices = [], []
    for matrix in itertools.product(vectors, repeat=n):
        permutation = tuple(lookup[tuple(sum(v[j] * matrix[j][i] for j in range(n)) % q
                                        for i in range(n))] for v in vectors)
        if len(set(permutation)) == len(vectors):
            matrices.append(matrix)
            permutations.append(permutation)
    expected = 1
    for j in range(n):
        expected *= q ** n - q ** j
    check(len(matrices) == expected, "literal GL order")
    space_lookup = {mask: i for i, mask in enumerate(spaces)}
    images = tuple(tuple(space_lookup[sum(1 << permutation[i]
                                         for i in indices(mask, len(vectors)))]
                         for mask in spaces) for permutation in permutations)
    allowed = tuple(tuple(sum(1 << g for g in range(len(matrices))
                              if spaces[images[g][a]] & ~spaces[c] == 0)
                          for c in range(len(spaces))) for a in range(len(spaces)))
    return tuple(matrices), tuple(permutations), images, allowed


def tables(q, vectors, lookup, spaces, bases):
    space_lookup = {mask: i for i, mask in enumerate(spaces)}
    joins = tuple(tuple(space_lookup[literal_span(a + b, vectors, lookup, q)]
                        for b in bases) for a in bases)
    intersections = tuple(tuple(space_lookup[a & b] for b in spaces) for a in spaces)
    flags = tuple((c, d) for c in range(len(spaces)) for d in range(len(spaces))
                  if spaces[c] & ~spaces[d] == 0)
    return joins, intersections, flags


def stage_factors(q, u, g, images, spaces, dimensions, joins, intersections):
    up = images[g][u]
    es = tuple(dimensions[joins[u][s]] - dimensions[u] for s in range(len(spaces)))
    factors = []
    for s, e in enumerate(es):
        fixed_image = spaces[images[g][intersections[u][s]]]
        capacities = []
        for c in range(len(spaces)):
            b = dimensions[intersections[up][c]]
            d = dimensions[c] - b
            entries = []
            for previous in range(e + 1):
                value = 0
                if fixed_image & ~spaces[c] == 0 and e <= d:
                    value = 1
                    for j in range(previous, e):
                        value *= q ** dimensions[c] - q ** (b + j)
                entries.append(value)
            capacities.append(tuple(entries))
        factors.append(tuple(capacities))
    return es, tuple(factors)


def reference_check(q, n, u, g, a, b, c, d, bases, matrices, expected, construct):
    values = tuple(tuple(sum(v[j] * matrices[g][j][i] for j in range(n)) % q
                         for i in range(n)) for v in bases[u])
    problem = REFERENCE.Problem(q, n, bases[u], values,
                                (bases[a], bases[b]), (bases[c], bases[d]))
    check(REFERENCE.count_extensions(problem) == expected, "reference count")
    if not construct:
        return 0
    matrix = REFERENCE.construct_extension(problem)
    check((matrix is None) == (expected == 0), "reference existence")
    if matrix is not None:
        # These complete permutations are independent of the reference's rank check.
        vectors = tuple(itertools.product(range(q), repeat=n))
        outputs = {tuple(sum(v[j] * matrix[j][i] for j in range(n)) % q
                         for i in range(n)) for v in vectors}
        check(len(outputs) == len(vectors), "constructed literal bijection")
        lookup = {v: i for i, v in enumerate(vectors)}
        for source, capacity in ((a, c), (b, d)):
            source_mask = literal_span(bases[source], vectors, lookup, q)
            capacity_mask = literal_span(bases[capacity], vectors, lookup, q)
            for i in indices(source_mask, len(vectors)):
                value = tuple(sum(vectors[i][j] * matrix[j][r] for j in range(n)) % q
                              for r in range(n))
                check(capacity_mask & (1 << lookup[value]), "constructed inclusion")
        for v, value in zip(bases[u], values):
            actual = tuple(sum(v[j] * matrix[j][i] for j in range(n)) % q
                           for i in range(n))
            check(actual == value, "constructed prescribed values")
    return 1


def census(q, n):
    vectors, lookup, spaces, bases, dims = geometry(q, n)
    matrices, permutations, images, allowed = literal_groups(q, n, vectors, lookup, spaces)
    joins, intersections, flags = tables(q, vectors, lookup, spaces, bases)
    total = positive = partials = references = constructions = 0
    digest = hashlib.sha256()
    for u, mask in enumerate(spaces):
        restrictions = {}
        for g, permutation in enumerate(permutations):
            key = tuple(permutation[i] for i in indices(mask, len(vectors)))
            old_mask, representative = restrictions.get(key, (0, g))
            restrictions[key] = (old_mask | (1 << g), representative)
        expected_partials = 1
        for j in range(dims[u]):
            expected_partials *= q ** n - q ** j
        check(len(restrictions) == expected_partials, "complete partial injections")
        partials += len(restrictions)
        for partial_mask, g in restrictions.values():
            es, factors = stage_factors(q, u, g, images, spaces, dims, joins, intersections)
            tails = []
            for e in range(n - dims[u] + 1):
                value = 1
                for j in range(dims[u] + e, n):
                    value *= q ** n - q ** j
                tails.append(value)
            for a in range(len(spaces)):
                for b in range(len(spaces)):
                    s = joins[a][b]
                    for c, d in flags:
                        predicted = factors[a][c][0] * factors[s][d][es[a]] * tails[es[s]]
                        actual = (partial_mask & allowed[a][c] & allowed[b][d]).bit_count()
                        check(predicted == actual, "cumulative formula versus literal GL")
                        digest.update(actual.to_bytes(2, "little"))
                        if total % 1021 == 0 or (q, n) == (2, 2):
                            constructions += reference_check(q, n, u, g, a, b, c, d,
                                                               bases, matrices, actual,
                                                               total % 3063 == 0)
                            references += 1
                        total += 1
                        positive += int(actual > 0)
    return {"q": q, "n": n, "spaces": len(spaces), "target_flags": len(flags),
            "gl": len(matrices), "partial_injections": partials, "cases": total,
            "positive": positive, "reference_counts": references,
            "reference_constructions": constructions, "counts_sha256": digest.hexdigest()}


def fixtures():
    x, y, z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    fixed = ((1, 1, 0),)
    first = REFERENCE.Problem(2, 3, fixed, (z,), ((x,),), ((x,),))
    second = REFERENCE.Problem(2, 3, fixed, (z,), ((y,),), ((x, y),))
    joint = REFERENCE.Problem(2, 3, fixed, (z,), ((x,), (y,)), ((x,), (x, y)))
    counts = tuple(REFERENCE.count_extensions(p) for p in (first, second, joint))
    check(counts == (4, 12, 0), "mixed prescribed relation fixture")
    vectors = tuple(itertools.product(range(2), repeat=3))
    literal = [0, 0, 0]
    for matrix in itertools.product(vectors, repeat=3):
        outputs = tuple(tuple(sum(v[j] * matrix[j][i] for j in range(3)) % 2
                              for i in range(3)) for v in vectors)
        if len(set(outputs)) == 8 and outputs[6] == z:
            a = matrix[0] in ((0, 0, 0), x)
            b = matrix[1] in ((0, 0, 0), x, y, (1, 1, 0))
            for i, passed in enumerate((a, b, a and b)):
                literal[i] += int(passed)
    check(tuple(literal) == counts, "literal missed-compatibility counts")
    dimension = REFERENCE.Problem(2, 3, (), (), ((x,), (y,)), ((x,), (x,)))
    check(REFERENCE.count_extensions(dimension) == 0, "cumulative dimension fixture")
    feasible = REFERENCE.Problem(2, 3, fixed, ((1, 1, 0),),
                                 ((x,), (y,)), ((x,), (x, y)))
    check(REFERENCE.count_extensions(feasible) == 4, "changed compatible image")
    check(REFERENCE.construct_extension(feasible) is not None, "positive joint fixture")
    return {"separate_and_joint_counts": counts, "compatible_joint_count": 4,
            "dimension_obstruction": 0}


def malformed_controls():
    x, y = (1, 0), (0, 1)
    good = dict(q=2, n=2, u=(), images=(), sources=((x,),), capacities=((x,),))
    mutations = ({"q": 4}, {"q": True}, {"n": 7}, {"n": True},
                 {"sources": ((x,),) * 9, "capacities": ((x,),) * 9},
                 {"sources": ()}, {"sources": [(x,)]}, {"u": []},
                 {"u": (x,), "images": ()},
                 {"u": (x, y), "images": (x, x)},
                 {"sources": (((True, 0),),)}, {"sources": (((2, 0),),)},
                 {"sources": (((1,),),)},
                 {"sources": ((x,), (y,)), "capacities": ((x,), (y,))})
    for mutation in mutations:
        arguments = good | mutation
        for operation in (REFERENCE.count_extensions, REFERENCE.construct_extension):
            try:
                operation(REFERENCE.Problem(**arguments))
            except ValueError:
                continue
            raise RuntimeError("malformed boundary accepted")
    return len(mutations)


def longer_flags():
    cases = 0
    for q in (2, 3, 5, 7):
        for n in range(7):
            standard = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
            matrix = tuple(tuple((int(i == j) + int(i + 1 == j)) % q
                                 for j in range(n)) for i in range(n))
            u = standard[::2]
            images = tuple(REFERENCE.combine(v, matrix, q, n) for v in u)
            for k in (0, 1, 2, 8):
                sources = tuple(standard[:min(n, i + 1)][::2 if i % 2 else 1]
                                for i in range(k))
                capacities = tuple(tuple(REFERENCE.combine(v, matrix, q, n)
                                         for v in standard[:min(n, i + 1)])
                                   for i in range(k))
                problem = REFERENCE.Problem(q, n, u, images, sources, capacities)
                check(REFERENCE.count_extensions(problem) > 0, "attained longer flag")
                check(REFERENCE.construct_extension(problem) is not None,
                      "longer-flag constructor")
                cases += 1
    return cases


def main():
    check(len(sys.argv) == 1, "no command-line options are supported")
    domains = tuple(census(q, n) for q, n in
                    ((2, 0), (2, 1), (2, 2), (3, 2), (5, 2), (2, 3)))
    receipt = {"status": "PASS_NESTED_LATE_CAPACITY_COMPLETION", "domains": domains,
               "fixtures": fixtures(), "malformed_controls": malformed_controls(),
               "longer_flag_cases": longer_flags()}
    paths = tuple(sorted(path for path in PACKAGE.iterdir() if path.is_file()))
    check(len(paths) == 7, "unexpected package file inventory")
    check(all(path.stat().st_size <= 131072 for path in paths), "package file bound")
    receipt["package_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in paths}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
