#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Complete replays and semantic controls for the finite copy-cost theorem."""

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


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def run(script, *args, package=HERE):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script), *map(str, args)], capture_output=True, text=True, timeout=120, cwd=package)


class PackageTests(unittest.TestCase):
    def test_01_complete_primary_replay(self):
        result = run("verify.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("copy_floor=64", result.stdout)

    def test_02_complete_independent_replay(self):
        result = run("independent.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"maximal_nonorthogonal_cliques": 27968', result.stdout)

    def test_03_semantic_certificate_mutations(self):
        original = json.loads((HERE / "CERTIFICATE.json").read_text())
        changes = [
            lambda c: c["atoms"]["pair_rank_rows"].__setitem__(0, "6" + c["atoms"]["pair_rank_rows"][0][1:]),
            lambda c: c["nonorthogonality"]["clique_counts_including_empty"].__setitem__("9", 1),
            lambda c: c["frames"]["orthogonal_pair_frame_count_histogram"].__setitem__("0", 1),
            lambda c: c["model"]["live_global_indices"].pop(),
            lambda c: c["conclusion"].__setitem__("minimum_copy_cost", 63),
        ]
        with tempfile.TemporaryDirectory(prefix="root-star-controls-") as tmp:
            path = Path(tmp) / "bad.json"
            for index, change in enumerate(changes):
                corrupted = copy.deepcopy(original)
                change(corrupted)
                path.write_text(json.dumps(corrupted))
                for script in ("verify.py", "independent.py"):
                    with self.subTest(control=index, script=script):
                        result = run(script, "--certificate", path)
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn("FAIL_", result.stderr)

    def test_04_mathematical_controls(self):
        primary, separate = module("verify"), module("independent")
        # Neither clique routine may silently stop at the desired bound eight.
        complete9 = [((1 << 9) - 1) ^ (1 << i) for i in range(9)]
        counts, witness = primary.clique_census(complete9)
        self.assertEqual(counts[9], 1)
        self.assertEqual(len(witness), 9)
        self.assertEqual(separate.maximal_cliques(complete9), [(1 << 9) - 1])
        roots, gram, removed, live, pairing, orth, nonorth, supports = primary.model()
        frames = primary.all_frames(orth)
        # Treating a live trimmed star as an untrimmed star loses 90 obstructions.
        normal = live[0]
        full, trimmed = supports[2 * normal][2], supports[2 * normal + 1][2]
        misses = lambda mask: sum(not any(mask >> i & 1 for i in frame) for frame in frames)
        self.assertEqual((misses(full), misses(trimmed)), (0, 90))
        # One removed coordinate cannot still realize the diagonal target 4I.
        self.assertTrue(any(sum(gram[a][b] ** 2 for b in removed[:-1]) != 4 for a in live))
        # A duplicate endpoint creates two misses on a real frame.
        self.assertEqual(sum(0 in frame for frame in frames), 90)

    def test_05_source_corruption_and_optimized_relocation(self):
        with tempfile.TemporaryDirectory(prefix="root-star standalone with spaces ") as tmp:
            package = Path(tmp) / "package"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            before = {p.relative_to(package): p.read_bytes() for p in package.rglob("*") if p.is_file()}
            for script in ("verify.py", "independent.py"):
                result = run(script, package=package)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = {p.relative_to(package): p.read_bytes() for p in package.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            path = package / "sources" / "pr1226-PROOF.md"
            path.write_bytes(path.read_bytes() + b"\nchanged source\n")
            for script in ("verify.py", "independent.py"):
                result = run(script, package=package)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("source", result.stderr)

    def test_06_exact_regeneration_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory(prefix="root-star-receipt-") as tmp:
            path = Path(tmp) / "receipt.json"
            result = run("verify.py", "--write-certificate", path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(path.read_bytes(), (HERE / "CERTIFICATE.json").read_bytes())
            path.write_bytes(b"preserve this occupied output\n")
            result = run("verify.py", "--write-certificate", path)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_bytes(), b"preserve this occupied output\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
