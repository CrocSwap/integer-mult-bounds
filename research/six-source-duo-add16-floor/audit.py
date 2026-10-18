#!/usr/bin/env python3
"""Audit the full-cover table and every orbit's unpruned hidden-prefix choices.

This portable check does not establish table completeness by itself. verify.py
rebuilds the table with two independent complete C++ enumerations.
Tairitsu-Aya, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
import struct

HERE = Path(__file__).resolve().parent
COVERS_SHA256 = "251100fa9f200ddb24cefac8a6b8255cfa43d1f3bd7e4bc3f45120d4f3aa7262"
INCUMBENT = [2, 16, 8, 16, 1, 4, 48, 4, 3, 4, 32, 8, 4, 16]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalize(word):
    names = {}
    return tuple(names.setdefault(x, len(names)) for x in word)


def orbit(word):
    result = set()
    for row in (word, word[::-1]):
        for shift in range(16):
            result.add(normalize(row[shift:] + row[:shift]))
    return result


def prefixes(word):
    out = [0]
    for label in word:
        out.append(out[-1] ^ (1 << label))
    require(out[-1] == 0, "restored singleton expansion")
    return out[:-1]


def differences(points):
    return {a ^ b for a in points for b in points}


def word_stats(steps, n=6):
    require(all(type(s) is int and 0 < s < (1 << n) and s.bit_count() in (1, 2)
                for s in steps), "singleton/DUO alphabet")
    points = [0]
    for step in steps:
        points.append(points[-1] ^ step)
    require(points[-1] == 0, "connector restoration")
    points.pop()
    return {"calls": len(steps), "adds": sum(s.bit_count() for s in steps),
            "prefixes": points, "coverage": len(differences(points)),
            "missing_masks": sorted(set(range(1 << n)) - differences(points))}


def compress(word, hidden):
    points = prefixes(word)
    kept = [i for i in range(16) if i not in hidden]
    steps = [points[a] ^ points[b] for a, b in zip(kept, kept[1:] + kept[:1])]
    stats = word_stats(steps)
    require(stats["calls"] == 13 and stats["adds"] == 16, "charged thirteen-call word")
    return {"unit_labels": list(word), "hidden_prefixes": list(hidden),
            "steps": steps, **stats}


def invertible_rows(size, rng):
    rows = [1 << i for i in range(size)]
    if size > 1:
        for _ in range(12):
            a, b = rng.sample(range(size), 2)
            rows[a] ^= rows[b]
    return rows


def apply_rows(matrix, values):
    out = []
    for mask in matrix:
        value = 0
        for column, entry in enumerate(values):
            if mask & (1 << column):
                value ^= entry
        out.append(value)
    return out


def matrix_product(left, right):
    # Deliberately use literal scalar entries for the expected block matrix.
    size = len(left)
    return [sum((sum(((left[i] >> k) & 1) * ((right[k] >> j) & 1)
                     for k in range(size)) % 2) << j for j in range(size))
            for i in range(size)]


def full_column_replay(size, mutation=None):
    """All 70*size arbitrary input columns, with noncommuting dense F2 maps."""
    rng = random.Random(20261014 + size)
    sources = [[1 << (j * size + c) for c in range(size)] for j in range(6)]
    initial_targets = [[1 << ((6 + j) * size + c) for c in range(size)] for j in range(63)]
    initial_connector = [1 << (69 * size + c) for c in range(size)]
    targets = [list(row) for row in initial_targets]
    connector = list(initial_connector)
    bs = [invertible_rows(size, rng) for _ in range(6)]
    aa = [invertible_rows(size, rng) for _ in range(63)]
    if size > 1:
        bs[0] = [1 << i for i in range(size)]
        bs[0][0] ^= 2
        aa[0] = [1 << i for i in range(size)]
        aa[0][0], aa[0][1] = aa[0][1], aa[0][0]
        require(matrix_product(aa[0], bs[0]) != matrix_product(bs[0], aa[0]),
                "noncommuting positive-control maps")
    points = word_stats(INCUMBENT)["prefixes"]
    reads = defaultdict(list)
    for mask in range(1, 64):
        first, second = next((i, j) for i, j in combinations(range(14), 2)
                             if points[i] ^ points[j] == mask)
        reads[first].append(mask)
        reads[second].append(mask)
    if mutation == "drop_readout":
        first = min(t for t in reads if 1 in reads[t])
        reads[first].remove(1)
    elif mutation == "move_readout":
        first, second = sorted(t for t in reads if 1 in reads[t])
        reads[second].remove(1)
        reads[first].append(1)
    steps = list(INCUMBENT)
    if mutation == "shrink_duo":
        first = next(i for i, step in enumerate(steps) if step.bit_count() == 2)
        steps[first] &= steps[first] - 1
    for boundary, step in enumerate(steps):
        for mask in reads[boundary]:
            delta = apply_rows(aa[mask - 1], connector)
            targets[mask - 1] = [x ^ y for x, y in zip(targets[mask - 1], delta)]
        if mutation == "drop_source" and boundary == 13:
            continue
        # A DUO exposes only its outer boundaries; there are no reads here.
        for j in range(6):
            if step & (1 << j):
                delta = apply_rows(bs[j], sources[j])
                connector = [x ^ y for x, y in zip(connector, delta)]
    expected = [list(row) for row in initial_targets]
    for mask in range(1, 64):
        for j in range(6):
            if not mask & (1 << j):
                continue
            product = matrix_product(aa[mask - 1], bs[j])
            for row in range(size):
                for column in range(size):
                    if product[row] & (1 << column):
                        expected[mask - 1][row] ^= 1 << (j * size + column)
    return connector == initial_connector and targets == expected


def compute(data):
    require(hashlib.sha256(data).hexdigest() == COVERS_SHA256, "full-cover table SHA256")
    require(len(data) == 7480 * 8, "7480 full-cover records")
    codes = [v for (v,) in struct.iter_unpack("<Q", data)]
    require(codes == sorted(set(codes)), "unique sorted full-cover table")
    words = {tuple((code >> (3 * i)) & 7 for i in range(16)) for code in codes}
    groups = defaultdict(set)
    profile_histogram = Counter()
    for word in words:
        require(normalize(word) == word and max(word) == 5, "canonical six-source word")
        profile = tuple(sorted(Counter(word).values()))
        require(profile in ((2, 2, 2, 2, 2, 6), (2, 2, 2, 2, 4, 4)), "even multiplicity profile")
        profile_histogram[",".join(map(str, profile))] += 1
        require(differences(prefixes(word)) == set(range(64)), "actual full-cover word")
        family = orbit(word)
        require(family <= words, "full-cover table closed under normalized dihedral action")
        groups[min(family)].add(word)
    for representative, family in groups.items():
        require(family == orbit(representative), "complete disjoint orbit partition")
    patterns = [p for p in combinations(range(16), 3)
                if all((a - b) % 16 not in (1, 15) for a, b in combinations(p, 2))]
    require(len(patterns) == 352, "all cyclic three-edge matching patterns")
    histogram = Counter()
    best = None
    for word in sorted(groups):
        points = prefixes(word)
        for hidden in patterns:
            if any(word[(v - 1) % 16] == word[v] for v in hidden):
                continue
            retained = [points[i] for i in range(16) if i not in hidden]
            size = len(differences(retained))
            histogram[size] += 1
            require(size < 64, "unexpected thirteen-call full cover")
            if best is None or size > best["coverage"]:
                best = compress(word, hidden)
    require(best["coverage"] == 63, "sharp retained-coverage maximum")
    repair = 0
    for index in (0, 1, 2, 6):
        repair ^= best["prefixes"][index]
    require(best["missing_masks"] == [12] and repair == 12,
            "four-readout repair of the sharp near miss")
    incumbent = word_stats(INCUMBENT)
    require((incumbent["calls"], incumbent["adds"], incumbent["coverage"]) == (14, 16, 64),
            "PR2128 incumbent positive control")
    require(len(differences(prefixes(tuple(best["unit_labels"])))) == 64,
            "exposing forbidden internal prefixes invalidates the exclusion")
    for size in (1, 2, 3):
        require(full_column_replay(size), "complete dirty-input positive replay")
    mutations = ["drop_readout", "move_readout", "shrink_duo", "drop_source"]
    for mutation in mutations:
        require(not full_column_replay(2, mutation), "behavioral mutation not detected: " + mutation)
    return {
        "full_unit_words": len(words), "full_unit_codes_sha256": COVERS_SHA256,
        "full_cover_multiplicity_profiles": dict(sorted(profile_histogram.items())),
        "unit_orbits": len(groups),
        "orbit_size_histogram": {str(k): v for k, v in sorted(Counter(map(len, groups.values())).items())},
        "cyclic_deletion_patterns": len(patterns),
        "tested_orbit_deletions": sum(histogram.values()),
        "retained_coverage_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "max_coverage": best["coverage"], "max_witness": best,
        "incumbent_steps": INCUMBENT, "incumbent": incumbent,
        "positive_full_column_dimensions": [1, 2, 3],
        "positive_full_input_columns": [70, 140, 210],
        "behavioral_mutations_rejected": mutations,
        "batch_at_minimum_add_budget": {"root_queries": 140, "adds": 142,
                                         "source_calls": 14, "source_adds": 16, "readouts": 126},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write audit receipt exclusively instead of comparing RESULT")
    args = parser.parse_args()
    result = compute((HERE / "FULL-COVERS.bin").read_bytes())
    if args.out:
        with args.out.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(result == expected["audit"], "exact portable audit receipt")
    print("PASS_DUO_ADD16_TABLE_AUDIT: 7480 covers, 251 orbits, 86900 deletions, maximum 63/64")
    print("Table completeness is separately established by verify.py's two complete native censuses.")


if __name__ == "__main__":
    main()
