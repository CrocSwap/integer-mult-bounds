"""Complete fixed-cover classification. Exact nullspaces, modular rejection only."""

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
GEOMETRY_HASH = "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bounded_bytes(path):
    with path.open("rb") as source:
        data = source.read(100_001)
    require(len(data) <= 100_000, "oversized package input")
    return data


def read_json(path):
    return json.loads(bounded_bytes(path))


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate():
    sources = read_json(HERE / "SOURCES.json")
    expected = read_json(HERE / "LIVE-SOURCES.json")
    require(type(sources.get("schema_version")) is int, "source schema type")
    require(canonical_json(sources) == canonical_json(expected), "source inventory")
    pins = read_json(HERE / "PREDECESSORS.json")
    require(
        type(pins.get("schema_version")) is int and pins["schema_version"] == 1,
        "predecessor schema",
    )
    require(set(pins) == {"schema_version", "files"}, "predecessor fields")
    require(len(pins["files"]) == 2, "predecessor inventory size")
    fixed = read_json(HERE / "PREDECESSOR-PINS.json")
    require(canonical_json(pins) == canonical_json(fixed), "predecessor inventory")
    for row in pins["files"]:
        data = bounded_bytes(HERE / row["retained_path"])
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "predecessor bytes")
    data = bounded_bytes(ROOT / GEOMETRY)
    require(
        len(data) < 100_000 and hashlib.sha256(data).hexdigest() == GEOMETRY_HASH,
        "canonical geometry bytes",
    )
    namespace = {"__name__": "authenticated_geometry"}
    exec(compile(data, GEOMETRY, "exec"), namespace)  # Authenticated source, no pyc.
    return namespace


def binary_basis(values):
    pivots = {}
    for x in values:
        for p, row in sorted(pivots.items(), reverse=True):
            if x >> p & 1:
                x ^= row
        if x:
            pivots[x.bit_length() - 1] = x
    return tuple(pivots.values())


def root_closure(indices, labels):
    basis = binary_basis(labels[i] for i in indices)
    span = {0}
    for row in basis:
        span |= {x ^ row for x in tuple(span)}
    return [i for i, label in enumerate(labels) if label in span], len(basis)


def load_fixture(geometry):
    _, points, labels, _ = geometry["root_data"]()
    fixture = read_json(HERE / "vendor/PR3307-WITNESS.json")
    require(type(fixture["schema_version"]) is int, "fixture schema")
    for key, size, dimension in (("U_roots", 32, 7), ("V_roots", 8, 4)):
        ids = fixture[key]
        require(len(ids) == size and len(set(ids)) == size, "fixture support size")
        require(all(type(i) is int and 0 <= i < 112 for i in ids), "root index")
        closure, rank = root_closure(ids, labels)
        require(closure == ids and rank == dimension, "complete cover closure")
    directions = tuple(tuple(h) for h in fixture["directions"])
    cuts = tuple(row[0] for row in fixture["individual_cuts"])
    require(len(directions) == len(cuts) == 8 and len(set(cuts)) == 8, "normal count")
    require(
        all(len(h) == 8 and all(type(x) is int for x in h) for h in directions),
        "normal type",
    )
    require(
        all(
            sum(a * b for a, b in zip(h, g, strict=True)) == 8 * (i == j)
            for i, h in enumerate(directions)
            for j, g in enumerate(directions)
        ),
        "orthogonal normal basis",
    )
    require(
        all(points[t] == h for h, t in zip(directions, cuts, strict=True)),
        "normal is not its indexed root",
    )
    return points, labels, fixture, dict(zip(directions, cuts, strict=True))


def seven_spaces(labels):
    all_roots = (1 << 112) - 1
    kernels = tuple(
        all_roots
        ^ sum(1 << i for i, label in enumerate(labels) if (label & x).bit_count() & 1)
        for x in range(512)
    )
    spaces = []
    for p, q in itertools.combinations(range(9), 2):
        free = tuple(j for j in range(q) if j != p)
        for a in range(1 << p):
            x = (1 << p) | a
            for b in range(1 << len(free)):
                y = (1 << q) | sum(((b >> i) & 1) << j for i, j in enumerate(free))
                spaces.append((x, y, kernels[x] & kernels[y]))
    require(len(spaces) == 43_435, "incomplete binary seven-space enumeration")
    require(len({(x, y) for x, y, _ in spaces}) == 43_435, "duplicate annihilator")
    return spaces


