"""Exact shortest paths for the directed two-axis elementary record alphabet."""

import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import sys


GATES = ("C01", "C10", "X0", "X1", "S0", "S1", "CZ", "omega")
IDENTITY = ((0, 1, 2, 3), (0, 0, 0, 0))
TARGET = "31023223"
FARTHEST = "02133322"
TARGET_WORD = ("C01", "X1", "C10", "S1", "omega", "omega")
FARTHEST_WORD = ("C01", "C10", "C01", "X0", "S0", "X0", "omega", "omega")
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
         "verify.py", "independent_check.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def step(state, gate):
    """Left-compose one gate on its four literal basis-column images."""
    need(gate in GATES, "unknown gate")
    permutation, phases = state
    output, exponent = [], []
    for index in range(4):
        y, p = permutation[index], phases[index]
        bit0, bit1 = y & 1, y >> 1
        if gate == "C01":
            y ^= bit0 << 1
        elif gate == "C10":
            y ^= bit1
        elif gate == "X0":
            y ^= 1
        elif gate == "X1":
            y ^= 2
        elif gate == "S0":
            p += bit0
        elif gate == "S1":
            p += bit1
        elif gate == "CZ":
            p += 2 * bit0 * bit1
        else:
            p += 1
        output.append(y)
        exponent.append(p % 4)
    return tuple(output), tuple(exponent)


def code(state):
    return "".join(str(value) for part in state for value in part)


def census():
    distance, parent = {IDENTITY: 0}, {}
    pending = deque([IDENTITY])
    transitions = 0
    for _ in range(3072):
        need(bool(pending), "group exhausted before 3072 states")
        state = pending.popleft()
        for gate in GATES:
            following = step(state, gate)
            transitions += 1
            if following not in distance:
                need(len(distance) < 3072, "group exceeds 3072 states")
                distance[following] = distance[state] + 1
                parent[following] = (state, gate)
                pending.append(following)
    need(not pending, "unprocessed states")
    need(transitions == 24576, "incomplete edge census")
    return distance, parent


def shortest_word(state, parents):
    result = []
    for _ in range(8):
        if state == IDENTITY:
            break
        state, gate = parents[state]
        result.append(gate)
    need(state == IDENTITY, "parent chain exceeds diameter")
    return tuple(reversed(result))


def execute(word):
    need(len(word) <= 16, "word exceeds bounded fixture length")
    state = IDENTITY
    for gate in word:
        state = step(state, gate)
    return code(state)


def certificate(distance):
    return {"schema": "two-axis-monomial-distances/1",
            "gates": list(GATES),
            "distances": sorted([[code(state), value]
                                 for state, value in distance.items()])}


def rejected(action, message):
    try:
        action()
    except ValueError as error:
        need(str(error) == message, "unexpected rejection reason")
    else:
        raise ValueError("control was accepted: " + message)


def check_words(distance, parents):
    by_code = {code(state): state for state in distance}
    need(distance[by_code[TARGET]] == 6, "target distance")
    need(distance[by_code[FARTHEST]] == 8, "farthest distance")
    need(execute(TARGET_WORD) == TARGET, "six-record endpoint")
    need(execute(FARTHEST_WORD) == FARTHEST, "eight-record endpoint")
    lengths = Counter()
    for state, value in distance.items():
        word = shortest_word(state, parents)
        need(len(word) == value and execute(word) == code(state), "word replay")
        lengths[value] += 1
    need(execute(TARGET_WORD[:-1]) != TARGET, "omitted absolute phase control")
    need(execute(("C10",) + TARGET_WORD[1:]) != TARGET, "CNOT direction control")
    need(execute(TARGET_WORD[:3] + ("S0",) + TARGET_WORD[4:]) != TARGET,
         "phase-axis control")
    need(execute(TARGET_WORD[:3] + ("S1",) * 3 + TARGET_WORD[4:]) != TARGET,
         "directed S control")
    rejected(lambda: step(IDENTITY, "S1_inverse"), "unknown gate")
    rejected(lambda: execute(("omega",) * 17), "word exceeds bounded fixture length")
    return sorted(lengths.items())


def receipt(histogram, payload):
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        path = root / name
        need(path.is_file() and not path.is_symlink(), "missing regular package file")
        need(path.stat().st_size <= 1_000_000, "package file too large")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"result": "PASS_TWO_AXIS_MONOMIAL_GEODESICS", "states": 3072,
            "transitions": 24576, "histogram": histogram, "target_distance": 6,
            "diameter": 8, "shortest_words_replayed": 3072,
            "semantic_controls": 4, "domain_controls": 2,
            "distance_certificate_sha256": hashlib.sha256(json.dumps(
                payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "python": sys.version.split()[0], "files_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", type=Path)
    args = parser.parse_args()
    distance, parents = census()
    expected = certificate(distance)
    histogram = check_words(distance, parents)
    need(histogram == list(enumerate((1, 8, 42, 162, 467, 884, 940, 475, 93))),
         "distance distribution")
    if args.write_certificate is not None:
        with args.write_certificate.open("x", encoding="utf-8") as output:
            output.write(json.dumps(expected, separators=(",", ":")) + "\n")
        print("WROTE_DISTANCE_CERTIFICATE states=3072")
        return
    print(json.dumps(receipt(histogram, expected), sort_keys=True))


if __name__ == "__main__":
    main()
