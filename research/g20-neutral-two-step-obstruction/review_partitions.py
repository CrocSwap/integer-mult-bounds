#!/usr/bin/env python3
"""Independent multiset checker for concave-power dominance certificates."""
import argparse
from collections import Counter
from hashlib import sha256
import gzip
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(delta, certificate):
    require(all(type(r) is int and r > 0 and type(c) is int and c != 0 for r, c in delta), "integer nonzero terms")
    require(len(set(r for r, _ in delta)) == len(delta), "one coefficient per rank")
    positive = Counter({r: c for r, c in delta if c > 0})
    negative = Counter({r: -c for r, c in delta if c < 0})
    covered = Counter()
    used = Counter()
    strict = False
    for target, group in certificate["groups"]:
        require(type(target) is int and target > 0, "positive integer target")
        require(group and all(type(r) is int and r > 0 for r in group), "nonempty positive group")
        require(sum(group) >= target, "sufficient integer rank sum")
        covered[target] += 1
        used.update(group)
        strict |= len(group) > 1 or sum(group) > target
    left = certificate["left"]
    require(all(type(r) is int and r > 0 for r in left), "positive integer leftovers")
    used.update(left)
    strict |= bool(left)
    require(covered == negative, "every negative occurrence covered once")
    require(used == positive, "every positive occurrence used exactly once")
    require(strict == bool(delta), "strictness for every nonzero canonical delta")
    return "positive" if strict else "zero"


def joint_certificate(certificate):
    """Check supplied joint rows and aggregate claims, without rebuilding them."""
    proofs = {}
    for item in certificate["partitions"]:
        key = tuple(map(tuple, item["delta"]))
        require(key not in proofs, "unique global partition")
        check(item["delta"], item["proof"])
        proofs[key] = item["proof"]
    outcomes = []
    global_counts = Counter()
    branch_keys = set()
    for branch in certificate["branches"]:
        first = tuple(branch["first"])
        require(first not in branch_keys, "unique first-word branch")
        branch_keys.add(first)
        shapes, counts = Counter(), Counter()
        for row in branch["outcomes"]:
            require(len(row) == 6, "joint outcome descriptor width")
            require(all(type(value) is int and value >= 0 for value in row[:5]), "integer joint descriptor")
            delta = row[5]
            key = tuple(map(tuple, delta))
            require(key in proofs, "joint shape has a proof")
            verdict = check(delta, proofs[key])
            counts["strict_loss" if verdict == "positive" else "zero"] += 1
            counts["candidates"] += 1
            counts["zero_contact"] += row[4] == 0
            shapes[key] += 1
            outcomes.append({"delta": delta})
        require(dict(counts) == branch["counts"], "exact branch verdict and contact counts")
        declared_shapes = {}
        for delta, count in branch["shapes"]:
            key = tuple(map(tuple, delta))
            require(key not in declared_shapes and type(count) is int and count > 0, "unique counted branch shape")
            declared_shapes[key] = count
        require(declared_shapes == shapes, "exact branch shape multiplicities")
        global_counts.update(counts)
    require(dict(global_counts) == certificate["counts"], "exact aggregate joint counts")
    require(len(branch_keys) == certificate["first_counts"]["zero"], "listed neutral first branch count")
    used = Counter(tuple(map(tuple, row["delta"])) for row in outcomes)
    partitions = [{"delta": delta, "count": count, "partition": proofs[delta]} for delta, count in used.items()]
    return partitions, outcomes, {"branches": len(branch_keys), "all_global_proofs_checked": len(proofs),
                                 "proofs_unused_by_joint_rows": len(proofs.keys() - used.keys())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partitions", type=Path)
    parser.add_argument("--outcomes", type=Path)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    joint = None
    if args.certificate:
        require(not args.partitions and not args.outcomes, "one certificate input mode")
        raw = args.certificate.read_bytes()
        if args.certificate.suffix == ".gz":
            raw = gzip.decompress(raw)
        certificate = json.loads(raw)
        if "partitions" in certificate and "branches" in certificate:
            partitions, outcomes, joint = joint_certificate(certificate)
        else:
            partitions, outcomes = certificate["shapes"], certificate["outcomes"]
        outcomes_raw = raw
    else:
        require(args.partitions is not None and args.outcomes is not None, "paired partition and outcome inputs")
        raw = args.partitions.read_bytes()
        partitions = json.loads(raw)
        outcomes_raw = args.outcomes.read_bytes()
        outcomes = json.loads(outcomes_raw)["outcomes"]
    observed = Counter(tuple(tuple(z) for z in row["delta"]) for row in outcomes)
    listed = {}
    signs = Counter()
    for row in partitions:
        key = tuple(tuple(z) for z in row["delta"])
        require(key not in listed, "unique shape")
        require(type(row["count"]) is int and row["count"] > 0, "positive multiplicity")
        listed[key] = row["count"]
        signs[check(row["delta"], row["partition"])] += row["count"]
    require(listed == observed, "all outcome shapes and exact multiplicities")
    examples = [
        ([(1, 2), (2, -1)], {"groups": [[2, [1, 1]]], "left": []}),
        ([(1, -1), (2, 1)], {"groups": [[1, [2]]], "left": []}),
        ([(1, 1)], {"groups": [], "left": [1]}),
        ([], {"groups": [], "left": []}),
    ]
    require([check(*x) for x in examples] == ["positive", "positive", "positive", "zero"], "strictness cases")
    negative_controls = {
        "double-used positive occurrence": ([(1, 2), (2, -1)], {"groups": [[2, [1, 1]]], "left": [1]}),
        "empty covering group": ([(1, 2), (2, -1)], {"groups": [[2, []]], "left": [1, 1]}),
        "insufficient group rank": ([(1, 1), (2, -1)], {"groups": [[2, [1]]], "left": []}),
        "uncovered negative occurrence": ([(1, 2), (2, -2)], {"groups": [[2, [1, 1]]], "left": []}),
        "omitted positive leftover": ([(1, 1)], {"groups": [], "left": []}),
        "invented positive occurrence": ([(1, -1)], {"groups": [[1, [1]]], "left": []}),
        "bool accepted as integer": ([(1, True)], {"groups": [], "left": [1]}),
    }
    rejected = []
    for name, args in negative_controls.items():
        try:
            check(*args)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("Control unexpectedly accepted: " + name)
    print(json.dumps({
        "schema": "independent-concave-power-partition-review-v1",
        "partitions_sha256": sha256(raw).hexdigest(),
        "outcomes_sha256": sha256(outcomes_raw).hexdigest(),
        "shapes": len(partitions),
        "candidates": len(outcomes),
        "signs": dict(signs),
        "controls": rejected,
        "scope": "exact delta-sign verification; outcome census is not independently re-enumerated",
        "joint": joint,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
