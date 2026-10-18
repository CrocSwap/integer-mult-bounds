"""Conditional P112 mixed566 shortening arithmetic. Nick Petalas, Apache-2.0."""

import hashlib
import json
from itertools import product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCES_HASH = "fa15f5bb7d2cbce142800f0d239a5bca8cab7e85cdd35a5c5f5e99e342c0755b"
PREDECESSORS_HASH = "06f9fdd0efe3d5eb1b0c010ba9199e9253ca0375e62340dc3bb356893e9756f4"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(100_001)
    require(len(data) <= 100_000, "input exceeds bound")
    return data


def read_json(path):
    return json.loads(read_bytes(path))


def canonical(value):
    """JSON equality preserves schema types, including bool versus int."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate(root=ROOT):
    package = root / "research/p112-mixed566-cut32"
    for name, expected in (
        ("SOURCES.json", SOURCES_HASH),
        ("PREDECESSORS.json", PREDECESSORS_HASH),
    ):
        data = read_bytes(package / name)
        require(hashlib.sha256(data).hexdigest() == expected, name + " manifest pin")
    sources = read_json(package / "SOURCES.json")
    prior = read_json(package / "PREDECESSORS.json")
    for manifest in (sources, prior):
        require(
            type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
            "manifest version",
        )
    rows = [r for r in sources["files"] if r["usage"] == "input"] + prior["files"]
    require(len(rows) == 4, "four fixed live inputs")
    for row in rows:
        require(row["usage"] == "input", "live source usage")
        data = read_bytes(root / row["path"])
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob")
    return read_json(package / "vendor/pr3295-RESULT.json")


def check_premise_receipt(prior):
    require(prior["schema"] == "p112-six-piece-concentration/v1", "source schema")
    require(
        prior["planes"]["relevant_live_fibers"]
        == {"82": [12, 12, 29, 29], "84": [11, 11, 31, 31]},
        "live fibers",
    )
    require(
        [a["threshold"] for a in prior["axes"][0]] == [10, 18],
        "inherited concentration thresholds",
    )
    require(
        [a["maximum"] for a in prior["small_fibers"]] == [8, 8],
        "inherited small-fiber capacity",
    )
    require(
        prior["normalization"]["maximum_five_node_lines"] == 20, "parabolic premise"
    )


def certificate(cut=32):
    require(type(cut) is int and cut in (32, 33), "bounded common cut")
    capacities = (12, 20, 20)
    budget = sum(capacities)
    e6_required = 2 * (78 - cut)
    e6_allowed = 22 + 32 + 32
    require(e6_required > e6_allowed, "E6 incidence gap")
    rows = []
    for union, axis_size in ((82, 29), (84, 31)):
        retained = union - cut
        deficit = budget - retained
        singletons = [c - deficit for c in capacities]
        require(
            all(j >= t for j, t in zip(singletons, (10, 18, 18), strict=True)),
            "axis concentration not forced",
        )
        bounds = []
        for assignment in product((0, 1), repeat=3):
            loads = [
                sum(
                    c
                    for c, side in zip(capacities, assignment, strict=True)
                    if side == axis
                )
                for axis in (0, 1)
            ]
            bounds.append(sum(min(axis_size, load) for load in loads))
        maximum = max(bounds)
        require(maximum < retained, "D6 two-axis covering gap")
        rows.append(
            {
                "union": union,
                "retained_at_least": retained,
                "deficit_at_most": deficit,
                "singleton_lower": singletons,
                "axis_size": axis_size,
                "all_assignment_bounds": bounds,
                "coverage_at_most": maximum,
                "gap": retained - maximum,
            }
        )
    return {
        "schema_version": 1,
        "status": "PASS_P112_MIXED566_CUT32_CONDITIONAL",
        "cut": cut,
        "binary_rank_bounds": [5, 6, 6],
        "support_budget": budget,
        "intersection_dimension_at_most": 1,
        "E6": {"required_incidence": e6_required, "allowed_incidence": e6_allowed},
        "D6": rows,
        "inherited_concentration_replayed": False,
        "sharpness_claimed": False,
        "new_caller_claimed": False,
    }


def main():
    check_premise_receipt(authenticate())
    result = certificate()
    require(
        canonical(result) == canonical(read_json(PACKAGE / "RESULT.json")),
        "computed result differs from receipt",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
