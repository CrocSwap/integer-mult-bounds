#!/usr/bin/env python3
"""Subprocess corruption and relocation controls for the research certificate.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
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

PACKAGE = Path(__file__).resolve().parent


class CertificateControls(unittest.TestCase):
    def run_script(self, script, cwd, certificate=None):
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        if certificate is not None:
            command += ["--certificate", str(certificate)]
        return subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                              timeout=90, check=False)

    def test_relocated_optimized_positive_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relocated = root / "package"
            relocated.mkdir()
            for name in ("verify.py", "independent.py", "CERTIFICATE.json"):
                shutil.copyfile(PACKAGE / name, relocated / name)
            for name in ("verify.py", "independent.py"):
                with self.subTest(engine=name):
                    result = self.run_script(relocated / name, root)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("PASS_SHEAR_3X4", result.stdout)

    def test_corrupted_certificates_are_rejected(self):
        original = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
        variants = []
        # Same correct endpoint, but the asserted minimum is deliberately too
        # large. Only a shorter-word check can rule out the new claimed cost.
        inflated = copy.deepcopy(original)
        one = next(row for row in inflated["orbits"] if row["minimum"] == 1)
        one["restricted_witness"] = [[0, 1], [0, 1]] + one["restricted_witness"]
        one["minimum"] += 2
        variants.append(("inflated_minimum_with_valid_word", inflated,
                         "shorter unrestricted word exists"))
        dirty = copy.deepcopy(original)
        one = next(row for row in dirty["orbits"] if row["minimum"] == 1)
        one["restricted_witness"][0][1] = 1
        variants.append(("wrong_dirty_input_column", dirty, "representative dirty endpoint"))
        omitted = copy.deepcopy(original)
        omitted["orbits"].pop()
        variants.append(("omitted_orbit", omitted, "missing labeled shear"))
        spheres = copy.deepcopy(original)
        spheres["unrestricted"]["spheres"][-1] -= 1
        variants.append(("incomplete_ball_receipt", spheres, "sphere counts differ"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for label, data, diagnostic in variants:
                path = root / (label + ".json")
                path.write_text(json.dumps(data))
                for name in ("verify.py", "independent.py"):
                    with self.subTest(corruption=label, engine=name):
                        result = self.run_script(PACKAGE / name, root, path)
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn("certificate differs" if name == "verify.py"
                                      else diagnostic, result.stderr)

    def test_predecessor_3x3_census(self):
        # Recompute the smaller PR1306 theorem with the new coset method.
        # Neither the predecessor implementation nor its certificate is loaded.
        spec = importlib.util.spec_from_file_location("coset_checker", PACKAGE / "verify.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        expected = [1, 9, 36, 84, 126, 132, 96, 28]
        for feedback, spheres in (
                (False, [1, 21, 264, 2436, 17142]),
                (True, [1, 30, 570, 8415, 101610])):
            with self.subTest(feedback=feedback):
                result = module.census(3, 3, feedback)
                self.assertEqual(result["spheres"], spheres)
                self.assertEqual([result["lengths"].count(i) for i in range(8)], expected)


if __name__ == "__main__":
    unittest.main()
