#!/usr/bin/env python3
"""Replay the complete domain repair. ywz65/Codex; Apache-2.0."""
import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
from itertools import combinations
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pairs(rows):
    result = {}
    for key, value in rows:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def prefix_masks(edges):
    result = [0]
    for edge in edges:
        result.append(result[-1] ^ edge)
    return result


def differences(vertices):
    return {a ^ b for a in vertices for b in vertices} - {0}


def admissible(word):
    require(len(word) == 13 and all(type(x) is int and 0 <= x < 6 for x in word), "word alphabet/length")
    counts = [word.count(j) for j in range(6)]
    require(all(counts) and sum(c % 2 for c in counts) == 3, "complete parity domain")
    return counts


def build_result():
    manifest = read_json(PACKAGE / "SOURCES.json")
    for row in manifest["files"] + manifest["vendored_files"]:
        if row["usage"] == "input":
            require(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source hash: " + row["path"])
    census = load_module("complete_trio_census", PACKAGE / "census.py")
    old = load_module("old_trio_census", PACKAGE / "vendor/pr2134/search.py")
    prior = read_json(PACKAGE / "vendor/pr2134/CERTIFICATE.json")
    # A separate total-profile subtraction derivation of the full singleton set.
    derived = set()
    for total in ((2, 2, 2, 2, 4, 4), (2, 2, 2, 2, 2, 6)):
        for trio in combinations(range(6), 3):
            derived.add(tuple(sorted(c - (j in trio) for j, c in enumerate(total))))
    require(derived == set(census.profiles()) and len(derived) == 5, "complete profile derivations")
    for delta in range(64):
        for state in range(64):
            require(census.translate(1 << state, delta) == 1 << (state ^ delta), "XOR bit translation")
    rows = census.enumerate_profiles()
    histogram = Counter()
    old_histogram = Counter()
    for row in rows:
        histogram.update({int(k): v for k, v in row["histogram"].items()})
        if tuple(row["counts"]) in old.PROFILES:
            old_histogram.update(row["histogram"])
    require(dict(old_histogram) == prior["enumeration"]["histogram_nonzero_pair_masks"], "entire old-subdomain histogram")
    require(sum(histogram.values()) == 5675670 and max(histogram) == 61 and histogram[61] == 88,
            "complete census result")
    require(sum(old_histogram.values()) == 2342340, "retained subdomain count")

    controls = []
    def rejects(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("control did not reject: " + name)

    omitted = [0, 1, 2, 3, 3, 4, 4] + [5]*6
    require(admissible(omitted) == [1, 1, 1, 2, 2, 6], "review counterexample")
    rejects("old actual predicate rejects legal omitted profile", lambda: old.analyze_word(omitted))
    rejects("one odd count cannot close with a distinct-label TRIO",
            lambda: admissible([0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5]))
    rejects("missing source", lambda: admissible([0]*13))
    rejects("out-of-alphabet source", lambda: admissible([0]*12+[6]))

    witness = prior["maximum_witness"]
    word = witness["singleton_word"]
    counts = admissible(word)
    trio = sum((c % 2) << j for j, c in enumerate(counts))
    edges = [1 << label for label in word] + [trio]
    vertices = prefix_masks(edges)
    require(vertices[-1] == 0 and trio.bit_count() == 3, "restored closing TRIO")
    cover = differences(vertices)
    require(len(cover) == 61 and sorted(set(range(1, 64))-cover) == [11, 40], "retained maximizing witness")
    for cut in range(14):
        rotated = prefix_masks(edges[cut:] + edges[:cut])
        require(set(rotated) == {v ^ vertices[cut] for v in vertices}, "cyclic vertex translation")
        require(differences(rotated) == cover, "all TRIO placements")
    changed = None
    for i in range(12):
        swapped = edges[:]
        swapped[i], swapped[i+1] = swapped[i+1], swapped[i]
        if differences(prefix_masks(swapped)) != cover:
            changed = i
            break
    require(changed is not None, "arbitrary commutation must not stand in for rotation")
    for target in (11, 40):
        indices = witness["four_readout_indices_for_missing_masks"][str(target)]
        require(len(indices) == 4 and len(set(indices)) == 4, "four distinct readouts")
        mask = 0
        for i in indices:
            mask ^= vertices[i]
        require(mask == target, "four-readout repair")
    baseline = prior["positive_control"]["incumbent_singleton_word"]
    require(len(baseline) == 16 and len(differences(prefix_masks([1 << x for x in baseline]))) == 63,
            "incumbent full-cover positive control")
    return {"schema_version": 1, "status": "PASS_COMPLETE_SIX_TRIO_PROFILES",
            "profiles": rows, "eligible": sum(histogram.values()), "maximum": 61, "at_maximum": 88,
            "old_eligible": sum(old_histogram.values()), "added_eligible": 3333330,
            "omitted_example": omitted, "maximum_witness": witness,
            "rotation_checks": 14, "xor_translation_basis_checks": 4096,
            "noninvariant_adjacent_swap": changed, "rejected_controls": controls,
            "minimum_output_readouts": 130, "completed_unit_calls": 144, "incumbent_unit_calls": 142,
            "scope": "complete one-TRIO domain repair; no new supplier or kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = build_result()
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(same(result, read_json(PACKAGE / "RESULT.json")), "complete typed receipt mismatch")
    print(result["status"] + " eligible=5675670 max=61 at_max=88 calls=144")


if __name__ == "__main__":
    main()
