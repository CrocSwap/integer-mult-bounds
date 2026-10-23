#!/usr/bin/env python3
"""Finite dirty-state control for a direct product call vs. the A/B alphabet."""

from itertools import product


def step(state, operation):
    x, y, z = state
    if operation == "B":
        return x, y, z ^ x
    if operation == "A":
        return x, y ^ z, z
    if operation == "D":
        return x, y ^ x, z
    raise ValueError(operation)


def run(state, word):
    for operation in word:
        state = step(state, operation)
    return state


def desired(state):
    x, y, z = state
    return x, y ^ x, z


def realizes(word, states):
    return all(run(state, word) == desired(state) for state in states)


def main():
    states = tuple(product((0, 1), repeat=3))
    if not realizes(("D",), states):
        raise SystemExit("FAIL: direct product call misses a dirty state")
    if not realizes(("B", "A", "B", "A"), states):
        raise SystemExit("FAIL: B A B A does not realize the product")

    checked_short = 0
    for length in range(4):
        for word in product(("A", "B"), repeat=length):
            checked_short += 1
            if realizes(word, states):
                raise SystemExit(
                    "FAIL: old-alphabet word of length "
                    f"{length} realizes the product: {''.join(word)}"
                )

    print(
        "PASS_CONNECTOR_DIRECT_CALL_PHYSICAL_GAP "
        f"dirty_states={len(states)} short_words={checked_short} "
        "old_alphabet_minimum=4 witness=BABA direct_calls=1"
    )


if __name__ == "__main__":
    main()
