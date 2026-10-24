#!/usr/bin/env python3
"""Every even length from 4 through 18 meets every positive length-22 split.

The checker replays explicit witnesses. It does not census words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_EVEN_RETURN_LENGTHS splits=10 lengths=8 odd_return=false no_new_kappa"
LABELS = 7
LENGTH = 22
LENGTHS = [4, 6, 8, 10, 12, 14, 16, 18]
WITNESSES = [
    (11, 10, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 4, 3, 5, 3, 4, 3, 6, 3, 5, 3, 6]),
    (11, 10, [4, 5, 4, 6, 4, 5, 4, 6, 3, 0, 3, 1, 3, 0, 3, 2, 3, 0, 3, 1, 0, 2]),
    (11, 10, [4, 5, 6, 5, 4, 6, 0, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 2, 0, 1, 0, 3]),
    (11, 10, [5, 6, 5, 6, 4, 0, 4, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 2, 0, 1, 0, 3]),
    (11, 9, [0, 1, 0, 2, 0, 1, 0, 2, 3, 3, 4, 3, 5, 3, 4, 3, 6, 3, 4, 5, 4, 6]),
    (11, 9, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 3, 4, 3, 5, 3, 4, 3, 6, 3, 5, 6]),
    (11, 9, [5, 6, 5, 6, 4, 4, 0, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 2, 0, 1, 0, 3]),
    (11, 8, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 3, 4, 3, 5, 3, 4, 4, 6, 4, 5, 6]),
    (11, 8, [5, 6, 5, 6, 4, 4, 3, 0, 4, 4, 3, 1, 3, 0, 3, 2, 3, 0, 3, 1, 0, 2]),
    (11, 8, [6, 3, 6, 4, 6, 3, 6, 5, 6, 3, 6, 4, 3, 5, 2, 2, 0, 1, 2, 2, 0, 1]),
    (11, 7, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 3, 4, 3, 5, 3, 6, 6, 4, 5, 6, 6]),
    (11, 7, [4, 5, 4, 6, 4, 5, 4, 6, 3, 3, 0, 1, 3, 3, 0, 2, 3, 3, 0, 1, 0, 2]),
    (11, 7, [5, 6, 5, 6, 4, 4, 3, 0, 4, 4, 3, 1, 4, 4, 3, 0, 3, 2, 0, 1, 0, 2]),
    (11, 6, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 3, 4, 4, 5, 6, 3, 3, 4, 4, 5, 6]),
    (11, 6, [5, 6, 5, 6, 4, 4, 3, 0, 4, 4, 3, 1, 4, 4, 0, 2, 4, 4, 0, 1, 0, 2]),
    (10, 10, [0, 1, 0, 2, 0, 1, 0, 2, 3, 4, 3, 5, 3, 4, 3, 6, 3, 4, 3, 5, 6, 4]),
    (10, 10, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 4, 3, 5, 3, 4, 3, 6, 3, 5, 6, 3]),
    (10, 10, [3, 4, 3, 5, 3, 4, 3, 6, 3, 4, 3, 5, 3, 4, 3, 6, 0, 2, 2, 1, 0, 1]),
    (10, 10, [5, 6, 5, 6, 0, 4, 4, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 2, 0, 1, 0, 3]),
    (10, 9, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 3, 3, 4, 3, 5, 3, 4, 3, 6, 5, 6]),
    (10, 9, [5, 6, 5, 6, 4, 4, 3, 4, 4, 0, 3, 1, 3, 0, 3, 2, 3, 0, 3, 1, 0, 2]),
    (10, 9, [6, 3, 6, 4, 6, 3, 6, 5, 6, 3, 6, 4, 3, 5, 2, 2, 0, 2, 2, 1, 0, 1]),
    (10, 8, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 3, 3, 3, 4, 3, 5, 3, 4, 6, 5, 6]),
    (10, 8, [4, 5, 4, 6, 4, 5, 4, 6, 3, 3, 0, 3, 3, 1, 3, 3, 0, 2, 0, 1, 0, 2]),
    (10, 8, [5, 6, 5, 6, 4, 4, 3, 4, 4, 0, 4, 4, 3, 1, 3, 0, 3, 2, 0, 1, 0, 2]),
    (10, 7, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 3, 3, 3, 4, 3, 5, 3, 4, 5, 6, 6]),
    (10, 7, [4, 5, 4, 6, 4, 5, 4, 6, 3, 3, 2, 3, 3, 0, 3, 3, 2, 1, 3, 3, 0, 1]),
    (10, 7, [5, 6, 5, 6, 4, 4, 3, 4, 4, 0, 4, 4, 3, 1, 4, 4, 0, 2, 0, 1, 0, 2]),
    (9, 9, [0, 1, 3, 0, 3, 2, 0, 1, 0, 2, 3, 3, 3, 4, 3, 5, 3, 4, 3, 6, 6, 5]),
    (9, 9, [4, 5, 4, 6, 4, 5, 4, 6, 3, 3, 0, 3, 3, 1, 0, 3, 3, 2, 0, 1, 0, 2]),
    (9, 9, [5, 6, 5, 6, 4, 4, 3, 4, 4, 0, 3, 4, 4, 1, 3, 0, 3, 2, 0, 1, 0, 2])
]


def fail(message):
    raise SystemExit("FAIL_EVEN_RETURN_LENGTHS " + message)


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


def positive_splits():
    rows = []
    half = 1 << (LABELS - 1)
    for small in range(1, LENGTH):
        for large in range(small, LENGTH):
            budget = large * (large - 1) // 2 + small * (small - 1) // 2 - (half - 1)
            excess = large * small - half
            need = -((-excess) // 2) if excess > 0 else 0
            upper = budget + budget * budget // 4 if budget > 0 else budget
            if (large <= LENGTH // 2 and small <= LENGTH // 2 and large * small >= half
                    and budget >= 0 and upper >= need):
                rows.append((large, small))
    return rows


def simulate(word):
    state = 0
    states = [0]
    for label in word:
        state ^= 1 << label
        states.append(state)
    return states


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    for state in range(1 << LABELS):
        for label in range(LABELS):
            flipped = state ^ (1 << label)
            require(flipped.bit_count() % 2 != state.bit_count() % 2, "a step kept the weight parity")
    admitted = [split for split in positive_splits() if sum(split) < LENGTH]
    require(sorted(admitted, reverse=True) == sorted({(s, t) for s, t, _word in WITNESSES}, reverse=True),
            "the positive splits moved")
    covered = {split: set() for split in admitted}
    for large, small, word in WITNESSES:
        states = simulate(word)
        even = sum(state.bit_count() % 2 == 0 for state in set(states))
        odd = len(set(states)) - even
        observed = tuple(sorted((even, odd), reverse=True))
        require(len(word) == LENGTH and states[-1] == 0, "a witness is not restored")
        require(observed == (large, small), "a witness missed its split")
        require(len(word) - len(set(states)) == LENGTH - (large + small), "a witness missed its revisit count")
        require(all(0 <= label < LABELS for label in word), "a witness label left the alphabet")
        distances = {right - left for left, earlier in enumerate(states) for right in range(left + 1, len(states)) if states[right] == earlier}
        require(all(distance % 2 == 0 for distance in distances), "an odd return occurred")
        covered[(large, small)].update(distance for distance in distances if distance in LENGTHS)
    require(all(covered[split] == set(LENGTHS) for split in admitted), "an even length is missing")
    return {"splits": len(admitted), "lengths": LENGTHS, "odd_return": False, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
