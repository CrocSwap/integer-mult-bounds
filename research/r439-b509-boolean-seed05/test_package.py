#!/usr/bin/env python3
"""Source/certificate controls and relocated optimized replay. Apache-2.0.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
"""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b509_verifier", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="b509 package space ")
        cls.root = Path(cls.temporary.name) / "source root"
        cls.package = cls.root / "research/r439-b509-boolean-seed05"
        shutil.copytree(HERE, cls.package, ignore=shutil.ignore_patterns("__pycache__"))
        for name in V.SOURCE_PATHS:
            target = cls.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(V.ROOT / name, target)
        cls.receipt = V.load(HERE / "EXPECTED.json")
        cls.base = V.load(V.ROOT / V.WORD)
        cls.prior = V.load(V.ROOT / V.PRIOR)["gates"]
        cls.gates = V.load(HERE / "CANDIDATE.json")["gates"]
        cls.candidate = V.replace(cls.base, cls.gates)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def command(self, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", self.package / "verify.py", *args],
                              cwd=self.temporary.name, capture_output=True, text=True)

    def test_01_relocated_optimized_receipt(self):
        out = Path(self.temporary.name) / "relocated output"
        result = self.command("--output", str(out))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(V.load(out / "RESULT.json"), self.receipt)

    def test_02_corrupted_source_rejected(self):
        path = self.root / V.WORD
        raw = path.read_bytes()
        try:
            path.write_bytes(raw + b"corrupted")
            result = self.command()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)
        finally:
            path.write_bytes(raw)

    def test_03_candidate_receipt_cannot_underbill(self):
        path = self.package / "EXPECTED.json"
        raw = path.read_bytes()
        bad = copy.deepcopy(self.receipt)
        bad["words"]["candidate"]["additions"] -= 1
        try:
            V.write(path, bad)
            result = self.command()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)
        finally:
            path.write_bytes(raw)

    def test_04_preserve_existing_output(self):
        output = Path(self.temporary.name) / "existing output"
        output.mkdir()
        sentinel = output / "sentinel"
        sentinel.write_text("preserve me")
        result = self.command("--output", str(output))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("output already exists", result.stderr)
        self.assertEqual(sentinel.read_text(), "preserve me")
        self.assertEqual(list(output.iterdir()), [sentinel])

    def test_05_dirty_helper_is_arbitrary(self):
        # All incoming helper values are preserved with the same increment.
        for dirty in (0, 1):
            for source in (0, 1):
                values = {w: dirty if w == 468 else source if w == 33 else 0 for w in V.WIRES}
                result = []
                for gates in (self.base["B"][283:314], self.gates):
                    state = dict(values)
                    for d, s in V.operations(gates):
                        state[d] ^= state[s]
                    result.append(state)
                self.assertEqual(*result)
                self.assertEqual(result[0][468], dirty ^ source)

    def test_06_integer_equality_is_false(self):
        self.assertNotEqual(V.column_map(self.prior), V.column_map(self.gates))
        self.assertEqual(V.column_map(self.prior, 2), V.column_map(self.gates, 2))
        self.assertNotEqual(V.column_map(self.prior, 3), V.column_map(self.gates, 3))

    def test_07_typed_and_foreign_operands(self):
        for invalid in ([True, 38, [33]], [509, True, [33]],
                        [509, 38, [True]], [509, 38, [660]], [509, 38, [38]]):
            with self.assertRaises(ValueError):
                V.operations([invalid])

    def test_08_duplicate_json_key(self):
        with self.assertRaises(ValueError):
            json.loads('{"frame":509,"frame":0}', object_pairs_hook=V.strict_pairs)

    def test_09_positive_growth_guard_is_not_f2_equality(self):
        # A two-gate square is identity mod 2 but changes the positive matrix.
        extra = [[509, 38, [33]], [509, 38, [33]]]
        self.assertEqual(V.column_map(self.gates, 2), V.column_map(self.gates + extra, 2))
        self.assertNotEqual(V.column_map(self.gates), V.column_map(self.gates + extra))

    def test_10_concurrent_block_comparisons(self):
        earlier = V.load(HERE / "OVERLAP1127.json")
        same_mechanism = V.load(HERE / "OVERLAP1208.json")
        self.assertEqual(len(earlier["gates"]), 22)
        self.assertEqual(len(same_mechanism["gates"]), 20)
        for item in (earlier, same_mechanism):
            self.assertEqual(V.column_map(item["gates"], 2), V.column_map(self.gates, 2))
        self.assertEqual(V.column_map(same_mechanism["gates"]), V.column_map(self.gates))
        self.assertNotEqual(same_mechanism["gates"], self.gates)


if __name__ == "__main__":
    unittest.main()
