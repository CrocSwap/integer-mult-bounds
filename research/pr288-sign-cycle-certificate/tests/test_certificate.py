"""Regression and adversarial controls for the standalone exact checker."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import check_certificate as checker


class FieldAndNumberingTests(unittest.TestCase):
    def test_exact_field_laws_and_polynomial_relation(self):
        add, mul = checker.field_add, checker.field_multiply
        self.assertEqual(mul(3, 3), 2)  # t^2 = -1 in F3
        self.assertEqual(add(1, 3), 4)  # label eta(4) = 1+t
        for a in range(9):
            self.assertEqual(mul(a, 1), a)
            self.assertEqual(add(a, 0), a)
            if a:
                self.assertEqual(mul(a, checker.field_inverse(a)), 1)
            for b in range(9):
                self.assertEqual(mul(a, b), mul(b, a))
                for c in range(9):
                    self.assertEqual(mul(mul(a, b), c), mul(a, mul(b, c)))
                    self.assertEqual(mul(a, add(b, c)), add(mul(a, b), mul(a, c)))

    def test_projective_normalization_and_source_numbering_landmarks(self):
        points, edges = checker.projective_graph()
        self.assertEqual(len(points), 91)
        self.assertEqual(len(edges), 910)
        self.assertEqual(points[0], (0, 0, 1))
        self.assertEqual(points[1], (0, 1, 0))
        self.assertEqual(points[10], (1, 0, 0))
        self.assertEqual(points[90], (1, 8, 8))
        self.assertEqual([edges[q] for q in (7, 30, 113, 114)],
                         [(0, 155), (3, 93), (11, 121), (11, 130)])


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance_bytes = (ROOT / "instance.json").read_bytes()
        cls.instance = json.loads(cls.instance_bytes)
        cls.certificate = json.loads((ROOT / "certificate.json").read_bytes())

    def check(self, certificate, instance_bytes=None):
        with tempfile.TemporaryDirectory() as directory:
            instance_path = Path(directory) / "instance.json"
            certificate_path = Path(directory) / "certificate.json"
            instance_path.write_bytes(self.instance_bytes if instance_bytes is None else instance_bytes)
            certificate_path.write_text(json.dumps(certificate), encoding="utf-8")
            return checker.verify(instance_path, certificate_path)

    def mutation(self):
        return copy.deepcopy(self.certificate)

    def test_original_certificate_is_accepted(self):
        result = checker.verify(ROOT / "instance.json", ROOT / "certificate.json")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["sign_product"], -1)
        self.assertEqual(result["certified_incidences"], 4)
        self.assertEqual(result["distinct_length_five_paths"], 3)
        self.assertEqual(result["physical_edges_in_paths"], 11)

    def test_geometrically_valid_balanced_cycle_proves_no_obstruction(self):
        # Both real sessions traverse edge 0 forwards and edge 110 backwards.
        # Every supplied path is valid; only the claimed contradiction is absent.
        first = [0, 92, 11, 130, 66, 155]
        second = [0, 92, 11, 103, 47, 164]
        certificate = self.mutation()
        certificate["cycle_nodes"] = [["session", 7], ["edge", 0],
                                      ["session", 8], ["edge", 110]]
        certificate["incidences"] = [
            {"path": first, "sign": 1}, {"path": second, "sign": 1},
            {"path": second, "sign": -1}, {"path": first, "sign": -1},
        ]
        with self.assertRaisesRegex(checker.CertificateError, "balanced cycle"):
            self.check(certificate)

    def test_proper_subcycle_is_rejected(self):
        certificate = self.mutation()
        certificate["cycle_nodes"] = certificate["cycle_nodes"][:2]
        certificate["incidences"] = [certificate["incidences"][0]] * 2
        with self.assertRaisesRegex(checker.CertificateError, "at least four"):
            self.check(certificate)

    def test_recomputed_sign_rejects_a_flipped_label(self):
        certificate = self.mutation()
        certificate["incidences"][0]["sign"] *= -1
        with self.assertRaisesRegex(checker.CertificateError, "sign does not match"):
            self.check(certificate)

    def test_six_edge_path_is_rejected(self):
        certificate = self.mutation()
        certificate["incidences"][0]["path"].insert(1, 1)
        with self.assertRaisesRegex(checker.CertificateError, "exactly five edges"):
            self.check(certificate)

    def test_dimension_cannot_be_changed(self):
        certificate = self.mutation()
        certificate["dimension"] = 6
        with self.assertRaisesRegex(checker.CertificateError, "dimension must be exactly 5"):
            self.check(certificate)

    def test_wrong_session_endpoint_is_rejected(self):
        certificate = self.mutation()
        certificate["incidences"][0]["path"][-1] = 164
        with self.assertRaisesRegex(checker.CertificateError, "wrong point-to-line"):
            self.check(certificate)

    def test_nonsimple_path_is_rejected(self):
        certificate = self.mutation()
        certificate["incidences"][0]["path"][2] = 0
        with self.assertRaisesRegex(checker.CertificateError, "path is not simple"):
            self.check(certificate)

    def test_nonincident_vertices_are_rejected(self):
        certificate = self.mutation()
        certificate["incidences"][0]["path"][1] = 91
        with self.assertRaisesRegex(checker.CertificateError, "not incident"):
            self.check(certificate)

    def test_genuine_incidence_path_using_removed_edges_is_rejected(self):
        certificate = self.mutation()
        # A simple five-edge path in the full graph; its third edge is C-edge 102.
        certificate["incidences"][0]["path"] = [0, 92, 10, 93, 67, 155]
        with self.assertRaisesRegex(checker.CertificateError, "uses removed edge 102"):
            self.check(certificate)

    def test_selected_edge_must_really_occur(self):
        certificate = self.mutation()
        certificate["cycle_nodes"][1] = ["edge", 1]
        with self.assertRaisesRegex(checker.CertificateError, "selected edge must occur"):
            self.check(certificate)

    def test_a_removed_edge_cannot_be_a_physical_cycle_node(self):
        certificate = self.mutation()
        certificate["cycle_nodes"][1] = ["edge", 8]
        with self.assertRaisesRegex(checker.CertificateError, "edge 8 is not physical"):
            self.check(certificate)

    def test_a_constant_zero_edge_cannot_be_a_session(self):
        certificate = self.mutation()
        certificate["cycle_nodes"][0] = ["session", 102]
        with self.assertRaisesRegex(checker.CertificateError, "session 102 is not in"):
            self.check(certificate)

    def test_repeated_cycle_node_is_rejected(self):
        certificate = self.mutation()
        certificate["cycle_nodes"][3] = certificate["cycle_nodes"][1]
        with self.assertRaisesRegex(checker.CertificateError, "nodes must be unique"):
            self.check(certificate)

    def test_cycle_must_alternate(self):
        certificate = self.mutation()
        certificate["cycle_nodes"][1], certificate["cycle_nodes"][2] = (
            certificate["cycle_nodes"][2], certificate["cycle_nodes"][1])
        with self.assertRaisesRegex(checker.CertificateError, "does not alternate"):
            self.check(certificate)

    def test_missing_incidence_is_rejected(self):
        certificate = self.mutation()
        certificate["incidences"].pop()
        with self.assertRaisesRegex(checker.CertificateError, "counts differ"):
            self.check(certificate)

    def test_boolean_is_not_a_sign_integer(self):
        certificate = self.mutation()
        certificate["incidences"][0]["sign"] = True
        with self.assertRaisesRegex(checker.CertificateError, "sign must be the integer"):
            self.check(certificate)

    def test_hash_mismatch_is_rejected(self):
        certificate = self.mutation()
        certificate["instance_sha256"] = "0" * 64
        with self.assertRaisesRegex(checker.CertificateError, "hash does not match"):
            self.check(certificate)

    def test_rebinding_certificate_does_not_bypass_the_source_pin(self):
        different_bytes = self.instance_bytes + b"\n"
        certificate = self.mutation()
        certificate["instance_sha256"] = hashlib.sha256(different_bytes).hexdigest()
        with self.assertRaisesRegex(checker.CertificateError, "pinned PR #288"):
            self.check(certificate, different_bytes)

    def test_instance_counts_permutation_and_partition_are_validated(self):
        mutations = [
            ("removed_edges", 0, self.instance["removed_edges"][1], "duplicate"),
            ("vertex_order", 0, self.instance["vertex_order"][1], "duplicate"),
            ("dropped_edges", 0, self.instance["constant_zero_edges"][0], "overlap"),
        ]
        for key, index, value, message in mutations:
            with self.subTest(field=key):
                instance = copy.deepcopy(self.instance)
                instance[key][index] = value
                with self.assertRaisesRegex(checker.CertificateError, message):
                    checker._validate_instance(instance)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(checker.CertificateError, "duplicate JSON key"):
            checker._parse_json(b'{"dimension": 5, "dimension": 6}', "test")

    def test_optimized_python_still_rejects_a_false_sign(self):
        certificate = self.mutation()
        certificate["incidences"][0]["sign"] *= -1
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "bad.json"
            candidate.write_text(json.dumps(certificate), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-O", "-B", str(ROOT / "check_certificate.py"),
                 "--instance", str(ROOT / "instance.json"), "--certificate", str(candidate)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertIn("sign does not match", completed.stderr)


if __name__ == "__main__":
    unittest.main()
