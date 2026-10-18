#!/usr/bin/env python3
"""Focused recursive-boundary, precision and frame rejection tests.

Prepared for @ssteeper with substantial OpenAI Codex assistance. Apache-2.0.
"""

import copy
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("quarter", HERE / "verify.py")
quarter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quarter)


class CircuitFailures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        quarter.check_sources()
        directory = quarter.ROOT / quarter.REPLAY / "jp8"
        cls.canonical = quarter.read(directory / "CANONICAL-WORD.json.gz")
        cls.original = quarter.read(directory / "LOCAL-PROGRAMS.json.gz")
        cls.candidate = {d: quarter.transform(es, d == "backward")[0]
                         for d, es in cls.original.items()}

    def blocks(self, direction):
        start, _, old = quarter.center_blocks(self.original[direction])
        return old[3], copy.deepcopy(self.candidate[direction][start + 99:start + 132])

    def test_crossing_child_is_not_just_an_endpoint_check(self):
        for direction in ("forward", "backward"):
            with self.subTest(direction=direction):
                old, bad = self.blocks(direction)
                si = next(i for i, e in enumerate(bad) if e[0] == "scalar" and e[1][0] == "scale")
                scale = bad.pop(si)
                ci = next(i for i, e in enumerate(bad) if e[0] == "center")
                bad.insert(ci if direction == "forward" else ci + 1, scale)
                original_rows, original_call, _ = quarter.block_map(old)
                bad_rows, bad_call, _ = quarter.block_map(bad)
                self.assertEqual(original_rows, bad_rows)
                self.assertNotEqual(original_call, bad_call)
                with self.assertRaisesRegex(ValueError, "recursive center input"):
                    quarter.check_block_pair(old, bad, direction == "backward")

    def test_dirty_center_clear_is_needed_in_reverse_gather(self):
        _, block = self.blocks("backward")
        correct, _, _ = quarter.block_map(block)
        bad, _, _ = quarter.block_map(block[1:])
        dirt = ("C", 3)
        self.assertTrue(all(dirt not in row for row in correct.values()))
        self.assertTrue(any(dirt in row for r, row in bad.items() if r[0] == "L"))

    def test_endpoint_neutral_prefix_excursion_is_rejected(self):
        old, _ = self.blocks("backward")
        # Add a reversible overshoot after an actual nonzero accumulation.
        bad = copy.deepcopy(old)
        bad[2:2] = [["scalar", ["scale", ["C", 3], 2**200, 1], 0],
                    ["scalar", ["scale", ["C", 3], 1, 2**200], 0]]
        self.assertEqual(quarter.block_map(old)[:2], quarter.block_map(bad)[:2])
        with self.assertRaisesRegex(ValueError, "192-bit"):
            quarter.cost_prefix(bad)

    def test_coefficient_work_is_disjoint_and_cleared(self):
        with self.assertRaisesRegex(ValueError, "alias"):
            list(quarter.lower(["add", ["L", 1], ["W", 0], 1, 4]))
        regs = (("L", 1), ("L", 2), quarter.W)
        rows = {r: {r: quarter.Q(1)} for r in regs}
        for primitive in quarter.lower(["add", ["L", 1], ["L", 2], -1, 4]):
            quarter.apply_primitive(rows, primitive)
        self.assertEqual(rows[quarter.W], {})
        self.assertEqual(rows[("L", 1)], {("L", 1): 1, ("L", 2): quarter.Q(-1, 4)})

    def test_quarter_scale_at_wrong_frame_is_rejected_by_native_auditor(self):
        for direction in ("forward", "backward"):
            with self.subTest(direction=direction):
                programs = copy.deepcopy(self.candidate)
                scale = next(e for e in programs[direction] if e[0] == "scalar"
                             and e[1][:2] == ["scale", ["C", 3]])
                scale[2] = self.canonical["center_frames"][3]
                with tempfile.TemporaryDirectory(prefix="center-frame-control-") as tmp:
                    out = Path(tmp).resolve()
                    self.assertTrue(out.is_relative_to(Path(tempfile.gettempdir()).resolve()))
                    for name, value in (("CANONICAL-WORD.json.gz", self.canonical),
                                        ("LOCAL-PROGRAMS.json.gz", programs)):
                        (out / name).write_bytes(gzip.compress(json.dumps(value).encode(), mtime=0))
                    proc = subprocess.run([sys.executable, "-I", "-B", str(quarter.ROOT / quarter.AUDITOR), str(out)],
                                          capture_output=True, text=True, timeout=120)
                    self.assertNotEqual(proc.returncode, 0)
                    self.assertIn("assert private[r]==f", proc.stderr)


if __name__ == "__main__":
    unittest.main()
