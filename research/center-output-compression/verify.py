#!/usr/bin/env python3
"""Exact finite evidence for the coupled-center observation theorem.

Produced by Nick Petalas. Apache-2.0. Standard library only.
The all-field proof is in README.md; this does not replay a native supplier.
"""

from collections import Counter
from itertools import product
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows, width, p):
    require(p in (2, 3), "unsupported field")
    require(0 <= width <= 6 and len(rows) <= 12, "matrix capacity")
    require(all(len(row) == width for row in rows), "matrix shape")
    work = [[v % p for v in row] for row in rows]
    pivot = 0
    for col in range(width):
        candidates = [i for i in range(pivot, len(work)) if work[i][col]]
        if not candidates:
            continue
        index = candidates[0]
        work[pivot], work[index] = work[index], work[pivot]
        inv = pow(work[pivot][col], -1, p)
        work[pivot] = [(v * inv) % p for v in work[pivot]]
        for i in range(len(work)):
            if i != pivot:
                coefficient = work[i][col]
                work[i] = [(a - coefficient * b) % p
                           for a, b in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def dot(row, vector, p):
    require(len(row) == len(vector) <= 6, "dot shape")
    return sum(a * b for a, b in zip(row, vector)) % p


def action(rows, vector, p):
    return tuple(dot(row, vector, p) for row in rows)


def observations(p):
    """All matrices with two columns and zero, one or two rows."""
    vectors = tuple(product(range(p), repeat=2))
    for height in range(3):
        yield from product(vectors, repeat=height)


def endpoint(vector, p):
    """Two three-step chains: A=I, B=(I,0)^T, R=(0,I)."""
    a, b, c, d, u, v = vector
    return ((a + u) % p, (b + v) % p, c, d,
            (c + u) % p, (d + v) % p)


def schur_inverse_output(y, p):
    # S=I-BR, so S^-1=I+BR. This works in characteristic two as well.
    a, b, c, d = y
    return ((a + c) % p, (b + d) % p, c, d)


def target_noise(target, p):
    # S^-1 B=B in this model, so C=T S^-1 B consists of T's first columns.
    return tuple(tuple(v % p for v in row[:2]) for row in target)


def check_target_records(targets, label, zero_fiber, minimum, p):
    j = rank(label, 2, p)
    for index, target in enumerate(targets):
        noise = target_noise(target, p)
        predicted = rank(label + noise, 2, p) == j
        literal = all(not any(action(target, x, p)) for x in zero_fiber)
        require(predicted == literal, "target-specific recovery criterion")
        if literal:
            minimum[index] = min(minimum[index], j)


def check_fibers(label, inputs, p):
    fibers = {}
    zero_fiber = []
    for vector in inputs:
        result = endpoint(vector, p)
        seen = result[:4] + action(label, result[4:], p)
        fibers.setdefault(seen, set()).add(vector[:4])
        if not any(seen):
            zero_fiber.append(vector[:4])
        recovered = schur_inverse_output(result[:4], p)
        recovered = tuple((v - result[4 + i]) % p if i < 2 else v
                          for i, v in enumerate(recovered))
        require(recovered == vector[:4], "full center decoder")
    j = rank(label, 2, p)
    require(len(fibers) == p ** (4 + j), "observation image size")
    require(all(len(xs) == p ** (2 - j) for xs in fibers.values()),
            "sharp ambiguity in every observation fiber")
    require(len(zero_fiber) == p ** (2 - j), "zero fiber size")
    return len(fibers), zero_fiber


def recoverable_dimension(label, p):
    identity = tuple(tuple(int(i == j) for j in range(6)) for i in range(6))
    columns = tuple(endpoint(row, p) for row in identity)
    m_rows = tuple(zip(*columns))
    observed = m_rows[:4] + tuple(
        tuple(sum(row[i] * m_rows[4 + i][col] for i in range(2)) % p
              for col in range(6)) for row in label)
    old_rows = identity[:4]
    return 4 + rank(observed, 6, p) - rank(observed + old_rows, 6, p)


def census(p):
    targets = [(row,) for row in product(range(p), repeat=4)]
    identity = tuple(tuple(int(i == j) for j in range(4)) for i in range(4))
    targets.extend((identity, identity[:2]))
    minimum = [3] * len(targets)
    inputs = tuple(product(range(p), repeat=6))
    counts = Counter()
    strata = Counter()
    for label in observations(p):
        j = rank(label, 2, p)
        fibers, zero_fiber = check_fibers(label, inputs, p)
        check_target_records(targets, label, zero_fiber, minimum, p)
        require(recoverable_dimension(label, p) == 2 + j,
                "recoverable old-output dimension")
        strata[j] += 1
        counts["observation_matrices"] += 1
        counts["input_executions"] += len(inputs)
        counts["fibers"] += fibers
        counts["collision_witnesses"] += len(zero_fiber) - 1
        counts["target_tests"] += len(targets)
    for target, best in zip(targets, minimum):
        require(best == rank(target_noise(target, p), 2, p),
                "minimum center observations for target")
    counts["targets"] = len(targets)
    return {"field": p, **dict(counts), "rank_strata": dict(sorted(strata.items()))}


def rejection_controls():
    controls = 0
    zero = (0,) * 6
    collision = (1, 0, 0, 0, 1, 0)
    require(endpoint(zero, 2)[:4] == endpoint(collision, 2)[:4], "collision")
    require(zero[:4] != collision[:4], "old output changes")
    false_claims = (
        (recoverable_dimension((), 2) == 4, "no-record full recovery"),
        (recoverable_dimension(((1, 0),), 2) == 4, "one-record full recovery"),
        (rank(((1, 0), (1, 0)), 2, 2) == 2, "duplicate record rank"),
        (endpoint(collision, 2)[4:] == (0, 0), "discard dirty center outputs"),
        (target_noise(((0, 0, 1, 0),), 2) == ((1, 0),),
         "every target needs all centers"),
    )
    for claim, message in false_claims:
        try:
            require(claim, message)
        except ValueError:
            controls += 1
        else:
            raise ValueError("accepted false claim: " + message)
    for rows, width, p in ((((1, 0),), 3, 2), (((1,),), 1, 5)):
        try:
            rank(rows, width, p)
        except ValueError:
            controls += 1
        else:
            raise ValueError("accepted malformed matrix or unsupported field")
    return controls


def main():
    result = {"claim_type": "scoped proof with finite corroboration",
              "censuses": [census(p) for p in (2, 3)],
              "rejection_controls": rejection_controls(),
              "application": {"old_dimension": 632, "center_dimension": 8,
                              "recoverable_by_observation_rank":
                              {str(j): 624 + j for j in range(9)}}}
    print(json.dumps(result, sort_keys=True))
    print("PASS_CENTER_OUTPUT_COMPRESSION")


if __name__ == "__main__":
    main()
