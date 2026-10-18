"""Check the ten-singleton closure obstruction for P112 A2 shortening."""

import argparse
import json
import sys
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/p112-root-simplex-exclusion/geometry.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_retained_sources():
    rows = json.loads((PACKAGE / "SOURCES.json").read_text())["retained_files"]
    require(len(rows) == 2, "expected predecessor proof and receipt")
    for row in rows:
        require(
            row["local_path"]
            in ("vendor/PR3249-PROOF.md", "vendor/PR3249-RESULT.json"),
            "unexpected retained source path",
        )
        data = (PACKAGE / row["local_path"]).read_bytes()
        require(sha256(data).hexdigest() == row["sha256"], "retained source pin")


def load_geometry():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    pin = next(row for row in pins if row["path"] == SOURCE)
    path = ROOT / SOURCE
    require(sha256(path.read_bytes()).hexdigest() == pin["sha256"], "source pin")
    sys.path.insert(0, str(path.parent))
    import geometry

    return geometry


def binary_span(values):
    require(len(values) <= 120, "too many binary vectors")
    require(all(type(x) is int and 0 <= x < 512 for x in values), "nine-bit input")
    span = {0}
    basis = []
    for value in values:
        if value not in span:
            basis.append(value)
            span.update(x ^ value for x in tuple(span))
    return tuple(basis), span


def projective(pair):
    divisor = gcd(*pair)
    if not divisor:
        return (0, 0)
    pair = tuple(x // divisor for x in pair)
    return pair if next(x for x in pair if x) > 0 else tuple(-x for x in pair)


def validate_tight(support, all_labels):
    require(len(support) == len(set(support)) == 10, "expected ten singleton labels")
    require(len(all_labels) == len(set(all_labels)) == 120, "expected full E8 labels")
    basis, span = binary_span(support)
    require(len(basis) == 5, "ten singleton labels do not span five dimensions")
    closure = tuple(sorted(label for label in all_labels if label in span))
    require(closure == tuple(sorted(support)), "ten-singleton closure adds a root")
    return tuple(sorted(span))


def inspect_fiber(labels, all_labels):
    require(len(labels) == len(set(labels)) == 27, "expected a 27-line A2 fiber")
    basis, span = binary_span(labels)
    require(len(basis) == 7 and len(span) == 128, "fiber span is not seven-dimensional")
    coordinates = {0: 0}
    for i, row in enumerate(basis):
        coordinates.update(
            {x ^ row: c | (1 << i) for x, c in tuple(coordinates.items())}
        )
    histogram = Counter()
    tight = []
    for a, b in combinations(range(1, 128), 2):
        if not a < b < (a ^ b):
            continue
        support = tuple(
            label
            for label in labels
            if not ((coordinates[label] & a).bit_count() & 1)
            and not ((coordinates[label] & b).bit_count() & 1)
        )
        histogram[len(support)] += 1
        if len(support) == 10:
            tight.append(validate_tight(support, all_labels))
    require(sum(histogram.values()) == 2667, "incomplete codimension-two census")
    require(max(histogram) == 10 and len(tight) == 216, "fiber capacity changed")
    require(len(set(tight)) == 216, "duplicate tight five-flat")
    return {
        "subspaces": 2667,
        "intersection_histogram": dict(sorted(histogram.items())),
        "tight_flats": 216,
        "tight_closure_full_e8_lines": 10,
        "tight_flats_sha256": sha256(repr(sorted(tight)).encode()).hexdigest(),
        "witness_labels": sorted(label for label in all_labels if label in tight[0]),
    }


def singleton_budget(singletons):
    require(type(singletons) is int and 0 <= singletons <= 10, "singleton range")
    # PR3249 gives support<=12. Ten singletons force support<=10 here.
    return singletons + (10 if singletons == 10 else 12)


def compute():
    check_retained_sources()
    geometry = load_geometry()
    roots, _, _, coordinates = geometry.root_data()
    all_labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
        for row in coordinates
    )
    a = roots[0]
    b = next(root for root in roots if abs(geometry.dot(a, root)) == 4)
    classes = {}
    for root, label in zip(roots, all_labels, strict=True):
        key = projective((geometry.dot(a, root), geometry.dot(b, root)))
        classes.setdefault(key, []).append(label)
    require(
        sorted(map(len, classes.values())) == [1, 1, 1, 27, 27, 27, 36], "A2 fibers"
    )
    fibers = {
        str(key): inspect_fiber(value, all_labels)
        for key, value in sorted(classes.items())
        if len(value) == 27
    }
    budget = max(singleton_budget(n) for n in range(11))
    require(budget == 21 and 3 * budget < 2 * (78 - 45), "shortening inequality")
    require(112 - (45 + 3 * 12) == 31 > 30, "E6 normalization gap")
    require(112 - (46 + 3 * 12) == 30, "next normalization boundary changed")
    return {
        "claim": "three-rank5-common-support45-intersection-at-most-one",
        "scope": "characteristic-zero; threshold sufficient, sharpness unknown",
        "plane_root_indices": [roots.index(a), roots.index(b)],
        "fibers": fibers,
        "per_piece_incidence_plus_singleton_upper_bound": budget,
        "three_piece_upper_bound": 3 * budget,
        "minimum_twice_residual_union_at45": 2 * (78 - 45),
        "minimum_orthogonal_live_roots_at45": 31,
        "support46_not_claimed": "30 perpendicular roots no longer force E6",
        "inherited_not_replayed": [
            "P112 five-flat capacity12",
            "A2 Weyl transitivity",
            "A2 live union minimum78",
            "rank-six parabolic gap30/36",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(compute()))
    if args.output:
        require(
            not args.output.resolve().is_relative_to(ROOT), "external output required"
        )
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(
            result == json.loads((PACKAGE / "RESULT.json").read_text()),
            "receipt differs",
        )
    print(
        "PASS_P112_A2_SUPPORT45 fibers=3 flats=8001 tight=648 closure=10 threshold=45"
    )


if __name__ == "__main__":
    main()
