#!/usr/bin/env python3
"""Certify the shorter selected left-map word; standard library, no writes."""

import hashlib
import json
from pathlib import Path


TARGET = (3, 5, 9, 17, 32, 65, 129, 1, 256)
# Temporal order; each pair means row[target] ^= row[control].
WORD = (
    (7, 0), (6, 0), (4, 0), (3, 0), (2, 0),
    (0, 1), (1, 0), (2, 1), (1, 2), (2, 1),
    (3, 2), (2, 3), (3, 2), (4, 3), (3, 4),
    (4, 3), (5, 4), (4, 5), (5, 4), (6, 5),
    (5, 6), (6, 5), (7, 6), (6, 7), (7, 6),
)
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
         "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def word_matrix(word):
    require(len(word) <= 27, "word exceeds the fixed certificate domain")
    rows = [1 << i for i in range(9)]
    for target, control in word:
        require(0 <= target < 9 and 0 <= control < 9, "invalid coordinate")
        require(target != control, "a CNOT needs two coordinates")
        rows[target] ^= rows[control]
    return tuple(rows)


def apply_word(coordinates, word):
    require(len(coordinates) == 9, "nine coordinates required")
    result = list(coordinates)
    for target, control in word:
        result[target] ^= result[control]
    return tuple(result)


def direct_map(x):
    """Separate, explicit coordinate oracle, without interpreting WORD."""
    return (x[0] ^ x[1], x[0] ^ x[2], x[0] ^ x[3], x[0] ^ x[4],
            x[5], x[0] ^ x[6], x[0] ^ x[7], x[0], x[8])


def check_complete_addresses(f):
    require(f in (1, 2), "finite census is registered only for f=1,2")
    mask = (1 << f) - 1
    count = 1 << (9 * f)
    inverse = tuple(reversed(WORD))
    for address in range(count):
        coordinates = tuple((address >> (f * i)) & mask for i in range(9))
        actual = apply_word(coordinates, WORD)
        require(actual == direct_map(coordinates), "complete address mismatch")
        require(actual[8] == coordinates[8], "spectator changed")
        require(apply_word(actual, inverse) == coordinates, "inverse mismatch")
    return count


def check_controls():
    require(word_matrix(WORD[1:]) != TARGET, "extra deletion escaped")
    swapped = tuple((control, target) for target, control in WORD)
    require(word_matrix(swapped) != TARGET, "control-direction mutant escaped")
    x = (2, 0, 0, 0, 0, 0, 0, 0, 0)
    low = apply_word(tuple(value & 1 for value in x), WORD)
    first_column_only = tuple((x[i] & 2) | low[i] for i in range(9))
    require(first_column_only != direct_map(x), "one-column mutant escaped")
    return 3


def package_hashes():
    root = Path(__file__).resolve().parent
    result = {}
    for name in FILES:
        require((root / name).stat().st_size <= 131072, "source exceeds cap")
        data = (root / name).read_bytes()
        require(len(data) <= 131072, "package source exceeds hash bound")
        result[name] = hashlib.sha256(data).hexdigest()
    return result


def main():
    require(len(WORD) == 25, "new gate count changed")
    require(word_matrix(WORD) == TARGET, "matrix identity failed")
    counts = {str(f): check_complete_addresses(f) for f in (1, 2)}
    controls = check_controls()
    print(json.dumps({
        "status": "PASS_SELECTED_LINEAR_CNOT_CANCELLATION",
        "claim_type": "finite certificate and scoped all-column proof",
        "new_left_gate_count": len(WORD),
        "cited_predecessor_left_gate_count": 27,
        "matrix_rows": TARGET,
        "complete_addresses_and_inverse_checks": counts,
        "rejected_mutants": controls,
        "package_sha256": package_hashes(),
        "no_new_kappa": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
