#!/usr/bin/env python3
"""Exact finite controls for the clean-helper flag-count proof."""
from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(vectors, n):
    basis = [0] * n
    for value in vectors:
        x = value
        for bit in range(n - 1, -1, -1):
            if x & (1 << bit):
                if basis[bit]:
                    x ^= basis[bit]
                else:
                    basis[bit] = x
                    break
    return sum(bool(x) for x in basis)


def step(state, frame, x, y):
    """Multiply a formal group-algebra matrix by I+([frame]+1)xy^T."""
    result = dict(state)
    for exponent, rows in state.items():
        term = tuple(y if (row & x).bit_count() % 2 else 0 for row in rows)
        shifted = tuple(a + b for a, b in zip(exponent, frame))
        for key in (exponent, shifted):
            before = result.get(key, (0,) * len(rows))
            after = tuple(a ^ b for a, b in zip(before, term))
            if any(after):
                result[key] = after
            else:
                result.pop(key, None)
    return result


def word(n, frames):
    state = {(0,) * len(frames[0][0]): tuple(1 << i for i in range(n))}
    for frame, x, y in frames:
        state = step(state, frame, x, y)
    return state


def projectors(n):
    return [(x, y) for x in range(1, 1 << n) for y in range(1, 1 << n)
            if (x & y).bit_count() % 2 == 1]


def short_identity_controls():
    ps = projectors(3)
    require(len(ps) == 28, "wrong scalar projector count")
    total = 0
    identities = 0
    letters = [(sign, x, y) for sign in (-1, 1) for x, y in ps]
    for length in range(1, 4):
        for choices in product(letters, repeat=length):
            frames = [((sign,), x, y) for sign, x, y in choices]
            state = word(3, frames)
            total += 1
            if state == {(0,): (1, 2, 4)}:
                identities += 1
                rx = rank([x for _, x, _ in choices], 3)
                ry = rank([y for _, _, y in choices], 3)
                require(rx + ry <= length, "identity span inequality")
    require(identities > 0, "missing identity controls")
    return total, identities


def example_controls():
    e11, e22, e12 = (1, 0, 0, 0), (0, 0, 0, 1), (0, 1, 0, 0)
    direct = [(e11, 1, 1), (e22, 1, 1), (e11, 2, 2), (e22, 2, 2)]
    upper = (e12, 3, 1)
    inverse = (tuple(-v for v in e12), 3, 1)
    calls = direct[:2] + [upper, inverse] + direct[2:]
    expected = {(1, 0, 0, 1): (1, 2, 0), (0, 0, 0, 0): (0, 0, 4)}
    require(word(3, calls) == expected, "restored output or upper cancellation")
    require(word(3, calls[:3] + calls[4:]) != expected, "missing upper call accepted")
    require(word(3, direct) == expected, "direct sharp fixture")
    e21 = (0, 0, 1, 0)
    asymmetric = direct + [(e21, 2, 2)]
    expected_asymmetric = {(1, 0, 0, 1): (1, 0, 0),
                           (1, 0, 1, 1): (0, 2, 0),
                           (0, 0, 0, 0): (0, 0, 4)}
    require(word(3, asymmetric) == expected_asymmetric, "triangular targets")
    return len(calls), len(direct)


def main():
    total, identities = short_identity_controls()
    with_pair, direct = example_controls()
    print(f"PASS_CLEAN_HELPER_FLAG_BOUND short_words={total} "
          f"identity_words={identities} cancellation_calls={with_pair} "
          f"sharp_calls={direct} controls=4")


if __name__ == "__main__":
    main()
