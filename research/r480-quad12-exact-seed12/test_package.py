"""Admission and packaging failure modes. Hanson Sun, Codex assistance; Apache-2.0."""
import copy
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Package(unittest.TestCase):
    def test_independent_minimum_detects_wrong_claims(self):
        check = runpy.run_path(str(HERE / "optimality.py"))["check_minimum"]
        identity = [[int(i == j) for j in range(6)] for i in range(6)]
        one = copy.deepcopy(identity)
        one[0][1] = 1
        self.assertEqual(check(identity, 0)["minimum"], 0)
        self.assertEqual(check(one, 1)["minimum"], 1)
        commuting = copy.deepcopy(one)
        commuting[2][3] = 1
        self.assertEqual(check(commuting, 2)["shortest_programs"], 2)
        with self.assertRaisesRegex(ValueError, "below independent distance"):
            check(one, 0)
        with self.assertRaisesRegex(ValueError, "exceeds independent distance"):
            check(one, 2)
        with self.assertRaisesRegex(ValueError, "invalid claimed distance"):
            check(one, True)

    def test_source_location_and_wire_binding(self):
        v = runpy.run_path(str(HERE / "verify.py"))
        original = v["C"]["original_word"]()
        witness = json.loads((HERE / "WITNESS.json").read_text())
        for field, value in (("start", 848), ("frame", 313), ("assignment_seed", True),
                             ("registers", list(reversed(witness["registers"])))):
            bad = copy.deepcopy(witness)
            bad[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "witness location"):
                v["build"](original, bad)

    def test_existing_output_survives(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "marker"
            marker.write_text("retain")
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                     "--output", directory], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileExistsError", result.stderr)
            self.assertEqual(marker.read_text(), "retain")

    def test_minimal_offline_optimized_replay_and_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="quad12 minimal path with spaces ") as directory:
            root = Path(directory)
            package = root / HERE.relative_to(ROOT)
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            pins = json.loads((HERE / "SOURCES.json").read_text())
            for relative in pins["execution_inputs"]:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            env = {**os.environ, "PYTHONOPTIMIZE": "2", "PYTHONPATH": "/nonexistent/quad12"}

            def run(*extra):
                return subprocess.run(command + list(extra), text=True, capture_output=True, env=env)

            good = run()
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            certificate = package / "CERTIFICATE.json"
            before = certificate.read_bytes()
            corrupted = json.loads(before)
            corrupted["independent_minimum"]["layers"][0] = True
            certificate.write_text(json.dumps(corrupted))
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("certificate mismatch", bad.stderr)
            certificate.write_bytes(before)
            source = root / next(iter(pins["execution_inputs"]))
            source.write_bytes(source.read_bytes() + b"corrupt")
            bad = run("--write-certificate")
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source SHA256 mismatch", bad.stderr)
            self.assertEqual(certificate.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
