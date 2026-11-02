#!/usr/bin/env python3
"""Check finite upper certificates, without running a tree optimizer."""

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SIZES = tuple(range(2, 18))
HISTOGRAM = {2: 9, 3: 1, 4: 4, 7: 1, 8: 1}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    require(path.stat().st_size <= 65536, "JSON exceeds 64 KiB")
    return json.loads(path.read_text(encoding="utf-8"))


def authenticate_sources():
    manifest = load_json(PACKAGE / "SOURCES.json")
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    expected = {
        "research/balanced-query-tree/PROOF.md",
        "research/balanced-query-tree/README.md",
    }
    require(len(rows) == 2 and {row["path"] for row in rows} == expected, "source inventory")
    for row in rows:
        payload = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == row["sha256"], "source SHA256")
        header = f"blob {len(payload)}\0".encode()
        require(hashlib.sha1(header + payload).hexdigest() == row["git_blob"], "source blob")
    return {row["path"]: row["sha256"] for row in rows}


def check_certificate(certificate, histogram):
    require(set(certificate) == {"schema", "leaves", "roots", "hinges"}, "certificate fields")
    require(certificate["schema"] == "query-tree-hinge-upper/1", "schema")
    require(type(certificate["leaves"]) is int and certificate["leaves"] == 19, "leaves")
    require(type(certificate["roots"]) is int and certificate["roots"] == 3, "roots")
    require(all(type(n) is int and n in SIZES for n in histogram), "node sizes")
    require(all(type(c) is int and 0 < c <= 16 for c in histogram.values()), "multiplicities")
    require(sum(histogram.values()) == 16, "sixteen binary nodes")
    rows = certificate["hinges"]
    require(isinstance(rows, list) and len(rows) == 15, "hinge inventory")
    split_checks = root_checks = 0
    scores = []
    for threshold, row in zip(range(3, 18), rows, strict=True):
        require(set(row) == {"threshold", "upper"}, "hinge fields")
        require(type(row["threshold"]) is int and row["threshold"] == threshold, "threshold")
        upper = row["upper"]
        require(isinstance(upper, list) and len(upper) == 17, "upper dimensions")
        require(all(type(v) is int and 0 <= v <= 256 for v in upper), "upper range")
        require(upper[0] == 0, "leaf has no reward")
        for size in SIZES:
            toll = max(threshold - size, 0)
            for left in range(1, size):
                bound = toll + upper[left - 1] + upper[size - left - 1]
                require(upper[size - 1] >= bound, "binary split upper bound")
                split_checks += 1
        score = sum(count * max(threshold - size, 0) for size, count in histogram.items())
        for first in range(1, 18):
            for second in range(1, 19 - first):
                third = 19 - first - second
                bound = upper[first - 1] + upper[second - 1] + upper[third - 1]
                require(bound <= score, "root upper bound exceeds attaining histogram")
                root_checks += 1
        scores.append(score)
    return scores, split_checks, root_checks


def construct_attainer():
    # Reconstruct the named forest independently from the stored histogram.
    nodes = [(1, 1), (1, 2), (2, 2), (3, 4), (4, 4)]
    trees = {1: ()}
    for left, right in nodes:
        trees[left + right] = (trees[left], trees[right])
    pending = [trees[4], trees[7], trees[8]]
    histogram = {}
    leaves = []
    # A forest with 19 leaves has 16 internal nodes and 35 nodes in total.
    for _ in range(35):
        require(bool(pending), "attainer traversal ended early")
        tree = pending.pop()
        if not tree:
            leaves.append(1)
        else:
            frontier = [tree]
            size = 0
            for _ in range(15):
                if not frontier:
                    break
                item = frontier.pop()
                if item:
                    frontier.extend(item)
                else:
                    size += 1
            require(not frontier, "subtree traversal bound")
            histogram[size] = histogram.get(size, 0) + 1
            pending.extend(tree)
    require(not pending and len(leaves) == 19, "attainer leaf count")
    require(histogram == HISTOGRAM, "attainer histogram")
    return histogram


def check_hinge_decomposition():
    # Exact rational checks of the basis identity in the written proof.
    fixtures = [tuple(Fraction(1, n**power) for n in SIZES) for power in (1, 2, 3)]
    fixtures += [tuple(Fraction(max(k - n, 0)) for n in SIZES) for k in range(3, 18)]
    fixtures += [tuple(Fraction(7) for _ in SIZES), tuple(Fraction(31 - n) for n in SIZES)]
    for values in fixtures:
        slope = values[-2] - values[-1]
        second = {k: values[k - 3] - 2 * values[k - 2] + values[k - 1] for k in range(3, 17)}
        require(slope >= 0 and all(v >= 0 for v in second.values()), "convex fixture")
        for n, value in zip(SIZES, values, strict=True):
            reconstructed = values[-1] + slope * (17 - n)
            reconstructed += sum(delta * max(k - n, 0) for k, delta in second.items())
            require(reconstructed == value, "hinge decomposition")
    return len(fixtures) * len(SIZES)


def rejection_controls(certificate, histogram):
    controls = []
    bad = copy.deepcopy(certificate)
    bad["hinges"][0]["upper"][1] -= 1
    controls.append((bad, histogram))
    bad = copy.deepcopy(certificate)
    bad["hinges"][-1]["upper"][7] += 1
    controls.append((bad, histogram))
    bad = copy.deepcopy(certificate)
    bad["hinges"].pop()
    controls.append((bad, histogram))
    bad = copy.deepcopy(certificate)
    bad["hinges"][0]["upper"][0] = False
    controls.append((bad, histogram))
    bad = copy.deepcopy(certificate)
    bad["leaves"] = 18
    controls.append((bad, histogram))
    wrong_histogram = dict(histogram)
    wrong_histogram[2] -= 1
    wrong_histogram[3] += 1
    controls.append((certificate, wrong_histogram))
    for candidate, counts in controls:
        try:
            check_certificate(candidate, counts)
        except ValueError:
            continue
        raise ValueError("semantic control accepted")
    return len(controls)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    sources = authenticate_sources()
    certificate = load_json(PACKAGE / "CERTIFICATE.json")
    histogram = construct_attainer()
    scores, splits, roots = check_certificate(certificate, histogram)
    receipt = {
        "marker": "PASS_QUERY_TREE_TOPOLOGY_OPTIMUM",
        "claim_type": "scoped proof with finite integer certificate",
        "hinge_scores": scores,
        "split_inequalities": splits,
        "root_inequalities": roots,
        "basis_identity_checks": check_hinge_decomposition(),
        "rejection_controls": rejection_controls(certificate, histogram),
        "source_sha256": sources,
        "package_sha256": {
            name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
            for name in ("CERTIFICATE.json", "verify.py", "generate.py", "README.md", "SOURCES.json")
        },
    }
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        with args.receipt.open("x", encoding="utf-8") as stream:
            written = stream.write(payload)
            require(written == len(payload), "short receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
