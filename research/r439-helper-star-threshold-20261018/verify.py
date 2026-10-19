#!/usr/bin/env python3
"""Verify the minimal q=3 helper-star boundary and its local positive invoice."""

from itertools import product


ROLES = ("x", "a", "h", "y1", "y2", "y3")
HELPERS = {"a", "h"}
TARGETS = {"y1", "y2", "y3"}
Q = len(TARGETS)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def direct_word(q=Q):
    return [(0, f"y{i}", src) for i in range(1, q + 1) for src in ("a", "h")]


def mixed_word(q=Q):
    return ([(0, "h", "a")]
            + [(0, f"y{i}", "h") for i in range(1, q + 1)]
            + [(0, "h", "a")])


def execute(state, word):
    values = dict(zip(ROLES, state))
    for frame, dest, src in word:
        need(frame == 0, "word left the common zero frame")
        values[dest] ^= values[src]
    return tuple(values[role] for role in ROLES)


def expected(state):
    x, a, h, y1, y2, y3 = state
    return x, a, h, y1 ^ a ^ h, y2 ^ a ^ h, y3 ^ a ^ h


def semantic_response(word):
    """Return the target-by-helper matrix, rejecting non-identity helper rows."""
    columns = []
    for helper in ("a", "h"):
        state = [0] * len(ROLES)
        state[ROLES.index(helper)] = 1
        out = execute(tuple(state), word)
        need(out[ROLES.index("x")] == 0, "D changed source x")
        need(out[ROLES.index("a")] == state[ROLES.index("a")],
             "D changed helper a")
        need(out[ROLES.index("h")] == state[ROLES.index("h")],
             "D changed helper h")
        columns.append([out[ROLES.index(f"y{i}")] for i in range(1, Q + 1)])
    return [[columns[j][i] for j in range(len(columns))]
            for i in range(Q)]


def validate_h2_sem(word):
    for frame, dest, src in word:
        need(frame == 0, "not a zero-frame word")
        need(dest != src, "ADD has identical destination and source")
        need(dest in HELPERS | TARGETS and src in HELPERS | TARGETS,
             "operand outside target/helper set")
        need(not (dest in HELPERS and src in TARGETS),
             "target feeds a helper: violates retained H1")


def first_counterexample(word):
    for state in product((0, 1), repeat=len(ROLES)):
        if execute(state, word) != expected(state):
            return state
    return None


def positive_envelope(word, reverse=False):
    values = {role: 1 for role in ROLES}
    peak = 1
    sequence = reversed(word) if reverse else word
    for frame, dest, src in sequence:
        need(frame == 0, "integer bill found a nonzero frame")
        values[dest] += values[src]
        peak = max(peak, values[dest])
    return peak


def main():
    direct = direct_word()
    mixed = mixed_word()
    validate_h2_sem(mixed)
    need(len(direct) == 2 * Q == 6, "direct invoice changed")
    need(len(mixed) == Q + 2 == 5, "wrapped invoice changed")
    K = semantic_response(direct)
    N = semantic_response(mixed)
    need(K == N == [[1, 1] for _ in range(Q)],
         "semantic D response N differs from the required K")

    states = list(product((0, 1), repeat=len(ROLES)))
    for state in states:
        want = expected(state)
        need(execute(state, direct) == want,
             f"direct word differs at dirty state {state}")
        need(execute(state, mixed) == want,
             f"helper-star word differs at dirty state {state}")
        need(execute(want, reversed(direct)) == state,
             f"direct inverse differs at state {state}")
        need(execute(want, reversed(mixed)) == state,
             f"helper-star inverse differs at state {state}")

    # The general q+2 versus 2q formula makes q=3 the first strict saving.
    costs = {q: (2 * q, q + 2) for q in range(1, 9)}
    need(costs[1] == (2, 3) and costs[2] == (4, 4),
         "q=1/q=2 break-even controls changed")
    need(costs[3] == (6, 5), "q=3 is not the first positive point")
    need(all((mixed_cost < direct_cost) == (q >= 3)
             for q, (direct_cost, mixed_cost) in costs.items()),
         "q threshold formula failed")

    direct_f = positive_envelope(direct)
    direct_b = positive_envelope(direct, reverse=True)
    mixed_f = positive_envelope(mixed)
    mixed_b = positive_envelope(mixed, reverse=True)
    need((direct_f, direct_b) == (3, 3), "direct F/B profile changed")
    need((mixed_f, mixed_b) == (3, 3), "mixed F/B profile changed")

    # Negative controls: omit restoration, or update one target from a instead.
    unrestored = mixed[:-1]
    wrong_target = list(mixed)
    wrong_target[1] = (0, "y1", "a")
    need(first_counterexample(unrestored) is not None,
         "omitted restoration control unexpectedly passed")
    need(first_counterexample(wrong_target) is not None,
         "wrong-target-source control unexpectedly passed")

    print("PASS_HELPER_STAR_Q3 states=64 direct=6 mixed=5 saving=1 "
          "F=3/3 B=3/3 controls=2")


if __name__ == "__main__":
    main()
