# SPDX-License-Identifier: Apache-2.0
"""Behavior and failure controls for the public candidate/padding CLI."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("transfer", HERE / "verify.py")
transfer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transfer)


class TransferTests(unittest.TestCase):
    def run_cli(self, data, *, output=False, raw=False):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "candidate.json"
            source.write_text(data if raw else json.dumps(data), encoding="utf-8")
            target = Path(directory) / "padded.json"
            args = [sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                    "--candidate", str(source)]
            if output:
                args += ["--pad-output", str(target)]
            result = subprocess.run(args, capture_output=True, text=True, timeout=60, check=False)
            saved = json.loads(target.read_text()) if target.exists() else None
            return result, saved

    def test_complete_retained_fixture_receipt(self):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py")],
                                capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout.split("\nPASS_")[0])
        observed = {name: (row["original"]["cost"], row["padded"]["cost"],
                           row["padded"]["terms"], row["padded"]["all_pairs_mismatches"])
                    for name, row in record["fixtures"].items()}
        self.assertEqual(observed, {
            "P120": (72, 72, 8, 0), "P112": (64, 72, 16, 896),
            "P111_HIT_g0.txt": (63, 72, 17, 1000),
            "P111_HIT_g111.txt": (63, 72, 17, 1000),
            "P104_HIT_flip_3a.txt": (56, 72, 24, 1728)})
        self.assertEqual(record["transfers"]["six_line_subsets"], 64)
        self.assertEqual(record["transfers"]["disjoint_gluing"]["cost"], 136)
        self.assertEqual(record["transfers"]["disjoint_gluing"]["all_pairs_mismatches"], 3168)

    def test_singleton_padding_and_reimport(self):
        data = {"live": [0], "terms": [{"left": [1], "right": [1]}]}
        result, saved = self.run_cli(data, output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout.split("\nPASS_")[0])
        self.assertEqual(record["original"]["cost"], 1)
        self.assertEqual(record["padded"]["cost"], 120)
        second, _ = self.run_cli(saved)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(json.loads(second.stdout.split("\nPASS_")[0])["ranks"], [1] * 120)

    def test_free_entry_and_forbidden_entry(self):
        free = next(j for j in range(1, 120) if not (transfer.PAIRING[0] >> j & 1))
        forbidden = next(j for j in range(1, 120) if transfer.PAIRING[0] >> j & 1)
        terms = [{"left": [1, 0], "right": [1, 0]},
                 {"left": [0, 1], "right": [0, 1]},
                 {"left": [1, 0], "right": [0, 7]}]
        result, _ = self.run_cli({"live": [0, free], "terms": terms})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout.split("\nPASS_")[0])["ranks"], [1, 1, 0])
        result, saved = self.run_cli({"live": [0, forbidden], "terms": terms}, output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("forbidden off-diagonal", result.stderr)
        self.assertIsNone(saved)

    def test_non_symmetric_rational_terms_and_reordered_ids(self):
        data = {"live": [1, 0], "terms": [
            {"left": ["1/3", 0], "right": [3, 0]},
            {"left": [0, -2], "right": [0, "-1/2"]}]}
        result, _ = self.run_cli(data, output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout.split("\nPASS_")[0])
        self.assertEqual(record["original"]["ranks"], [1, 1])
        self.assertEqual(record["padded"]["cost"], 120)
        self.assertGreater(record["padded"]["all_pairs_mismatches"], 0)

    def test_semantic_corruptions(self):
        cases = [
            ({"live": [0, 1], "terms": [{"left": [1, 0], "right": [1, 0]}]}, "diagonal"),
            ({"live": [0], "terms": [{"left": [1], "right": [-1]}]}, "diagonal"),
            ({"live": [0, 0], "terms": []}, "duplicate line"),
            ({"live": [True], "terms": []}, "line ID"),
            ({"live": [120], "terms": []}, "line ID"),
            ({"live": [0], "terms": [{"left": [1, 0], "right": [1]}]}, "factor width"),
            ({"live": [0], "terms": [{"left": [1.0], "right": [1]}]}, "rational coefficient"),
            ({"live": [0], "terms": [{"left": [True], "right": [1]}]}, "rational coefficient"),
            ({"live": [0], "terms": [{"left": ["1/0"], "right": [1]}]}, "REJECT"),
            ({"live": [0], "terms": [{"left": ["1e1000000000"], "right": [1]}]},
             "rational coefficient syntax"),
            ({"live": [0], "terms": [{"left": [str(1 << 256)], "right": [1]}]}, "coefficient domain"),
            ({"live": [], "terms": [{"left": [], "right": []}] * 257}, "term capacity"),
        ]
        for data, reason in cases:
            with self.subTest(reason=reason):
                result, saved = self.run_cli(data, output=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn(reason, result.stderr)
                self.assertIsNone(saved)

    def test_empty_set_and_input_capacity(self):
        result, saved = self.run_cli({"live": [], "terms": []}, output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout.split("\nPASS_")[0])
        self.assertEqual(record["original"]["cost"], 0)
        self.assertEqual(record["padded"]["cost"], 120)
        self.assertEqual(len(saved["live"]), 120)
        result, _ = self.run_cli({"live": [0] * 121, "terms": []})
        self.assertEqual(result.returncode, 1)
        self.assertIn("live capacity", result.stderr)

    def test_byte_and_json_depth_limits(self):
        for payload in (" " * (16 * 1024 * 1024 + 1), "[" * 4000 + "]" * 4000):
            result, saved = self.run_cli(payload, raw=True, output=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("REJECT", result.stderr)
            self.assertIsNone(saved)

    def test_duplicate_json_fields(self):
        result, _ = self.run_cli('{"live":[0],"live":[],"terms":[]}', raw=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate JSON key", result.stderr)

    def test_denominator_capacity_before_dense_arithmetic(self):
        data = {"live": [0], "terms": [
            {"left": ["1/" + str(1 << 200)], "right": ["1/" + str((1 << 199) - 1)]}]}
        result, _ = self.run_cli(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("common denominator capacity", result.stderr)

    def test_zero_cost_terms_cannot_supply_a_missing_diagonal(self):
        free = next(j for j in range(1, 120) if not (transfer.PAIRING[0] >> j & 1))
        result, _ = self.run_cli({"live": [0, free], "terms": [
            {"left": [1, 0], "right": [0, 1]}]})
        self.assertEqual(result.returncode, 1)
        self.assertIn("diagonal", result.stderr)

    def test_source_corruption_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = next(r for r in json.loads((HERE / "SOURCES.json").read_text())["files"]
                       if r["usage"] == "input")
            path = root / row["path"]
            path.parent.mkdir(parents=True)
            path.write_text("changed source", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source hash"):
                transfer.check_pins(root)
            source = root / "input.json"
            source.write_text('{"live":[0],"terms":[{"left":[1],"right":[1]}]}')
            target = root / "existing.json"
            target.write_text("preserve me")
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                     "--candidate", str(source), "--pad-output", str(target)],
                                    capture_output=True, text=True, timeout=60, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(target.read_text(), "preserve me")


if __name__ == "__main__":
    unittest.main()
