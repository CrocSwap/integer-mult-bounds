"""Behavioral and publication controls. All disposable exports share one root."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from model import census, error, lift, member
from verify import PACKAGE, source_index


class Behavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = Path(
            os.environ.get(
                "IMB_RUN_ROOT", str(Path.home() / ".cache/integer-mult-bounds-runs")
            )
        )
        parent.mkdir(parents=True, exist_ok=True)
        cls.scratch = tempfile.TemporaryDirectory(prefix="maximal-lattice-", dir=parent)
        cls.root = Path(cls.scratch.name)

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def export(self, name):
        destination = self.root / name
        shutil.copytree(
            PACKAGE, destination, ignore=shutil.ignore_patterns("__pycache__")
        )
        return destination

    def command(self, package, optimized=False):
        options = ["-O"] if optimized else []
        return subprocess.run(
            [sys.executable, *options, "-B", str(package / "verify.py")],
            cwd=self.root,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )

    def test_rank_two_complete_shift_domain(self):
        result = census(2)
        self.assertEqual(result["shifts"], 65536)
        self.assertEqual(result["survivor_counts"], [10240, 3072, 1024])
        self.assertEqual(result["nonperiods_rejected"], 64512)

    def test_zero_error_is_insufficient(self):
        # This shift fools the origin-only test but fails at another input.
        z = [0, 0, 0, 0, 0, 0, 0, 2]
        self.assertEqual(error(z, 2), (0, 0, 0, 0, 0, 0, 0, 0))
        self.assertFalse(member(z, 2))
        x = [0, 0, 0, 0, 0, 0, 0, 1]
        self.assertNotEqual(
            error([a + b for a, b in zip(x, z, strict=True)], 2), error(x, 2)
        )

    def test_signed_floor_literal_outputs(self):
        self.assertEqual(lift([-1, 0, 0, 0], 1), [-1, 0, -1, 1])
        self.assertEqual(lift([0, -1, 0, 0], 1), [1, -1, 0, -1])
        self.assertEqual(lift([0, -1, 0, 0], 1, inverse=True), [0, -1, 1, -1])

    def test_boundary_limits(self):
        for rank in (-1, 8, True):
            with self.subTest(rank=rank), self.assertRaises(ValueError):
                lift([0] * 4, rank)
        for vector in ([0] * 3, [True, 0, 0, 0], [1 << 4096, 0, 0, 0]):
            with self.subTest(vector=str(vector)[:40]), self.assertRaises(ValueError):
                lift(vector, 1)
        with self.assertRaises(ValueError):
            census(3)

    def test_corrupt_source_rejected_before_execution(self):
        package = self.export("source-corrupt")
        path = package / "vendor/prefix_index.py"
        path.write_text("raise RuntimeError('must not execute')\n")
        with self.assertRaisesRegex(ValueError, "source SHA256"):
            source_index(package)

    def test_git_free_normal_optimized_and_read_only(self):
        package = self.export("git-free")
        before = {
            p.relative_to(package): p.read_bytes()
            for p in package.rglob("*")
            if p.is_file()
        }
        ordinary, optimized = (
            self.command(package),
            self.command(package, optimized=True),
        )
        self.assertEqual(ordinary.returncode, 0, ordinary.stderr)
        self.assertEqual(optimized.returncode, 0, optimized.stderr)
        self.assertEqual(ordinary.stdout, optimized.stdout)
        self.assertEqual(json.loads(ordinary.stdout)["rank7_optimal_coset_bits"], 343)
        after = {
            p.relative_to(package): p.read_bytes()
            for p in package.rglob("*")
            if p.is_file()
        }
        self.assertEqual(before, after)

    def test_stale_and_wrong_type_receipts_rejected(self):
        for name, replacement in (
            ("wrong-count", 342),
            ("wrong-type", "343"),
            ("wrong-float", 343.0),
        ):
            package = self.export(name)
            path = package / "RESULT.json"
            result = json.loads(path.read_text())
            result["rank7_optimal_coset_bits"] = replacement
            path.write_text(json.dumps(result))
            execution = self.command(package)
            self.assertNotEqual(execution.returncode, 0)
            self.assertIn("typed result receipt differs", execution.stderr)


if __name__ == "__main__":
    unittest.main()
