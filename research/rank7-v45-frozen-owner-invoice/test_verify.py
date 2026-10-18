# SPDX-License-Identifier: Apache-2.0
"""Positive literal replay and semantic controls independent of file checksums."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import verify
from frames import HELPERS, recount, span, v45_word
from owners import (
    check_fill,
    complete_profile,
    idle_invoice,
    source_windows,
    strict_cost_increase,
)


class InvoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = verify.PACKAGE.parents[1]
        (
            _hashes,
            cls.data,
            cls.parents,
            cls.order,
            cls.dispatch,
            cls.profiles,
            cls.windows,
            cls.bins,
        ) = verify.load_sources(cls.root)
        cls.widths = {
            provider: recount(word)[1] for provider, word in cls.parents.items()
        }
        cls.fill = cls.data[verify.ALLOCATION + "FILL.json.gz"]
        cls.plan = cls.data[verify.ALLOCATION + "vendor/PLAN.json.gz"]

    def check_rows(self, rows):
        return check_fill(
            {**self.fill, "rows": rows},
            self.order,
            self.dispatch,
            self.plan,
            self.windows,
            self.widths,
        )

    def test_literal_idle_and_joint_invoice(self):
        old, _, _ = idle_invoice(self.bins, self.windows, set())
        new, touched, _ = idle_invoice(self.bins, self.windows, {25, 27, 41, 43})
        self.assertEqual(dict(old), {1: 17316, 3: 5861, 5: 6215, 14: 1, 48: 27291})
        self.assertEqual(dict(touched), {(0, 1): 2370, (0, 2): 147})
        self.assertEqual(
            verify.clean(verify.difference(new, old)), {"1": 2370, "2": 147}
        )
        local, _, _ = verify.frame_variants(
            self.parents,
            self.data[verify.CONSTRUCTION + "data/STAGE1-FRAME-EDITS.json"],
            HELPERS,
        )
        before = complete_profile(old, self.profiles, self.dispatch)
        after = complete_profile(new, local, self.dispatch)
        self.assertEqual(
            verify.clean(verify.difference(after, before)),
            {"1": 1038, "2": 6807, "3": 3996, "4": -6660},
        )

    def test_geometric_failure_controls(self):
        rows = self.fill["rows"]
        with self.assertRaisesRegex(ValueError, "complete role count"):
            self.check_rows(rows[:-1])
        key, occupied = next(
            (key, entries)
            for key, entries in self.bins.items()
            if sum(entry[3] for entry in entries) < self.windows[key[:2]][0]
        )
        _offset, time, helper, _width = max(occupied)
        changed = list(rows)
        index = next(i for i, row in enumerate(rows) if row[:2] == [time, helper])
        changed[index] = list(rows[index])
        changed[index][5] += 1
        with self.assertRaisesRegex(ValueError, "nonoverlapping compact source prefix"):
            self.check_rows(changed)
        with self.assertRaisesRegex(ValueError, "unique call/helper role"):
            self.check_rows([rows[0], rows[0], *rows[2:]])
        first = list(rows[0])
        first[2] = 74
        with self.assertRaisesRegex(ValueError, "known owner window"):
            self.check_rows([first, *rows[1:]])
        first = list(rows[0])
        first[5] = 49
        with self.assertRaisesRegex(ValueError, "bin capacity"):
            self.check_rows([first, *rows[1:]])

    def test_source_window_and_dispatch_controls(self):
        template = self.data[verify.ALLOCATION + "vendor/TEMPLATE.json.gz"]
        later = next(
            i
            for i, (stage, replica) in enumerate(self.order)
            if stage == 1 and replica == self.order[0][1]
        )
        bad_order = list(self.order)
        bad_order[0], bad_order[later] = bad_order[later], bad_order[0]
        with self.assertRaisesRegex(ValueError, "per-replica chronology"):
            source_windows(template, bad_order)
        wrong = dict(self.dispatch)
        wrong[tuple(self.order[0])] = "missing"
        with self.assertRaisesRegex(
            ValueError, "bound provider widths|dispatch override"
        ):
            check_fill(
                self.fill, self.order, wrong, self.plan, self.windows, self.widths
            )
        first = list(self.fill["rows"][0])
        first[2:4] = next(
            key
            for key, (_cap, begin, end) in self.windows.items()
            if not begin < first[0] <= end
        )
        with self.assertRaisesRegex(ValueError, "source availability window"):
            self.check_rows([first, *self.fill["rows"][1:]])

    def test_actual_frame_controls(self):
        record = self.data[verify.CONSTRUCTION + "data/STAGE1-FRAME-EDITS.json"]
        parent = self.parents["gauge44"]
        child = v45_word(parent, record, HELPERS)
        old, _ = recount(parent)
        new, _ = recount(child)
        self.assertEqual(
            verify.clean(verify.difference(new, old)),
            {"1": -2, "2": 10, "3": 6, "4": -10},
        )
        child["helper_final"]["249"] = []
        with self.assertRaisesRegex(ValueError, "monotone frame climb"):
            recount(child)
        stale = {**record, "frame_edits": record["frame_edits"][:-1]}
        with self.assertRaisesRegex(ValueError, "source edit inventory"):
            v45_word(parent, stale, HELPERS)
        self.assertEqual(span((1, 2, 3)), frozenset({0, 1, 2, 3}))
        self.assertEqual(span((1,)), frozenset({0, 1}))
        with self.assertRaisesRegex(ValueError, "nine-bit"):
            span((True,))
        with self.assertRaisesRegex(ValueError, "at most nine"):
            span(tuple(range(10)))

    def test_proof_accepts_splitting_and_rejects_reversed_or_unbalanced_claim(self):
        self.assertEqual(
            strict_cost_increase({1: 2, 2: -1}),
            {"negative_rank": 2, "positive_rank_mass": 2, "saving_domain": "a > 0"},
        )
        for false_claim in ({1: -2, 2: 1}, {1: 3, 2: -1}, {1: 2, 2: -3, 4: 1}):
            with self.subTest(delta=false_claim), self.assertRaises(ValueError):
                strict_cost_increase(false_claim)
        idle, _, _ = idle_invoice(self.bins, self.windows, {25, 27, 41, 43})
        bad_idle = Counter(idle)
        del bad_idle[48]
        with self.assertRaisesRegex(ValueError, "complete rank mass"):
            complete_profile(bad_idle, self.profiles, self.dispatch)

    def test_corrupt_export_rejected_and_optimized_cli(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in verify.authenticate(self.root):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.root / name, target)
            path = root / (verify.ALLOCATION + "PROFILE.json")
            path.write_bytes(path.read_bytes() + b" ")
            bad = subprocess.run(
                [
                    sys.executable,
                    "-O",
                    "-B",
                    str(verify.PACKAGE / "verify.py"),
                    "--source-root",
                    str(root),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source bytes:", bad.stderr)
        good = subprocess.run(
            [sys.executable, "-O", "-Werror", "-B", str(verify.PACKAGE / "verify.py")],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(
            good.stdout,
            "PASS_V45_FROZEN_OWNER_INVOICE 16 subsets; strictly higher moment for every a > 0\n",
        )

    def test_json_boundary(self):
        self.assertEqual(verify.unique_object([("x", 2)]), {"x": 2})
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"x":1,"x":2}', object_pairs_hook=verify.unique_object)


if __name__ == "__main__":
    unittest.main()
