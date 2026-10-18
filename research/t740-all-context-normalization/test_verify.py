#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Nick Petalas.
"""Behavioral controls for the source-to-normal-form implication."""
import unittest
from collections import Counter
from copy import deepcopy

import algebra
import verify


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = verify.load_inputs()
        cls.order, cls.times, cls.dispatch = verify.chronology(cls.data)
        cls.allowed, cls.streams = verify.windows(cls.data["template"])
        cls.lengths = [[len(c["orthogonal_axes"]) for c in r["idle_children"]]
                       for r in cls.data["phases"]["recipes"]]

    def row_at(self, child, cut):
        time = self.times[0][cut]
        stage, caller = self.order[time]
        widths = self.data["providers"][self.dispatch[stage, caller % 74]]["widths"]
        helper = next(i for i, width in enumerate(widths) if 0 < width <= self.lengths[0][child])
        return [time, helper, 0, child, 0, 0]

    def accept(self, row, data=None, used=None, allowed=None):
        prepared = (self.order, self.times, self.dispatch, self.allowed if allowed is None else allowed,
                    self.streams, self.lengths)
        counts = [0] * (verify.OWNERS * verify.PORTS)
        verify.accept_row(row, self.data if data is None else data, prepared,
                          {0: [0] * 20} if used is None else used, counts, Counter())
        return counts[0]

    def test_legal_diagonal_transport(self):
        self.assertEqual(self.accept(self.row_at(4, 0)), 1)
        self.assertEqual(self.accept(self.row_at(14, 5)), 1)

    def test_host_before_noncommuting_boundary_rejected(self):
        with self.assertRaisesRegex(ValueError, "noncommuting"):
            self.accept(self.row_at(14, 4))

    def test_host_after_residual_boundary_rejected(self):
        with self.assertRaisesRegex(ValueError, "noncommuting"):
            self.accept(self.row_at(4, 4))

    def test_changed_physical_stream_rejected(self):
        data = dict(self.data)
        data["plan"] = deepcopy(self.data["plan"])
        data["plan"]["pairs"]["4"] = 0
        with self.assertRaisesRegex(ValueError, "physical streams"):
            self.accept(self.row_at(4, 0), data=data)

    def test_duplicate_hosted_axes_rejected(self):
        row = self.row_at(4, 0)
        used = {0: [0] * 20}
        self.accept(row, used=used)
        with self.assertRaisesRegex(ValueError, "overlap"):
            self.accept(row, used=used)

    def test_new_touch_removes_legal_transport(self):
        template = deepcopy(self.data["template"])
        template["execution_schedule"].insert(1, {"kind": "bridge", "dst": 0, "src": 2,
                                                    "coefficient": 1})
        allowed, _ = verify.windows(template)
        with self.assertRaisesRegex(ValueError, "noncommuting"):
            self.accept(self.row_at(4, 0), allowed=allowed)

    def test_terminal_before_residual_sites_rejected(self):
        template = deepcopy(self.data["template"])
        events = template["execution_schedule"]
        terminal = next(e for e in events if e["kind"] == "terminal")
        events.remove(terminal)
        events.insert(0, terminal)
        with self.assertRaisesRegex(ValueError, "terminal permutation"):
            verify.windows(template)

    def test_journal_preimage_rejected(self):
        journal = deepcopy(self.data["journal"])
        journal["edits"][0][1][-1] += 1
        with self.assertRaisesRegex(ValueError, "preimage"):
            verify.edits_for(self.data["base"]["rows"], journal)

    def test_exact_source_hash_rejected(self):
        sources = verify.json.loads((verify.HERE / "SOURCES.json").read_bytes())
        pin = dict(next(row for row in sources["files"] if row["usage"] == "input"))
        pin["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA256"):
            verify.checked_bytes(verify.ROOT / pin["path"], pin)

    def test_full_word_and_rank_changing_phase(self):
        recipe = self.data["phases"]["recipes"][0]
        expected, _ = algebra.replay(self.data["template"], recipe)
        self.assertEqual(expected, self.data["reference"]["polynomial_matrix"])
        changed = deepcopy(recipe)
        changed["idle_children"][8]["orthogonal_axes"].pop()
        with self.assertRaisesRegex(ValueError, "ambient phase"):
            algebra.replay(self.data["template"], changed)

    def test_nonzero_port_and_reference_corruption(self):
        recipe = self.data["phases"]["recipes"][111]
        terms, _ = algebra.replay(self.data["template"], recipe)
        self.assertEqual(terms, self.data["reference"]["polynomial_matrix"])
        data = dict(self.data)
        data["reference"] = deepcopy(data["reference"])
        data["reference"]["polynomial_matrix"][0][-1] += 1
        with self.assertRaisesRegex(ValueError, "identity baseline"):
            verify.normal_forms(data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
