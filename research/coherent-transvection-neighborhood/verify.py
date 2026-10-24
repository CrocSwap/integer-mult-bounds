#!/usr/bin/env python3
"""Exact cycle-constrained binary chart neighborhoods. Standard library only."""

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(vectors, width):
    """Canonical reduced basis, with decreasing pivot positions."""
    rows = [0] * width
    for vector in vectors:
        value = vector
        for pivot in range(width - 1, -1, -1):
            if value >> pivot & 1 and rows[pivot]:
                value ^= rows[pivot]
        if value:
            pivot = value.bit_length() - 1
            rows[pivot] = value
            for other in range(width):
                if other != pivot and rows[other] >> pivot & 1:
                    rows[other] ^= value
    return tuple(row for row in reversed(rows) if row)


def span(rows):
    values = [0]
    for row in rows:
        values += [value ^ row for value in values]
    return frozenset(values)


def pairing(left, right, n):
    mask = (1 << n) - 1
    return (((left & mask) & (right >> n)).bit_count()
            + ((right & mask) & (left >> n)).bit_count()) & 1


def transvect(value, axis, n):
    return value ^ (axis if pairing(value, axis, n) else 0)


def kernel(equations, width):
    reduced = basis(equations, width)
    pivots = {row.bit_length() - 1 for row in reduced}
    answer = []
    for free in range(width):
        if free not in pivots:
            value = 1 << free
            for row in reduced:
                if row >> free & 1:
                    value |= 1 << (row.bit_length() - 1)
            answer.append(value)
    return tuple(answer)


def combine(coefficients, rows):
    value = 0
    for index, row in enumerate(rows):
        if coefficients >> index & 1:
            value ^= row
    return value


def validate_basis(rows, width, expected=None):
    require(isinstance(rows, tuple) and len(rows) <= width, "basis size/type")
    require(all(type(x) is int and 0 < x < 1 << width for x in rows),
            "basis vector range")
    require(len(basis(rows, width)) == len(rows), "dependent basis")
    require(expected is None or len(rows) == expected, "basis dimension")


def intersection_basis(n, charts, allowed):
    """B=A intersect all charts, using L=L-perp and coefficient kernels."""
    equations = []
    for chart in charts:
        for vector in chart:
            equations.append(sum(pairing(axis, vector, n) << j
                                 for j, axis in enumerate(allowed)))
    return basis((combine(c, allowed) for c in kernel(equations, len(allowed))),
                 2 * n)


def representatives(n, allowed, common):
    """One or two axes per nonzero coset of B in A; no endpoint enumeration."""
    extended = basis(common, 2 * n)
    complement = []
    for axis in allowed:
        candidate = basis((*extended, axis), 2 * n)
        if len(candidate) > len(extended):
            complement.append(axis)
            extended = candidate
    answer = []
    for coefficients in range(1, 1 << len(complement)):
        axis = combine(coefficients, complement)
        answer.append(axis)
        partner = next((b for b in common if pairing(axis, b, n)), None)
        if partner is not None:
            answer.append(axis ^ partner)
    return tuple(answer)


def neighborhood(n, charts, allowed):
    """Validated public enumerator, bounded to n<=9 and at most 64 charts."""
    require(type(n) is int and 1 <= n <= 9, "n must be in 1..9")
    require(isinstance(charts, tuple) and 1 <= len(charts) <= 64,
            "nonempty chart tuple of size at most 64 required")
    validate_basis(allowed, 2 * n)
    for chart in charts:
        validate_basis(chart, 2 * n, n)
        require(all(pairing(x, y, n) == 0 for x in chart for y in chart),
                "nonisotropic chart")
    common = intersection_basis(n, charts, allowed)
    equations = [sum(pairing(a, b, n) << j for j, a in enumerate(allowed))
                 for b in common]
    t = len(basis(equations, len(allowed)))
    r = len(allowed) - len(common)
    require(0 <= t <= min(r, len(common)), "pairing rank invariant")
    axes = representatives(n, allowed, common)
    count = (1 << (r + 1)) - (1 << (r - t)) - 1
    require(len(axes) == count, "representative count invariant")
    return axes, (len(allowed), len(common), t)


def all_subspaces(width):
    require(0 <= width <= 4, "exhaustive subspace width cap")
    layers = [{frozenset({0})}]
    for dimension in range(width):
        following = set()
        for space in layers[dimension]:
            for value in range(1, 1 << width):
                if value not in space:
                    following.add(space | frozenset(x ^ value for x in space))
        layers.append(following)
    return tuple(sorted((s for layer in layers for s in layer),
                        key=lambda s: (len(s), tuple(sorted(s)))))


def literal_image(space, axis, n):
    return frozenset(transvect(x, axis, n) for x in space)


