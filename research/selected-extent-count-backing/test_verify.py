#!/usr/bin/env python3
"""Behavior and source-binding controls, also under optimized Python."""

import importlib.util
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "extent_verify", Path(__file__).with_name("verify.py")
)
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class BackingTests(unittest.TestCase):
    def test_literal_asymmetric_peaks(self):
        with verify.source_modules() as m:
            for a, b, expected in ((1, 1, 12), (1, 32, 19), (32, 1, 27)):
                self.assertEqual(verify.product_case(m, a, b)[2], expected)

    def test_one_cell_short_and_zero_domain(self):
        with verify.source_modules() as m:
            with self.assertRaisesRegex(ValueError, "backing budget"):
                verify.product_case(m, 1, 1, short=True)
        with self.assertRaisesRegex(ValueError, "positive product"):
            verify.product_peak(1, 0)

    def test_padding_changes_peak_not_output(self):
        with verify.source_modules() as m:
            narrow = verify.extent_case(m, 3, 1, 1, (1, 1, 1), 0, 1, 8)[0]
            wide = verify.extent_case(m, 3, 1, 1, (1, 1, 1), 0, 1, 256)[0]
            self.assertEqual((narrow[7], wide[7]), (21, 267))
            self.assertEqual((narrow[9], wide[9]), (12, 12))

    def test_source_corruption_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in verify.authenticate():
                suffix = ".md" if path == "NOTICE" else ".py"
                source = verify.REPO / (verify.SOURCE + path + suffix)
                destination = root / (verify.SOURCE + path + suffix)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            changed = root / (verify.SOURCE + "cardinal_counts.py")
            changed.write_bytes(
                changed.read_bytes() + b"\nraise RuntimeError('executed')\n"
            )
            with self.assertRaisesRegex(ValueError, "source hash"):
                with verify.source_modules(root):
                    self.fail("corrupt source loaded")

    def test_preloaded_modules_cannot_replace_source(self):
        missing = object()
        previous = sys.modules.get("words", missing)
        try:
            for hostile in (None, types.ModuleType("words")):
                sys.modules["words"] = hostile
                with verify.source_modules() as m:
                    self.assertIsNot(m.words, hostile)
                    self.assertEqual(verify.product_case(m, 3, 7)[:2], [3, 7])
                self.assertIs(sys.modules["words"], hostile)
        finally:
            if previous is missing:
                sys.modules.pop("words", None)
            else:
                sys.modules["words"] = previous

    def test_erased_backing_is_counted_until_release(self):
        with verify.source_modules() as m, verify.counted(m) as census:
            count = m.cardinal_counts.Count.literal(31)
            census.start()
            census.base.clear()
            count.close()
            self.assertEqual(list(count.tape.cells[1:]), [4] * 6)
            self.assertEqual(census.peak, 7)
            self.assertEqual(len(census.roots), 1)
            del count
            self.assertEqual(len(census.roots), 0)

    def test_complete_native_add(self):
        with verify.source_modules() as m:
            row = verify.action_case(m, 2, (2, 3, 2))
            self.assertEqual(row[:3], [2, [2, 3, 2], 108])


if __name__ == "__main__":
    unittest.main()
