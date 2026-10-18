"""Independent rounding oracle and public-command behavior.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from bisect import bisect_left
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rounded_f0", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def nearest_table(value, candidates, bits):
    """Definition-level finite set oracle; no logarithm or quotient rounding."""
    index = bisect_left(candidates, value)
    if candidates[index] == value:
        return value
    low, high = candidates[index - 1:index + 1]
    distance_low, distance_high = value - low, high - value
    if distance_low != distance_high:
        return low if distance_low < distance_high else high
    # Determine parity by expressing each endpoint on the shared local grid.
    step = high - low
    return low if (low / step).denominator == 1 and int(low / step) % 2 == 0 else high


class RoundedF0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events, _ = v.load_events()

    def test_rounding_against_enumerated_number_system(self):
        checks = 0
        for bits in range(2, 8):
            positive = {Q(m) * Q(2) ** e for e in range(-20, 8)
                        for m in range(2 ** (bits - 1), 2 ** bits)}
            candidates = sorted(positive | {-x for x in positive} | {Q(0)})
            for denominator_power in range(10):
                for numerator in range(-64, 65):
                    value = Q(numerator, 2 ** denominator_power)
                    self.assertEqual(v.rn(value, bits), nearest_table(value, candidates, bits))
                    checks += 1
        self.assertEqual(checks, 7740)
        # Explicit ties across a binade boundary, including negative values.
        self.assertEqual(v.rn(Q(15, 8), 3), Q(2))
        self.assertEqual(v.rn(Q(-15, 8), 3), Q(-2))
        self.assertEqual(v.rn(Q(9, 8), 3), Q(1))
        self.assertEqual(v.rn(Q(11, 8), 3), Q(3, 2))

    def test_power_of_two_scaling_and_sign(self):
        baseline, _ = v.execute(self.events, v.initial(53), 53)
        for scale in (Q(-1), Q(1, 128), Q(16)):
            entry = v.initial(53, signal=scale)
            actual, info = v.execute(self.events, entry, 53)
            self.assertEqual(actual, [scale * x for x in baseline])
            self.assertEqual(actual[224:], entry[224:])
            self.assertEqual([f["event"] for f in info["faults"]], [3887, 4060])

    def test_real_word_semantic_controls(self):
        # A changed sign or an omitted dirty cancellation must fail the original
        # endpoint contract, rather than merely change a cosmetic trace hash.
        for at, replacement in ((3887, None), (4060, None), (3887, 1)):
            altered = self.events.copy()
            if replacement is None:
                altered.pop(at)
            else:
                gate = altered[at][1].copy()
                gate[3] = replacement
                altered[at] = ["scalar", gate, altered[at][2]]
            with self.assertRaisesRegex(ValueError, "Exact witness endpoint"):
                v.witness(altered, 53)

    def test_git_free_optimized_public_cli_and_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            source_rel = "research/joint-query/certificate.json.gz"
            source = root / source_rel
            source.parent.mkdir(parents=True)
            shutil.copyfile(v.ROOT / source_rel, source)
            command = [sys.executable, "-Werror", "-I", "-O", "-B", str(package / "verify.py")]

            def run():
                return subprocess.run(command, text=True, capture_output=True, timeout=90)

            good = run()
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("PASS_QQ16_F0_ROUNDED_SCALAR", good.stdout)
            receipt = package / "RESULT.json"
            original = receipt.read_bytes()
            receipt.write_bytes(original.replace(b'"event_count": 26099', b'"event_count": 26098'))
            bad_receipt = run()
            self.assertNotEqual(bad_receipt.returncode, 0)
            self.assertIn("Receipt mismatch", bad_receipt.stderr)
            receipt.write_bytes(original)
            source.write_bytes(b"wrong immutable input")
            bad_source = run()
            self.assertNotEqual(bad_source.returncode, 0)
            self.assertIn("Source hash mismatch", bad_source.stderr)

    def test_numeric_and_namespace_boundaries(self):
        for bits in (1, 257, True):
            with self.assertRaisesRegex(ValueError, "Precision range"):
                v.rn(Q(1), bits)
        with self.assertRaisesRegex(ValueError, "Non-dyadic"):
            v.rn(Q(1, 3), 53)
        for token in (("X", 0), ("C", 8), ("L", -1)):
            with self.assertRaises(ValueError):
                v.register(token)


if __name__ == "__main__":
    unittest.main()
