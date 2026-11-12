"""Independent literal-word witness against pooling chronological exit cuts.

No author executable is imported. This is bounded exact review evidence,
not a fixed-tape runtime or an asymptotic proof.
"""

from collections import Counter
from itertools import product
from math import gcd, lcm, prod
import json


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def literal_census(n):
    # Repeated tuple entries represent distinct physical roles/paid sites.
    roles = (3, 3, 5)
    paid = (2, 2)
    ambient = 5
    g = 0
    while ambient * 3 ** (g + 1) <= n:
        g += 1
    source = Counter()
    exit_cuts = []
    units = 0
    for depth in range(g + 1):
        for path in product(paid, repeat=depth):
            rho = prod(path)
            for word in product(roles, repeat=g - depth):
                c = prod(word)
                if ambient * rho * c > n:
                    continue
                units += 1
                for rank in roles:
                    parent_absent = depth == 0 or (
                        ambient * (rho // path[-1]) * c * rank > n
                    )
                    if parent_absent:
                        source[rho * c * rank] += 1
                if depth == g:
                    for rank in paid:
                        exit_cuts.append((rho * c * rank, 1))
    return g, source, exit_cuts, units


def main():
    widths = [1] * 5
    witness = None
    total_units = total_cuts = 0
    for n in range(5, 136):
        g, source, cuts, units = literal_census(n)
        total_units += units
        total_cuts += len(cuts)
        exact = pooled = 1
        for s, count in source.items():
            if s == n:
                continue
            e = n - s
            require(0 < e < n, "source complement does not contract")
            factor = widths[e] // gcd(widths[e], count)
            exact = lcm(exact, factor)
            pooled = lcm(pooled, factor)
        census = Counter()
        for e, count in cuts:
            require(0 < e < n, "exit does not contract")
            exact = lcm(exact, widths[e] // gcd(widths[e], count))
            census[e] += count
        for e, count in census.items():
            pooled = lcm(pooled, widths[e] // gcd(widths[e], count))
        widths.append(sum(source.values()) * exact)
        if n == 135:
            require(g == 3, "height drift")
            require(source == {81: 16, 135: 8, 90: 8, 60: 16, 100: 4},
                    "literal source census drift")
            require(census == {16: 16}, "literal exit census drift")
            require(widths[16] == 24, "smaller width drift")
            require((exact, pooled) == (12509640, 1563705), "LCM drift")
            require(exact % 24 == 0, "correct policy fails an individual cut")
            require((16 * pooled) % 24 == 0, "pooled policy fails even aggregate")
            require(pooled % 24 != 0, "negative control was not detected")
            witness = dict(rank=n, height=g, source=dict(sorted(source.items())),
                           exit_cuts=len(cuts), exit_rank=16, smaller_width=24,
                           exact_replication=exact, pooled_replication=pooled,
                           pooled_cut_remainder=pooled % 24,
                           correct_width=widths[n])
    print(json.dumps(dict(status="PASS_SEPARATE_CHRONOLOGICAL_EXIT_CONTROL",
                          ordinary_ranks=131, literal_units=total_units,
                          literal_cuts=total_cuts, witness=witness),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
