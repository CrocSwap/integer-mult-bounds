#!/usr/bin/env python3
"""Exact complete sign-family certificate. Standard library, no file writes."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


CUT_MAXIMA = [F(2601, 2048)] * 5 + [F(21, 16)] * 4 + [F(85, 64)] + [F(23, 16)] * 11


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity():
    return [[F(i == j) for j in range(8)] for i in range(8)]


def multiply(a, b):
    return [[sum((a[i][k] * b[k][j] for k in range(8)), F(0))
             for j in range(8)] for i in range(8)]


def norm(a):
    return max(sum(map(abs, row), F(0)) for row in a)


def split(symbol):
    require(len(symbol) in (2, 4, 8) and symbol[0] == 1, "bad node")
    even, odd = symbol[::2], symbol[1::2]
    m = len(even)
    quotient = [F(0)] * m
    for j in range(m):
        quotient[j] = odd[j] - sum(
            (even[k] * quotient[j-k] for k in range(1, j+1)), F(0))
    schur = even.copy()
    for j in range(1, m):
        schur[j] -= sum((odd[k] * quotient[j-1-k] for k in range(j)), F(0))
    require(schur[0] == even[0] == 1, "constant term changed")
    return even, schur, quotient


def compile_symbol(symbol, wrong_sign=False):
    """Breadth-first split, then bottom-up assemble the fixed 15-node tree."""
    require(len(symbol) == 8 and symbol[0] == 1, "bad root")
    nodes = {1: (list(range(8)), list(symbol))}
    quotients = {}
    for node in range(1, 8):
        indices, current = nodes[node]
        even, schur, quotient = split(current)
        nodes[2*node] = (indices[::2], even)
        nodes[2*node+1] = (indices[1::2], schur)
        quotients[node] = quotient
    words = {node: [identity()] for node in range(8, 16)}
    for node in range(7, 0, -1):
        indices, _ = nodes[node]
        evens, odds = indices[::2], indices[1::2]
        m = len(evens)
        upper, lower = identity(), identity()
        quotient = quotients[node]
        for i in range(m):
            for j in range(i+1):
                lower[odds[i]][evens[j]] = quotient[i-j]
                if i > j:
                    upper[evens[i]][odds[j]] = quotient[i-j-1]
        if wrong_sign and node == 1:
            lower[1][0] *= -1
        words[node] = [upper] + words[2*node] + words[2*node+1] + [lower]
    require(len(words[1]) == 22, "wrong schedule length")
    return words[1]


def toeplitz(symbol):
    return [[symbol[i-j] if i >= j else F(0) for j in range(8)]
            for i in range(8)]


def execute(symbol, factors):
    require(len(factors) == 22, "missing macro")
    state = identity()
    prefix_norms = []
    for step in range(22):
        state = multiply(factors[step], state)
        if step < 21:
            prefix_norms.append(norm(state))
    require(state == toeplitz(symbol), "wrong endpoint")
    return prefix_norms


def census():
    rows = []
    for signs in product((-1, 1), repeat=7):
        symbol = [F(1), F(signs[0], 8)] + [F(s, 16) for s in signs[1:]]
        require(sum(map(abs, symbol[1:]), F(0)) == F(1, 2), "tail budget")
        values = execute(symbol, compile_symbol(symbol))
        rows.append({"signs": list(signs), "maximum": str(max(values)),
                     "prefix_norms": list(map(str, values))})
    require(len(rows) == 128, "incomplete sign domain")
    return rows


def check_census(rows):
    require(len(rows) == 128, "incomplete sign domain")
    domain = set(product((-1, 1), repeat=7))
    require({tuple(row["signs"]) for row in rows} == domain, "wrong sign domain")
    for row in rows:
        values = list(map(F, row["prefix_norms"]))
        require(len(values) == 21, "incomplete cut domain")
        require(max(values) == F(row["maximum"]) == F(23, 16), "wrong maximum")
        require(values.index(F(23, 16)) == 10, "wrong first attaining cut")
    maxima = [max(F(row["prefix_norms"][j]) for row in rows) for j in range(21)]
    require(maxima == CUT_MAXIMA, "wrong cut envelope")


def controls():
    symbol = [F(1), F(1, 8)] + [F(1, 16)] * 6
    factors = compile_symbol(symbol)
    missing_left = factors.copy()
    missing_left[-1] = identity()
    reversed_order = list(reversed(factors))
    mutants = (compile_symbol(symbol, wrong_sign=True), missing_left, reversed_order)
    rejected = 0
    for factors in mutants:
        try:
            execute(symbol, factors)
        except ValueError as error:
            require(str(error) == "wrong endpoint", "unexpected control failure")
            rejected += 1
    require(rejected == 3, "endpoint mutation accepted")
    return ["wrong_root_left_sign", "missing_root_left", "reversed_macro_order"]


def census_controls(rows):
    mutants = [rows[:-1], [rows[0]] + rows[1:-1] + [rows[0]]]
    for kind in ("omitted_cut", "wrong_maximum", "completed_cut_is_proper"):
        changed = json.loads(json.dumps(rows))
        if kind == "omitted_cut":
            changed[0]["prefix_norms"].pop()
        elif kind == "wrong_maximum":
            changed[0]["maximum"] = "3/2"
        else:
            changed[0]["prefix_norms"][-1] = "3/2"
        mutants.append(changed)
    rejected = 0
    for changed in mutants:
        try:
            check_census(changed)
        except ValueError:
            rejected += 1
    require(rejected == 5, "census mutation accepted")
    return ["omitted_symbol", "duplicated_symbol", "omitted_cut",
            "wrong_maximum", "completed_cut_is_proper"]


def main():
    require(sys.argv[1:] in ([], ["--details"]), "usage: verify.py [--details]")
    rows = census()
    check_census(rows)
    distribution = Counter(row["maximum"] for row in rows)
    package = Path(__file__).resolve().parent
    source_hashes = {name: sha256((package / name).read_bytes()).hexdigest()
                     for name in ("verify.py", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")}
    receipt = {"status": "PASS_TRIANGULAR_PARITY_SIGN_CUBE", "symbols": 128,
               "proper_cuts_per_symbol": 21, "proper_prefixes": 2688,
               "maximum_distribution": dict(distribution),
               "cut_maxima": list(map(str, CUT_MAXIMA)),
               "controls": controls() + census_controls(rows),
               "certificate_sha256": sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
               "source_sha256": source_hashes}
    if sys.argv[1:] == ["--details"]:
        receipt["certificate"] = rows
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
