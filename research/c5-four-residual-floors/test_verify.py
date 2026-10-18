#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the exact lower-bound certificate."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify as v


class CertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads((v.HERE / "CERTIFICATE.json").read_bytes())
        cls.planes = v.geometry(v.ROOT)
        entry = cls.certificate["cores"][0]
        cls.rows = v.support_rows(tuple(cls.planes[i] for i in entry["core"]))

    def test_missing_case_rejected(self):
        broken = copy.deepcopy(self.certificate)
        broken["cores"][0]["cases"].pop()
        with self.assertRaisesRegex(ValueError, "complete slack cases"):
            v.verify(certificate=broken)

    def test_duplicate_case_rejected(self):
        broken = copy.deepcopy(self.certificate)
        broken["cores"][0]["cases"].append(broken["cores"][0]["cases"][0])
        with self.assertRaisesRegex(ValueError, "complete slack cases"):
            v.verify(certificate=broken)

    def test_wrong_cover_rejected(self):
        broken = copy.deepcopy(self.certificate)
        broken["cores"][0]["cover_weights"][0] = 100
        with self.assertRaisesRegex(ValueError, "cover inequality"):
            v.verify(certificate=broken)

    def test_false_separator_rejected(self):
        entry = self.certificate["cores"][0]
        case = copy.deepcopy(entry["cases"][0])
        case["dual_weights"] = [0] * 10
        with self.assertRaisesRegex(ValueError, "separating bound"):
            v.check_case(self.rows, entry["cover_weights"], entry["cover_scale"], case)

    def test_negative_unknown_count_multiplier_rejected(self):
        entry = self.certificate["cores"][0]
        case = copy.deepcopy(entry["cases"][0])
        case["dual_weights"][8] = -1
        with self.assertRaisesRegex(ValueError, "lower-bound-only counts"):
            v.check_case(self.rows, entry["cover_weights"], entry["cover_scale"], case)

    def test_rank_counts_without_traces_are_insufficient(self):
        entry = self.certificate["cores"][0]
        with patch.object(v, "trace_consistent", return_value=True):
            with self.assertRaisesRegex(ValueError, "admissible-term dual inequality"):
                v.check_case(self.rows, entry["cover_weights"], entry["cover_scale"],
                             entry["cases"][0])

    def test_odd_cycle_half_trace_and_anchor(self):
        hits = (1,) * 10
        tight = [False] * 5 + [True] * 5
        self.assertTrue(v.trace_consistent(31, 31, hits, tight))
        tight[0] = True
        self.assertFalse(v.trace_consistent(31, 31, hits, tight))

    def test_each_input_pin_rejects_corruption(self):
        for corrupted in v.HASHES:
            with self.subTest(input=corrupted), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                target = root / v.INPUT
                target.mkdir(parents=True)
                for name in v.HASHES:
                    shutil.copyfile(v.ROOT / v.INPUT / name, target / name)
                with (target / corrupted).open("ab") as stream:
                    stream.write(b"corruption")
                with self.assertRaisesRegex(ValueError, "scientific input SHA256"):
                    v.geometry(root)

    def test_wrong_physical_order_rejected(self):
        local = [self.planes[i] for i in v.CORES[0]]
        local[1], local[2] = local[2], local[1]
        with self.assertRaisesRegex(ValueError, "physical C5 order"):
            v.check_cycle(local)


if __name__ == "__main__":
    unittest.main()
