# SPDX-License-Identifier: Apache-2.0
"""Mathematical failure controls for the new journal and adapted cap.

Adapted from Nick Petalas's PR3024 controls by Jeremy Diviney with
OpenAI Codex assistance. Deterministic regeneration and prefix-hole controls
are added for this changed inventory; the obsolete sign test is omitted.
"""

import copy
import unittest

import cap_check as cap_proof
import common
import construct

lift = common.load(common.P/'vendor/lift.py', 'test_lift')


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        common.authenticate()
        cls.context = common.context()
        cls.base = cls.context.base
        cls.journal = common.read(common.P/'EXCHANGE.json')
        cls.edits = lift.patch(cls.base, cls.journal)
        cls.order = cls.context.order
        cls.dispatch = cls.context.dispatch
        cls.widths = cls.context.widths
        cls.windows = cls.context.win
        cls.families = cls.context.families

    def check_difference(self, edits):
        return lift.differential(
            self.base, edits, self.widths, self.windows, self.families
        )

    def test_deterministic_new_exchange(self):
        journal, delta = construct.construct(self.context)
        self.assertEqual(journal, self.journal)
        self.assertEqual((len(journal['edits']), delta['affected_bins']), (145, 55))

    def test_literal_lift_endpoints_and_dispatch(self):
        first = self.base[0]
        self.assertEqual(
            lift.row_at(self.base, 9 * lift.BASE_ROLES),
            [9, first[1], first[2] + 666, *first[3:]],
        )
        order, dispatch = lift.chronology(self.order, self.dispatch)
        self.assertEqual(len(order), 6660)
        self.assertEqual(order[9], [self.order[0][0], self.order[0][1] + 666])
        self.assertEqual(dispatch[tuple(order[9])], self.dispatch[tuple(self.order[0])])
        self.assertEqual(len(lift.Rows(self.base, self.edits)), 2717280)

    def test_journal_rejects_duplicate_stale_and_changed_identity(self):
        bad = copy.deepcopy(self.journal)
        bad["edits"].append(bad["edits"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            lift.patch(self.base, bad)
        for field, message in [(1, "preimage"), (2, "identity")]:
            bad = copy.deepcopy(self.journal)
            bad["edits"][0][field][1] += 1
            with self.assertRaisesRegex(ValueError, message):
                lift.patch(self.base, bad)
        bad = {**self.journal, "copies": 9}
        with self.assertRaisesRegex(ValueError, "multiplicity"):
            lift.patch(self.base, bad)

    def test_complete_literal_delta_and_omitted_move_control(self):
        self.assertEqual(self.check_difference(self.edits)["idle_delta"], common.DELTA)
        moved = next(
            i
            for i, row in self.edits.items()
            if row[2:5] != lift.row_at(self.base, i)[2:5]
        )
        bad = {i: row for i, row in self.edits.items() if i != moved}
        with self.assertRaises(ValueError):
            self.check_difference(bad)

    def test_unavailable_window_and_overflow(self):
        index = next(iter(self.edits))
        for defect in ("window", "capacity"):
            bad = {i: list(row) for i, row in self.edits.items()}
            row = bad[index]
            if defect == "window":
                owner, child = next(
                    (o, c)
                    for (o, c), (_, lo, hi) in self.windows.items()
                    if not lo < row[0] // 10 <= hi
                )
                row[2:4] = [owner, child]
            else:
                row[5] = 48
            with self.assertRaises(ValueError):
                self.check_difference(bad)

    def test_same_call_family_collision(self):
        index = next(iter(self.edits))
        row = self.edits[index]
        original, copy_index = divmod(row[0], 10)
        helper = (row[1] + 1) % 408
        other = lift.row_at(
            self.base, copy_index * lift.BASE_ROLES + original * 408 + helper
        )
        bad = {i: list(value) for i, value in self.edits.items()}
        bad[index][2:5] = other[2:5]
        with self.assertRaisesRegex(ValueError, "same-call"):
            lift.affected_calls(self.base, bad, self.families)

    def test_full_interval_cap_and_primal_corruptions(self):
        certificate = common.read(common.P / "vendor/PR3133-CAP.json")
        root = common.load(common.MAIN / "tools/root.py", "test_root")
        result = cap_proof.verify_cap(certificate, root)
        self.assertEqual(
            (result["patterns"], result["tight_patterns"], result["strict_patterns"]),
            (2551, 12, 2539),
        )
        self.assertEqual(result["invariant"]["first_multiple_of_74"], 740)
        for defect in ("basis", "local", "bracket"):
            bad = copy.deepcopy(certificate)
            if defect == "basis":
                bad["basis_patterns"][0]["count_per_replica"] = "671"
            elif defect == "local":
                bad["local_per_call"]["1"] -= 1
            else:
                bad["cap_lower"] = "1/1000"
            with self.assertRaises(ValueError):
                cap_proof.verify_cap(bad, root)

    def test_unpaid_prefix_hole(self):
        key, window = next((key, value) for key, value in self.windows.items() if value[0] == 48)
        time = max(0, window[1]+1)*10
        owner, child = key
        helper = 0
        row = [time, helper, owner, child, 0, 1]
        with self.assertRaisesRegex(ValueError, 'compact prefix'):
            lift.check_bin((owner, child, 0), {0: row}, self.widths, self.windows)

    def test_paid_mass(self):
        self.assertEqual(sum(r * n for r, n in common.DELTA.items()), 0)
        root = common.load(common.MAIN / 'tools/root.py', 'mass_root')
        with self.assertRaises(ValueError):
            root.kappa_from_profile({1: 65088 * 740 - 1}, 740)


if __name__ == "__main__":
    unittest.main()