def exhaustive_triples(n):
    """All ordered triples, all allowed subspaces, and every literal axis."""
    spaces = all_subspaces(2 * n)
    lags = tuple(s for s in spaces if len(s) == 1 << n
                 and all(pairing(x, y, n) == 0 for x in s for y in s))
    images = {(i, a): literal_image(s, a, n)
              for i, s in enumerate(lags) for a in range(1 << (2 * n))}
    space_bases = {s: basis(s, 2 * n) for s in spaces}
    cached = {}
    cases = 0
    histogram = Counter()
    for indices in product(range(len(lags)), repeat=3):
        charts = tuple(lags[i] for i in indices)
        original = tuple(charts)
        common = charts[0] & charts[1] & charts[2]
        rows = tuple(space_bases[s] for s in charts)
        require(span(intersection_basis(n, rows, identity(n))) == common,
                "coefficient-kernel intersection mismatch")
        outcomes = {a: tuple(images[i, a] for i in indices)
                    for a in range(1 << (2 * n))}
        for allowed in spaces:
            bspace = allowed & common
            key = (allowed, bspace)
            if key not in cached:
                reps, dimensions = neighborhood(n, rows, space_bases[allowed])
                literal_t = len({tuple(pairing(a, b, n) for b in bspace)
                                 for a in allowed}).bit_length() - 1
                require(dimensions == (len(allowed).bit_length() - 1,
                                       len(bspace).bit_length() - 1, literal_t),
                        "dimension or pairing rank mismatch")
                fibers = {frozenset(bspace)}
                for a in allowed - bspace:
                    fibers.add(frozenset(a ^ b for b in bspace
                                         if pairing(a, b, n) == 0))
                cached[key] = (reps, dimensions, fibers)
            reps, dimensions, fibers = cached[key]
            actual = {}
            for a in allowed:
                actual.setdefault(outcomes[a], set()).add(a)
            changed = set(actual) - {original}
            delivered = [outcomes[a] for a in reps]
            require(len(delivered) == len(set(delivered)), "duplicate output")
            require(set(delivered) == changed, "incomplete neighborhood")
            require({frozenset(f) for f in actual.values()} == fibers,
                    "incorrect exact fiber law")
            m, b, t = dimensions
            require(len(actual) == (1 << (m - b + 1)) - (1 << (m - b - t)),
                    "incorrect closed count")
            cases += 1
            histogram[dimensions] += 1
    return {"n": n, "lagrangians": len(lags), "allowed_subspaces": len(spaces),
            "triple_subspace_cases": cases, "distinct_axis_problems": len(cached),
            "parameter_histogram": [[*k, v] for k, v in sorted(histogram.items())]}


def map_value(columns, value):
    return combine(value, columns)


def identity(n):
    return tuple(1 << j for j in range(2 * n))


def map_word(n, word):
    columns = identity(n)
    for axis in word:
        columns = tuple(transvect(x, axis, n) for x in columns)
    return columns


def compose(left, right):
    return tuple(map_value(left, x) for x in right)


def cycle_axes(n, transports, edges):
    """Root axes satisfying R_v a = S_e R_u a on every declared edge."""
    require(type(n) is int and 1 <= n <= 9, "cycle n range")
    require(isinstance(transports, tuple) and isinstance(edges, tuple)
            and 1 <= len(transports) <= 64 and len(edges) <= 128, "graph size")
    require(all(isinstance(edge, tuple) and len(edge) == 3 for edge in edges),
            "edge shape")
    require(transports[0] == identity(n), "root transport must be identity")
    for columns in (*transports, *(edge[2] for edge in edges)):
        validate_basis(columns, 2 * n, 2 * n)
        require(all(pairing(columns[i], columns[j], n)
                    == pairing(1 << i, 1 << j, n)
                    for i in range(2 * n) for j in range(2 * n)),
                "nonsymplectic transport")
    equations = []
    for u, v, operator in edges:
        require(type(u) is int and type(v) is int
                and 0 <= u < len(transports) and 0 <= v < len(transports),
                "edge vertex range")
        other = compose(operator, transports[u])
        differences = tuple(x ^ y for x, y in zip(transports[v], other))
        for bit in range(2 * n):
            equations.append(sum(((x >> bit) & 1) << j
                                 for j, x in enumerate(differences)))
    return kernel(equations, 2 * n)


def graph_controls():
    n = 2
    ident = identity(n)
    root_maps = (ident, map_word(n, (1, 4)), map_word(n, (2, 8, 3)))
    inverse_one = map_word(n, (4, 1))
    inverse_two = map_word(n, (3, 8, 2))
    total = 0
    dimensions = Counter()
    for h1 in range(1 << (2 * n)):
        for h2 in range(1 << (2 * n)):
            chord = compose(root_maps[2], compose(map_word(n, (h1,)), inverse_one))
            back = compose(map_word(n, (h2,)), inverse_two)
            edges = ((0, 1, root_maps[1]), (0, 2, root_maps[2]),
                     (1, 2, chord), (2, 0, back))
            allowed = span(cycle_axes(n, root_maps, edges))
            direct = set()
            for a in range(1 << (2 * n)):
                axes = tuple(map_value(r, a) for r in root_maps)
                coherent = all(axes[v] == map_value(s, axes[u])
                               for u, v, s in edges)
                literal = all(compose(map_word(n, (axes[v],)), s)
                              == compose(s, map_word(n, (axes[u],)))
                              for u, v, s in edges)
                require(coherent == literal, "literal conjugation mismatch")
                if literal:
                    direct.add(a)
                total += 1
            require(allowed == direct, "cycle kernel mismatch")
            dimensions[len(basis(allowed, 2 * n))] += 1
    return {"graphs": 256, "literal_axis_tests": total,
            "allowed_dimension_histogram": sorted(dimensions.items())}


