#!/usr/bin/env python3
"""Behavioral controls for arithmetic budgets, ownership and source binding."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_checker():
    sys.path.insert(0, str(ROOT))
    import verify
    return verify


verify = load_checker()


class ArithmeticTests(unittest.TestCase):
    def test_sharp_inverse_and_occupied_content(self):
        self.assertEqual(verify.check_case("inverse", 5, 2, census=True),
                         {"peak": 10, "occupied": 70, "borrowed": 3,
                          "bits": 4, "result": 3})

    def test_every_one_word_underbudget_rejects(self):
        cases = {"divide": (2, 0, 1), "add": (2, 1, 1),
                 "subtract": (2, 0, 1), "negate": (2, 1, 0),
                 "multiply": (3, 2, 2), "inverse": (5, 2, 0)}
        for name, values in cases.items():
            with self.subTest(operation=name):
                good = verify.check_case(name, *values)
                self.assertEqual(good["peak"], verify.BOUNDS[name])
                with self.assertRaisesRegex(ValueError, "^scratch word budget$"):
                    verify.check_case(name, *values, budget=verify.BOUNDS[name] - 1)

    def test_nonunit_frees_all_temporaries(self):
        case = verify.check_case("inverse", 15, 6, census=True)
        self.assertIsNone(case["result"])
        self.assertEqual(case["peak"], 10)
        self.assertEqual(case["occupied"], 84)

    def test_borrowed_one_can_be_the_inverse_operand(self):
        arena = verify.TrackedArena(4)
        mod = arena.literal(5)
        ring = verify.Ring(mod)
        protected = frozenset(arena.live)
        arena.entry = arena.peak = len(protected)
        arena.budget = 10
        result = ring.inverse(ring.one)
        self.assertEqual(result.inspect(), 1)
        arena.free(result)
        self.assertEqual(frozenset(arena.live), protected)
        self.assertEqual(ring.one.inspect(), 1)
        self.assertEqual(mod.inspect(), 5)
        ring.close()
        arena.free(mod)
        self.assertEqual(arena.live, set())

    def test_alias_subtraction_and_division(self):
        self.assertEqual(verify.check_case("subtract", 9, 7, alias=True)["result"], 0)
        self.assertEqual(verify.check_case("divide", 9, 7, alias=True)["result"], (1, 0))

    def test_exact_arena_capacity_and_explicit_rollback(self):
        for capacity in (12, 13):
            with self.subTest(capacity=capacity):
                arena = verify.Arena(4, capacity=capacity)
                mod = arena.literal(5)
                ring = verify.Ring(mod)
                operand = arena.literal(2)
                protected = frozenset(arena.live)
                if capacity == 12:
                    with self.assertRaisesRegex(ValueError, "fixed register inventory"):
                        ring.inverse(operand)
                    arena.rollback(protected)
                else:
                    result = ring.inverse(operand)
                    self.assertEqual(result.inspect(), 3)
                    arena.free(result)
                self.assertEqual(frozenset(arena.live), protected)
                self.assertEqual(operand.inspect(), 2)
                arena.free(operand)
                ring.close()
                arena.free(mod)
                self.assertEqual(arena.live, set())

    def test_underbudget_failure_uses_caller_rollback(self):
        verify.rollback_control()
        self.assertEqual(verify.check_case("inverse", 5, 2)["result"], 3)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.path = Path(self.scratch.name) / "package"
        shutil.copytree(ROOT, self.path, ignore=shutil.ignore_patterns("__pycache__"))

    def run_export(self):
        return subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B",
                               str(self.path / "verify.py")],
                              cwd=self.scratch.name, text=True,
                              capture_output=True, timeout=60, check=False)

    def test_git_free_optimized_export(self):
        before = {str(p.relative_to(self.path)): p.read_bytes()
                  for p in self.path.rglob("*") if p.is_file()}
        run = self.run_export()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("PASS_SELECTED_WORD_SCRATCH inverse=10_words", run.stdout)
        after = {str(p.relative_to(self.path)): p.read_bytes()
                 for p in self.path.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_source_rejected_before_execution(self):
        path = self.path / "vendor" / "words.py"
        path.write_bytes(path.read_bytes() + b'\nraise RuntimeError("MUTANT_EXECUTED")\n')
        run = self.run_export()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("snapshot SHA256", run.stderr)
        self.assertNotIn("MUTANT_EXECUTED", run.stderr)

    def test_wrong_git_blob_rejects(self):
        path = self.path / "SNAPSHOTS.json"
        record = json.loads(path.read_text())
        record["files"][0]["git_blob"] = "0" * 40
        path.write_text(json.dumps(record))
        run = self.run_export()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("snapshot Git blob", run.stderr)

    def test_wrong_dependency_and_original_path_reject(self):
        path = self.path / "SNAPSHOTS.json"
        original = path.read_text()
        for mutation, message in (("commit", "scientific dependency"),
                                  ("path", "original source path")):
            with self.subTest(mutation=mutation):
                record = json.loads(original)
                if mutation == "commit":
                    record["source_commit"] = "0" * 40
                else:
                    record["files"][0]["source_path"] = "wrong/words.py"
                path.write_text(json.dumps(record))
                run = self.run_export()
                self.assertNotEqual(run.returncode, 0)
                self.assertIn(message, run.stderr)

    def test_missing_source_pin_rejects(self):
        path = self.path / "SNAPSHOTS.json"
        record = json.loads(path.read_text())
        record["files"].pop()
        path.write_text(json.dumps(record))
        run = self.run_export()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("complete snapshot inventory", run.stderr)

    def test_understated_receipt_rejects(self):
        path = self.path / "RESULT.json"
        record = json.loads(path.read_text())
        record["bounds"]["inverse"] = 9
        path.write_text(json.dumps(record))
        run = self.run_export()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("fixed arithmetic receipt", run.stderr)


if __name__ == "__main__":
    unittest.main()
