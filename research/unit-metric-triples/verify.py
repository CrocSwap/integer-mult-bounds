"""Exact finite corroboration of the unit-triple theorem; no source imports.

Produced by Nick Petalas. Apache-2.0.
"""

import argparse
from fractions import Fraction as F
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import platform

import metric


def check(condition, message):
    if not condition:
        raise ValueError(message)


def literal_normalization(p, w):
    """Construct actual normalized rational factors rather than anchor shortcuts."""
    q = tuple(tuple(w[j] * row[j] for j in range(3)) for row in p)
    active = tuple(j for j in range(3) if any(row[j] for row in p))
    mins_p = {j: min(metric.valuation(row[j]) for row in p if row[j]) for j in active}
    mins_q = {j: min(metric.valuation(row[j]) for row in q if row[j]) for j in active}
    gamma = min(mins_p[j] + mins_q[j] for j in active)
    left = tuple(tuple(row[j] / F(2) ** mins_p[j] if j in active else F(0)
                       for j in range(3)) for row in p)
    right = tuple(tuple(row[j] * F(2) ** (mins_p[j] - gamma) if j in active else F(0)
                        for j in range(3)) for row in q)
    a = tuple(sum(1 << j for j, x in enumerate(row) if x.numerator % 2) for row in left)
    b = tuple(sum(1 << j for j, x in enumerate(row) if x.numerator % 2) for row in right)
    check((a, b, gamma) == metric.anchors(p, w), "literal canonical anchor disagreement")
    return a, b, left, right


def literal_witness(p, w, order, labels):
    a, b, left, right = literal_normalization(p, w)
    check(len(order) == len(labels) == len(set(order)), "witness length or duplicate")
    for index, i in enumerate(order):
        x, y = labels[index]
        check(0 < x < 8 and 0 < y < 8 and x & a[i] == x and y & b[i] == y,
              "literal supported label")
        diagonal = sum(((x >> j) & 1) * ((y >> j) & 1) for j in range(3)) % 2
        check(diagonal == 1, "literal self pairing")
        for later in range(index + 1, len(order)):
            k = order[later]
            value = sum(left[i][j] * right[k][j] for j in range(3))
            pairing = sum(((x >> j) & 1) * ((labels[later][1] >> j) & 1)
                          for j in range(3)) % 2
            check(value != 0 or pairing == 0, "literal forward zero")
    return len(order)


def positive_factors():
    fixtures = []
    for deltas in ((0, 0, 0), (0, 1, 2), (1, 0, 3), (2, 3, 0)):
        for common in (-3, 0, 2):
            p = tuple(tuple(F(row[j]) * F(2) ** (common + deltas[j]) for j in range(3))
                      for row in product((0, 1, -1), repeat=3)
                      if any(row[j] and deltas[j] == 0 for j in range(3)))
            fixtures.append(metric.rows(p))
    fixtures.extend((metric.rows(((1, 0, 0), (-1, 0, 0), (3, 0, 0))),
                     metric.rows(((1, 1, 0), (1, -1, 0), (3, 1, 0))),
                     metric.rows(((F(1, 3), 1, 2), (1, F(-1, 5), 4), (3, 1, 0)))))
    return tuple(fixtures)


def check_positive(w):
    count, rows_checked = 0, 0
    for p in positive_factors():
        order, labels = metric.witness(w, p)
        check(len(order) == len(p), "positive witness omitted a row")
        rows_checked += literal_witness(p, w, order, labels)
        count += 1
    return count, rows_checked


def check_negative(w):
    p, order, labels = metric.obstruction(w)
    literal_witness(p, w, order, labels)
    a, b, _, _ = literal_normalization(p, w)
    check(a == b and all(x == a[0] for x in a[:3]) and a[0].bit_count() == 2,
          "two-coordinate orthogonal core")
    m = metric.gram(p, w)
    check(all(m[i][j] == 0 for i in range(3) for j in range(3) if i != j),
          "core is not orthogonal")
    check(all(m[i][i] > 0 for i in range(4)), "nonpositive diagonal")
    histogram, attempts = metric.exact_histogram(p, w)
    check(histogram == (1, 24, 288, 1296, 0), "literal box histogram changed")
    check(attempts == 36745, "enumerated assignment count changed")
    return attempts


def rejection_controls():
    count = 0
    for bad in ((1, 1), (1, 1, 0), (1, -1, 1), (1, 2, 1), (1, F(1, 2), 1),
                (True, 1, 1), (1.0, 1, 1), (1, 1, F((1 << 129) + 1))):
        try:
            metric.weights(bad)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid metric accepted")
    for bad in ((), ((0, 0, 0),), ((1, 2),), ((1.0, 0, 0),),
                ((1 << 1025, 0, 0),), ((1, 0, 0),) * 65):
        try:
            metric.rows(bad)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid factor accepted")
    for w, p in (((1, 3, 5), ((1, 0, 0),)),
                 ((1, 5, 9), ((1, 0, 0), (0, 2, 0)))):
        try:
            metric.witness(w, p)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid full-witness contract accepted")
    w = metric.weights((1, 3, 5))
    p, order, labels = metric.obstruction(w)
    wrong = ((1, 1), (1, 1), (1, 1))
    check(not metric.accepts(p, w, order, wrong), "wrong zero pairing accepted")
    check(not metric.accepts(p, w, (0, 0, 3), labels), "duplicate row accepted")
    check(not metric.accepts(p, w, order, ((4, 4),) + labels[1:]), "unsupported label accepted")
    check(not metric.accepts(p, w, order, ((True, 1),) + labels[1:]), "Boolean label accepted")
    check(not metric.universal((1, 3, 5)) and metric.universal((3, 7, 11)),
          "residue-pattern distinction")
    return count + 5


def run():
    values = (F(1), F(3), F(5), F(7), F(1, 3), F(3, 7))
    positive = negative = witnesses = witness_rows = attempts = 0
    for entry in product(values, repeat=3):
        w = metric.weights(entry)
        if metric.universal(w):
            positive += 1
            n, r = check_positive(w)
            witnesses += n
            witness_rows += r
        else:
            negative += 1
            attempts += check_negative(w)
    check(positive + negative == 216 and positive == 54, "unit-triple enumeration")
    for order in permutations(range(3)):
        w = tuple(F((1, 3, 5)[j]) for j in order)
        p, _, _ = metric.obstruction(w)
        check(metric.exact_histogram(p, w)[0][-1] == 0, "permuted full obstruction")
    w = metric.weights((1, 3, 5))
    p, _, _ = metric.obstruction(w)
    check(metric.gram(p, w) == ((4, 0, 0, 1), (0, 32, 0, 13),
                               (0, 0, F(96, 5), -3), (1, 13, -3, 6)),
          "displayed independent-third-weight example")
    return {"metric_triples": 216, "universal_triples": positive,
            "obstructed_triples": negative, "full_witnesses": witnesses,
            "full_witness_rows": witness_rows,
            "negative_ordered_label_assignments": attempts,
            "additional_permutations": 6, "controls": rejection_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="exclusively create an external receipt")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if args.receipt is not None:
        destination = args.receipt.resolve()
        check(root not in destination.parents and destination != root, "receipt must be external")
    result = run()
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "metric.py", "verify.py")
    result["sha256"] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                        for name in files}
    result["python"] = platform.python_version()
    result["status"] = "PASS_UNIT_METRIC_TRIPLES"
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        with args.receipt.open("x", encoding="utf-8") as stream:
            check(stream.write(payload) == len(payload), "short receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
