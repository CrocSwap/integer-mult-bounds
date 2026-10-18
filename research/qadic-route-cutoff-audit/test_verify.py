#!/usr/bin/env python3
"""Failure boundaries additional to the eight mathematical replay controls."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("width_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Boundaries(unittest.TestCase):
    def test_source_drift_rejected_before_execution(self):
        inputs = audit.pinned_inputs()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, raw in inputs.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            router = root / audit.ROUTER
            router.write_bytes(router.read_bytes() + b"\nraise RuntimeError('untrusted')\n")
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                audit.pinned_inputs(root)

    def test_cutoff_does_not_supply_a_coefficient(self):
        stock = json.loads(audit.pinned_inputs()[audit.STOCK])
        stock["branches"]["bootstrap"]["stages"][1]["actual_stock_coefficient"] = 6748
        with self.assertRaisesRegex(ValueError, "reserve coefficient"):
            audit.cutoff_rows(stock)

    def test_stopped_membership_is_a_required_premise(self):
        stock = json.loads(audit.pinned_inputs()[audit.STOCK])
        data = stock["branches"]["bootstrap"]["stages"]
        data[1]["cutoff_log2"] = data[0]["cutoff_log2"]
        with self.assertRaisesRegex(ValueError, "membership premise"):
            audit.cutoff_rows(stock)

    def test_power_of_two_radix_breaks_strict_roundtrip(self):
        # At q=4,w=2, Q=P=4: the least q-adic width is 1, not 2.
        self.assertEqual(audit.radix_width(4, 4), 1)
        with self.assertRaisesRegex(ValueError, "strict round-trip"):
            audit.roundtrip_case(4, 2)

    def test_dummy_rectangle_violation_rejected(self):
        q, w = 3, 2
        high, before, middle, suffix, raw = audit.payload(q, w)
        padded = audit.embed_two_fields(raw, high, 4, before, middle, suffix)
        # First padded address x=0,z=0,y=3 lies outside the genuine rectangle.
        padded[3 * suffix] = 1
        with self.assertRaisesRegex(ValueError, "dummy rectangle"):
            audit.unpad_two_fields(padded, high, 4, before, middle, suffix)


if __name__ == "__main__":
    unittest.main()
