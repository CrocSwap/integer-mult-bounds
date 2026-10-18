# SPDX-License-Identifier: Apache-2.0
"""Reject a stale R1 invoice even when its adjacent payload hash is updated."""

import copy
import unittest

import materialize as m
import verify
import verify_release as release


class InvoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.invoice = m.read(release.EVIDENCE / "DISCOVERY-INVOICE.json.gz")
        cls.native = m.read(release.EVIDENCE / "NATIVE-RECEIPT.json")
        cls.finite = {"stock": verify.physical_bound()}

    def check(self, invoice):
        return release.invoice_receipt(invoice, self.native, self.finite)

    def test_actual_native_prefix_and_stale_r1(self):
        self.assertEqual(self.check(self.invoice)["global_prefix_bits"], 1479)
        with self.assertRaisesRegex(ValueError, "invoice local profile"):
            self.check(m.read(m.PACKAGE / "vendor/PR3030-INVOICE.json.gz"))

    def test_unaccepted_invoice(self):
        for field in ("status", "strict_checks"):
            changed = copy.deepcopy(self.invoice)
            if field == "status":
                changed[field] = "FAIL"
            else:
                changed[field]["precision"] = False
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.check(changed)

    def test_understated_global_prefix(self):
        changed = copy.deepcopy(self.invoice)
        changed["global_prefix_bits"] -= 1
        with self.assertRaisesRegex(ValueError, "global prefix formula"):
            self.check(changed)

    def test_understated_local_prefix(self):
        changed = copy.deepcopy(self.invoice)
        changed["providers"]["gauge44"]["local"]["backward"]["prefix_bits"] -= 1
        with self.assertRaisesRegex(ValueError, "authenticated local prefix"):
            self.check(changed)

    def test_stale_native_artifact(self):
        changed = copy.deepcopy(self.invoice)
        old = m.read(m.PACKAGE / "vendor/PR3030-INVOICE.json.gz")
        changed["providers"]["extra"]["artifacts"]["INDEPENDENT-LOCAL-REPLAY.json"] = (
            old["providers"]["extra"]["artifacts"]["INDEPENDENT-LOCAL-REPLAY.json"])
        with self.assertRaisesRegex(ValueError, "invoice native artifact"):
            self.check(changed)

    def test_understated_stock_with_adjusted_sum(self):
        changed = copy.deepcopy(self.invoice)
        changed["blocknorm"]["stock_l2_bits"] -= 1
        changed["blocknorm"]["actual_prefix_bits"] -= 1
        changed["global_prefix_bits"] -= 1
        with self.assertRaisesRegex(ValueError, "blocknorm formula"):
            self.check(changed)


if __name__ == "__main__":
    unittest.main()
