"""Independent determinant oracle and live-input binding controls. Apache-2.0."""
from fractions import Fraction
import importlib.util
import itertools
import json
import math
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("native_lift_verifier", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def permutation_determinant(matrix):
    """Leibniz sum, independent of the verifier's elimination/inverse witness."""
    denominator = math.lcm(*(x.denominator for row in matrix for x in row))
    integers = [[int(x*denominator) for x in row] for row in matrix]
    total, n = 0, len(matrix)
    for p in itertools.permutations(range(n)):
        product = math.prod(integers[i][p[i]] for i in range(n))
        if product:
            odd = sum(p[i] > p[j] for i in range(n) for j in range(i+1, n)) % 2
            total += -product if odd else product
    return Fraction(total, denominator**n)


class IndependentChecks(unittest.TestCase):
    def test_three_minor_determinants_by_permutations(self):
        result = json.loads((HERE / "RESULT.json").read_text())
        for matrix, determinant in (("source_minor", "source_minor_det"),
                                    ("scatter_minor", "scatter_minor_det"),
                                    ("native_output_coefficient_minor", "native_output_coefficient_det")):
            a = [[Fraction(x) for x in row] for row in result[matrix]]
            self.assertEqual(permutation_determinant(a), Fraction(result[determinant]))
            a[-1] = a[0].copy()
            self.assertEqual(permutation_determinant(a), 0)

    def copy_inputs(self, destination):
        pins = json.loads((HERE / "SOURCES.json").read_text())
        for row in pins["files"]:
            if row["usage"] == "input":
                target = destination / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(V.ROOT / row["path"], target)

    def test_input_relocation_then_archive_corruption(self):
        with tempfile.TemporaryDirectory(prefix="centre-rank-inputs-") as tmp:
            root = Path(tmp)
            self.copy_inputs(root)
            data, kernel = V.load(root)
            self.assertEqual(kernel.DIM, 512)
            self.assertEqual(len(data["programs"]["forward"]), 24767)
            archive = root / V.ARCHIVE
            with archive.open("ab") as output:
                output.write(b"corruption")
            with self.assertRaisesRegex(ValueError, "source hash"):
                V.load(root)

    def test_kernel_corruption_rejected_before_import(self):
        with tempfile.TemporaryDirectory(prefix="centre-rank-kernel-") as tmp:
            root = Path(tmp)
            self.copy_inputs(root)
            with (root / V.KERNEL).open("a") as output:
                output.write('\nraise RuntimeError("unbound kernel executed")\n')
            with self.assertRaisesRegex(ValueError, "source hash"):
                V.load(root)


if __name__ == "__main__":
    unittest.main()