def modular_dependencies(points, ids, prime):
    """Incremental row echelon basis with coordinates of each dependent row."""
    pivots, basis, dependencies = {}, [], []
    for index in ids:
        vector, coeff = [x % prime for x in points[index]], [0] * 8
        for p, (row, coordinates) in pivots.items():
            scale = vector[p]
            if scale:
                vector = [
                    (x - scale * y) % prime for x, y in zip(vector, row, strict=True)
                ]
                coeff = [
                    (x + scale * y) % prime
                    for x, y in zip(coeff, coordinates, strict=True)
                ]
        p = next((i for i, x in enumerate(vector) if x), None)
        if p is None:
            dependencies.append((index, coeff))
            continue
        coeff[len(basis)] = prime - 1
        basis.append(index)
        inverse = pow(vector[p], -1, prime)
        pivots[p] = (
            [x * inverse % prime for x in vector],
            [-x * inverse % prime for x in coeff],
        )
    require(len(basis) == 8, "baseline fails full modular rank")
    return basis, dependencies


def small_cuts(ids, basis, dependencies, prime):
    """All <=2 deletion sets that can lower rank, allowing modular false positives."""
    groups, zero, cuts = {}, [], set()
    for i, index in enumerate(basis):
        column = tuple(row[i] for _, row in dependencies)
        support = [j for j, value in enumerate(column) if value]
        if not support:
            zero.append(index)
            cuts.add((index,))
            continue
        if len(support) == 1:
            cuts.add(tuple(sorted((index, dependencies[support[0]][0]))))
        inverse = pow(column[support[0]], -1, prime)
        key = tuple(x * inverse % prime for x in column)
        for previous in groups.get(key, []):
            cuts.add(tuple(sorted((index, previous))))
        groups.setdefault(key, []).append(index)
    # A modular singleton may be a false positive. Test EVERY pair containing it.
    for index in zero:
        for other in ids:
            if index != other:
                cuts.add(tuple(sorted((index, other))))
    return sorted(cuts)


def exact_nullspace(rows):
    pivots = {}
    for row in rows:
        vector = list(map(Fraction, row))
        for p, basis in pivots.items():
            scale = vector[p]
            if scale:
                vector = [x - scale * y for x, y in zip(vector, basis, strict=True)]
        p = next((i for i, x in enumerate(vector) if x), None)
        if p is not None:
            pivots[p] = [x / vector[p] for x in vector]
    output = []
    for free in range(8):
        if free in pivots:
            continue
        vector = [Fraction(int(i == free)) for i in range(8)]
        for p, row in reversed(tuple(pivots.items())):
            vector[p] = -sum(row[i] * vector[i] for i in range(p + 1, 8))
        output.append(primitive(vector))
    require(
        all(
            all(sum(x * y for x, y in zip(h, r, strict=True)) == 0 for r in rows)
            for h in output
        ),
        "nullspace residual",
    )
    return output


def primitive(vector):
    scale = math.lcm(*(x.denominator for x in vector))
    integers = tuple(int(x * scale) for x in vector)
    divisor = math.gcd(*integers)
    require(divisor != 0, "zero projective vector")
    result = tuple(x // divisor for x in integers)
    return max(result, tuple(-x for x in result))


def classify(points, labels, fixture, allowed):
    cover = set(fixture["U_roots"]) | set(fixture["V_roots"])
    outside = [i for i in range(112) if i not in cover]
    records, candidates, active = set(), 0, 0
    for a, b, mask in seven_spaces(labels):
        ids = [i for i in outside if not (mask >> i & 1)]
        basis, dependencies = modular_dependencies(points, ids, 101)
        cuts = small_cuts(ids, basis, dependencies, 101)
        active += bool(cuts)
        for cut in cuts:
            candidates += 1
            nullspace = exact_nullspace([points[i] for i in ids if i not in cut])
            require(len(nullspace) <= 1, "unexpected multidimensional nullspace")
            for direction in nullspace:
                require(direction in allowed, "additional qualifying direction")
                required = tuple(
                    i
                    for i in ids
                    if sum(x * y for x, y in zip(direction, points[i], strict=True))
                )
                require(required == (allowed[direction],), "unexpected necessary cut")
                records.add((a, b, required[0], direction))
    require(len(records) == 8, "missing normal witness")
    return {
        "schema_version": 1,
        "binary_seven_spaces": 43_435,
        "baseline_full_rank": 43_435,
        "spaces_with_modular_small_cut": active,
        "exact_candidate_nullspaces": candidates,
        "classification": [
            {"annihilator": [a, b], "required_root": t, "direction": list(h)}
            for a, b, t, h in sorted(records)
        ],
        "pair_span_histogram": {
            "0": math.comb(112 - len(allowed), 2),
            "1": len(allowed) * (112 - len(allowed)),
            "2": math.comb(len(allowed), 2),
        },
        "arbitrary_cover_universal_span_five": "UNSETTLED",
    }


def main():
    geometry = authenticate()
    points, labels, fixture, allowed = load_fixture(geometry)
    actual = classify(points, labels, fixture, allowed)
    expected = read_json(HERE / "RESULT.json")
    require(
        canonical_json(actual) == canonical_json(expected), "classification receipt"
    )
    print(
        "PASS_ALPHA74_FIXED_COVER_COMPLETE spaces=43435 "
        "candidates=320 directions=8 maxspan=2"
    )


if __name__ == "__main__":
    main()
