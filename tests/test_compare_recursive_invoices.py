# SPDX-License-Identifier: Apache-2.0
"""Independent finite tariff checks and real algebra controls for signed invoices."""

import copy
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/compare_recursive_invoices.py"
SPEC = importlib.util.spec_from_file_location("compare_recursive_invoices", SCRIPT)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def invoice(paid=None, targets=None):
    return {"schema": M.SCHEMA,
            "contract": {"model": "declared-complete-recursive-invoice",
                         "rank_semantics": "one Gaussian child of integer rank r",
                         "ambient_rank": 145,
                         "boundary": "same arbitrary independent inputs and charged outputs"},
            "paid": {str(r): n for r, n in (paid or {}).items()},
            "targets": {str(r): n for r, n in (targets or {}).items()}}


class InvoiceComparisonTests(unittest.TestCase):
    def test_real_h4_split_is_uniformly_worse(self):
        result = M.compare_invoices(invoice({4: 1}), invoice({2: 2}))
        self.assertEqual(result["classification"], "uniformly_worse")
        self.assertEqual(result["signed_net_delta"], {"2": 2, "4": -1})
        self.assertEqual(result["hinges"], [{"rank": 0, "value": 0},
                                             {"rank": 2, "value": 2},
                                             {"rank": 4, "value": 0}])
        self.assertEqual(result["rank_mass"]["delta"]["paid_minus_targets"], 0)
        self.assertEqual(result["power_moment"]["new_minus_old_sign"], "strictly_positive")

    def test_owned_relation_debits_surrendered_h9_target(self):
        result = M.compare_invoices(invoice({1: 1, 8: 1}, {9: 1}), invoice())
        self.assertEqual(result["classification"], "uniformly_better")
        self.assertEqual(result["delta_targets"], {"9": -1})
        self.assertEqual(result["signed_net_delta"], {"1": -1, "8": -1, "9": 1})
        self.assertEqual([row["value"] for row in result["hinges"]], [0, -1, -1, 0])
        self.assertEqual(result["power_moment"]["new_minus_old_sign"], "strictly_negative")

    def test_scalar_only_and_equal_net_moments(self):
        self.assertEqual(M.compare_invoices(invoice({4: 1}), invoice({4: 1}))["classification"], "equal")
        result = M.compare_invoices(invoice(), invoice({7: 2}, {7: 2}))
        self.assertEqual(result["classification"], "equal")
        self.assertEqual(result["delta_paid"], {"7": 2})
        self.assertEqual(result["delta_targets"], {"7": 2})

    def test_mixed_hinges_are_inconclusive(self):
        result = M.compare_invoices(invoice({2: 3}), invoice({1: 4}))
        self.assertEqual(result["classification"], "inconclusive")
        self.assertEqual(result["power_moment"]["new_minus_old_sign"], "not_determined")

    def test_unequal_mass_and_large_gaps_need_no_expanded_rank_array(self):
        result = M.compare_invoices(invoice(), invoice({145: 1}))
        self.assertEqual(result["classification"], "uniformly_worse")
        self.assertEqual(result["rank_mass"]["delta"]["paid"], 145)
        value = invoice({M.MAX_RANK: 1})
        value["contract"]["ambient_rank"] = M.MAX_RANK
        zero = copy.deepcopy(value)
        zero["paid"] = {}
        self.assertEqual(len(M.compare_invoices(zero, value)["hinges"]), 2)

    def test_exhaustive_independent_discrete_slope_tariffs(self):
        # Every extreme tariff min(r,k), including linear r, occurs among these
        # slopes. Direct cumulative evaluation is independent of hinge code.
        slopes = [s for s in itertools.product(range(3), repeat=4)
                  if all(s[i] >= s[i + 1] for i in range(3))]
        tariffs = [list(itertools.accumulate(s)) for s in slopes]
        for delta in itertools.product(range(-2, 3), repeat=4):
            old = invoice({r: -d for r, d in enumerate(delta, 1) if d < 0})
            new = invoice({r: d for r, d in enumerate(delta, 1) if d > 0})
            # Add matching but nonconstant paid/target entries to exercise the
            # signed presentation without changing its actual tariff value.
            new["targets"] = {str(r): r for r in range(1, 5)}
            old["targets"] = dict(new["targets"])
            values = [sum(d * f for d, f in zip(delta, tariff)) for tariff in tariffs]
            expected = ("equal" if not any(delta) else
                        "uniformly_better" if max(values) <= 0 else
                        "uniformly_worse" if min(values) >= 0 else "inconclusive")
            self.assertEqual(M.compare_invoices(old, new)["classification"], expected, delta)

    def test_changed_contract_rejected(self):
        for key, value in (("model", "other"), ("rank_semantics", "different rank"),
                           ("ambient_rank", 146), ("boundary", "different ownership")):
            old, new = invoice(), invoice()
            new["contract"][key] = value
            with self.assertRaisesRegex(ValueError, "contracts differ"):
                M.compare_invoices(old, new)

    def test_histogram_and_contract_domain_rejections(self):
        for histogram in ({"01": 1}, {"0": 1}, {"+1": 1}, {"1.0": 1},
                          {" 1": 1}, {"١": 1}, {"146": 1}, {"1": True},
                          {"1": -1}, {"1": 1.0}, {"1": 10**61},
                          {"1" * 10000: 1}, {True: 1}):
            value = invoice()
            value["paid"] = histogram
            with self.assertRaises(ValueError):
                M.validate_invoice(value)
        for contract in ({}, {**invoice()["contract"], "ambient_rank": True},
                         {**invoice()["contract"], "boundary": " "},
                         {**invoice()["contract"], "model": "x" * (M.MAX_TEXT + 1)}):
            value = invoice()
            value["contract"] = contract
            with self.assertRaises(ValueError):
                M.validate_invoice(value)

    def test_json_duplicate_numbers_and_resource_controls(self):
        good = json.dumps(invoice()).encode()
        cases = [good.replace(b'"paid": {}', b'"paid": {"1":1,"1":2}'),
                 good.replace(b'"paid": {}', b'"paid": {"1":' + b'9' * 5000 + b'}'),
                 good.replace(b'"paid": {}', b'"paid": {"1":NaN}'),
                 good.replace(b'"paid": {}', b'"paid": {"1":1e5}'),
                 b'x' * (M.MAX_BYTES + 1), b'\xff', b'[' * 2000]
        for raw in cases:
            with self.assertRaises(ValueError):
                M.parse_invoice(raw)
        too_many = invoice()
        too_many["contract"]["ambient_rank"] = M.MAX_RANK
        too_many["paid"] = {str(r): 0 for r in range(1, M.MAX_SUPPORT + 2)}
        with self.assertRaises(ValueError):
            M.validate_invoice(too_many)

    def test_cli_binds_exact_bytes_and_rejects_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            old_path, new_path = Path(folder) / "old.json", Path(folder) / "new.json"
            old_raw = (json.dumps(invoice({1: 1, 8: 1}, {9: 1})) + "\n").encode()
            old_path.write_bytes(old_raw)
            new_path.write_text(json.dumps(invoice()))
            completed = subprocess.run([sys.executable, "-I", "-B", str(SCRIPT),
                                        str(old_path), str(new_path)], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["classification"], "uniformly_better")
            self.assertEqual(report["inputs"]["old"]["sha256"], sha256(old_raw).hexdigest())
            new_path.write_text('{"paid":{"1":' + '9' * 5000 + '}}')
            failed = subprocess.run([sys.executable, "-I", "-O", "-B", str(SCRIPT),
                                     str(old_path), str(new_path)], capture_output=True, text=True)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(failed.stdout, "")
            self.assertEqual(json.loads(failed.stderr)["status"], "INVALID_RECURSIVE_INVOICE")
            self.assertNotIn("Traceback", failed.stderr)


if __name__ == "__main__":
    unittest.main()
