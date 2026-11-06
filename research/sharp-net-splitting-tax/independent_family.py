#!/usr/bin/env python3
"""Independent rational-radical net-tax fixtures for t=1/2,sigma=3/2.

No primary or predecessor imports. @CubeJerry, OpenAI Codex assistance.
"""
from fractions import Fraction as F
from math import isqrt
import json


def main():
    count = ties = 0
    bound = F(8, 27)
    for b in range(1, 101):
        for a in range(b, 10*b + 1):
            q, remainder = divmod(a*a, b*b)
            k = isqrt(remainder)
            if k*k != remainder:
                continue
            y, z = F(k, b), F(a, b)
            net = q+y-z
            # Independent completing-the-square identity.
            if net != (z-F(1,2))**2-(y-F(1,2))**2:
                raise ValueError("square decomposition")
            value = net/z**3
            if not 0 <= value <= bound:
                raise ValueError("sharp bound")
            equality = q == 2 and y == F(1,2)
            if (value == bound) != equality:
                raise ValueError("equality classification")
            count += 1
            ties += equality
    # Full split and net split are different objectives.
    if F(5,2)/F(3,2)**3 <= bound:
        raise ValueError("omitted raw-charge negative control")
    if (2+F(1,2)-F(3,2))/F(3,2)**3 != bound:
        raise ValueError("attaining quotient2")
    print(json.dumps({"status":"PASS_INDEPENDENT_NET_SPLIT_FAMILY", "structured_fixtures":count, "attaining_fixtures":ties, "J":"b^2, 1<=b<=100", "R":"a^2, b<=a<=10b, square remainder", "bound":"8/27"}, sort_keys=True))


if __name__ == "__main__":
    main()
