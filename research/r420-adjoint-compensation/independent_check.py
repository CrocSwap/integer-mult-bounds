#!/usr/bin/env python3
"""Independent support-set and Boolean checks for the ten dirty probes.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORD = HERE.parent / "e8-bit-r420/data/bitE8mut-r420.json.gz"
SOURCE_SHA256 = "9721a3819efd68307f66f00d84a952eb28eb7c3ad2ce79653ce295c98a764784"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def gates(word, section):
    if section == "scatter":
        return [(0, 120 + t, [word["ret"][i] for i in row])
                for t, row in enumerate(word["scatter"])]
    return word[section]


def raw_supports(word):
    values = [{i} for i in range(660)]
    for section in ("A", "scatter", "B"):
        for _, destination, sources in gates(word, section):
            require(destination not in sources, "self-reading gate outside scope")
            delta = set()
            for source in sources:
                delta.symmetric_difference_update(values[source])
            values[destination].symmetric_difference_update(delta)
    return values[120:240]


def execute_boolean(word, dirt):
    values = [False] * 240 + [j in dirt for j in range(420)]
    for section in ("D", "A", "scatter", "B", "C"):
        for _, destination, sources in gates(word, section):
            delta = False
            for source in sources:
                delta ^= values[source]
            values[destination] ^= delta
    return values


def decode_hex(value):
    bits = format(int(value, 16), "b")
    require(len(bits) <= 420, "probe exceeds helper width")
    return {i for i, bit in enumerate(reversed(bits)) if bit == "1"}


def validate_labels(labels):
    require(len(labels) == 420 and all(0 < x < 1024 for x in labels), "zero or invalid column")
    pool = set(labels)
    require(len(pool) == len(labels), "duplicate columns conceal a pair")
    for i, first in enumerate(labels):
        for second in labels[i + 1:]:
            require(first ^ second not in pool, "three columns sum to zero")


def main():
    compressed = WORD.read_bytes()
    require(hashlib.sha256(compressed).hexdigest() == SOURCE_SHA256, "source pin mismatch")
    word = json.loads(gzip.decompress(compressed))
    require((word["v"], word["R"]) == (120, 420), "unexpected dimensions")
    raw = raw_supports(word)
    compensation = [set() for _ in range(120)]
    for frame, destination, sources in word["D"]:
        require(frame == 0 and 120 <= destination < 240 and
                all(240 <= source < 660 for source in sources), "invalid D interface")
        for source in sources:
            compensation[destination - 120].symmetric_difference_update({source})
    require(raw == [{t, 120 + t} | compensation[t] for t in range(120)], "baseline K=D fails")

    certificate = json.loads((HERE / "EXPECTED.json").read_text())
    probes = [decode_hex(row) for row in certificate["suite"]["pattern_hex"]]
    require(len(probes) == 10, "expected ten probes")
    labels = [sum(2 ** k for k, probe in enumerate(probes) if j in probe) for j in range(420)]
    require(labels == [1 + 2 * j for j in range(420)], "probe columns differ from construction")
    validate_labels(labels)
    require(2 * 420 > 2 ** 9 and 2 * 420 <= 2 ** 10, "minimality arithmetic")
    for probe in probes:
        expected = [False] * 240 + [j in probe for j in range(420)]
        require(execute_boolean(word, probe) == expected, "full-word Boolean probe failed")

    # Distinct mutated D parities of each promised weight exercise the real word.
    mutation_controls = []
    for support in ([81], [81, 82], [81, 82, 83]):
        mutant = copy.deepcopy(word)
        mutant["D"][81][2] = sorted(set(mutant["D"][81][2]) ^ {240 + j for j in support})
        syndrome = 0
        for j in support:
            syndrome ^= labels[j]
        detected = 0
        for k, probe in enumerate(probes):
            expected = [False] * 240 + [j in probe for j in range(420)]
            expected[120 + 81] = bool(syndrome & (2 ** k))
            require(execute_boolean(mutant, probe) == expected, "D fault syndrome differs from prediction")
            detected += bool(expected[120 + 81])
        require(detected > 0, "promised fault went undetected")
        mutation_controls.append({"weight": len(support), "detecting_probes": detected})

    rejected = []
    for name, index, replacement in (("zero_column", 0, 0), ("duplicate_columns", 1, labels[0]),
                                     ("triple_sum_zero", 2, labels[0] ^ labels[1])):
        malformed = labels.copy()
        malformed[index] = replacement
        try:
            validate_labels(malformed)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("malformed suite accepted: " + name)

    blind = copy.deepcopy(word)
    blind["D"][81][2] = sorted(set(blind["D"][81][2]) ^ {240, 241, 242, 243})
    require(all(len(probe & {0, 1, 2, 3}) % 2 == 0 for probe in probes), "four-term blind spot absent")
    require(all(execute_boolean(blind, probe) == execute_boolean(word, probe) for probe in probes),
            "four-term blind spot did not survive actual replay")
    require(execute_boolean(blind, {0})[201] and not execute_boolean(word, {0})[201],
            "singleton dirty input must expose the blind fault")
    print(json.dumps({"method": "support sets, then full-word Boolean execution", "test_count": 10,
                      "baseline_K_equals_D": True, "all_columns_nonzero_distinct_sum_free": True,
                      "minimum_test_count": 10, "mutated_word_controls": mutation_controls,
                      "malformed_suites_rejected": rejected,
                      "weight_four_fault_passes_all_ten": [0, 1, 2, 3]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
