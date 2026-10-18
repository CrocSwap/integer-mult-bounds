"""Mixed-rank A2 shortening and one literal P112 caller. Apache-2.0."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PROFILE = (5,) * 5 + (6,) * 5
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
DISTANCE = (0, 53, 78, 92, 100, 106, 109, 111, 112)
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_bytes(path, limit=2_000_000):
    require(path.is_file() and not path.is_symlink(), "missing or linked source")
    require(path.stat().st_size <= limit, "source capacity exceeded")
    return path.read_bytes()


def authenticate():
    sources = json.loads(bounded_bytes(PACKAGE / "SOURCES.json"))
    require(len(sources["files"]) == 4, "live/provenance inventory")
    require(len(sources["retained_files"]) == 6, "retained inventory")
    for row in sources["files"]:
        if row["usage"] == "input":
            raw = bounded_bytes(ROOT / row["path"])
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "live hash")
    for row in sources["retained_files"]:
        raw = bounded_bytes(PACKAGE / row["local_path"])
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained hash")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], "retained Git blob")


def binary_basis(values):
    require(len(values) <= 512, "binary input capacity")
    basis = []
    for value in values:
        require(type(value) is int and 0 <= value < 512, "nine-bit label")
        for row in basis:
            value = min(value, value ^ row)
        if value:
            basis = sorted(
                [min(row, row ^ value) for row in basis] + [value], reverse=True
            )
    return tuple(basis)


def projective(pair):
    divisor = gcd(*pair)
    if divisor == 0:
        return (0, 0)
    pair = tuple(x // divisor for x in pair)
    return pair if next(x for x in pair if x) > 0 else tuple(-x for x in pair)


def fiber_capacity(labels):
    require(len(labels) == len(set(labels)) == 27, "fiber size")
    basis = binary_basis(labels)
    require(len(basis) == 7, "fiber rank")
    coordinates = {0: 0}
    for i, row in enumerate(basis):
        coordinates.update(
            {x ^ row: c | (1 << i) for x, c in tuple(coordinates.items())}
        )
    code = tuple(coordinates[x] for x in labels)
    kernels = tuple(
        tuple(x for x in code if not ((a & x).bit_count() & 1)) for a in range(128)
    )
    six = Counter(len(kernels[a]) for a in range(1, 128))
    five = Counter()
    for a, b in combinations(range(1, 128), 2):
        if a < b < (a ^ b):
            five[sum(not ((b & x).bit_count() & 1) for x in kernels[a])] += 1
    require(sum(five.values()) == 2667 and max(five) == 10, "rank5 fiber capacity")
    require(sum(six.values()) == 127 and max(six) == 16, "rank6 fiber capacity")
    return {"rank5": dict(sorted(five.items())), "rank6": dict(sorted(six.items()))}


def geometric_receipt():
    sys.path.insert(0, str((ROOT / GEOMETRY).parent))
    import geometry

    roots, points, labels, coordinates = geometry.root_data()
    data = bounded_bytes(ROOT / "research/one-sided-six-multisets/data/data.txt")
    rows = data.decode("utf-8").splitlines()
    require(tuple(map(int, rows[0].split())) == labels, "live data label binding")
    require(
        tuple(tuple(map(int, row.split())) for row in rows[2:114]) == points,
        "live data root binding",
    )
    chamber = geometry.chamber_receipt(roots, points, coordinates)
    require(sorted(chamber["rank_six_parabolic_counts"])[-2:] == [30, 36], "E6 gap")
    index = {root: i for i, root in enumerate(roots)}
    planes = set()
    for i, j in combinations(range(120), 2):
        d = geometry.dot(roots[i], roots[j])
        if abs(d) == 4:
            third = geometry.canonical(
                tuple(x - (d // 4) * y for x, y in zip(roots[i], roots[j], strict=True))
            )
            planes.add(tuple(sorted((i, j, index[third]))))
    require(len(planes) == 1120, "A2 plane census")
    unions = Counter(
        sum(any(geometry.dot(roots[i], p) for i in plane) for p in points)
        for plane in planes
    )
    require(dict(unions) == {78: 896, 80: 224}, "A2 union spectrum")
    a, b = (roots[i] for i in min(planes)[:2])
    full_labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
        for row in coordinates
    )
    fibers = {}
    for root, label in zip(roots, full_labels, strict=True):
        key = projective((geometry.dot(a, root), geometry.dot(b, root)))
        if key != (0, 0):
            fibers.setdefault(key, []).append(label)
    require(sorted(map(len, fibers.values())) == [1, 1, 1, 27, 27, 27], "A2 fibers")
    capacities = [
        fiber_capacity(value)
        for key, value in sorted(fibers.items())
        if len(value) == 27
    ]
    bind_original(points, labels)
    return {"A2_union_histogram": unions, "fibers": capacities, "chamber": chamber}


def bind_original(points, labels):
    original = json.loads(
        bounded_bytes(PACKAGE / "vendor/bx_data.json"), parse_float=Fraction
    )
    require(len(original["L"]) == len(original["LAB"]) == 112, "original inventory")
    columns = (1, 52, 278, 138, 492, 418, 346, 154, 350)
    require(len(binary_basis(columns)) == 9, "label isomorphism rank")
    current = dict(zip(points, labels, strict=True))
    for raw, before in zip(original["L"], original["LAB"], strict=True):
        doubled = tuple(2 * Fraction(x) for x in raw)
        require(all(x.denominator == 1 for x in doubled), "integral doubled root")
        root = max(tuple(map(int, doubled)), tuple(-int(x) for x in doubled))
        require(type(before) is int and 0 < before < 512, "original label")
        mapped = 0
        for i in range(9):
            if before & (1 << i):
                mapped ^= columns[i]
        require(current[root] == mapped, "original/live root-label binding")


def historical_survivor(weights):
    require(6 <= len(weights) <= 10, "original(6,4) piece count")
    require(
        tuple(sorted(weights)) == weights and all(w in CAP for w in weights), "profile"
    )
    if sum(w - 2 for w in weights) >= 36:
        return False
    for level in range(1, 7):
        retained = weights[: len(weights) - 6 + level]
        total = sum(CAP[w] for w in retained)
        target = sum(32 if w == 7 else CAP[w] for w in retained)
        if level == 1 and target < 53 and total < 73:
            return False
        if level == 2 and target < 78 and total < 82:
            return False
        if level >= 3 and total < DISTANCE[level]:
            return False
    small = weights[: len(weights) - 6]
    if sum(CAP[w] for w in small) >= 53:
        return True
    if sum(small) <= 7:
        return False
    return not any(
        all(
            sum(w for w, side in zip(small, assignment, strict=True) if side == k) <= 6
            for k in (0, 1)
        )
        for assignment in product((0, 1), repeat=len(small))
    )


def mixed_bound(support, ranks=(5, 5, 6)):
    require(type(support) is int and 0 <= support <= 112, "common support")
    require(
        isinstance(ranks, tuple)
        and len(ranks) == 3
        and all(r in (5, 6) for r in ranks),
        "endpoint ranks",
    )
    pieces = sum(CAP[r] for r in ranks)
    singletons = sum(10 if r == 5 else 16 for r in ranks)
    normalization = support + pieces <= 81
    return {
        "common_support": support,
        "ranks": ranks,
        "global_piece_capacity": pieces,
        "singleton_capacity": singletons,
        "code_union_cap": support + pieces,
        "A2_classification_valid": normalization,
        "required_twice_residual_union": 2 * (78 - support),
        "incidence_plus_singletons_cap": pieces + singletons,
        "excluded": normalization and 2 * (78 - support) > pieces + singletons,
    }


def application(deleted=4):
    require(type(deleted) is int and 0 <= deleted <= 7, "deletion count")
    retained = PROFILE[: len(PROFILE) - deleted]
    require(6 - deleted >= 2, "retained code dimension")
    small, endpoints = retained[:-3], retained[-3:]
    result = mixed_bound(sum(CAP[w] for w in small), endpoints)
    require(result["common_support"] < 53, "restriction injectivity")
    require(result["excluded"], "mixed theorem does not apply")
    return {
        "profile": PROFILE,
        "cell": (6, 4),
        "deleted": deleted,
        "retained": retained,
        "small": small,
        "retained_code_dimension": 6 - deleted,
        "bound": result,
    }


def compute():
    authenticate()
    geometry = geometric_receipt()
    survivors = [
        weights
        for n in range(6, 11)
        for weights in combinations_with_replacement(range(2, 8), n)
        if historical_survivor(weights)
    ]
    require(len(survivors) == 69 and PROFILE in survivors, "historical caller")
    return {
        "schema": "p112-mixed-a2-caller/v1",
        "geometry": geometry,
        "historical_cell_survivors": survivors,
        "historical_count": 69,
        "application": application(),
        "theorem_support37": mixed_bound(37),
        "unclaimed_support38": mixed_bound(38),
        "global_flat_censuses_replayed": False,
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
            encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
            require(stream.write(encoded) == len(encoded), "short receipt write")
    print("PASS_P112_MIXED_A2_CALLER support37 caller36 count69 inequality84>80")


if __name__ == "__main__":
    main()
