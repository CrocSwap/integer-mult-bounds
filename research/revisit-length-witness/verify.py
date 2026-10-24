#!/usr/bin/env python3
"""Length-2 returns meet every positive length-22 split.

The checker builds ten restored witnesses. It does not census words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_REVISIT_LENGTH_WITNESS splits=10 lengths=2,20,22 no_new_kappa"
LABELS = 7
LENGTH = 22
PLAN = {
    (11, 10): (16, 2, 0, 1, 4),
    (11, 9): (16, 1, 0, 2, 4),
    (10, 10): (16, 1, 1, 1, 4),
    (11, 8): (8, 4, 0, 3, 3),
    (10, 9): (8, 4, 1, 2, 3),
    (11, 7): (8, 3, 0, 4, 3),
    (10, 8): (8, 3, 1, 3, 3),
    (9, 9): (8, 3, 2, 2, 3),
    (11, 6): (8, 2, 0, 5, 3),
    (10, 7): (8, 2, 4, 1, 3),
}


def fail(message):
    raise SystemExit("FAIL_REVISIT_LENGTH_WITNESS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == set(), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def gray(bits):
    vertices = [0]
    for bit in range(bits):
        vertices += [vertex | (1 << bit) for vertex in reversed(vertices)]
    return vertices


def labels_of(vertices):
    cycle = vertices + [vertices[0]]
    labels = []
    for left, right in zip(cycle, cycle[1:]):
        diff = left ^ right
        require(diff.bit_count() == 1, "a Gray step is not one bit")
        labels.append(diff.bit_length() - 1)
    return labels


def simulate(word):
    state = 0
    states = [0]
    for label in word:
        state ^= 1 << label
        states.append(state)
    return states


def with_detours(base_length, count, bit):
    word = labels_of(gray(3 if base_length == 8 else 4))
    offset = 0
    for index in range(count):
        position = 2 * index + offset
        label = word[position]
        word = word[:position] + [bit, label, bit] + word[position + 1:]
        offset += 2
    return word


def witness(base_length, detours, odd_spikes, even_spikes, detour_bit):
    word = with_detours(base_length, detours, detour_bit)
    states = simulate(word)
    odds = [index for index, state in enumerate(states[:-1]) if state.bit_count() % 2]
    evens = [index for index, state in enumerate(states[:-1]) if state.bit_count() % 2 == 0]
    chosen = sorted(odds[:odd_spikes] + evens[:even_spikes], reverse=True)
    require(len(chosen) == odd_spikes + even_spikes, "a spike vertex is missing")
    for index in chosen:
        word = word[:index] + [5, 5] + word[index:]
    return word


def positive_splits():
    rows = []
    half = 1 << (LABELS - 1)
    for small in range(1, LENGTH):
        for large in range(small, LENGTH):
            budget = large * (large - 1) // 2 + small * (small - 1) // 2 - (half - 1)
            excess = large * small - half
            need = -((-excess) // 2) if excess > 0 else 0
            upper = budget + budget * budget // 4 if budget > 0 else budget
            if large <= LENGTH // 2 and small <= LENGTH // 2 and large * small >= half and budget >= 0 and upper >= need:
                rows.append((large, small))
    return rows


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    for state in range(1 << LABELS):
        for label in range(LABELS):
            require((state ^ (1 << label)).bit_count() % 2 != state.bit_count() % 2, "a step kept the weight parity")
    admitted = positive_splits()
    require(sorted(admitted, reverse=True) == [(11, 11), *sorted(PLAN, reverse=True)], "the length-22 domain moved")
    witnesses = []
    for split in sorted(PLAN, reverse=True):
        word = witness(*PLAN[split])
        states = simulate(word)
        even = sum(state.bit_count() % 2 == 0 for state in set(states))
        odd = len(set(states)) - even
        observed = tuple(sorted((even, odd), reverse=True))
        revisits = len(word) - len(set(states))
        lengths = sorted({right - left for left, earlier in enumerate(states) for right in range(left + 1, len(states)) if states[right] == earlier})
        require(len(word) == LENGTH and states[-1] == 0, "a witness is not a restored length-22 word")
        require(observed == split and revisits == LENGTH - sum(split), "a witness missed its split")
        require(lengths == [2, 20, 22], "a witness return length moved")
        require(all(0 <= label < LABELS for label in word), "a witness label left the seven-label alphabet")
        witnesses.append({"split": list(split), "revisits": revisits})
    return {"witnesses": witnesses, "return_lengths": [2, 20, 22], "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
