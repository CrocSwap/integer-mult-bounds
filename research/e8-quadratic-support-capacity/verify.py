"""Analytic E8 support capacities, with exact label binding. Apache-2.0."""

import argparse
import json
from hashlib import sha1, sha256
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
WITNESSES = (
    (4, 5, (124, 94, 208, 18), 12),
    (5, 6, (210, 249, 50, 247, 170), 20),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_bytes(path, limit=100_000):
    require(path.is_file() and not path.is_symlink(), "missing or linked source")
    require(path.stat().st_size <= limit, "source exceeds byte bound")
    return path.read_bytes()


def authenticate(root=ROOT):
    pins = json.loads(bounded_bytes(PACKAGE / "SOURCES.json"))
    require(
        set(pins) == {"schema_version", "base_commit", "files", "credit"},
        "source manifest fields",
    )
    rows = pins["files"]
    require(isinstance(rows, list) and len(rows) == 3, "three exact source rows")
    expected = {
        (GEOMETRY, "input"),
        ("docs/research/agent-task-catalog.json", "provenance"),
        ("certificates/selected-result.json", "provenance"),
    }
    require(
        all(
            isinstance(row, dict)
            and set(row) == {"path", "usage", "git_blob", "sha256"}
            and isinstance(row["path"], str)
            and isinstance(row["usage"], str)
            and all(
                isinstance(row[key], str)
                and len(row[key]) == size
                and set(row[key]) <= set("0123456789abcdef")
                for key, size in (("git_blob", 40), ("sha256", 64))
            )
            for row in rows
        ),
        "malformed source row",
    )
    require(
        {(row["path"], row["usage"]) for row in rows} == expected, "source inventory"
    )
    pin = next(row for row in rows if row["usage"] == "input")
    raw = bounded_bytes(root / GEOMETRY)
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(
        sha256(raw).hexdigest() == pin["sha256"] and blob == pin["git_blob"],
        "geometry bytes differ from pin",
    )
    return raw


def load_geometry():
    raw = authenticate()
    module = ModuleType("capacity_pinned_geometry")
    # Execute the bytes just authenticated; never consult an existing pyc.
    exec(compile(raw, GEOMETRY, "exec"), module.__dict__)
    return module


def rank(values, bits=9):
    require(len(values) <= 512 and 1 <= bits <= 9, "binary rank input bound")
    basis = []
    for original in values:
        require(type(original) is int and 0 <= original < 1 << bits, "binary vector")
        value = original
        for row in basis:
            value = min(value, value ^ row)
        if value:
            basis = sorted(basis + [value], reverse=True)
    return len(basis)


def span(basis):
    require(len(basis) <= 8 and rank(basis, 8) == len(basis), "independent direction")
    values = [0]
    for row in basis:
        values += [value ^ row for value in values]
    require(len(set(values)) == 1 << len(basis), "span cardinality")
    return tuple(values)


def quadratic_table(simple):
    require(len(simple) == 8 and all(len(row) == 8 for row in simple), "E8 basis")
    gram = tuple(
        tuple(sum(a * b for a, b in zip(x, y, strict=True)) // 4 for y in simple)
        for x in simple
    )
    require(all(gram[i][i] == 2 for i in range(8)), "simple root norms")
    polar = tuple(sum((gram[i][j] % 2) << j for j in range(8)) for i in range(8))
    require(rank(polar, 8) == 8, "nondegenerate polar form")
    table = tuple(
        (
            x.bit_count()
            + sum(
                gram[i][j]
                for i in range(8)
                for j in range(i + 1, 8)
                if x >> i & 1 and x >> j & 1
            )
        )
        % 2
        for x in range(256)
    )
    for x in range(256):
        for y in range(256):
            pairing = (
                sum((polar[i] & y).bit_count() for i in range(8) if x >> i & 1) % 2
            )
            require(table[x ^ y] == table[x] ^ table[y] ^ pairing, "polarization")
    require(sum(table) == 120, "plus type, Gauss sum sixteen")
    return table, gram


def affine_bound(dimension, polar_rank, balanced):
    require(type(dimension) is int and 0 <= dimension <= 5, "affine dimension")
    require(
        type(polar_rank) is int
        and 0 <= polar_rank <= dimension
        and polar_rank % 2 == 0
        and type(balanced) is bool,
        "restriction type",
    )
    radical = dimension - polar_rank
    require(radical <= 8 - dimension, "radical exceeds ambient perpendicular")
    if balanced:
        require(radical > 0, "a nontrivial radical character is required")
        return 1 << (dimension - 1)
    if dimension + radical == 8:
        return ((1 << dimension) - 16) // 2
    return ((1 << dimension) + (1 << (dimension - polar_rank // 2))) // 2


def branch_receipt():
    rows = []
    for dimension in (4, 5):
        for polar_rank in range(0, dimension + 1, 2):
            radical = dimension - polar_rank
            if radical > 8 - dimension:
                continue
            for balanced in (False, True):
                if balanced and radical == 0:
                    continue
                rows.append(
                    {
                        "affine_dimension": dimension,
                        "polar_rank": polar_rank,
                        "balanced": balanced,
                        "upper_bound": affine_bound(dimension, polar_rank, balanced),
                    }
                )
    require(
        max(row["upper_bound"] for row in rows if row["affine_dimension"] == 4) == 12,
        "rank-five upper bound",
    )
    require(
        max(row["upper_bound"] for row in rows if row["affine_dimension"] == 5) == 20,
        "rank-six upper bound",
    )
    return rows


def witness_receipt(points, labels):
    require(
        len(points) == len(labels) == 112 and all(label & 1 for label in labels),
        "live affine labels",
    )
    result = []
    for dimension, offset, basis, expected in WITNESSES:
        affine = {offset ^ value for value in span(basis)}
        support = sorted(label for label in labels if label >> 1 in affine)
        require(
            len(support) == expected and rank(support) == dimension + 1,
            "attaining P112 support",
        )
        result.append(
            {
                "binary_rank": dimension + 1,
                "affine_offset": offset,
                "direction_basis": basis,
                "support_labels": support,
                "support_size": len(support),
            }
        )
    return result


def compute():
    geometry = load_geometry()
    roots, points, labels, coordinates = geometry.root_data()
    table, gram = quadratic_table(geometry.SIMPLE)
    residues = tuple(
        sum((int(x) % 2) << i for i, x in enumerate(row)) for row in coordinates
    )
    require(
        len(set(residues)) == 120
        and set(residues) == {x for x in range(256) if table[x]},
        "all root lines equal all quadratic-one vectors",
    )
    by_root = dict(zip(roots, residues, strict=True))
    require(
        all(
            label == 1 | (by_root[root] << 1)
            for root, label in zip(points, labels, strict=True)
        ),
        "actual leading-one labels, not an assumed rank identification",
    )
    return {
        "schema": "e8-quadratic-support-capacity/v1",
        "gram": gram,
        "polar_rank": 8,
        "quadratic_ones": 120,
        "Gauss_sum": 16,
        "root_residue_bijection": 120,
        "live_label_bindings": 112,
        "polarization_pairs": 65536,
        "restriction_cases": branch_receipt(),
        "P112_attainment": witness_receipt(points, labels),
        "upper_bounds_full120_and_P112": {"5": 12, "6": 20},
        "global_flat_census_replayed": False,
        "new_shortening_claim": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(compute()))
    if args.output is None:
        require(
            result == json.loads(bounded_bytes(PACKAGE / "RESULT.json")),
            "receipt mismatch",
        )
    else:
        require(
            not args.output.resolve().is_relative_to(ROOT), "external output required"
        )
        with args.output.open("x", encoding="utf-8") as stream:
            text = json.dumps(result, indent=2, sort_keys=True) + "\n"
            require(stream.write(text) == len(text), "short write")
    print("PASS_E8_QUADRATIC_CAPACITY rank5=12 rank6=20 full120_and_P112")


if __name__ == "__main__":
    main()