def sharp_fixtures():
    n = 3
    disjoint = ((1, 2, 4), (1, 16, 32), (8, 2, 32))
    common = ((1, 2, 4), (1, 16, 32), (1, 2 ^ 16, 4 ^ 32))
    require(all(len(span(x) & span(y)) == 2
                for charts in (disjoint, common)
                for i, x in enumerate(charts) for y in charts[i + 1:]),
            "pairwise-distance fixture")
    counts = []
    for charts in (disjoint, common):
        reps, parameters = neighborhood(n, charts, identity(n))
        spaces = tuple(span(c) for c in charts)
        actual = {tuple(literal_image(s, a, n) for s in spaces)
                  for a in range(1 << (2 * n))} - {spaces}
        require(len(actual) == len(reps), "triple fixture literal count")
        counts.append({"m_b_t": parameters, "changed_tuples": len(reps)})
    require([x["changed_tuples"] for x in counts] == [63, 47],
            "pairwise data does not determine tuple count")
    allowed = tuple(x for x in identity(n) if x != 8)
    reps, parameters = neighborhood(n, common, allowed)
    require(len(reps) == 15 and parameters == (5, 1, 0), "cycle restriction fixture")
    return {"same_pairwise_distances": counts,
            "one_cycle_constraint": {"m_b_t": parameters, "changed_tuples": len(reps)}}


def rejection_controls():
    good = ((1, 2), (4, 8), (1 ^ 4, 2 ^ 8))
    calls = (
        lambda: neighborhood(0, good, (1,)),
        lambda: neighborhood(10, good, (1,)),
        lambda: neighborhood(2, (), (1,)),
        lambda: neighborhood(2, good, (1, 1)),
        lambda: neighborhood(2, good, (16,)),
        lambda: neighborhood(2, ((1, 4),), (1,)),
        lambda: neighborhood(2, ((1,),), (1,)),
        lambda: cycle_axes(2, (identity(2),), ((0, 1, identity(2)),)),
        lambda: cycle_axes(2, (identity(2),), ((0, 0, (1, 2, 4, 9)),)),
        lambda: cycle_axes(2, (identity(2),), ((0, 0),)),
        lambda: cycle_axes(2, (identity(2),), ((0, 0, identity(2)),) * 129),
    )
    for call in calls:
        try:
            call()
        except ValueError:
            continue
        raise ValueError("invalid input accepted")
    return len(calls)


def mutation_controls():
    n = 2
    chart = frozenset({0, 1, 2, 3})
    charts = ((1, 2),) * 3
    reps, parameters = neighborhood(n, charts, identity(n))
    target = {literal_image(chart, a, n) for a in range(16)} - {chart}
    first_only = tuple(a for a in reps if a in (4, 8, 12))
    require({literal_image(chart, a, n) for a in first_only} != target,
            "omitted second coset representative survived")
    raw = [literal_image(chart, a, n) for a in range(16) if a not in chart]
    require(len(raw) != len(set(raw)), "unquotiented axes survived")
    require(parameters == (4, 2, 2) and len(reps) != (1 << 2) - 1,
            "omitted pairing-rank correction survived")
    require(chart in {literal_image(chart, a, n) for a in (*reps, 0)},
            "trivial outcome contamination survived")
    restricted = ((1, 2, 4), (1, 16, 32), (1, 18, 36))
    axes, _ = neighborhood(3, restricted, (1, 2, 4, 16, 32))
    require(len(axes) == 15 and len(axes) != (1 << 6) - (1 << 4) - 1,
            "unrestricted ambient formula survived")
    return ["omit-second-representative", "omit-axis-quotient", "omit-pairing-rank",
            "include-fixed-outcome", "ignore-allowed-axis-space"]


def receipt():
    package = Path(__file__).resolve().parent
    files = ("verify.py", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    return {
        "schema": "coherent-transvection-neighborhood/v1",
        "claim_type": "scoped proof with finite exact corroboration",
        "source_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                          for name in files},
        "exhaustive": [exhaustive_triples(n) for n in (1, 2)],
        "graph": graph_controls(), "sharp_fixtures": sharp_fixtures(),
        "rejection_controls": rejection_controls(), "mutation_controls": mutation_controls(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    actual = json.loads(json.dumps(receipt(), sort_keys=True))
    if args.write_receipt is not None:
        args.write_receipt.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(Path(__file__).with_name("RESULT.json").read_text())
        require(actual == expected, "receipt or source hash mismatch")
    count = sum(row["triple_subspace_cases"] for row in actual["exhaustive"])
    print(f"PASS_COHERENT_TRANSVECTION_NEIGHBORHOOD cases={count} "
          f"literal_graph_axes={actual['graph']['literal_axis_tests']}")


if __name__ == "__main__":
    main()
