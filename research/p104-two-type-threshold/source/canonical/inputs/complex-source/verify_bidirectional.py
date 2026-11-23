"""Rebuild the rational circuit and replay its scalar map and caller tariff."""
import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
from graphlib import TopologicalSorter
from math import gcd, lcm
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_component import canonical, check, check_decrease, expected_columns, factor, inspect, margin, read


@cache
def rational(text):
    return Fraction(text)


def reconstruct(parent, delta):
    check(canonical(parent) == delta["parent"], "parent word")
    moves = {k: (a, b) for k, a, b in parent["moves"]}
    forms = {k: dict(row) for k, row in parent["forms"]}
    for k in delta["removed"]:
        del moves[k], forms[k]
    for k, a, b in delta["moves"]:
        check(k not in forms, "new transfer label")
        moves[k], forms[k] = (a, b), {}

    differences = {}
    literals = {}
    for k, kind, entries in delta["differences"]:
        check(k not in differences and k in forms, "changed coefficient row")
        weights = {j: rational(s) for j, s in entries}
        check(len(weights) == len(entries) and all(weights.values()), "distinct nonzero weights")
        if kind == "add":
            change = weights
            literals[k] = change
        else:
            check(kind == "combine", "difference format")
            change = {}
            for j, weight in weights.items():
                for donor, value in literals[j].items():
                    change[donor] = change.get(donor, 0) + weight * value
            change = {j: v for j, v in change.items() if v}
        differences[k] = len(change)
        row = forms[k]
        for j, v in change.items():
            coefficient = rational(row.get(j, "0")) + v
            if coefficient:
                row[j] = str(coefficient)
            else:
                del row[j]
    deps = {k: tuple(j for j in sorted(row) if j >= 0) for k, row in sorted(forms.items())}
    word = dict(parent, forms=[[k, sorted(row.items())] for k, row in sorted(forms.items())],
                moves=[[k, a, b] for k, (a, b) in sorted(moves.items())],
                schedule=list(TopologicalSorter(deps).static_order()))
    check(canonical(word) == delta["word"], "reconstructed word")
    return word, sum(differences.values())


def forward(word, layout):
    """Check all terminal rows. Find the smallest grid that contains every scalar product."""
    n, first = len(word["initial"]), word["first_output"]
    columns, _ = expected_columns(layout, n)
    want = [{} for _ in range(n)]
    for i, column in enumerate(columns):
        for j, fraction in column.items():
            want[j][i] = Fraction(*fraction)
    rows = dict(word["forms"])
    stock = {~i: ({i: 1}, 1, 1) for i in range(n)}
    uses = Counter(j for row in rows.values() for j, _ in row)
    grid = literal_bits = 1
    products = 0
    for k in word["schedule"]:
        terms = []
        divisor = 1
        for j, s in rows[k]:
            num, den = factor(s)
            literal_bits = max(literal_bits, num.bit_length(), den.bit_length())
            values, source_den, content = stock[j]
            total_den = den * source_den
            grid = lcm(grid, total_den // gcd(total_den, num * content))
            terms.append((values, num, total_den))
            divisor = lcm(divisor, total_den)
            uses[j] -= 1
            if not uses[j]:
                del stock[j]
        result = {}
        for values, num, den in terms:
            products += len(values)
            multiple = num * (divisor // den)
            for i, v in values.items():
                result[i] = result.get(i, 0) + multiple * v
        result = {i: v for i, v in result.items() if v}
        if first <= k < first + n:
            check(result.keys() == want[k-first].keys() and
                  all(v == divisor * want[k-first][i] for i, v in result.items()), f"terminal row {k-first}")
        else:
            content = gcd(*result.values())
            common = gcd(content, divisor)
            stock[k] = ({i: v // common for i, v in result.items()}, divisor // common, content // common)
    return products, grid, literal_bits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quotient", action="store_true", help="check the four-term quotient on the rebuilt parent")
    args = parser.parse_args()
    parent = read("WORD.json.gz")
    check(canonical(parent) == read("RATIONAL-RECEIPT.json")["word"], "initial word")
    prefix = "BIDIRECTIONAL"
    if args.quotient:
        parent, _ = reconstruct(parent, read("BIDIRECTIONAL.json.gz"))
        check(canonical(parent) == read("BIDIRECTIONAL-RECEIPT.json")["new_word"], "intermediate word")
        prefix = "BIDIRECTIONAL-QUOTIENT"
    verify_step(parent, prefix)


def verify_step(parent, prefix, layout=None):
    delta = read(prefix + ".json.gz")
    receipt = read(prefix + "-RECEIPT.json")
    word, edits = reconstruct(parent, delta)
    check(delta["word"] == receipt["new_word"] and len(word["moves"]) == receipt["moves"], "word and charge count")
    check(len(parent["moves"]) == receipt["old_moves"] and len(delta["removed"]) == receipt["retired"]
          and len(delta["moves"]) == receipt["new_moves"], "changed transfers")
    check(edits == receipt["coefficient_edits"] and len(delta["differences"]) == receipt["changed_rows"],
          "coefficient count")
    check_circuit(word, receipt, read("LAYOUT.json.gz") if layout is None else layout)
    return word


def check_circuit(word, receipt, layout):
    work, grid, bits = forward(word, layout)
    check([work, grid, bits] == [receipt["forward_terms"], int(receipt["minimum_product_grid"]),
                                 receipt["literal_peak_bits"]], "forward precision and work")
    paid, targets, adjoint = inspect(word, layout, read("CALLER-CENSUS.json"))
    check(adjoint == receipt["adjoint_terms"] and len(word["initial"]) == receipt["public"], "adjoint census")
    for name, bins in (("paid", paid), ("productive", targets)):
        check({str(k): v for k, v in bins.items()} == receipt[name], name)
    lower, upper = [Fraction(v, 10**14) for v in receipt["crossing_e14"]]
    check(margin(paid, targets, lower)[0] > 0 and margin(paid, targets, upper)[1] < 0, "crossing signs")
    check_decrease(paid, targets)
    lo, hi = margin(paid, targets, receipt["trial"])
    a, b = map(Fraction, receipt["trial_margin"])
    check(a <= lo <= hi <= b < 0, "trial margin")
    print(f"PASS {len(word['moves'])} transfers, {work} forward products, {adjoint} adjoint terms, "
          f"{len(word['initial'])} independent fields and both crossing signs")


if __name__ == "__main__":
    main()
