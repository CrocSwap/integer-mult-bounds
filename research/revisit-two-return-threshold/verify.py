#!/usr/bin/env python3
"""Check two new joint-return witnesses without predecessor executables."""

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_NAMES = (
    "README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
    "WITNESSES.json", "verify.py",
)
MAX_BYTES = 262144
WIDTH = 5
LENGTH = 22


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(name):
    path = ROOT / name
    require(path.is_file() and not path.is_symlink(), "regular file required")
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "file exceeds capacity")
    return data


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def check_domain(word):
    require(type(word) is list and len(word) == LENGTH, "word length")
    require(all(type(a) is int and 0 <= a < WIDTH for a in word), "label domain")


def prefix_model(word, initial=0):
    check_domain(word)
    require(type(initial) is int and 0 <= initial < 2**WIDTH, "initial state")
    states = [initial]
    for label in word:
        states.append(states[-1] ^ (1 << label))
    distinct = set(states[:-1])
    even = sum(x.bit_count() % 2 == 0 for x in distinct)
    pairs = [(i, j) for i in range(LENGTH) for j in range(i + 1, LENGTH + 1)
             if states[i] == states[j]]
    return {
        "states": states,
        "restored": states[-1] == initial,
        "distinct_prefixes": len(distinct),
        "revisits": LENGTH - len(distinct),
        "split": sorted([even, len(distinct) - even], reverse=True),
        "returns": sorted({j - i for i, j in pairs}),
        "return_pairs": [list(pair) for pair in pairs],
    }


def interval_model(word, initial=0):
    """Count labels inside each interval; use coordinate tuples for vertices."""
    check_domain(word)
    point = [(initial >> a) & 1 for a in range(WIDTH)]
    points = [tuple(point)]
    for label in word:
        point[label] = 1 - point[label]
        points.append(tuple(point))
    distinct = set(points[:-1])
    even = sum(sum(point) % 2 == 0 for point in distinct)
    pairs = []
    for left in range(LENGTH):
        counts = [0] * WIDTH
        for right in range(left + 1, LENGTH + 1):
            counts[word[right - 1]] += 1
            if all(count % 2 == 0 for count in counts):
                pairs.append([left, right])
    return {
        "states": [sum(bit * 2**a for a, bit in enumerate(point))
                   for point in points],
        "restored": points[-1] == points[0],
        "distinct_prefixes": len(distinct),
        "revisits": LENGTH - len(distinct),
        "split": sorted([even, len(distinct) - even], reverse=True),
        "returns": sorted({right - left for left, right in pairs}),
        "return_pairs": pairs,
    }


def check_witness(row):
    require(type(row) is dict and set(row) == {"split", "word"}, "witness schema")
    split = row["split"]
    require(type(split) is list and len(split) == 2, "split shape")
    require(all(type(x) is int for x in split), "split types")
    first = prefix_model(row["word"])
    require(first == interval_model(row["word"]), "independent models disagree")
    require(first["restored"], "endpoint not restored")
    require(first["split"] == split, "claimed split differs")
    require(first["revisits"] == 2, "revisit threshold not attained")
    require(first["distinct_prefixes"] == 20, "distinct-prefix count")
    require(first["returns"] == [4, 6, 18, 22], "joint return spectrum")
    require(set(row["word"]) == set(range(WIDTH)), "five used labels required")
    require(2 ** (WIDTH - 1) < first["distinct_prefixes"] <= 2**WIDTH,
            "sharp state-capacity inequality")
    return first


def rejected_controls(rows):
    controls = []
    bad = copy.deepcopy(rows[0])
    bad["word"][0] = 2
    controls.append(bad)
    bad = copy.deepcopy(rows[0])
    bad["word"].pop()
    controls.append(bad)
    bad = copy.deepcopy(rows[0])
    bad["word"][0] = True
    controls.append(bad)
    bad = copy.deepcopy(rows[0])
    bad["word"][0] = WIDTH
    controls.append(bad)
    bad = copy.deepcopy(rows[0])
    bad["split"] = [10, 10]
    controls.append(bad)
    bad = copy.deepcopy(rows[0])
    bad["split"] = [True, 9]
    controls.append(bad)
    # Restoration alone does not imply either the revisit or return claim.
    controls.append({"split": [11, 9], "word": [0] * LENGTH})
    for row in controls:
        try:
            check_witness(row)
        except ValueError:
            continue
        raise ValueError("semantic control was accepted")
    return len(controls)


def symmetry_checks(rows):
    transcript = hashlib.sha256()
    count = 0
    for row in rows:
        word = row["word"]
        variants = [[permutation[a] for a in word]
                    for permutation in itertools.permutations(range(WIDTH))]
        variants.append(list(reversed(word)))
        for variant in variants:
            observation = check_witness({"split": row["split"], "word": variant})
            transcript.update((canonical(observation) + "\n").encode())
            count += 1
        for initial in range(2**WIDTH):
            observation = prefix_model(word, initial)
            require(observation == interval_model(word, initial), "translated models")
            require(observation["split"] == row["split"], "translated split")
            require(observation["returns"] == [4, 6, 18, 22], "translated returns")
            transcript.update((canonical(observation) + "\n").encode())
            count += 1
    return {"cases": count, "sha256": transcript.hexdigest()}


def receipt():
    document = json.loads(read_bytes("WITNESSES.json"))
    require(type(document) is dict and set(document) == {"schema", "witnesses"},
            "certificate schema")
    require(document["schema"] == "joint-four-six-returns/v1", "certificate version")
    rows = document["witnesses"]
    require(type(rows) is list and len(rows) == 2, "two witnesses required")
    observations = [check_witness(row) for row in rows]
    require([row["split"] for row in rows] == [[11, 9], [10, 10]], "split coverage")
    return {
        "status": "PASS_JOINT_FOUR_SIX_RETURN_THRESHOLD",
        "claim_type": "finite attainers with a scoped counting argument",
        "width": WIDTH,
        "length": LENGTH,
        "observations": observations,
        "symmetries": symmetry_checks(rows),
        "rejected_controls": rejected_controls(rows),
        "source_sha256": {name: hashlib.sha256(read_bytes(name)).hexdigest()
                          for name in SOURCE_NAMES},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a generated receipt")
    args = parser.parse_args()
    result = receipt()
    if not args.emit:
        expected = json.loads(read_bytes("RESULT.json"))
        require(canonical(result) == canonical(expected), "receipt or source bytes differ")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
