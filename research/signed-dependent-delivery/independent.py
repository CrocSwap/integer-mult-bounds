#!/usr/bin/env python3
"""Independent exact signed-state checks; imports no package implementation.

Apache-2.0. Prepared with OpenAI Codex assistance for Ross Richardson.

Run from any directory with Python 3.  Dijkstra states retain every coefficient
of connector dirt and independent source inputs in the current delivered output.
Rational matrices are embedded in an integer coefficient lattice by one common
denominator.  This is an exact change of units, not a modular reduction.
"""

from fractions import Fraction
from heapq import heappop, heappush
from itertools import product
from math import gcd
from collections import Counter
import hashlib
import json
import time


def require(condition, message):
    """A verification gate that remains active under Python's -O option."""
    if not condition:
        raise ValueError(str(message))


def integer_rows(matrix):
    rows = tuple(tuple(Fraction(x) for x in row) for row in matrix)
    require(rows and rows[0], "nonempty source matrix required")
    require(all(len(row) == len(rows[0]) and any(row) for row in rows),
            "source rows must have equal width and be nonzero")
    denominator = 1
    for row in rows:
        for entry in row:
            denominator = denominator * entry.denominator // gcd(
                denominator, entry.denominator
            )
    return tuple(tuple(int(x * denominator) for x in row) for row in rows)


def signed_state_optimum(matrix, readers, sources, *, state_cap=1000000):
    """Search all signed words of price at most the closed-echo price.

    State (epoch, q, alpha, r) denotes
      z = z0 + B sum_j q_j v_j / D,
      y_epoch = y0 + alpha A z0 + A B sum_j r_j v_j / D.
    A delivery edge exists only at alpha=0, r=M_epoch.  Old delivered outputs
    cannot be written in later epochs.  Every A+/A-/B+/B- edge is admitted.
    """
    rows = integer_rows(matrix)
    k, d = len(rows), len(rows[0])
    a, b = tuple(readers), tuple(sources)
    require(len(a) == len(b) == k, "tariff shape mismatch")
    require(all(isinstance(x, (int, Fraction)) and x > 0 for x in a + b),
            "prices must be positive exact integers or fractions")
    bound = 2 * sum(a) + 2 * sum(b)
    zero = (0,) * d
    start = (0, zero, 0, zero)
    heap, distances = [(0, start)], {start: 0}
    popped = 0
    # Every untouched future epoch needs two signed readers to cancel its
    # independent dirt, and at least one B query to make its connector vary.
    future = [0] * k
    for i in range(k - 2, -1, -1):
        future[i] = future[i + 1] + 2 * a[i + 1] + b[i + 1]

    def offer(cost, state):
        epoch, _, alpha, _ = state
        if cost + future[epoch] + abs(alpha) * a[epoch] > bound:
            return
        if cost < distances.get(state, bound + 1):
            distances[state] = cost
            heappush(heap, (cost, state))

    while heap:
        cost, state = heappop(heap)
        if distances[state] != cost:
            continue
        popped += 1
        if len(distances) > state_cap:
            raise RuntimeError("independent search state cap exceeded")
        i, q, alpha, r = state
        if alpha == 0 and r == rows[i]:
            if i == k - 1 and q == zero:
                return cost, popped, len(distances)
            if i < k - 1:
                offer(cost, (i + 1, q, 0, zero))
        for sign in (-1, 1):
            offer(cost + b[i], (
                i, tuple(x + sign * y for x, y in zip(q, rows[i])), alpha, r
            ))
            offer(cost + a[i], (
                i, q, alpha + sign,
                tuple(x + sign * y for x, y in zip(r, q))
            ))
    raise ValueError("closed echo was not reached")


