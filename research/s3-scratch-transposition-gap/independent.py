#!/usr/bin/env python3
"""Support proof for length-2 S3 words, without the bit-matrix enumerator.

An algebra element is a set of permutations. Addition is symmetric difference.
This file does not import verify.py.
"""

def compose(later, earlier):
    return tuple(later[earlier[i]] for i in range(3))


def multiply(left, right):
    out = set()
    for a in left:
        for b in right:
            product = compose(a, b)
            if product in out:
                out.remove(product)
            else:
                out.add(product)
    return frozenset(out)


def main():
    identity = (0, 1, 2)
    s = (1, 0, 2)
    t = (0, 2, 1)
    gap = (2, 1, 0)
    ball = {identity}
    for a in (s, t):
        for b in (s, t):
            # (a + e)(b + e) = ab + a + b + e, the support of one length-2 expansion.
            ball |= set(multiply(frozenset({identity, a}), frozenset({identity, b})))
    if compose(s, s) != identity or compose(t, t) != identity:
        raise SystemExit("generator failed to be an involution")
    if gap in ball or len(ball) != 5:
        raise SystemExit(f"support changed: {sorted(ball)}")
    # The length-3 word s*t*s is the transposition, so the bound is sharp.
    word = compose(s, compose(t, s))
    if word != gap:
        raise SystemExit("s*t*s is not the gap")
    print('{"ball":5,"gap_in_ball":false,"length3_word":"sts"}')


if __name__ == "__main__":
    main()
