#!/usr/bin/env python3
"""Failure controls for proof-relevant mutations; no expensive full-suite replay.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gram = load("check_gram")
primary = load("verify")


class ProofMutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
        cls.roots = gram.roots_from_coordinates()
        cls.pairing = [[(gram.scalar(a, b) // 4 + 1) % 2 for b in cls.roots] for a in cls.roots]

    def test_wrong_dual_scale(self):
        witness = deepcopy(self.certificate["witness56"])
        witness["right_columns_doubled"][0] = [2 * x for x in witness["right_columns_doubled"][0]]
        with self.assertRaisesRegex(ValueError, "full witness identity"):
            gram.check_witness(witness, self.roots, self.pairing)

    def test_undercharged_complete_bill(self):
        witness = deepcopy(self.certificate["witness67"])
        witness["term_costs"][1] = 6
        witness["copy_cost"] = 66
        with self.assertRaisesRegex(ValueError, "full witness copy bill"):
            gram.check_witness(witness, self.roots, self.pairing)

    def test_missing_boundary_case(self):
        cert = deepcopy(self.certificate)
        cert["representative_cuts"].pop()
        with self.assertRaisesRegex(ValueError, "every representative"):
            gram.check(cert)

    def test_false_kernel_direction(self):
        cert = deepcopy(self.certificate)
        kernels = cert["representative_cuts"][0]["kernel_by_functional_hex"]
        key = next(iter(kernels))
        kernels[key] = (kernels[key] + 1) % 120
        with self.assertRaisesRegex(ValueError, "claimed kernel annihilates rows"):
            gram.check(cert)

    def test_missing_singular_functional(self):
        cert = deepcopy(self.certificate)
        kernels = cert["representative_cuts"][0]["kernel_by_functional_hex"]
        del kernels[next(iter(kernels))]
        with self.assertRaisesRegex(ValueError, "rank-eight Gram determinant"):
            gram.check(cert)

    def test_false_support_dimension(self):
        cert = deepcopy(self.certificate)
        cert["representative_cuts"][0]["support_dimensions"]["31"] = 8
        with self.assertRaisesRegex(ValueError, "independent support dimensions"):
            gram.check(cert)

    def test_determinant_singularity_and_pivot_controls(self):
        fixtures = [([[0, 2], [3, 4]], -6), ([[1, 2], [2, 4]], 0),
                    ([[4, 1, 2], [1, 3, 0], [2, 0, 5]], 43)]
        for matrix, determinant in fixtures:
            self.assertEqual(gram.bareiss(matrix), determinant)

    def test_changed_proof_source_rejected_without_touching_repository(self):
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory(prefix="e8-boundary-source-control-") as directory:
            root = Path(directory)
            for entry in manifest["files"]:
                if entry["usage"] == "input":
                    destination = root / entry["path"]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes((primary.ROOT / entry["path"]).read_bytes())
            with patch.object(primary, "ROOT", root):
                primary.source_pins()
                source = root / "research/complex-frame-pair-decoders/PROOF.md"
                source.write_bytes(source.read_bytes() + b"\nmutation control\n")
                with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                    primary.source_pins()


if __name__ == "__main__":
    unittest.main(verbosity=2)