def lattice_bill(matrix, readers, sources):
    """Independent finite enumeration of all improving integer kernel vectors."""
    rows = integer_rows(matrix)
    baseline = 2 * sum(sources)
    ranges = [range(-int(baseline // b), int(baseline // b) + 1) for b in sources]
    best, witness, candidates = baseline, (0,) * len(rows), 0
    for t in product(*ranges):
        if any(sum(t[i] * rows[i][j] for i in range(len(rows)))
               for j in range(len(rows[0]))):
            continue
        candidates += 1
        bill = sum(b * (abs(x) if x else 2) for b, x in zip(sources, t))
        if bill < best:
            best, witness = bill, t
    return 2 * sum(readers) + best, witness, candidates


def literal_word(net):
    """Produce the claimed local construction; signs are literal integers."""
    word = []
    for i, t in enumerate(net):
        sign = 1 if t >= 0 else -1
        word.extend(((i, "A", -sign), (i, "B", sign), (i, "A", sign)))
        if t == 0:
            word.append((i, "B", -1))
        else:
            word.extend((i, "B", sign) for _ in range(abs(t) - 1))
    return word


def exact_literal_map(matrix, word, *, require_delivery=True):
    """Propagate arbitrary dirt and independent source coefficients exactly.

    Every register is a coefficient vector on basis (z0,v_0,...,v_(d-1)).
    Output's own independent dirt is unchanged by grammar and omitted.  The
    target increment contains no z0 coefficient.  The result checks both the
    terminal map and, separately, every request boundary.
    """
    rows = tuple(tuple(Fraction(x) for x in row) for row in matrix)
    k, d = len(rows), len(rows[0])
    z = [Fraction(1)] + [Fraction(0)] * d
    ys = [[Fraction(0)] * (d + 1) for _ in rows]
    current = 0
    delivered = []
    for i, kind, sign in word:
        require(0 <= i < k and kind in ("A", "B") and sign in (-1, 1),
                "invalid literal query")
        if require_delivery:
            if i < current:
                return False
            while current < i:
                delivered.append(tuple(ys[current]) == (0,) + rows[current])
                current += 1
        if kind == "B":
            for j in range(d):
                z[j + 1] += sign * rows[i][j]
        else:
            for j in range(d + 1):
                ys[i][j] += sign * z[j]
    if require_delivery:
        while current < k:
            delivered.append(tuple(ys[current]) == (0,) + rows[current])
            current += 1
    expected = tuple((0,) + row for row in rows)
    return (tuple(z) == (1,) + (0,) * d and tuple(map(tuple, ys)) == expected
            and (all(delivered) if require_delivery else True))


def literal_inverse_cancels(matrix, word):
    """Check the complete word followed by its reversed sign-negated inverse."""
    rows = tuple(tuple(Fraction(x) for x in row) for row in matrix)
    k, d = len(rows), len(rows[0])
    # z0, all independent v, all independent output dirt.  This is a full
    # symbolic basis for the scalar specialization, not a zero-dirt trial.
    n = 1 + d + k
    z = [Fraction(int(j == 0)) for j in range(n)]
    ys = [[Fraction(int(j == 1 + d + i)) for j in range(n)] for i in range(k)]
    initial_z, initial_ys = tuple(z), tuple(map(tuple, ys))
    inverse = [(i, kind, -sign) for i, kind, sign in reversed(word)]
    for i, kind, sign in list(word) + inverse:
        if kind == "B":
            for j in range(d):
                z[1 + j] += sign * rows[i][j]
        else:
            for j in range(n):
                ys[i][j] += sign * z[j]
    return tuple(z) == initial_z and tuple(map(tuple, ys)) == initial_ys


def run():
    cases = [
        ("one", ((1,),), (1,), (1,)),
        ("same", ((1,), (1,)), (1, 1), (1, 1)),
        ("opposite", ((1,), (-1,)), (1, 1), (1, 1)),
        ("dependent_scale", ((1,), (2,)), (1, 1), (1, 1)),
        ("independent", ((1, 0), (0, 1)), (1, 1), (1, 1)),
        ("triangle", ((1, 0), (0, 1), (1, 1)), (1, 1, 1), (1, 1, 1)),
        ("arithmetic_progression", ((1, 0), (1, 1), (1, 2)),
         (1, 1, 1), (1, 1, 1)),
        ("rational", ((Fraction(1, 2),), (Fraction(3, 2),)),
         (1, 1), (1, 1)),
        ("priced_middle", ((1, 0), (1, 1), (1, 2)),
         (1, 1, 1), (1, 2, 1)),
        ("priced_readers", ((1, 0), (0, 1), (1, 1)),
         (2, 1, 1), (1, 1, 1)),
    ]
    records = []
    started = time.monotonic()
    def check(name, matrix, a, b):
        expected, net, kernels = lattice_bill(matrix, a, b)
        actual, popped, seen = signed_state_optimum(matrix, a, b)
        require(actual == expected, (name, actual, expected))
        word = literal_word(net)
        require(exact_literal_map(matrix, word), name + " literal map mismatch")
        require(literal_inverse_cancels(matrix, word), name + " inverse mismatch")
        require(sum(a[i] if kind == "A" else b[i] for i, kind, _ in word) == actual,
                name + " literal price mismatch")
        return dict(case=name, optimum=str(actual), net=net,
                    popped=popped, states=seen, kernel_vectors=kernels)

    for name, matrix, a, b in cases:
        records.append(check(name, matrix, a, b))

    families = []
    for k in (1, 2, 3):
        tariffs = (
            ((1,) * k, (1,) * k),
            ((1, 2, 1)[:k], (2, 1, 3)[:k]),
            ((Fraction(3, 2), 1, Fraction(5, 4))[:k],
             (Fraction(1, 2), Fraction(3, 2), 1)[:k]),
        )
        for slopes in product((0, 1, 2), repeat=k):
            matrix = tuple((1, s) for s in slopes)
            for tariff, (a, b) in enumerate(tariffs):
                name = "slopes_" + "".join(map(str, slopes)) + "_tariff_" + str(tariff)
                families.append(check(name, matrix, a, b))
    require(len(families) == 117, "slope family coverage mismatch")
    scaled = [
        ("common_half", ((Fraction(1, 2), 0),
                          (Fraction(1, 2), Fraction(1, 2)),
                          (Fraction(1, 2), 1))),
        ("individual_half", ((Fraction(1, 2), 0), (1, 1),
                              (Fraction(1, 2), 1))),
        ("mixed_denominators", ((Fraction(1, 2), Fraction(1, 3)),
                                (Fraction(1, 2), Fraction(2, 3)),
                                (Fraction(1, 2), 1))),
    ]
    scaled_records = [check(name, matrix, (1, 1, 1), (1, 1, 1))
                      for name, matrix in scaled]

    def statistics(values):
        return dict(cases=len(values), popped=sum(x["popped"] for x in values),
                    total_states=sum(x["states"] for x in values),
                    max_states=max(x["states"] for x in values),
                    optima=dict(sorted(Counter(x["optimum"] for x in values).items())),
                    records_sha256=hashlib.sha256(
                        json.dumps(values, sort_keys=True).encode()).hexdigest())

    matrix = ((1, 0), (1, 1), (1, 2))
    word = literal_word((1, -2, 1))
    require(exact_literal_map(matrix, word), "progression literal map mismatch")
    # The parity kernel (1,0,1) is valid mod 2 but not over Q: its exact
    # residual is (2,2).  A mod-two readout sign collapse would conceal it.
    parity_net = (1, 0, 1)
    require(all(sum(parity_net[i] * matrix[i][j] for i in range(3)) % 2 == 0
                for j in range(2)), "binary kernel control setup mismatch")
    require(not exact_literal_map(matrix, literal_word(parity_net)),
            "binary-only kernel defect survived")
    # Distinct defects test terminal dirt, product sign and restoration.
    require(not exact_literal_map(matrix, word[1:]), "omitted reader defect survived")
    wrong = list(word)
    i, kind, sign = wrong[1]
    wrong[1] = (i, kind, -sign)
    require(not exact_literal_map(matrix, wrong), "source-sign defect survived")
    # Middle epoch's two negative B calls have the same sign; replacing the
    # second one by its inverse breaks exact restoration.
    middle_b = [n for n, event in enumerate(word) if event[:2] == (1, "B")]
    require(len(middle_b) == 2 and word[middle_b[0]][2] == word[middle_b[1]][2],
            "same-sign middle source control setup mismatch")
    wrong = list(word)
    i, kind, sign = wrong[middle_b[1]]
    wrong[middle_b[1]] = (i, kind, -sign)
    require(not exact_literal_map(matrix, wrong), "middle-source inverse defect survived")
    # Adjacent readers commute algebraically, yet moving epoch 0's last
    # reader past epoch 1's first reader misses epoch 0's delivery cut.
    delayed = list(word)
    delayed[2], delayed[3] = delayed[3], delayed[2]
    require(exact_literal_map(matrix, delayed, require_delivery=False),
            "delayed reader control must preserve the endpoint")
    require(not exact_literal_map(matrix, delayed), "delayed reader defect survived")
    print(json.dumps(dict(checker="independent signed full-state Dijkstra",
                          benchmarks=records, slope_family=statistics(families),
                          rational_scalings=scaled_records,
                          all_cases=statistics(records + families + scaled_records),
                          defect_controls=5,
                          elapsed_seconds=round(time.monotonic() - started, 4)),
                     indent=2))


if __name__ == "__main__":
    run()
