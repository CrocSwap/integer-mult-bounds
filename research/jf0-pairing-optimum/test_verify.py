#!/usr/bin/env python3
"""Behavioral certificate checks, including actual removed-guard sensitivity."""
import ast
import copy
import itertools
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import oracle
import verify as primary

ROOT = Path(__file__).resolve().parent
P, Q = json.loads((ROOT / "source/jf0.json").read_text())
ORDERS = json.loads((ROOT / "CERTIFICATE.json").read_text())["lower_minor_orders"]
B = json.loads((ROOT / "candidate-witness.json").read_text())["binary_matrix"]


def rejects(function, args, fragment):
    try:
        function(*args)
    except ValueError as exc:
        if fragment not in str(exc):
            raise AssertionError("wrong rejecting predicate: " + str(exc)) from exc
    else:
        raise AssertionError("invalid certificate accepted")


class CertificateChecks(unittest.TestCase):
    def test_fixed_positive_and_independent_oracle(self):
        result = primary.verify()
        self.assertEqual(result["minimum_pairing_cost"], 19)
        self.assertEqual(oracle.evaluate(P, Q, B), (6, 6, 7))

    def test_non_equivalence_positive(self):
        words = [1, 2, 260, 1676, 16, 32, 468, 140, 260, 1536, 1536]
        alternative = [[(word >> j) & 1 for j in range(11)] for word in words]
        self.assertNotEqual(alternative, B)
        self.assertEqual(primary.certify(P, Q, ORDERS, alternative)["minimum_pairing_cost"], 19)
        self.assertEqual(oracle.evaluate(P, Q, alternative), (6, 6, 7))

    def test_equivalent_presentations(self):
        # Six coordinate permutations, each with reversed line labels and
        # independent nonzero integer gauges on all P and Q vectors.
        perm = list(reversed(range(11)))
        inverse = {old: new for new, old in enumerate(perm)}
        pairing = [[B[i][k] for k in perm] for i in perm]
        for coordinates in itertools.permutations(range(3)):
            points = [[((-1) ** i) * (i + 1) * P[i][j] for j in coordinates] for i in perm]
            lines = [[-(i + 2) * Q[i][j] for j in coordinates] for i in perm]
            orders = [[inverse[i] for i in ORDERS[j]] for j in coordinates]
            got = primary.certify(points, lines, orders, pairing)
            self.assertEqual(got["minimum_pairing_cost"], 19)
            self.assertEqual(tuple(got["attaining_ranks"]), oracle.evaluate(points, lines, pairing))

    def test_unit_diagonal_and_binary_domain(self):
        for value, predicate in [(0, "unit pairing diagonal"), (2, "binary pairing")]:
            bad = copy.deepcopy(B)
            bad[0][0] = value
            rejects(primary.witness_ranks, (P, Q, bad), predicate)
            with self.assertRaises(ValueError):
                oracle.evaluate(P, Q, bad)

    def test_forbidden_incidence(self):
        bad = copy.deepcopy(B)
        bad[0][6] = 1  # Rational dot product 2, even but not zero.
        rejects(primary.witness_ranks, (P, Q, bad), "rational incidence support")
        with self.assertRaises(ValueError):
            oracle.evaluate(P, Q, bad)

    def test_source_model_diagonal(self):
        points = copy.deepcopy(P)
        points[0] = [0, 0, 0]
        rejects(primary.witness_ranks, (points, Q, B), "nonzero rational diagonal")
        rejects(oracle.evaluate, (points, Q, B), "nonzero rational diagonal")

    def test_reciprocal_pair_description(self):
        with tempfile.TemporaryDirectory(prefix="jf0-pairs-") as folder:
            path = Path(folder) / "witness.json"
            witness = json.loads((ROOT / "candidate-witness.json").read_text())
            witness["reciprocal_pairs"] = [[j, i] for i, j in reversed(witness["reciprocal_pairs"])]
            path.write_text(json.dumps(witness))
            self.assertEqual(oracle.verify(ROOT / "source/jf0.json", path)["total"], 19)
            witness["reciprocal_pairs"] = []
            path.write_text(json.dumps(witness))
            with self.assertRaises(ValueError):
                oracle.verify(ROOT / "source/jf0.json", path)

    def test_nonattaining_matrix(self):
        bad = copy.deepcopy(B)
        bad[2][8] = 0
        self.assertEqual(primary.witness_ranks(P, Q, bad), [7, 6, 7])
        self.assertEqual(oracle.evaluate(P, Q, bad), (7, 6, 7))
        rejects(primary.certify, (P, Q, ORDERS, bad), "lower and attaining ranks agree")

    def test_minor_distinctness_and_support(self):
        bad = copy.deepcopy(ORDERS)
        bad[0][0] = bad[0][1]
        rejects(primary.lower_bound, (P, Q, bad), "distinct minor indices")
        bad = copy.deepcopy(ORDERS)
        bad[0][0] = 1
        rejects(primary.lower_bound, (P, Q, bad), "minor support")

    def test_triangular_control_detects_actual_guard_removal(self):
        bad = copy.deepcopy(ORDERS)
        bad[0][1], bad[0][2] = bad[0][2], bad[0][1]
        rejects(primary.lower_bound, (P, Q, bad), "forced triangular zero")

        class RemoveGuard(ast.NodeTransformer):
            count = 0

            def visit_Expr(self, node):
                call = node.value
                if (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                        and call.func.id == "require" and len(call.args) == 2
                        and isinstance(call.args[1], ast.Constant)
                        and call.args[1].value == "forced triangular zero"):
                    self.count += 1
                    return ast.copy_location(ast.Pass(), node)
                return self.generic_visit(node)

        remover = RemoveGuard()
        tree = ast.fix_missing_locations(remover.visit(ast.parse((ROOT / "verify.py").read_text())))
        self.assertEqual(remover.count, 1)
        namespace = {"__file__": str(ROOT / "verify.py"), "__name__": "removed_guard_variant"}
        exec(compile(tree, "removed_guard_variant", "exec"), namespace)
        # The same behavioral control fails when its actual guard is removed.
        with self.assertRaisesRegex(AssertionError, "invalid certificate accepted"):
            rejects(namespace["lower_bound"], (P, Q, bad), "forced triangular zero")

    def test_source_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix="jf0-certificate-") as folder:
            destination = Path(folder) / "package"
            shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns("__pycache__"))
            source = destination / "source/jf0.json"
            original = source.read_bytes()
            source.write_bytes(original.replace(b"-2", b"-3", 1))
            rejects(primary.verify, (destination,), "source SHA256")
            source.write_bytes(original)
            receipt = destination / "RESULT.json"
            result = json.loads(receipt.read_text())
            result["minimum_pairing_cost"] = 18
            receipt.write_text(json.dumps(result))
            rejects(primary.verify, (destination,), "fixed result receipt")

    def test_missing_certificate_is_not_regenerated(self):
        with tempfile.TemporaryDirectory(prefix="jf0-missing-") as folder:
            destination = Path(folder) / "package"
            shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns("__pycache__"))
            missing = destination / "candidate-witness.json"
            missing.unlink()
            with self.assertRaises(FileNotFoundError):
                primary.verify(destination)
            self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
