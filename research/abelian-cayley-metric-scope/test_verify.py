#!/usr/bin/env python3
"""Independent small-metric oracles and admission controls; no solver needed."""
# Copyright 2026 Jerry Chen. SPDX-License-Identifier: Apache-2.0
# Prepared with substantial OpenAI Codex assistance.

from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("metric_scope", HERE / "verify.py")
scope = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope)


def floyd_metric(order, generators):
    """All-pairs closure, independent of the production single-source BFS."""
    distances = [[0 if i == j else order + 1 for j in range(order)]
                 for i in range(order)]
    for i in range(order):
        for generator in generators:
            distances[i][(i + generator) % order] = 1
    for k in range(order):
        for i in range(order):
            for j in range(order):
                distances[i][j] = min(distances[i][j], distances[i][k] + distances[k][j])
    return distances


def rational_rank(matrix):
    """Fraction row elimination, not the production determinant formula."""
    rows = [[Fraction(x) for x in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][column]
        rows[rank] = [x / divisor for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [x - scale * y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


class MetricTests(unittest.TestCase):
    def test_independent_distances_and_literal_partition(self):
        for order in (6, 8):
            for generators in (list(range(1, order, 2)), [1, order - 1]):
                with self.subTest(order=order, generators=generators):
                    self.assertEqual(scope.cayley_metric(order, generators),
                                     floyd_metric(order, generators))
            metric = floyd_metric(order, list(range(1, order, 2)))
            same = metric[0][2] + metric[0][4] + metric[2][4] + metric[1][3]
            cross = sum(metric[a][b] for a in (0, 2, 4) for b in (1, 3))
            self.assertEqual((same, cross), (8, 6))

    def test_frozen_certificate(self):
        actual = scope.canonical(scope.build_certificate())
        self.assertEqual(actual, (HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))

    def test_independent_rational_rank_and_relative_shear_rank(self):
        expected = floyd_metric(8, [1, 3, 5, 7])
        for i, left in enumerate(scope.SHEAR_POINTS):
            for j, right in enumerate(scope.SHEAR_POINTS):
                difference = [[left[a][b] - right[a][b] for b in range(2)] for a in range(2)]
                self.assertEqual(rational_rank(difference), expected[i][j])
                first, second = scope.shear(left), scope.shear(right)
                difference4 = [[first[a][b] - second[a][b] for b in range(4)] for a in range(4)]
                self.assertEqual(rational_rank(difference4), expected[i][j])

    def test_changed_or_omitted_shear_rejected(self):
        expected = floyd_metric(8, [1, 3, 5, 7])
        points = deepcopy(scope.SHEAR_POINTS)
        points[1][0][0] = 1
        with self.assertRaises(scope.VerificationError):
            scope.validate_shears(points, expected)
        with self.assertRaises(scope.VerificationError):
            scope.validate_shears(scope.SHEAR_POINTS[:-1], expected)

    def test_cycle_is_not_a_counterexample(self):
        for order in (6, 8):
            with self.assertRaisesRegex(scope.VerificationError, "bipartite"):
                scope.validate_counterexample(order, floyd_metric(order, [1, order - 1]))

    def test_bipartite_is_not_a_cycle_embedding(self):
        for order in (6, 8):
            with self.assertRaisesRegex(scope.VerificationError, "cycle metric"):
                scope.validate_cycle(order, floyd_metric(order, list(range(1, order, 2))))

    def test_damaged_distance(self):
        metric = floyd_metric(6, [1, 3, 5])
        metric[0][2] = metric[2][0] = 1
        with self.assertRaisesRegex(scope.VerificationError, "bipartite"):
            scope.validate_counterexample(6, metric)

    def test_distortion_rejects_contraction(self):
        original = scope.weighted_cuts

        def contracted(order, masks, weight):
            return original(order, masks, weight / 2)

        with patch.object(scope, "weighted_cuts", side_effect=contracted):
            with self.assertRaisesRegex(scope.VerificationError, "distortion"):
                scope.validate_counterexample(6, floyd_metric(6, [1, 3, 5]))

    def test_invalid_graph_and_witness_domains(self):
        for order, generators in ((6, [2, 4]), (6, [1]), (6, [0, 1, 5]),
                                  (6, [1, 1, 5]), (6, [True, 5]), (True, [1])):
            with self.subTest(order=order, generators=generators):
                with self.assertRaises(scope.VerificationError):
                    scope.cayley_metric(order, generators)
        with self.assertRaises(scope.VerificationError):
            scope.quadratic_value([[0, 1], [1, 0]], [0, 0], [1, -1])
        with self.assertRaises(scope.VerificationError):
            scope.weighted_cuts(6, [1], Fraction(-1))
        with self.assertRaises(scope.VerificationError):
            scope.cut_inequality_control([1, 1, 1])


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="abelian metric controls ")
        self.addCleanup(self.temporary.cleanup)
        self.package = Path(self.temporary.name) / "relocated package"
        self.package.mkdir()
        (self.package / "sources").mkdir()
        for name in ("verify.py", "CERTIFICATE.json", "SOURCES.json", "sources/pr288-README.md"):
            shutil.copyfile(HERE / name, self.package / name)

    def command(self, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B",
                               str(self.package / "verify.py"), *map(str, args)],
                              cwd=self.temporary.name, text=True, capture_output=True,
                              timeout=15, check=False)

    def reject(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("PASS_ABELIAN", result.stdout)
        self.assertIn("FAIL_ABELIAN", result.stderr)

    def test_optimized_minimal_relocation_and_identical_receipt(self):
        output = self.package / "fresh receipt.json"
        result = self.command("--write", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), scope.MARKER)
        self.assertEqual(output.read_bytes(), (HERE / "CERTIFICATE.json").read_bytes())

    def test_source_corruption_is_rejected(self):
        source = self.package / "sources/pr288-README.md"
        source.write_bytes(source.read_bytes().replace(b"their gap is 1", b"their gap is 2"))
        self.reject(self.command())

    def test_source_identity_corruption_is_rejected(self):
        path = self.package / "SOURCES.json"
        pristine = json.loads(path.read_text(encoding="utf-8"))
        for field, replacement in (("commit", "0" * 40),
                                   ("repository", "unrelated/repository"),
                                   ("path", "unrelated.md")):
            with self.subTest(field=field):
                value = deepcopy(pristine)
                value["source"][field] = replacement
                path.write_text(json.dumps(value), encoding="utf-8")
                self.reject(self.command())

    def test_missing_source_is_rejected(self):
        (self.package / "sources/pr288-README.md").unlink()
        self.reject(self.command())

    def test_receipt_mutations_fail_before_output(self):
        pristine = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        mutations = []
        value = deepcopy(pristine)
        value["counterexamples"].pop()
        mutations.append(("omitted counterexample", value))
        value = deepcopy(pristine)
        value["cycle_controls"].pop()
        mutations.append(("omitted positive control", value))
        value = deepcopy(pristine)
        value["counterexamples"][0]["five_point_witness"]["value"] = 0
        mutations.append(("erased violation", value))
        value = deepcopy(pristine)
        value["counterexamples"][1]["optimal_l1_distortion"] = "1"
        mutations.append(("false isometry", value))
        value = deepcopy(pristine)
        value["counterexamples"][0]["distances"][0][1] = True
        mutations.append(("boolean instead of integer", value))
        value = deepcopy(pristine)
        value["rational_shear_witness"]["rank_distances"][0][1] = 2
        mutations.append(("altered rational rank", value))
        for label, value in mutations:
            with self.subTest(label=label):
                path = self.package / "changed.json"
                path.write_text(json.dumps(value), encoding="utf-8")
                output = self.package / "must not exist.json"
                self.reject(self.command("--certificate", path, "--write", output))
                self.assertFalse(output.exists())

    def test_existing_output_is_preserved(self):
        path = self.package / "existing.json"
        path.write_bytes(b"do not overwrite\n")
        self.reject(self.command("--write", path))
        self.assertEqual(path.read_bytes(), b"do not overwrite\n")

    def test_missing_and_malformed_certificate_fail(self):
        self.reject(self.command("--certificate", self.package / "missing.json"))
        path = self.package / "malformed.json"
        path.write_text("{", encoding="utf-8")
        self.reject(self.command("--certificate", path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
