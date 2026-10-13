"""Arithmetic edge cases and faulty-optimizer/full-audit controls.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
"""

import contextlib
import copy
import importlib.util
import io
import shutil
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("verification", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class KernelTests(unittest.TestCase):
    def test_exact_cancellation_and_normalization(self):
        result = v.kernel.fused(F(3, 8), F(4, 16), F(-3, 32))
        self.assertEqual(result, 0)
        self.assertEqual((result.numerator, result.denominator), (0, 1))
        self.assertIs(type(result), F)

    def test_general_rational_fallback(self):
        self.assertEqual(v.kernel.fused(F(3, 7), F(2, 3), F(-1, 13)), F(19, 91))
        self.assertEqual(v.kernel.fused(F(3, 7), F(2, 3), None), F(2, 7))

    def test_large_denominator_alignment_both_directions(self):
        for q, x, y in [(F(2**190+1, 2**210), F(-3, 2**75), F(7, 8)),
                        (F(5, 2), F(17, 4), F(-11, 2**340))]:
            self.assertEqual(v.kernel.fused(q, x, y), y + q*x)

    def test_snapshot_preserves_aliased_row_behavior(self):
        row = {0: F(1), 1: F(1, 2)}
        initial = [row, row]
        reference, fused = copy.deepcopy(initial), copy.deepcopy(initial)
        v.adapter.auditor(engine="reference").apply(["add", 0, 1, -1, 1], reference)
        v.kernel.apply(["add", 0, 1, -1, 1], fused)
        self.assertEqual(reference, fused)
        self.assertEqual(fused, [{}, {}])

    def test_dual_scale_is_reciprocal(self):
        rows = [{0: F(3)}]
        v.kernel.apply(["scale", 0, -1, 8], rows, True)
        self.assertEqual(rows, [{0: F(-24)}])

    def run_fault(self, change, error="all-column endpoint failure"):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            word = directory / "FULL-WORD.json.gz"
            word.write_bytes(v.word_bytes())
            module = v.adapter.auditor(engine="fused")
            change(module)
            output = directory / "bad.json"
            log = io.StringIO()
            with contextlib.redirect_stdout(log):
                with self.assertRaisesRegex(RuntimeError, error):
                    module.run(word, output, v.ROOT)
            self.assertFalse(output.exists())
            return log.getvalue()

    def test_dropping_destination_detected_by_full_audit(self):
        def bad(module):
            module.apply.__globals__["fused"] = lambda q, x, y: q*x
        self.run_fault(bad, "nonzero entrance response")

    def test_missing_dual_detected_after_forward_success(self):
        def bad(module):
            correct = module.apply
            module.apply = lambda e, rows, dual=False: correct(e, rows, False)
        self.assertIn("endpoint forward PASS", self.run_fault(bad))

    def test_source_guard_rejects_changed_auditor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for item in v.adapter.source_pins()["files"]:
                dest = root / item["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(v.ROOT / item["path"], dest)
            source = root / v.adapter.AUDITOR
            source.write_bytes(source.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                v.adapter.auditor(root, "fused")

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "keep.json"
            path.write_text("preserve\n")
            with self.assertRaisesRegex(ValueError, "output already exists"):
                v.adapter.run(Path("unused.gz"), path)
            self.assertEqual(path.read_text(), "preserve\n")


if __name__ == "__main__":
    unittest.main()
