"""Check the rational graph over every input and price its 48 calls."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from hashlib import sha256
from math import gcd, isqrt, lcm
from pathlib import Path
import gzip
import json


ROOT = Path(__file__).resolve().parent
SCALE = 1 << 192


def check(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    raw = (ROOT / name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)


def canonical(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@cache
def factor(text):
    value = Fraction(text)
    return value.numerator, value.denominator


def frame_span(basis):
    points = {0}
    for vector in basis:
        check(0 < vector < 512 and vector not in points, "invalid frame basis")
        points.update([old ^ vector for old in points])
    return points


def expected_columns(layout, n):
    expected = [{i: (1, 1)} for i in range(n)]
    main = set()
    hosted = layout["hosted"]
    for port, x in enumerate(layout["live"]):
        y = x + 112
        main.update((x, y))
        if port in hosted["Dports"]:
            expected[x][y] = (1, 1)
        else:
            expected[x][y] = (1, 2)
            expected[y] = {x: (-1, 1), y: (1, 2)}
    for x, y in zip(hosted["X2"], hosted["Y2"], strict=True):
        main.update((x, y))
        expected[y][x] = (-1, 1)
    check(len(main) == 400, "main role count")
    return expected, main


def inspect(word, layout, caller):
    starts, ends = word["initial"], word["final"]
    n = len(starts)
    check(len(ends) == n == layout["public"] == len(layout["source_labels"]), "endpoint count")
    check(word["frames"] == layout["frames"], "layout frames")
    expected, main = expected_columns(layout, n)
    rank = [len(f) for f in word["frames"]]
    spans = list(map(frame_span, word["frames"]))
    moves = {k: (a, b) for k, a, b in word["moves"]}
    graph = dict(word["forms"])
    order = word["schedule"]
    first = word["first_output"]
    outputs = set(range(first, first + n))
    check(len(moves) == len(word["moves"]) and moves.keys().isdisjoint(outputs), "paid labels")
    check(len(order) == len(graph) == len(word["forms"]), "row count")
    check(set(order) == graph.keys() == moves.keys() | outputs, "schedule coverage")

    def grade(a, b):
        check(spans[a] < spans[b] or spans[b] < spans[a], "strictly nested charts")
        return abs(rank[b] - rank[a])

    calls = caller["calls"]
    paid = Counter({int(k): v for k, v in caller["fixed_caller_paid"].items()})
    targets = Counter({int(k): v for k, v in caller["fixed_root_targets"].items()})
    for i, (a, b) in enumerate(zip(starts, ends, strict=True)):
        if i not in main:
            targets[grade(a, b)] += calls

    bank = {~i: a for i, a in enumerate(starts)}
    consumers = defaultdict(list)
    for k in order:
        a = moves[k][0] if k in moves else ends[k - first]
        for donor, text in graph[k]:
            check(bank[donor] == a, f"donor chart at {k}")
            num, den = factor(text)
            consumers[donor].append((k, num, den))
        if k in moves:
            a, b = moves[k]
            paid[grade(a, b)] += calls
            bank[k] = b

    # Store a common positive denominator for every sparse adjoint row.
    back = {first + i: ({i: 1}, 1) for i in range(n)}
    terms = 0
    keys = [k for k in reversed(order) if k in moves] + [~i for i in range(n)]
    for k in keys:
        users = consumers[k]
        common = lcm(*(den * back[j][1] for j, num, den in users))
        row = {}
        for j, num, den in users:
            values, divisor = back[j]
            scale = num * (common // (den * divisor))
            for i, value in values.items():
                row[i] = row.get(i, 0) + scale * value
            terms += len(values)
        divisor = gcd(common, *row.values())
        back[k] = ({i: v // divisor for i, v in row.items() if v}, common // divisor)
    for i, want in enumerate(expected):
        row, divisor = back[~i]
        check(row.keys() == want.keys(), f"column support at {i}")
        check(all(v * want[j][1] == divisor * want[j][0] for j, v in row.items()), f"column {i}")
    return paid, targets, terms


def price(rank, saving):
    # Enclose rank**saving by successive integer square roots. Each bit
    # selects the next positive root. The last root bounds the full tail.
    lo = hi = rank * SCALE
    product_lo = product_hi = SCALE
    rem = Fraction(saving)
    for _ in range(152):
        lo = isqrt(lo * SCALE)
        hi = 1 + isqrt(hi * SCALE - 1)
        rem *= 2
        if rem >= 1:
            rem -= 1
            product_lo = product_lo * lo // SCALE
            product_hi = (product_hi * hi + SCALE - 1) // SCALE
    if rem:
        product_hi = (product_hi * hi + SCALE - 1) // SCALE
    mass = rank * SCALE * SCALE
    return mass // product_hi, (mass + product_lo - 1) // product_lo


def margin(paid, targets, saving):
    lo = hi = 0
    for rank in targets.keys() | paid.keys():
        count = targets[rank] - paid[rank]
        a, b = price(rank, saving)
        lo += min(count * a, count * b)
        hi += max(count * a, count * b)
    return Fraction(lo, SCALE), Fraction(hi, SCALE)


def check_decrease(paid, targets):
    # Bound the derivative divided by ln(2) from above on [0, 0.004].
    derivative = 0
    for rank in paid.keys() | targets.keys():
        count = targets[rank] - paid[rank]
        if count > 0:
            derivative -= count * (rank.bit_length() - 1) * price(rank, "0.004")[0]
        else:
            derivative -= count * (rank - 1).bit_length() * rank * SCALE
    check(derivative < 0, "strict decrease on the comparison interval")


def main():
    word = read("WORD.json.gz")
    layout = read("LAYOUT.json.gz")
    receipt = read("RATIONAL-RECEIPT.json")
    check(canonical(word) == receipt["word"] == read("EVENTS.json")["canonical_sha256"], "word pin")
    check(canonical(layout) == read("EVENTS.json")["child_layout_sha256"], "layout pin")
    paid, targets, terms = inspect(word, layout, read("CALLER-CENSUS.json"))
    check(terms == receipt["adjoint_terms"] and len(word["initial"]) == receipt["public"], "adjoint census")
    for name, bins in (("paid", paid), ("productive", targets)):
        check({str(k): v for k, v in bins.items()} == receipt[name], name)
    lower, upper = map(Fraction, receipt["crossing"])
    check(margin(paid, targets, lower)[0] > 0 and margin(paid, targets, upper)[1] < 0, "crossing signs")
    check_decrease(paid, targets)
    probe = margin(paid, targets, "0.00391884648")
    left, right = map(Fraction, receipt["target_margin"])
    check(left <= probe[0] <= probe[1] <= right < 0, "target interval")
    print(f"PASS {receipt['public']} columns, {terms} adjoint terms, both crossing signs and the target deficit")


if __name__ == "__main__":
    main()
