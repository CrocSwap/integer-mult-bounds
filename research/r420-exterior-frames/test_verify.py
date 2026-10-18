"""Focused algebra and failure-detection checks; Python standard library only.

Prepared for Ishan (@ishan-1729) with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

import gzip
import importlib.util
from itertools import permutations, product
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("exterior_verifier", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ExteriorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((HERE / "SOURCE.json").read_text())
        cls.word_path = v.ROOT / cls.source["word"]["path"]
        cls.word = v.load_word(cls.word_path, cls.source)
        cls.receipt = v.build_receipt(cls.word, cls.source)

    def test_three_dimensional_leibniz_oracle(self):
        # All 512 binary 3x3 matrices, including singular and negative determinants.
        # The oracle explicitly sums signed permutations; no exterior operations.
        terms = [(p, (-1) ** sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3)))
                 for p in permutations(range(3))]
        for values in product((0, 1), repeat=9):
            matrix = [values[i:i + 3] for i in (0, 3, 6)]
            expected = sum(sign * matrix[0][p[0]] * matrix[1][p[1]] * matrix[2][p[2]]
                           for p, sign in terms)
            blade = {0: 1}
            for row in matrix:
                blade = v.wedge(blade, row)
            self.assertEqual(blade.get(7, 0), expected)

    def test_projectors_on_nonorthogonal_examples(self):
        # Span((1,1,0), (0,1,1)) has normal (1,-1,1), hence P=I-n*n^T/3.
        blade = v.wedge(v.wedge({0: 1}, [1, 1, 0]), [0, 1, 1])
        matrix = v.projection_numerator(blade, 3)
        self.assertEqual(matrix, [[2, 1, -1], [1, 2, 1], [-1, 1, 2]])
        v.check_projector(matrix, 3, 2)
        self.assertEqual(v.projection_numerator({0: 1}, 3), [[0] * 3 for _ in range(3)])
        self.assertEqual(v.projection_numerator({7: 1}, 3), [[int(i == j) for j in range(3)] for i in range(3)])

    def test_all_frames_basis_order_invariant(self):
        for ids, expected in zip(self.word["frames"], self.receipt["frames"]):
            alternate, _ = v.frame_certificate(self.word["lines"], ids, seed=0)
            self.assertEqual(alternate["blade"], expected["blade"])
            self.assertEqual(alternate["norm_squared"], expected["norm_squared"])
            self.assertEqual(alternate["projector_denominator"], expected["projector_denominator"])
            v.check_dyadic(alternate)

    def test_mathematical_controls(self):
        self.assertEqual(len(self.receipt["controls"]["rejected"]), 8)
        a2 = self.receipt["controls"]["A2_control"]
        self.assertEqual(a2["root_ids"], [0, 73, 78])
        self.assertEqual(a2["norm_squared"], 3)
        self.assertTrue(any(a2["radical_mod_3"]))

    def test_receipt_matches_all_fields(self):
        self.assertEqual(self.receipt, json.loads((HERE / "CERTIFICATE.json").read_text()))

    def test_recompressed_input_and_corruption(self):
        with TemporaryDirectory(prefix="r420 exterior ") as tmp:
            path = Path(tmp) / "word.json.gz"
            path.write_bytes(gzip.compress(json.dumps(self.word, indent=1).encode(), compresslevel=1, mtime=78))
            self.assertEqual(v.load_word(path, self.source), self.word)
            corrupted = json.loads(json.dumps(self.word))
            corrupted["frames"][1].pop()
            path.write_bytes(gzip.compress(json.dumps(corrupted).encode(), mtime=0))
            with self.assertRaisesRegex(v.Reject, "word semantic SHA-256 mismatch"):
                v.load_word(path, self.source)

    def test_cli_rejects_tampered_certificate_without_output(self):
        with TemporaryDirectory(prefix="r420 exterior ") as tmp:
            tmp = Path(tmp)
            bad = json.loads(json.dumps(self.receipt))
            bad["frames"][78]["norm_squared"] += 1
            certificate = tmp / "bad certificate.json"
            certificate.write_text(json.dumps(bad))
            output = tmp / "output.json"
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                     "--check", str(certificate), "--output", str(output)],
                                    cwd=tmp, text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 1)
            self.assertIn("certificate mismatch", result.stderr)
            self.assertFalse(output.exists())

    def test_output_reuse_is_rejected_and_preserved(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "existing.json"
            output.write_text("preserve me")
            with self.assertRaisesRegex(v.Reject, "output already exists"):
                v.main(["--output", str(output)])
            self.assertEqual(output.read_text(), "preserve me")


if __name__ == "__main__":
    unittest.main(verbosity=2)
