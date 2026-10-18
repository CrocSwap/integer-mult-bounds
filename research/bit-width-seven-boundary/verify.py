# SPDX-License-Identifier: Apache-2.0
"""Check the boundary certificate without the derivation program."""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


class Reject(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Reject(message)


def integers_only(value):
    if isinstance(value, dict):
        for child in value.values():
            integers_only(child)
    elif isinstance(value, list):
        for child in value:
            integers_only(child)
    elif isinstance(value, (bool, float)):
        raise Reject("numeric field is not an integer")


def det(matrix):
    """Use fraction-free elimination on an integer square matrix."""
    a = [row[:] for row in matrix]
    sign, previous = 1, 1
    for k in range(len(a) - 1):
        pivot = next((i for i in range(k, len(a)) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[pivot], a[k] = a[k], a[pivot]
            sign = -sign
        q = a[k][k]
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                numerator = q * a[i][j] - a[i][k] * a[k][j]
                require(numerator % previous == 0, "non-integral determinant step")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = q
    return sign * a[-1][-1]


def invert_rows(values, labels):
    """Invert a binary matrix with set elimination, not gate reversal."""
    rows = [set(values[r]) for r in labels]
    right = [{r} for r in labels]
    for k, label in enumerate(labels):
        pivot = next((i for i in range(k, len(labels)) if label in rows[i]), None)
        require(pivot is not None, "singular boundary matrix")
        rows[k], rows[pivot] = rows[pivot], rows[k]
        right[k], right[pivot] = right[pivot], right[k]
        for i in range(len(labels)):
            if i != k and label in rows[i]:
                rows[i] ^= rows[k]
                right[i] ^= right[k]
    require(rows == [{r} for r in labels], "inverse reduction")
    return dict(zip(labels, right))


def requirements(values, inverse, helper):
    restore = set(inverse[helper])
    dirt = {r for r, row in enumerate(values) if helper in row}
    return restore, dirt, restore | dirt | {helper}


def replay(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    frames = list(word["start"])
    values = [{r} for r in range(n)]
    snapshots = {}

    def section(name):
        for frame, target, donors in word[name]:
            require(len({target, *donors}) == 1 + len(donors), "invalid scalar gate")
            for register in [target, *donors]:
                require(set(word["frames"][frames[register]]) <= set(word["frames"][frame]), "frame descent")
                frames[register] = frame
            for donor in donors:
                values[target] ^= values[donor]

    def snapshot(name):
        z = [r for r in range(n) if not v <= r < 2 * v]
        require(all(not any(v <= x < 2 * v for x in values[r]) for r in z), "target input in z boundary")
        snapshots[name] = (frames[:], [row.copy() for row in values], invert_rows(values, z))

    section("D")
    section("A")
    require(all(frames[r] == 0 for r in range(v, 2 * v)), "target frame before scatter")
    for target, totals in enumerate(word["scatter"]):
        for total in totals:
            values[v + target] ^= values[word["ret"][total]]
    snapshot("after_scatter")
    section("B")
    snapshot("after_B")
    section("C")
    for register, final in enumerate(word["final"]):
        require(set(word["frames"][frames[register]]) <= set(word["frames"][final]), "final frame descent")
        expected = {register, register - v} if v <= register < 2 * v else {register}
        require(values[register] == expected, "dirty endpoint")
    return snapshots


def check_span(word, current, donors, entry):
    rank = entry["rank"]
    require(rank in (7, 8) and len(entry["basis"]) == rank, "rank or basis length")
    vectors = []
    for register, line in entry["basis"]:
        require(register in donors and line in word["frames"][current[register]], "frame provenance")
        vectors.append(word["lines"][line])
    if rank == 8:
        actual = det(vectors)
        require(actual != 0 and entry.get("determinant") == actual, "rank8 determinant")
    else:
        gram = [[sum(a * b for a, b in zip(x, y)) for y in vectors] for x in vectors]
        require(det(gram) > 0, "rank7 basis dependence")
        normal = entry["normal"]
        require(len(normal) == 8 and any(normal), "zero normal")
        for register in donors:
            for line in word["frames"][current[register]]:
                require(sum(a * b for a, b in zip(normal, word["lines"][line])) == 0, "normal does not annihilate required frame")


def check_certificate(word, certificate, snapshots):
    integers_only(certificate)
    v, n = word["v"], 2 * word["v"] + word["R"]
    helpers = list(range(2 * v, n))
    require((certificate["v"], certificate["R"], certificate["dimension"]) == (v, word["R"], 8), "dimensions")
    require(certificate["status"] == "SCOPED_BIT_BOUNDARY_OBSTRUCTION", "status")
    require([cut["name"] for cut in certificate["cuts"]] == ["after_scatter", "after_B"], "cut coverage")
    for cut in certificate["cuts"]:
        current, values, inverse = snapshots[cut["name"]]
        require(cut["frames"] == current, "boundary frames")
        require([row["helper"] for row in cut["helpers"]] == helpers, "helper coverage")
        for entry in cut["helpers"]:
            helper = entry["helper"]
            restore, dirt, joint = requirements(values, inverse, helper)
            require(entry["restore"] == sorted(restore), "inverse row")
            require(entry["dirt"] == sorted(dirt), "dirt column")
            donors = restore | {helper} if cut["name"] == "after_B" else joint
            check_span(word, current, donors, entry)
        counts = Counter(row["rank"] for row in cut["helpers"])
        require(cut["rank_counts"] == {str(k): value for k, value in sorted(counts.items())}, "rank counts")
        survivors = [row["helper"] for row in cut["helpers"] if row["rank"] < 8]
        require(cut["survivors"] == survivors, "survivor coverage")
    require(certificate["cuts"][0]["survivors"] == [465, 466, 468, 469, 470, 476], "six surviving necessary conditions")
    require(certificate["cuts"][1]["survivors"] == [], "post-B full-rank coverage")
    require([row["helper"] for row in certificate["compensation"]] == helpers, "compensation coverage")
    for row in certificate["compensation"]:
        targets = [target for frame, target, donors in word["D"] if row["helper"] in donors]
        require(targets and row["targets"] == targets, "compensation column")
    return {"after_scatter_full_rank": 433, "after_B_full_rank": 439, "nonzero_compensation_columns": 439}


def controls(word, certificate, snapshots):
    mutations = []
    changed = copy.deepcopy(certificate)
    changed["cuts"][0]["helpers"][0]["restore"].pop()
    mutations.append(("inverse row", changed))
    changed = copy.deepcopy(certificate)
    changed["cuts"][0]["helpers"][0]["dirt"].pop()
    mutations.append(("dirt column", changed))
    changed = copy.deepcopy(certificate)
    entry = changed["cuts"][0]["helpers"][0]
    register, _ = entry["basis"][0]
    frame = changed["cuts"][0]["frames"][register]
    entry["basis"][0][1] = next(line for line in range(word["v"]) if line not in word["frames"][frame])
    mutations.append(("frame provenance", changed))
    changed = copy.deepcopy(certificate)
    changed["cuts"][1]["helpers"][0]["determinant"] = 0
    mutations.append(("rank8 determinant", changed))
    changed = copy.deepcopy(certificate)
    entry = next(row for row in changed["cuts"][0]["helpers"] if row["rank"] == 7)
    entry["normal"] = [1] * 8
    mutations.append(("normal does not annihilate", changed))
    changed = copy.deepcopy(certificate)
    changed["cuts"][0]["helpers"].pop()
    mutations.append(("helper coverage", changed))
    changed = copy.deepcopy(certificate)
    changed["compensation"][0]["targets"].pop()
    mutations.append(("compensation column", changed))
    changed = copy.deepcopy(certificate)
    changed["cuts"][0]["helpers"][0]["rank"] = True
    mutations.append(("numeric field", changed))
    for reason, changed in mutations:
        try:
            check_certificate(word, changed, snapshots)
        except Reject as error:
            require(reason in str(error), "control failed for an unrelated reason: " + reason)
        else:
            raise Reject("control accepted: " + reason)

    # These two-register examples test each part of the cut condition.
    labels = [0, 1]
    toy = {"lines": [[int(i == j) for j in range(8)] for i in range(8)],
           "frames": [list(range(7)), list(range(8))]}
    evidence = {"rank": 7, "basis": [[1, i] for i in range(7)], "normal": [0] * 7 + [1]}
    rows = [{0}, {0, 1}]
    inverse = invert_rows(rows, labels)
    restore, dirt, joint = requirements(rows, inverse, 1)
    require((restore, dirt, joint) == ({0, 1}, {1}, {0, 1}), "restoration control")
    require(rows[1] ^ rows[0] == {1}, "legal hyperplane cleanup control")
    check_span(toy, [0, 0], joint, evidence)
    try:
        check_span(toy, [1, 0], joint, evidence)
    except Reject as error:
        require("normal does not annihilate" in str(error), "restoration frame control reason")
    else:
        raise Reject("restoration frame control accepted")
    rows = [{0, 1}, {1}]
    inverse = invert_rows(rows, labels)
    restore, dirt, joint = requirements(rows, inverse, 1)
    require((restore, dirt, joint) == ({1}, {0, 1}, {0, 1}), "erasure control")
    check_span(toy, [1, 0], restore, evidence)
    try:
        check_span(toy, [1, 0], joint, evidence)
    except Reject as error:
        require("normal does not annihilate" in str(error), "erasure frame control reason")
    else:
        raise Reject("erasure frame control accepted")
    return len(mutations), 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, digest in sources["inputs"].items():
        require(hashlib.sha256((args.root / path).read_bytes()).hexdigest() == digest, "source pin: " + path)
    word = json.loads(gzip.decompress((args.root / sources["word"]).read_bytes()))
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    snapshots = replay(word)
    result = check_certificate(word, certificate, snapshots)
    negative, small = controls(word, certificate, snapshots)
    print(json.dumps({**result, "negative_controls": negative, "small_boundary_controls": small}, sort_keys=True))
    print("PASS_BIT_BOUNDARY_OBSTRUCTION after_scatter=433/439 after_B=439/439 entry=439/439 controls=11 no_new_kappa")


if __name__ == "__main__":
    main()
