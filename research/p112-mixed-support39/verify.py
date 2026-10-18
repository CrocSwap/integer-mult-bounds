"""Check the cut39 implication with explicit inherited premises.

Nick Petalas. Apache-2.0. No pending Git objects are needed at replay time.
"""

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from itertools import combinations
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
EXPECTED_SOURCES = {
    "schema_version": 1,
    "base_commit": "463113d675af7410ac91d53a4fed51ec6494eb9a",
    "files": [
        {
            "path": "certificates/selected-result.json",
            "usage": "provenance",
            "git_blob": "b1fea0c94436b236cc2b7d41a7be032811b94c81",
            "sha256": "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
        },
        {
            "path": "docs/research/agent-task-catalog.json",
            "usage": "provenance",
            "git_blob": "67f085acd86acd7d4e03922d9cf4b26bca66fed5",
            "sha256": "47b42433f5a85809a3aadd29c2c339da2c6ed728e4f7762df6b88bccb7874cf0",
        },
        {
            "path": "research/p112-root-simplex-exclusion/geometry.py",
            "usage": "input",
            "git_blob": "222ea556faf2b275f73815c4e7d0d5f1e3294f2f",
            "sha256": "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021",
        },
    ],
    "retained_files": [
        {
            "local_path": "vendor/pr3267-PROOF.md",
            "source_path": "research/p112-mixed-support38/PROOF.md",
            "commit": "008f042859a5183d1323228a68aa1038f8d7718a",
            "pr": 3267,
            "git_blob": "3b45a136005ac98de7bf7b8110ab2fbb54318b7e",
            "sha256": "74b3e610a69a2f5e372595efbc17f3215c3f1af53a0f536dbbc12e5abb821327",
        },
        {
            "local_path": "vendor/pr3267-RESULT.json",
            "source_path": "research/p112-mixed-support38/RESULT.json",
            "commit": "008f042859a5183d1323228a68aa1038f8d7718a",
            "pr": 3267,
            "git_blob": "4bde18468f8c4698b0b75d964c8511f288778ec0",
            "sha256": "877feb226afef1f36fce8762c7df092869b289aab10efb78e69d9d3b5e5f3f76",
        },
        {
            "local_path": "vendor/pr3269-PROOF.md",
            "source_path": "research/e8-quadratic-support-capacity/PROOF.md",
            "commit": "ebe02d33157dc6c6d3b35df204e4a39242b7429e",
            "pr": 3269,
            "git_blob": "4da8e98edcfbbb9d5cd17b7ee921aa323d2fc724",
            "sha256": "0a68df931e4da65a9568a5ad3731c2a6c6f6b6fca57839d7d4c12a6fba0b333e",
        },
        {
            "local_path": "vendor/pr3269-RESULT.json",
            "source_path": "research/e8-quadratic-support-capacity/RESULT.json",
            "commit": "ebe02d33157dc6c6d3b35df204e4a39242b7429e",
            "pr": 3269,
            "git_blob": "c500166c56c36b42efe7fe592b8119fa04e83cda",
            "sha256": "e7f12a2a9305f63bd98f0f8b7aa2f804251871e134dc6004b0667e89d52a933d",
        },
    ],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    require(path.is_file() and not path.is_symlink(), "missing or linked input")
    require(path.stat().st_size <= 100_000, "input size bound")
    return path.read_bytes()


def authenticate(package=PACKAGE, root=ROOT):
    source = json.loads(read_bytes(package / "SOURCES.json"))
    require(
        json.dumps(source, sort_keys=True) == json.dumps(EXPECTED_SOURCES, sort_keys=True),
        "fixed source inventory, usage and schema",
    )
    rows = [r for r in source["files"] if r["usage"] == "input"]
    for row in rows + source["retained_files"]:
        path = root / row["path"] if "path" in row else package / row["local_path"]
        raw = read_bytes(path)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], "input Git blob")
    return source


