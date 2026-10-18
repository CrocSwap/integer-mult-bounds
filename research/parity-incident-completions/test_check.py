#!/usr/bin/env python3
"""Focused counterexample and certificate-corruption tests (also run with -O)."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("incident_checker", HERE / "check.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class TinyResidualTests(unittest.TestCase):
    def test_pr920_h6_minimum_frames_are_not_incident_safe(self):
        g = checker.Geometry(6)
        A, B = checker.span([7, 25]), checker.span([11, 19])
        frames = list(g.extensions(A, g.perp(B)))
        self.assertEqual([z for z, _ in frames], [3, 35])
        self.assertEqual([g.characteristic(U) for _, U in frames], [7, 25])
        self.assertEqual([g.residual_failures(U, {7, 25}) for _, U in frames], [[7], [25]])
        self.assertEqual([g.residual_failures(g.perp(U), {11, 19}) for _, U in frames], [[], []])
        for (_, U), label, expected in zip(frames, [7, 25],
                                           [{0, 3, 29, 30}, {0, 30, 36, 58}]):
            residual = U & g.hyperplanes[label]
            self.assertEqual(residual, expected)
            self.assertEqual(len(residual), 4)
            self.assertTrue(residual.isdisjoint(g.odd))

    def test_zero_and_nonzero_nonalternating_residuals_are_allowed(self):
        g = checker.Geometry(3)
        self.assertEqual(g.residual_failures(checker.span([1]), {1}), [])
        self.assertEqual(g.residual_failures(checker.span([1, 2]), {1}), [])
        self.assertEqual(g.residual_failures(checker.span([3]), {4}), [4])

    def test_characteristic_target_with_zero_residual_is_allowed(self):
        g = checker.Geometry(4)
        U = checker.span([1, 2, 4])
        self.assertEqual(g.characteristic(g.perp(U)), 8)
        self.assertEqual(g.perp(U) & g.hyperplanes[8], {0})
        self.assertEqual(g.residual_failures(g.perp(U), {8}), [])

    def test_characteristic_in_source_span_but_not_actual_labels_is_allowed(self):
        g = checker.Geometry(6)
        sources = {7, 11, 19, 28}
        U = checker.span([1, 2, 4, 8, 16])
        self.assertEqual(g.characteristic(U), 31)
        self.assertIn(31, checker.span(sources))
        self.assertNotIn(31, sources)
        self.assertEqual(g.residual_failures(U, sources), [])
        self.assertEqual(g.residual_failures(g.perp(U), {32}), [])

    def test_target_only_failure_constructs_actual_alternating_residual(self):
        g = checker.Geometry(8)
        U = checker.span([1, 2, 4, 8, 16])
        self.assertEqual(g.residual_failures(U, {7, 11, 19, 28}), [])
        self.assertEqual(g.residual_failures(g.perp(U), {224}), [224])
        self.assertEqual(g.perp(U) & g.hyperplanes[224], {0, 96, 160, 192})

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"node": 1, "node": 2}', object_pairs_hook=checker.unique_object)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"),
                                     object_pairs_hook=checker.unique_object)

    def rejects(self, mutate, message=None):
        candidate = copy.deepcopy(self.certificate)
        mutate(candidate)
        with self.assertRaisesRegex(ValueError, message or ".+"):
            checker.check(candidate)

    def test_complete_certificate(self):
        result = checker.check(self.certificate)
        self.assertEqual(result["enumerated_nodes"], 692)
        self.assertEqual(result["frames"], 3096)
        self.assertEqual(result["one_extra_dimension_repairs"], 12)
        self.assertEqual(result["two_extra_dimension_repairs"], 100)
        self.assertEqual(result["no_incident_safe_frame"], 20)
        self.assertEqual(result["one_extra_safe_frame_census"], 168)

    def test_omitted_record(self):
        self.rejects(lambda c: c["records"].pop(0), "missing record")

    def test_duplicated_record(self):
        self.rejects(lambda c: c["records"].insert(0, copy.deepcopy(c["records"][0])),
                     "duplicate or unordered")

    def test_modified_source_hash(self):
        filename = next(iter(self.certificate["source_sha256"]))
        self.rejects(lambda c: c["source_sha256"].__setitem__(filename, "0" * 64),
                     "source hash manifest")

    def test_missing_source_pin(self):
        filename = next(iter(self.certificate["source_sha256"]))
        self.rejects(lambda c: c["source_sha256"].pop(filename), "source hash manifest")

    def test_modified_dag_hash(self):
        self.rejects(lambda c: c.__setitem__("dag_sha256", "0" * 64), "DAG hash")

    def test_extra_source_vector(self):
        self.rejects(lambda c: c["records"][0]["source_basis"].append(0), "source_basis differs")

    def test_omitted_frame(self):
        self.rejects(lambda c: c["records"][0]["frames"].pop(), "frame enumeration")

    def test_duplicated_frame(self):
        self.rejects(lambda c: c["records"][0]["frames"].append(copy.deepcopy(c["records"][0]["frames"][0])),
                     "frame enumeration")

    def test_modified_characteristic(self):
        self.rejects(lambda c: c["records"][0]["frames"][0].__setitem__("characteristic", 0),
                     "frame enumeration")

    def test_modified_source_classification(self):
        self.rejects(lambda c: c["records"][0]["frames"][0].__setitem__("source_bad", [7]),
                     "frame enumeration")

    def test_modified_target_classification(self):
        self.rejects(lambda c: c["records"][0]["frames"][0].__setitem__("target_bad", [11]),
                     "frame enumeration")

    def test_modified_summary(self):
        self.rejects(lambda c: c["summary"].__setitem__("safe_frames", 3096), "summary differs")

    def test_invalid_repair_vector(self):
        def mutate(c):
            r = next(r for r in c["records"] if r.get("repair"))
            r["repair"]["extra_basis"][0] = 1024
        self.rejects(mutate, "invalid vector")

    def test_false_impossibility(self):
        def mutate(c):
            r = next(r for r in c["records"] if r.get("repair"))
            r["repair"] = None
        self.rejects(mutate, "unproved impossibility")

    def test_signed_kernel_rejects_output_sign_flip(self):
        # The checker must verify signed coefficients without relying on the
        # constructor's assert-based verify(), which is disabled by -O.
        checker.check(self.certificate)
        from experiments.parity_side import ParitySide
        circuit = ParitySide(10)
        target = next(iter(circuit.outputs))
        circuit.outputs[target] *= -1
        with self.assertRaisesRegex(ValueError, "signed kernel entry"):
            checker.rebuild_graph(circuit)


if __name__ == "__main__":
    unittest.main()
