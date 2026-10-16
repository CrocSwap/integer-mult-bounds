"""Behavioral controls for the source-bound exact sensitivity replay."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HOME = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("clean_dual_audit", HOME / "verify.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class SensitivityControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = AUDIT.load_json(HOME / "WORD.json")

    def test_cleanup_omission_and_wrong_sign_fail_zero(self):
        for coefficient in ("0", "1"):
            bad = copy.deepcopy(self.word)
            bad["program"][1830][3] = coefficient
            with self.assertRaisesRegex(ValueError, "ideal private erasure must be zero"):
                AUDIT.forward(bad)

    def test_missing_native_return_fails_common_chart(self):
        bad = copy.deepcopy(self.word)
        bad["program"][1825] = ["sign", "C", "-1", bad["program"][1825][2]]
        with self.assertRaisesRegex(ValueError, "common ADD chart"):
            AUDIT.forward(bad)

    def test_wrong_source_sign_rejects_complete_boundary(self):
        bad = copy.deepcopy(self.word)
        bad["program"][0][1] = "X1"
        inputs, errors, *_ = AUDIT.forward(bad)
        with self.assertRaisesRegex(ValueError, "complete inverse-transpose boundary: X0"):
            AUDIT.boundary_check(inputs, errors, bad)

    def test_input_and_trace_bounds(self):
        self.assertEqual(AUDIT.span((1, 2)), frozenset((0, 1, 2, 3)))
        self.assertEqual(AUDIT.span(tuple(1 << i for i in range(9))), frozenset(range(512)))
        with self.assertRaisesRegex(ValueError, "binary frame"):
            AUDIT.span(tuple(1 << i for i in range(10)))
        bad = copy.deepcopy(self.word)
        bad["program"].append(bad["program"][-1])
        with self.assertRaisesRegex(ValueError, "fixed word size"):
            AUDIT.forward(bad)
        with tempfile.TemporaryDirectory() as temporary:
            oversized = Path(temporary) / "oversized.json"
            oversized.write_bytes(b" " * (AUDIT.MAX_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "bounded input bytes"):
                AUDIT.load_json(oversized)

    def test_signed_cancellation_and_rounded_zero_debt(self):
        row = {"dirty": AUDIT.Q(1)}
        AUDIT.add_scaled(row, {"dirty": AUDIT.Q(-1)}, AUDIT.Q(1))
        self.assertEqual(row, {})
        self.assertEqual(AUDIT.scalar_execute(self.word, 1831, "C", {"D31": AUDIT.Q(1)}, {}), 0)
        self.assertEqual(AUDIT.scalar_execute(self.word, 1831, "C", {"D31": AUDIT.Q(1)}, {1825: AUDIT.Q(1, 1024)}), AUDIT.Q(1, 1024))
        state = AUDIT.scalar_execute(self.word, AUDIT.EVENTS, None, {}, {1825: AUDIT.Q(1)})
        self.assertEqual(state, {r: 0 for r in self.word["initial_frames"]})

    def test_git_free_cli_source_receipt_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "research" / HOME.name
            shutil.copytree(HOME, package, ignore=shutil.ignore_patterns("__pycache__"))
            for row in AUDIT.load_json(HOME / "SOURCES.json")["files"]:
                if row["usage"] == "input":
                    target = root / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(AUDIT.ROOT / row["path"], target)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_P104_CLEAN_DUAL_PRECISION", result.stdout)
            receipt = package / "RESULT.json"
            original = receipt.read_bytes()
            corrupted = json.loads(original)
            corrupted["events"] = float(corrupted["events"])
            receipt.write_text(json.dumps(corrupted))
            result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("committed scientific receipt mismatch", result.stderr)
            receipt.write_bytes(original)
            result = subprocess.run(command + ["--write-result", str(receipt)], capture_output=True, text=True, timeout=120, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileExistsError", result.stderr)
            word_path = package / "WORD.json"
            word_path.write_bytes(word_path.read_bytes() + b" ")
            result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)


if __name__ == "__main__":
    unittest.main()