def geometry():
    authenticate()
    spec = importlib.util.spec_from_file_location("bound_geometry", ROOT / GEOMETRY)
    require(spec is not None and spec.loader is not None, "geometry loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inherited():
    old = json.loads(read_bytes(PACKAGE / "vendor/pr3267-RESULT.json"))
    capacity = json.loads(read_bytes(PACKAGE / "vendor/pr3269-RESULT.json"))
    require(old["status"] == "PASS_MIXED_P112_SUPPORT38", "predecessor receipt")
    require(old["A2"]["union_histogram"] == {"78": 896, "80": 224}, "A2 unions")
    require(old["D6"]["axis_maximum_histogram"] == {"18": 896}, "D6 capacity")
    require(old["D6"]["live_axis_fibers"] == 896, "D6 coverage")
    require(old["budgets"]["E6_allowance"] == 76, "A2 joint budget")
    require(
        capacity["upper_bounds_full120_and_P112"] == {"5": 12, "6": 20},
        "global label capacities",
    )
    return {
        "global_support": [12, 12, 20],
        "A2_joint": [22, 22, 32],
        "D6_exclusive_rank6": 18,
        "capacity_censuses_rerun": False,
    }


def classify(g, roots, coordinates):
    five_max = max(
        sum(all(c[i] == 0 for i in omitted) for c in coordinates)
        for omitted in combinations(range(8), 3)
    )
    require(five_max == 20, "rank-at-most-five parabolics")
    faces = []
    for omitted in combinations(range(8), 2):
        count = sum(all(c[i] == 0 for i in omitted) for c in coordinates)
        if count < 29:
            continue
        normals = [
            r
            for r in roots
            if all(g.dot(r, s) == 0 for i, s in enumerate(g.SIMPLE) if i not in omitted)
        ]
        require((count, len(normals)) in ((30, 2), (36, 3)), "normal root plane")
        if count == 30:
            require(g.dot(*normals) == 0, "D6 orthogonal normals")
        faces.append(
            {
                "omitted": list(omitted),
                "root_lines": count,
                "normal_root_lines": len(normals),
            }
        )
    require([x["root_lines"] for x in faces] == [30, 36], "threshold29 classification")
    return {
        "rank_five_max": five_max,
        "qualifying_faces": faces,
        "perpendicular_live_roots_required": 29,
    }


def projective(x, y):
    require(x != 0 or y != 0, "nonzero projective pair")
    divisor = gcd(x, y)
    pair = (x // divisor, y // divisor)
    return max(pair, tuple(-v for v in pair))


def orthogonal_planes(g, roots, points):
    gram = [[g.dot(a, b) for b in roots] for a in roots]
    live = [roots.index(p) for p in points]
    unions, fibers = Counter(), Counter()
    for a, b in combinations(range(120), 2):
        if gram[a][b]:
            continue
        active = [t for t in live if gram[a][t] or gram[b][t]]
        unions[len(active)] += 1
        if len(active) == 82:
            histogram = Counter(projective(gram[a][t], gram[b][t]) for t in active)
            require(sorted(histogram.values()) == [12, 12, 29, 29], "minimum fibers")
            fibers[tuple(sorted(histogram.values()))] += 1
    require(
        dict(unions) == {82: 448, 84: 2688, 85: 448, 86: 168, 88: 28},
        "live D6 union histogram",
    )
    require(dict(fibers) == {(12, 12, 29, 29): 448}, "minimum plane coverage")
    return {
        "planes": sum(unions.values()),
        "union_histogram": dict(unions),
        "minimum_planes": 448,
        "live_fiber_sizes": [12, 12, 29, 29],
    }


def budget(cut):
    require(type(cut) is int and 0 <= cut <= 112, "common cut bound")
    return {
        "cut": cut,
        "union_upper": cut + 44,
        "E6_required_incidence": 2 * (78 - cut),
        "E6_allowance": 76,
        "D6_required_union": 82 - cut,
        "D6_cover_allowance": 12 + 12 + 18,
    }


def receipt():
    g = geometry()
    roots, points, _, coordinates = g.root_data()
    premises = inherited()
    new, boundary = budget(39), budget(40)
    require(new["E6_required_incidence"] > new["E6_allowance"], "strict E6 gap")
    require(new["D6_required_union"] > new["D6_cover_allowance"], "strict D6 gap")
    require(
        boundary["E6_required_incidence"] == boundary["E6_allowance"],
        "cut40 is only a losing count control",
    )
    require(
        boundary["D6_required_union"] == boundary["D6_cover_allowance"],
        "cut40 supplies no counterexample",
    )
    return json.loads(
        json.dumps(
            {
                "status": "PASS_MIXED_P112_SUPPORT39",
                "endpoint_ranks": [5, 5, 6],
                "intersection_upper_bound": 1,
                "inherited": premises,
                "classification": classify(g, roots, coordinates),
                "D6": orthogonal_planes(g, roots, points),
                "cut39": new,
                "cut40_losing_count_control": boundary,
            }
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = receipt()
    if args.output:
        with args.output.open("x") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        require(
            result == json.loads(read_bytes(PACKAGE / "RESULT.json")), "receipt changed"
        )
    print(result["status"], "D6:43>42 E6:78>76 inherited_capacities no_new_kappa")


if __name__ == "__main__":
    main()
