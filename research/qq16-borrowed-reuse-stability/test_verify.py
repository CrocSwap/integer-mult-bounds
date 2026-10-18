"""Behavior tests for the source-bound reuse audit. Apache-2.0."""

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("reuse_verifier", HERE / "verify.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class ReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = VERIFY.load_word(HERE)

    def run_cli(self, package, *args):
        return subprocess.run(
            [sys.executable, "-I", "-Werror", "-B", str(package / "verify.py"), *args],
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )

    def test_complete_source_projection(self):
        result = VERIFY.audit_word(self.word)
        self.assertEqual(result["pairs"][0], ["Y0", 2351, 2355, 0])
        self.assertEqual(result["pairs"][1], ["Y1", 81, 85, 1])
        self.assertEqual(result["read_only_X"], 112)
        self.assertEqual(result["restored_Y_pairs"], 112)
        self.assertEqual(result["borrowed_other_writes"], 0)

    def test_exact_and_biased_full_word_returns(self):
        current = {name: Q(0) for name in VERIFY.BORROWED}
        current.update(X1=Q(3), Y1=Q(1))
        exact = VERIFY.execute_constant(self.word, current, Q(0))
        self.assertEqual((exact["X1"], exact["Y1"]), (Q(3), Q(1)))
        for _ in range(3):
            current = VERIFY.execute_constant(self.word, current, Q(1, 2))
        self.assertEqual((current["X1"], current["Y1"]), (Q(3), Q(729, 64)))

    def test_nonconstant_native_action(self):
        vector = ((Q(1), Q(2)), (Q(-3), Q(4)))
        transformed = VERIFY.line(vector, 1, Q(0))
        self.assertEqual(transformed, ((Q(0), Q(5)), (Q(-2), Q(1))))
        self.assertEqual(sum(x * x for z in transformed for x in z), Q(30))
        returned = VERIFY.line(transformed, -1, Q(0))
        self.assertEqual(returned, vector)
        biased = VERIFY.line(VERIFY.line(vector, 1, Q(1, 2)), -1, Q(1, 2))
        self.assertEqual(biased, ((Q(9, 4), Q(9, 2)), (Q(-27, 4), Q(9))))

    def test_mutated_inverse_and_extra_borrowed_writes(self):
        for index, changes, message in [
            (85, {"sign": 1}, "missing native inverse pair"),
            (85, {"port": 2}, "wrong line label"),
            (81, {"port": True}, "wrong line label"),
            (81, {"op": "clear"}, "non-native borrowed write"),
        ]:
            mutant = copy.deepcopy(self.word)
            mutant[index].update(changes)
            with (
                self.subTest(changes=changes),
                self.assertRaisesRegex(ValueError, message),
            ):
                VERIFY.audit_word(mutant)
        mutant = copy.deepcopy(self.word)
        mutant[81] = {"op": "private_begin", "fields": ["Y1"], "name": "invalid"}
        with self.assertRaisesRegex(ValueError, "borrowed private lifetime"):
            VERIFY.audit_word(mutant)
        self.assertEqual(VERIFY.check_controls(self.word), 7)

    def test_capacity_and_temporal_boundary(self):
        with self.assertRaisesRegex(ValueError, "complete 2463-event"):
            VERIFY.audit_word(self.word[:-1])
        mutant = copy.deepcopy(self.word)
        mutant[32] = {"op": "checkpoint", "name": "lost_boundary"}
        with self.assertRaisesRegex(ValueError, "temporal boundary"):
            VERIFY.audit_word(mutant)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized"
            path.write_bytes(b"x" * ((1 << 18) + 1))
            with self.assertRaisesRegex(ValueError, "capacity"):
                VERIFY.read_bytes(path)

    def test_external_read_only_replay_and_overwrite_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "export"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            files = sorted(path for path in package.rglob("*") if path.is_file())
            before = {path: path.read_bytes() for path in files}
            run = self.run_cli(package)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PASS_QQ16_BORROWED_REUSE pairs=112", run.stdout)
            self.assertEqual(before, {path: path.read_bytes() for path in files})
            result_path = Path(directory) / "new-result.json"
            write = self.run_cli(package, "--write", str(result_path))
            self.assertEqual(write.returncode, 0, write.stderr)
            saved = result_path.read_bytes()
            again = self.run_cli(package, "--write", str(result_path))
            self.assertNotEqual(again.returncode, 0)
            self.assertIn("FileExistsError", again.stderr)
            self.assertEqual(result_path.read_bytes(), saved)

    def test_real_source_corruption_rejects_before_replay(self):
        for filename in ("WORD.json", "PR2540-PROOF.md", "PR2628-PROOF.md"):
            with (
                self.subTest(filename=filename),
                tempfile.TemporaryDirectory() as directory,
            ):
                package = Path(directory) / "export"
                shutil.copytree(
                    HERE, package, ignore=shutil.ignore_patterns("__pycache__")
                )
                path = package / "sources" / filename
                path.write_bytes(path.read_bytes() + b"\n")
                run = self.run_cli(package)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("source SHA256 drift", run.stderr)
                self.assertNotIn("PASS_QQ16", run.stdout)

    def test_typed_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "export"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            path = package / "RESULT.json"
            result = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(result["borrowed_other_writes"], 0)
            result["borrowed_other_writes"] = False
            path.write_text(json.dumps(result), encoding="utf-8")
            run = self.run_cli(package)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("typed result receipt drift", run.stderr)

    def test_small_precision_witness_and_horizon_guard(self):
        initial = {name: Q(0) for name in VERIFY.BORROWED}
        initial["Y1"] = Q(1)
        biased = initial
        for _ in range(3):
            biased = VERIFY.execute_constant(self.word, biased, Q(1, 2))
        self.assertEqual(biased["Y1"] - 1, Q(665, 64))
        for uses in (1, 2, 3, 7, 16):
            current = initial
            for _ in range(uses):
                current = VERIFY.execute_constant(self.word, current, Q(1, 4 * uses))
            self.assertGreater(current["Y1"], 1)
            self.assertLessEqual(current["Y1"] - 1, 1)


if __name__ == "__main__":
    unittest.main()
