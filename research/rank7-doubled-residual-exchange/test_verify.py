# SPDX-License-Identifier: Apache-2.0
"""Behavioral tests and a separate sorted-interval audit of the literal journal."""

import copy
import json
import tempfile
import unittest
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import geometry
import verify


def sorted_audit(order, fill, dispatch, providers, windows, plan):
    """No bit masks or predecessor owner implementation; caller supplies windows."""
    by_bin, same_call, helpers = defaultdict(list), set(), set()
    if len(fill["rows"]) != 543456:
        raise ValueError("role count")
    for time, helper, owner, child, port, offset in fill["rows"]:
        role = time, helper
        if role in helpers:
            raise ValueError("duplicate role")
        helpers.add(role)
        cap, low, high = windows[owner, child]
        if not low < time <= high:
            raise ValueError("window")
        family = owner, plan["pairs"][str(child)], plan["sides"][str(child)], port
        if (time, family) in same_call:
            raise ValueError("physical family")
        same_call.add((time, family))
        width = providers[dispatch[tuple(order[time])]]["widths"][helper]
        if offset < 0 or offset + width > cap:
            raise ValueError("capacity")
        by_bin[owner, child, port].append((offset, width))
    idle = Counter()
    for (owner, child), (cap, _, _) in windows.items():
        for port in range(112):
            end = 0
            for offset, width in sorted(by_bin[owner, child, port]):
                if offset != end:
                    raise ValueError("overlap or hole")
                end += width
            if end < cap:
                idle[cap - end] += 1
    return dict(sorted(idle.items()))


class ExchangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify.authenticate()
        s = verify.SOURCE
        cls.providers = verify.read(s / "allocation/PROVIDERS.json")
        cls.plan = verify.read(s / "allocation/vendor/PLAN.json.gz")
        cls.template = verify.read(s / "allocation/vendor/TEMPLATE.json.gz")
        order = verify.read(s / "allocation/ORDER.json")
        dispatch = {
            (a, b): p for a, b, p in verify.read(s / "allocation/DISPATCH.json")
        }
        fill = verify.apply(
            verify.read(s / "allocation/FILL.json.gz"),
            verify.read(verify.PACKAGE / "vendor/PR3018-EXCHANGE.json"),
        )
        cls.order, cls.parent, cls.dispatch = verify.doubled(order, fill, dispatch)
        cls.journal = verify.read(verify.PACKAGE / "EXCHANGE.json")
        cls.candidate = verify.apply(cls.parent, cls.journal)
        cls.windows = geometry.windows(cls.template, cls.order, 148)

    def test_sorted_interval_audit_and_paid_empty_bin(self):
        idle = sorted_audit(
            self.order,
            self.candidate,
            self.dispatch,
            self.providers,
            self.windows,
            self.plan,
        )
        self.assertEqual(idle, {1: 34632, 3: 9924, 5: 3440, 32: 1, 48: 56380})
        bins = defaultdict(list)
        for row in self.candidate["rows"]:
            provider = self.providers[self.dispatch[tuple(self.order[row[0]])]]
            bins[tuple(row[2:5])].append(provider["widths"][row[1]])
        for key, pattern in self.journal["targets"]:
            self.assertEqual(sorted(bins[tuple(key)]), pattern)
        self.assertNotIn([4, 8, 9, 9, 9, 9], [sorted(v) for v in bins.values()])
        self.assertEqual(self.order[:4], [[0, 0], [0, 74], [0, 37], [0, 111]])

    def test_clock_and_owner_mutants(self):
        bad = copy.deepcopy(self.candidate)
        index = next(i for i, old, new in self.journal["edits"] if old[2:5] != new[2:5])
        row = bad["rows"][index]
        row[0] = self.windows[tuple(row[2:4])][1]
        with self.assertRaisesRegex(ValueError, "window|duplicate role"):
            sorted_audit(
                self.order, bad, self.dispatch, self.providers, self.windows, self.plan
            )
        bad = copy.deepcopy(self.candidate)
        # Folding a copy's owner back into the first copy must not retain legality.
        for row in bad["rows"]:
            if row[2] >= 74:
                row[2] -= 74
        with self.assertRaises(ValueError):
            sorted_audit(
                self.order, bad, self.dispatch, self.providers, self.windows, self.plan
            )

    def test_exact_sign_and_root(self):
        self.assertEqual(
            verify.sign_certificate()["derivative_upper"], "-1711767/125000"
        )
        profile = {
            1: 3291372,
            2: 940392,
            3: 318948,
            4: 143856,
            5: 27416,
            8: 10656,
            32: 1,
            48: 56380,
        }
        self.assertEqual(
            verify.root(profile, 148),
            (
                Fraction("0.0017290353460708281979174"),
                Fraction("0.0017290353460708281979175"),
            ),
        )
        with self.assertRaisesRegex(ValueError, "rank mass"):
            verify.root({r: n for r, n in profile.items() if r != 32}, 148)
        with self.assertRaisesRegex(ValueError, "replica bound"):
            verify.root(profile, 149)

    def test_predecessor_authentication_and_journal_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = verify.read(verify.PACKAGE / "SOURCES.json")
            for entry in source["predecessor_files"]:
                path = folder / entry["local_path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((verify.PACKAGE / entry["local_path"]).read_bytes())
            source["files"] = []
            (folder / "SOURCES.json").write_text(json.dumps(source), encoding="utf-8")
            (folder / "vendor/moment.py").write_text(
                "raise RuntimeError('mutant')\n", encoding="utf-8"
            )
            with patch.object(verify, "PACKAGE", folder):
                with self.assertRaisesRegex(ValueError, "predecessor digest"):
                    verify.authenticate()
        bad = copy.deepcopy(self.journal)
        bad["edits"][0][2][1] += 1
        with self.assertRaisesRegex(ValueError, "role identity"):
            verify.apply(self.parent, bad)
        with self.assertRaisesRegex(ValueError, "preimage"):
            verify.apply(self.candidate, self.journal)


if __name__ == "__main__":
    unittest.main()
