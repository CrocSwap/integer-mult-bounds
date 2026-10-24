#!/usr/bin/env python3
"""Exact common-direction census; standard library only, no output files."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

IDENTITY = 273  # Three binary rows, least significant row first.
DIRECTIONS = tuple(range(1, 8))
UPPER_WORD = (1, 2, 4, 1, 2)
EXPECTED = {4: 7, 16: 126, 24: 420, 64: 504, 96: 672, 144: 672}
PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"
)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(left, right):
    result = 0
    for row_index in range(3):
        row = 0
        for column in range(3):
            if left >> (3 * row_index + column) & 1:
                row ^= right >> (3 * column) & 7
        result |= row << (3 * row_index)
    return result


def rank(rows):
    rows = list(rows)
    check(len(rows) <= 504, "rank input exceeds fixed census capacity")
    result = 0
    for bit in (1, 2, 4):
        pivot = next((j for j in range(result, len(rows)) if rows[j] & bit), None)
        if pivot is None:
            continue
        rows[result], rows[pivot] = rows[pivot], rows[result]
        for j in range(result + 1, len(rows)):
            if rows[j] & bit:
                rows[j] ^= rows[result]
        result += 1
    return result


def paid(left, direction):
    check(0 <= left < 8 and 1 <= direction < 8, "factor outside binary alphabet")
    check((left & direction).bit_count() % 2 == 0, "singular paid factor")
    outer = sum((direction if left >> row & 1 else 0) << (3 * row)
                for row in range(3))
    return IDENTITY ^ outer


def matrix_model():
    group = tuple(m for m in range(512)
                  if rank(tuple(m >> (3 * row) & 7 for row in range(3))) == 3)
    check(len(group) == 168, "wrong matrix group order")
    index = {matrix: i for i, matrix in enumerate(group)}
    factors = {b: tuple(paid(a, b) for a in range(8)
                        if (a & b).bit_count() % 2 == 0) for b in DIRECTIONS}
    transitions = {b: tuple(tuple(index[multiply(f, g)] for g in group)
                            for f in factors[b]) for b in DIRECTIONS}
    return group, index, factors, transitions


def validate_census(masks):
    check(set(masks) == set(product(DIRECTIONS, repeat=4)), "missing direction word")
    check(all(0 <= mask < (1 << 168) for mask in masks.values()), "invalid endpoint mask")
    histogram = dict(sorted(Counter(mask.bit_count() for mask in masks.values()).items()))
    check(histogram == EXPECTED, "four-direction histogram mismatch")
    return histogram


def matrix_census(index, transitions):
    states = {(): frozenset((index[IDENTITY],))}
    for _ in range(4):
        states = {word + (b,): frozenset(table[g] for table in transitions[b] for g in s)
                  for word, s in states.items() for b in DIRECTIONS}
    masks = {word: sum(1 << g for g in s) for word, s in states.items()}
    return masks, validate_census(masks)


def compose(left, right):
    return tuple(left[right[x]] for x in range(8))


def encode_action(action):
    # The images of the three basis vectors give the three columns.
    return sum(((action[1 << col] >> row) & 1) << (3 * row + col)
               for row in range(3) for col in range(3))


def action_model():
    actions = []
    for basis in product(range(1, 8), repeat=3):
        action = tuple((basis[0] if x & 1 else 0)
                       ^ (basis[1] if x & 2 else 0)
                       ^ (basis[2] if x & 4 else 0) for x in range(8))
        if len(set(action)) == 8:
            actions.append(action)
    actions.sort(key=encode_action)
    check(len(actions) == 168 and len(set(actions)) == 168, "wrong action group")
    index = {action: i for i, action in enumerate(actions)}
    factor_ids = {}
    for b in DIRECTIONS:
        permitted = []
        for a in range(8):
            action = tuple(x ^ (a if (b & x).bit_count() % 2 else 0)
                           for x in range(8))
            if len(set(action)) == 8:
                permitted.append(index[action])
        check(len(permitted) == 4, "wrong independent factor count")
        factor_ids[b] = tuple(permitted)
    table = tuple(tuple(index[compose(a, b)] for b in actions) for a in actions)
    return tuple(actions), factor_ids, table


def action_census(factor_ids, table):
    pairs = {(b, c): tuple(table[g][f] for f in factor_ids[b] for g in factor_ids[c])
             for b in DIRECTIONS for c in DIRECTIONS}
    masks = {}
    evaluations = 0
    for word in product(DIRECTIONS, repeat=4):
        mask = 0
        for first in pairs[word[:2]]:
            for last in pairs[word[2:]]:
                mask |= 1 << table[last][first]
                evaluations += 1
        masks[word] = mask
    check(evaluations == 614656, "incomplete independent parameter enumeration")
    return masks, evaluations


def upper_witnesses(index):
    witnesses = {IDENTITY: ()}
    for b in UPPER_WORD:
        next_witnesses = {}
        for current, word in sorted(witnesses.items()):
            for a in range(8):
                if (a & b).bit_count() % 2 == 0:
                    endpoint = multiply(paid(a, b), current)
                    next_witnesses.setdefault(endpoint, word + (a,))
        witnesses = next_witnesses
    check(set(witnesses) == set(index), "five-direction word is not universal")
    return witnesses


def check_upper(actions, factor_ids, table, witnesses):
    identity = actions.index(tuple(range(8)))
    endpoints = set()
    evaluations = 0
    for parameters in product(*(factor_ids[b] for b in UPPER_WORD)):
        endpoint = identity
        for factor in parameters:
            endpoint = table[factor][endpoint]
        endpoints.add(endpoint)
        evaluations += 1
    check(len(endpoints) == 168 and evaluations == 1024, "independent upper word incomplete")
    checks = 0
    for target, coefficients in sorted(witnesses.items()):
        for x in range(8):
            actual = x
            for a, b in zip(coefficients, UPPER_WORD, strict=True):
                actual ^= a if (b & actual).bit_count() % 2 else 0
            expected = sum(((target >> (3 * row) & x).bit_count() % 2) << row
                           for row in range(3))
            check(actual == expected, "literal component word changes the wrong input")
            checks += 1
    check(checks == 1344, "incomplete arbitrary-input checks")
    return checks


def free_maps_and_delta(group, factors):
    all_factors = set(f for fs in factors.values() for f in fs)
    conjugations = 0
    for free in group:
        inverse = next(g for g in group if multiply(free, g) == IDENTITY)
        check(multiply(inverse, free) == IDENTITY, "one-sided free inverse")
        for fs in factors.values():
            for factor in fs:
                check(multiply(multiply(free, factor), inverse) in all_factors,
                      "free conjugation leaves the paid alphabet")
                conjugations += 1
        translated = tuple(multiply(m, free) for m in group)
        check(set(translated) == set(group), "free right translation loses a target")
        rows = tuple((m ^ IDENTITY) >> (3 * row) & 7
                     for m in translated for row in range(3))
        check(rank(rows) == 3, "universal target does not have delta three")
    check(conjugations == 4704, "incomplete conjugation checks")
    return conjugations


def rejected(call):
    try:
        call()
    except ValueError:
        return 1
    raise ValueError("negative control was accepted")


def controls(masks, witnesses):
    count = rejected(lambda: paid(1, 1))
    count += rejected(lambda: paid(0, 0))
    count += rejected(lambda: paid(8, 1))
    full = (1 << 168) - 1
    count += rejected(lambda: check(masks[(1, 2, 4, 1)] == full, "four is not five"))
    altered = dict(masks)
    del altered[(1, 1, 1, 1)]
    count += rejected(lambda: validate_census(altered))
    altered = dict(masks)
    altered[(1, 2, 4, 1)] = full
    count += rejected(lambda: validate_census(altered))
    target = next(m for m, w in witnesses.items() if any(w))
    coefficients = list(witnesses[target])
    changed = next(i for i, a in enumerate(coefficients) if a)
    coefficients[changed] = 0
    current = IDENTITY
    for a, b in zip(coefficients, UPPER_WORD, strict=True):
        current = multiply(paid(a, b), current)
    count += rejected(lambda: check(current == target, "omitted nonidentity factor"))
    check(count == 7, "incomplete rejection controls")
    return count


def receipt(result):
    package = Path(__file__).resolve().parent
    source = json.loads((package / "SOURCES.json").read_text())
    check(len(source["files"]) <= 16, "source inventory exceeds fixed capacity")
    files = {name: sha256((package / name).read_bytes()).hexdigest()
             for name in PACKAGE_FILES}
    for row in source["files"]:
        if row["usage"] == "input":
            digest = sha256((package.parent.parent / row["path"]).read_bytes()).hexdigest()
            check(digest == row["sha256"], "predecessor input changed")
            files[row["path"]] = digest
    return {"result": result, "files_sha256": files}


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    group, index, factors, transitions = matrix_model()
    masks, histogram = matrix_census(index, transitions)
    actions, factor_ids, table = action_model()
    check(tuple(map(encode_action, actions)) == group, "independent group disagreement")
    independent, evaluations = action_census(factor_ids, table)
    check(independent == masks, "independent complete endpoint masks disagree")
    witnesses = upper_witnesses(index)
    dirty_checks = check_upper(actions, factor_ids, table, witnesses)
    conjugations = free_maps_and_delta(group, factors)
    control_count = controls(masks, witnesses)
    payload = [[list(w), str(mask)] for w, mask in sorted(masks.items())]
    result = {"group": len(group), "four_word_histogram": histogram,
              "independent_parameter_tuples": evaluations, "upper_word": UPPER_WORD,
              "upper_targets": len(witnesses), "arbitrary_input_checks": dirty_checks,
              "free_conjugations": conjugations, "delta_cases": len(group),
              "controls": control_count,
              "census_sha256": sha256(json.dumps(payload).encode()).hexdigest(),
              "witnesses_sha256": sha256(json.dumps(sorted(witnesses.items())).encode()).hexdigest()}
    print(json.dumps(receipt(result), sort_keys=True))
    print("PASS_RIGHT_VECTOR_THREE_ROLE_PRODUCTS group=168 words4=2401 "
          "max4=144 upper=5 delta=3 controls=7")


if __name__ == "__main__":
    main()
