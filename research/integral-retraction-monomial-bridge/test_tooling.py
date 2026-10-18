#!/usr/bin/env python3
"""Stdlib-only tests of log-auditing code and small fixture arithmetic.

No Lean invocation, mocked compiler, theorem checking, or axiom receipts.
Axiom-format strings below are deliberately synthetic parser unit-test inputs.
Run: PYTHONDONTWRITEBYTECODE=1 python3 test_tooling.py
"""
from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import check_axioms


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def matsub(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


class ParserTests(unittest.TestCase):
    def test_permitted_dependencies(self) -> None:
        # These are toy strings, NOT compiler output from PR1497Bridge.lean.
        text = ("'Toy.zero' does not depend on any axioms\n"
                "'Toy.quot' depends on axioms: [Quot.sound, propext, Classical.choice]\n")
        self.assertEqual(check_axioms.parse_records(text), {
            'Toy.zero': [],
            'Toy.quot': ['Classical.choice', 'Quot.sound', 'propext'],
        })

    def test_duplicate_record(self) -> None:
        line = "'Toy.zero' does not depend on any axioms\n"
        with self.assertRaises(ValueError):
            check_axioms.parse_records(line + line)

    def test_disallowed_dependencies(self) -> None:
        for dependency in ['Foreign.assumption', 'sorryAx', 'Lean.ofReduceBool']:
            with self.subTest(dependency=dependency), self.assertRaises(ValueError):
                check_axioms.parse_records(f"'Toy.bad' depends on axioms: [{dependency}]\n")

    def test_error_bearing_census(self) -> None:
        text = ("Toy.lean:1:1: error: unsolved goals\n"
                "'Toy.zero' does not depend on any axioms\n")
        with self.assertRaises(ValueError):
            check_axioms.parse_records(text)

    def test_incomplete_proof_warning(self) -> None:
        text = ("Toy.lean:1:1: warning: declaration uses 'sorry'\n"
                "'Toy.zero' does not depend on any axioms\n")
        with self.assertRaises(ValueError):
            check_axioms.parse_records(text)

    def test_complete_query_inventory(self) -> None:
        with tempfile.TemporaryDirectory(prefix='pr1497-parser-unit-') as temp:
            root = Path(temp)
            src, log = root / 'Toy.lean.txt', root / 'synthetic.txt'
            src.write_text('#print axioms Toy.zero\n', encoding='utf-8')
            log.write_text("'Toy.zero' does not depend on any axioms\n", encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_axioms.main([str(src), str(log)]), 0)

    def test_missing_unexpected_duplicate_queries(self) -> None:
        cases = [
            ('#print axioms Toy.zero\n', ''),
            ('#print axioms Toy.zero\n', "'Toy.other' does not depend on any axioms\n"),
            ('#print axioms Toy.zero\n#print axioms Toy.zero\n',
             "'Toy.zero' does not depend on any axioms\n"),
        ]
        with tempfile.TemporaryDirectory(prefix='pr1497-parser-unit-') as temp:
            root = Path(temp)
            src, log = root / 'Toy.lean.txt', root / 'synthetic.txt'
            for source, output in cases:
                src.write_text(source, encoding='utf-8')
                log.write_text(output, encoding='utf-8')
                with self.subTest(source=source, output=output), self.assertRaises(ValueError):
                    check_axioms.main([str(src), str(log)])


class FixtureArithmeticTests(unittest.TestCase):
    def test_signed_nonzero_w_identities(self) -> None:
        m, p, q, w = [[-2, 1]], [[1], [2]], [[3, -1]], [[1], [3]]
        self.assertEqual(matmul(m, p), [[0]])
        self.assertEqual(matmul(q, p), [[1]])
        residual = matsub([[1, 0], [0, 1]], matmul(p, q))
        self.assertEqual(residual, [[-2, 1], [-6, 3]])
        self.assertEqual(residual, matmul(w, m))
        self.assertNotEqual(residual, matmul([[-1], [-3]], m))

    def test_missing_identity_countermodels(self) -> None:
        one, zero = [[1]], [[0]]
        # M=P=Q=1, W=0: QP and residual hold, MP fails.
        self.assertEqual(matmul(one, one), one)
        self.assertEqual(matsub(one, matmul(one, one)), matmul(zero, one))
        self.assertNotEqual(matmul(one, one), zero)
        # M=W=1, P=Q=0: MP and residual hold, QP fails.
        self.assertEqual(matmul(one, zero), zero)
        self.assertEqual(matsub(one, matmul(zero, zero)), matmul(one, one))
        self.assertNotEqual(matmul(zero, zero), one)

    def test_signed_and_torsion_points(self) -> None:
        m, p, q = [-2, 1], [1, 2], [3, -1]
        x = [5, 10]
        self.assertEqual(sum(a * b for a, b in zip(x, m)), 0)
        theta = sum(a * b for a, b in zip(x, q))
        self.assertEqual(theta, 5)
        self.assertEqual([theta * a for a in p], x)
        self.assertEqual(5 * (-3), -15)
        self.assertNotEqual(3 * 5 + 10, 5)
        b = [1, 0]  # Bool XOR group, represented by integers modulo 2.
        self.assertEqual(sum(a * c for a, c in zip(b, m)) % 2, 0)
        t = sum(a * c for a, c in zip(b, q)) % 2
        self.assertEqual([t * a % 2 for a in p], b)


if __name__ == '__main__':
    unittest.main(verbosity=2)
