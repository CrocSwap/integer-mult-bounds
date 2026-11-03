#!/usr/bin/env python3
"""Read-only replay of the all-depth balanced power law. Standard library only."""
from collections import Counter
from hashlib import sha256
import json
from math import comb, factorial
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from census import check, full_census
from law import first_missing_prime, lifted_target, order_bound, root_target, unit_repeat_root
from order_checks import compare_divisors, zero_spectra
from quintic_rows import signature, small_quintic_rows
from oracle import dirty_basis, literal_matrix, matrix_target, primitive_period


def verify_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    retained = {}
    for source in manifest["files"]:
        local = source.get("vendored_as")
        if local:
            digest = sha256((HERE / local).read_bytes()).hexdigest()
            check(digest == source["sha256"], "retained source bytes differ: " + local)
            retained[local] = digest
    return retained


def coefficient_grid():
    cases = boundary = safe = 0
    for n in range(1, 25):
        for d in range(1, 129):
            m = n*d
            predicted = first_missing_prime(d, n)
            first = None
            for j in range(2, d+1):
                residue = (comb(d, j) * pow(n, j, m)) % m
                if residue and first is None:
                    first = j
                if predicted is None or j < predicted:
                    check(residue == 0, "lower binomial coefficient")
                    safe += 1
                if j == predicted:
                    check(residue == (d//j)*pow(n, j, m) % m and residue % d != 0,
                          "first surviving coefficient")
                    boundary += 1
                cases += 1
            check(first == predicted, "least obstructing pure level")
    return dict(n_range=[1, 24], d_range=[1, 128], binomial_tests=cases,
                lower_vanishings=safe, surviving_boundaries=boundary)


def source_witness_checks():
    rows = json.loads((HERE / "source/depth5-witnesses.json").read_text())["witnesses"]
    blocks = tests = surviving = splits = 0
    for size, targets in rows.items():
        n = int(size)
        for target, encoded in targets.items():
            t, word = int(target), tuple(map(int, encoded))
            check(Counter(word) == {label: n for label in range(1, 6)}, "witness balance")
            check(matrix_target(literal_matrix(word, 5), n) == t, "witness source endpoint")
            for cut in (len(word)//3, len(word)//2, 2*len(word)//3):
                prefix, prefix_top = signature(word[:cut], n, False)
                suffix, inverse_top = signature(word[cut:][::-1], n, True)
                check(prefix == suffix and (prefix_top-inverse_top) % n == t, "witness inverse-suffix join")
                splits += 1
            for d in (2, 3, 4, 5, 6, 10, 12):
                actual = matrix_target(literal_matrix(word*d, 5), n*d)
                expected = lifted_target(5, n, d, t)
                check(actual == expected, "retained witness repetition")
                tests += 1
                surviving += actual is not None
            blocks += 1
    return dict(witnesses=blocks, powered_words=tests, correct_powers=surviving, witness_splits=splits)


def examples():
    source = json.loads((HERE / "source/depth5-witnesses.json").read_text())["witnesses"]
    configs = [
        (5, 7, 5, tuple(map(int, source["7"]["1"])), 12),
        (5, 2, 10, tuple(x for x in range(1, 6) for _ in range(2)), 4),
        (5, 2, 25, tuple(x for x in range(1, 6) for _ in range(2)), 10),
        (6, 2, 8, tuple(x for x in range(1, 7) for _ in range(2)), 0),
        (7, 1, 7, tuple(range(1, 8)), 1),
        (11, 1, 11, tuple(range(1, 12)), 1),
    ]
    rows = []
    for h, n, d, block, c in configs:
        word = block*d
        check(matrix_target(literal_matrix(word, h), n*d) == c, "example endpoint")
        period = primitive_period(word)
        check(period == h*n, "example period")
        checked = dirty_basis(word, h, n*d, c)
        rows.append(dict(depth=h, modulus=n*d, target=c, repeats=d, period=period,
                         block=list(block), dirty_basis_cases=checked))
    empty_root_word = tuple(map(int, source["10"]["7"]))
    check(matrix_target(literal_matrix(empty_root_word, 5), 10) == 7 and
          primitive_period(empty_root_word) == 50, "nonvacuous empty-root boundary")
    unbalanced = (1, 2, 3, 4, 5, 6, 5, 4, 3, 2)*2
    unbalanced_counts = [unbalanced.count(i) for i in range(1, 7)]
    check(unbalanced_counts == [2, 4, 4, 4, 4, 2] and primitive_period(unbalanced) == 10
          and matrix_target(literal_matrix(unbalanced, 6), 2) == 1, "PR4748 balance boundary")
    h, n, d = 6, 2, 25
    blocks = tuple(x for x in range(1, h+1) for _ in range(n))
    matrix = literal_matrix(blocks*d, h)
    residues = {length: [matrix[i+length][i] % (n*d) for i in range(h+1-length)]
                for length in range(1, h)}
    check(all(not any(residues[j]) for j in range(1, 5)), "lower four levels")
    check(residues[5] == [10, 10], "first forbidden level is five")
    return dict(correct_words=rows, empty_root_witness=dict(word=list(empty_root_word), period=50),
                unbalanced_4748=dict(word=list(unbalanced), counts=unbalanced_counts, period=10,
                                     target=1, dirty_basis_cases=dirty_basis(unbalanced, 6, 2, 1)),
                bad_fifth_level=dict(depth=h, modulus=n*d,
                repeats=d, interval_residues={str(k): v for k, v in residues.items()}))


def build():
    pins = verify_pins()
    grid = coefficient_grid()
    corpus = full_census()
    examples_checked = examples()
    witness_checks = source_witness_checks()
    check(root_target(5, 2, 5, 7) == 1, "binary-root residue")
    check(unit_repeat_root(5, 10, 7) == (2, 1), "eligible empty unit root")
    check(corpus["rows"]["L5_n2"]["counts"][1] == 0, "empty unit root population")
    for h in (2, 3, 5, 7):
        check(corpus["rows"][f"L{h}_n1"]["counts"] == [factorial(h)], "unit prime sharpness")
    check(order_bound(5, 10, 7) == 5, "arithmetic order need not be attained")
    check(order_bound(5, 20, 4) == 10, "sharp nonunit order bound")
    check(order_bound(5, 50, 10) == 25 and order_bound(5, 50, 5) == 5,
          "full prime-power target congruence")
    quintic = small_quintic_rows()
    literal = recorded_literal(quintic)
    return dict(status="PASS_CHAIN_ALL_DEPTH_POWERS", retained_sources=pins,
                divisor_grid=compare_divisors(), zero_spectra=zero_spectra(), quintic=quintic,
                literal_receipt=literal,
                coefficients=grid, census=corpus, examples=examples_checked,
                credited_witnesses=witness_checks)


def recorded_literal(quintic):
    receipt = json.loads((HERE / "literal/RESULT.json").read_text(encoding="utf-8"))
    digest = sha256((HERE / "literal/LiteralQuintic.java").read_bytes()).hexdigest()
    check(digest == receipt["source_sha256"], "literal JVM source hash")
    check([item["n"] for item in receipt["rows"]] == [2, 3], "literal JVM domains")
    for item in receipt["rows"]:
        independent = quintic[str(item["n"])]["gaps"]
        check(item["row"] == independent["row"] and item["leaves"] == independent["all_words"],
              "literal JVM receipt differs from independent counters")
    return dict(source_sha256=digest, rows=receipt["rows"])


def main():
    result = build()
    expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
    check(result == expected, "retained result differs")
    files = {p.relative_to(HERE).as_posix(): sha256(p.read_bytes()).hexdigest()
             for p in sorted(HERE.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    print(json.dumps(dict(result=result, files=files), sort_keys=True))


if __name__ == "__main__":
    main()
