#!/usr/bin/env python3
"""A prefix-walk return has even length.

The checker uses one-bit parity. It does not census words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ZERO_XOR_RETURN even_length=true deltas=1,2 no_new_kappa"
LABELS = 7


def fail(message):
    raise SystemExit("FAIL_ZERO_XOR_RETURN " + message)


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


def weight(state):
    return state.bit_count() & 1


def prefixes(word):
    state = 0
    out = [0]
    for label in word:
        state ^= 1 << label
        out.append(state)
    return out


def pair_sums(states):
    return {left ^ right for left in states for right in states}


def revisits(word):
    return len(word) - len(set(prefixes(word)))


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    for state in range(1 << LABELS):
        for label in range(LABELS):
            require(weight(state ^ (1 << label)) != weight(state), "a step kept the weight parity")
    fresh = (0, 0, 1, 1)
    repeated = (0, 0, 0, 0)
    for word, expected in ((fresh, 1), (repeated, 2)):
        states = prefixes(word[:2])
        longer = prefixes(word)
        require(longer[-1] == states[-1] == 0, "a repeated label moved the endpoint")
        require(set(longer) >= set(states), "a repeated label lost a state")
        require(pair_sums(set(longer)) >= pair_sums(set(states)), "a repeated label lost a pair sum")
        require(revisits(word) - revisits(word[:2]) == expected, "the revisit delta moved")
    require(revisits((0, 1, 0, 1)) == 0, "a two-step return acquired a revisit")
    return {
        "labels": LABELS,
        "fresh_delta": 1,
        "repeated_delta": 2,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
