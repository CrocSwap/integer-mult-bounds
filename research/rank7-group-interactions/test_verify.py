# SPDX-License-Identifier: Apache-2.0
"""Independent mathematical fixtures and fail-closed source/replay controls."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from frames import ALL, Invalid, contained, dimension, frame, vertex
from verify import PACKAGE, ROOT, mobius, supports, synthetic_interaction


class FrameTests(unittest.TestCase):
    def test_all_four_dimensional_subspaces(self):
        # Independent closure in F2^4, against annihilator intersection in F2^9.
        spaces = {frozenset({0})}
        for vector in range(1, 16):
            spaces |= {s | frozenset(x ^ vector for x in s) for s in tuple(spaces)}
        self.assertEqual(len(spaces), 67)
        encoded = {s: frame(sorted(s - {0})) for s in spaces}
        for points, ann in encoded.items():
            self.assertEqual(dimension(ann), len(points).bit_length() - 1)
        for a, ann_a in encoded.items():
            for b, ann_b in encoded.items():
                self.assertEqual(contained(ann_a, ann_b), a <= b)
        self.assertEqual(frame([]), ALL)
        self.assertEqual(frame([1 << i for i in range(9)]), 1)

    def test_shared_register_can_interact_despite_equal_rank_mass(self):
        result = synthetic_interaction()
        self.assertEqual(result["mixed_difference"], {"1": 2, "2": -1})
        with self.assertRaisesRegex(Invalid, "cross-group charged edge"):
            supports(["first", "second"], [
                ("mixed", 0, vertex([1], 1, []), vertex([1, 2], 2, [1]))
            ])

    def test_register_support_is_stronger_than_edge_support(self):
        # Two distant edges can touch the same register without adjacency.
        edges = [
            ("first", 0, vertex([]), vertex([1, 2], 1, [1])),
            ("second", 0, vertex([1, 2]), vertex([1, 2, 4], 2, [1, 2])),
        ]
        with self.assertRaisesRegex(Invalid, "cross-group register"):
            supports(["first", "second"], edges)

    def test_mixed_difference_cannot_be_inferred_from_singletons(self):
        table = [{"1": 2 + mask.bit_count()} for mask in range(32)]
        self.assertTrue(all(not row for m, row in enumerate(mobius(table)) if m.bit_count() >= 2))
        table[7]["1"] += 1
        self.assertTrue(any(row for m, row in enumerate(mobius(table)) if m.bit_count() >= 3))
        for mask in (0, 1, 2, 4, 8, 16, 31):
            self.assertEqual(table[mask], {"1": 2 + mask.bit_count()})

    def test_optimized_read_only_git_free_export_and_corrupted_input(self):
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory)
            package = export / "research" / PACKAGE.name
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
            for row in manifest["files"]:
                if row["usage"] == "input":
                    output = export / row["path"]
                    output.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / row["path"], output)
            paths = [p for p in export.rglob("*") if p.is_file()]
            before = {p: p.read_bytes() for p in paths}
            for path in paths:
                path.chmod(0o444)
            # Isolated mode omits the script directory; add only this export.
            wrapper = (
                "import runpy,sys; sys.path.insert(0,sys.argv[1]); "
                "sys.argv=[sys.argv[1]+'/verify.py','--emit']; "
                "runpy.run_path(sys.argv[0],run_name='__main__')"
            )
            args = [sys.executable, "-I", "-O", "-B", "-X", "dev", "-W", "error",
                    "-c", wrapper, str(package)]
            result = subprocess.run(args, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), expected)
            self.assertEqual({p: p.read_bytes() for p in paths}, before)
            source = export / next(row["path"] for row in manifest["files"] if row["usage"] == "input")
            source.chmod(0o644)
            source.write_bytes(source.read_bytes() + b" ")
            result = subprocess.run(args, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("input SHA256", result.stderr)
            self.assertFalse((export / ".git").exists())
            # Restore writable files for portable temporary-directory cleanup.
            for path in paths:
                os.chmod(path, 0o644)


if __name__ == "__main__":
    unittest.main()
