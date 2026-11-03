"""Exhaustive fixed-point and orbit checks on the declared finite domains."""
from collections import Counter
from math import factorial, gcd

from law import lifted_target, order_bound, root_target, unit_repeat_root
from oracle import (balanced_words, canonical_rotation, literal_matrix, matrix_target,
                    phi, positional_counts, position_target, primitive_period)


def check(ok, why):
    if not ok:
        raise ValueError(why)


def domain():
    for depth in range(2, 8):
        yield depth, 1, list(range(1, 9))
    for depth in range(2, 6):
        yield depth, 2, [1, 5] if depth == 5 else list(range(1, 9))
    for depth in (2, 3):
        yield depth, 3, list(range(1, 9))
    yield 2, 4, list(range(1, 9))


def scan(depth, copies, repeats):
    counts, classes = [0] * copies, [set() for _ in range(copies)]
    periods = [Counter() for _ in range(copies)]
    observed = {d: [0] * (copies*d) for d in repeats}
    roots = [None, *range(copies)]
    forward = {d: {t: lifted_target(depth, copies, d, t) for t in roots} for d in repeats}
    blocks = comparisons = 0
    for word in balanced_words(depth, copies):
        intervals = positional_counts(word, depth)
        matrix = literal_matrix(word, depth)
        check(all(matrix[j][i-1] == x for (i, j), x in intervals.items()),
              "base positional and matrix counts disagree")
        root = position_target(intervals, depth, copies)
        if root is not None:
            counts[root] += 1
            classes[root].add(canonical_rotation(word))
            periods[root][primitive_period(word)] += 1
        for d in repeats:
            end = matrix if d == 1 else literal_matrix(word*d, depth)
            target = matrix_target(end, copies*d)
            check(target == forward[d][root], f"literal power disagreement at {(depth, copies, d, word)}")
            if target is not None:
                observed[d][target] += 1
            comparisons += 1
        blocks += 1
    check(blocks == factorial(depth*copies) // factorial(copies)**depth, "wrong multinomial mass")
    for d, actual in observed.items():
        for c, number in enumerate(actual):
            t = root_target(depth, copies, d, c)
            check(number == (counts[t] if t is not None else 0), "fixed-count transform")
    return dict(blocks=blocks, repeated_word_checks=comparisons, counts=counts,
                classes=[len(group) for group in classes], periods=periods,
                fixed_target_bins=sum(map(len, observed.values())))


def verify_orbits(rows):
    inspected = units = 0
    for (depth, m), row in rows.items():
        ds = [d for d in range(1, m+1) if m % d == 0]
        for c, count in enumerate(row["counts"]):
            fixed, exact = {}, {}
            for d in reversed(ds):
                t = root_target(depth, m//d, d, c)
                fixed[d] = 0 if t is None else rows[depth, m//d]["counts"][t]
                exact[d] = fixed[d] - sum(value for e, value in exact.items() if e % d == 0)
                check(exact[d] == row["periods"][c][depth*m//d], "least-period spectrum")
            check(sum(phi(d)*fixed[d] for d in ds) == depth*m*row["classes"][c], "Burnside count")
            bound = order_bound(depth, m, c)
            check(count % (depth*m//bound) == 0, "target-wise divisor of W")
            check(all(not value or bound % d == 0 for d, value in exact.items()),
                  "observed repetition exceeds eligible orders")
            if m > 1 and gcd(c, m) == 1:
                pair = unit_repeat_root(depth, m, c)
                exceptional = rows[depth, pair[0]]["counts"][pair[1]] if pair else 0
                check(count - exceptional == exact[1], "unit primitive count")
                check(depth*m*row["classes"][c] == count + (depth-1)*exceptional, "unit orbit count")
                units += 1
            inspected += 1
    return dict(targets=inspected, units=units)


def full_census():
    rows = {(h, n): scan(h, n, ds) for h, n, ds in domain()}
    orbits = verify_orbits(rows)
    summary = {f"L{h}_n{n}": {k: v for k, v in row.items() if k != "periods"}
               for (h, n), row in rows.items()}
    check(rows[3, 3]["counts"] == [270, 24, 0], "PR6037 depth-three count")
    check(rows[4, 2]["counts"] == [816, 0], "PR6652 depth-four count")
    check(rows[5, 2]["counts"][1] == 0, "depth-five binary obstruction")
    return dict(rows=summary, orbits=orbits,
                total_blocks=sum(r["blocks"] for r in rows.values()),
                repeated_word_checks=sum(r["repeated_word_checks"] for r in rows.values()),
                fixed_target_bins=sum(r["fixed_target_bins"] for r in rows.values()))
