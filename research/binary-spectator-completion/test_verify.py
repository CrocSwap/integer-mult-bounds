#!/usr/bin/env python3
"""Failure controls for the conditional spectator adapter. Apache-2.0."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("spectator_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class AdapterTests(unittest.TestCase):
    def test_padding_and_restriction(self):
        shape = (3, 3, 5, 3, 2)
        data = list(range(1, 271))
        padded, _ = verify.pad(data, shape)
        self.assertEqual(verify.restrict(padded, shape), data)

    def test_exact_binary_boundary(self):
        for n in (1, 2, 3, 4, 7, 8, 9, 2**100-1, 2**100, 2**100+1):
            result = verify.binary_ceiling(n)
            self.assertLess(result, 2*n)
            self.assertGreaterEqual(result, n)
            self.assertEqual(result & (result-1), 0)

    def test_incomplete_and_callee_volume(self):
        shape = (1, 2, 1, 2, 1)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            verify.pad([1, 2, 3], shape)
        with self.assertRaisesRegex(ValueError, "volume"):
            verify.exchange([1, 2, 3, 4], shape, lambda values, _: values[:-1])

    def test_capacity_and_types(self):
        with self.assertRaisesRegex(ValueError, "capacity"):
            verify.pad([], (1, 1024, 1, 1024, 1))
        for n in (True, False, 1.0, "1", 0, -1):
            with self.assertRaises(ValueError):
                verify.binary_ceiling(n)

    def test_failure_source_and_receipt(self):
        # A relocated Git-free export exercises the same public entry point.
        with tempfile.TemporaryDirectory(prefix="spectator-completion-") as temp:
            root = Path(temp)
            destination = root / "research" / HERE.name
            shutil.copytree(HERE, destination)
            sources = verify.read_json(HERE / "SOURCES.json")
            for item in sources["files"]:
                if item["usage"] == "input":
                    target = root / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(verify.ROOT / item["path"], target)
            command = [sys.executable, "-I", "-O", "-B", str(destination / "verify.py")]
            def run():
                return subprocess.run(command, capture_output=True, text=True, timeout=120)
            positive = run()
            self.assertEqual(positive.returncode, 0, positive.stderr)
            receipt = destination / "RESULT.json"
            original = receipt.read_bytes()
            record = json.loads(original)
            record["symbolic_cases"] = True
            receipt.write_text(json.dumps(record), encoding="utf-8")
            self.assertNotEqual(run().returncode, 0)
            receipt.write_bytes(original)
            receipt.rename(destination / "SAVED.json")
            self.assertNotEqual(run().returncode, 0)
            (destination / "SAVED.json").rename(receipt)
            source = destination / "sources/pr2399/README.md"
            source.write_bytes(source.read_bytes() + b"\nchanged\n")
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("pending source hash mismatch", bad.stderr)

    def test_duplicate_json(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            json.loads('{"x":1,"x":2}', object_pairs_hook=verify.strict_object)


if __name__ == "__main__":
    unittest.main()
