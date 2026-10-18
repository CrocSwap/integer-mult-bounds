"""Semantic controls deliberately bypass source hashes, plus package controls."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import verify as v

ROOT = Path(__file__).resolve().parent


class DualAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile, cls.certificate = v.load_inputs(ROOT)
        cls.result = v.audit(cls.profile, cls.certificate)
        cls.eta = {int(k): v.Q(x) for k, x in cls.result["dual_rank"].items()}
        cls.lam = {int(k): v.Q(x) for k, x in cls.result["dual_width"].items()}

    def test_exact_expected_report_and_strict_margins(self):
        self.assertEqual(self.result, json.loads((ROOT / "EXPECTED.json").read_bytes()))
        self.assertGreater(v.Q(self.result["minimum_dual_slack"]), v.Q(2, 10**11))
        self.assertGreater(v.Q(self.result["ideal_moment_rejection_margin_lower"]), v.Q(7, 10**10))

    def test_every_rank_multiplier_corruption(self):
        for rank in self.eta:
            with self.subTest(rank=rank):
                eta = dict(self.eta)
                eta[rank] += v.Q(1, 10**4)
                with self.assertRaisesRegex(ValueError, "dual inequality"):
                    v.check_dual(eta, self.lam)

    def test_every_width_multiplier_corruption(self):
        for width in self.lam:
            with self.subTest(width=width):
                lam = dict(self.lam)
                lam[width] += v.Q(1, 10**4)
                with self.assertRaisesRegex(ValueError, "dual inequality"):
                    v.check_dual(self.eta, lam)

    def test_feasible_but_too_weak_dual_is_rejected(self):
        eta = {r: x - 1 for r, x in self.eta.items()}
        with self.assertRaisesRegex(ValueError, "ideal moment does not reject"):
            v.check_dual(eta, self.lam)

    def test_missing_dual_coordinates(self):
        for original, other, is_eta in ((self.eta, self.lam, True), (self.lam, self.eta, False)):
            changed = dict(original)
            del changed[next(iter(changed))]
            with self.assertRaisesRegex(ValueError, "dual .* keys"):
                v.check_dual(changed, other) if is_eta else v.check_dual(other, changed)

    def test_changed_model_inputs(self):
        mutations = [
            ("profile", "profile", "1"),
            ("profile", "widths", "7"),
            ("certificate", "helper_widths", "9"),
            ("certificate", "rank_stock", "48"),
        ]
        for target, field, key in mutations:
            with self.subTest(target=target, field=field):
                profile, certificate = copy.deepcopy(self.profile), copy.deepcopy(self.certificate)
                obj = profile if target == "profile" else certificate
                obj[field][key] += 1
                with self.assertRaises(ValueError):
                    v.audit(profile, certificate)
        for field in ("calls", "patterns", "remainder_mass"):
            with self.subTest(field=field):
                certificate = copy.deepcopy(self.certificate)
                certificate[field] += 1
                with self.assertRaises(ValueError):
                    v.audit(self.profile, certificate)

    def test_changed_endpoints(self):
        for field in ("rejected_b", "kappa_upper"):
            with self.subTest(field=field):
                certificate = copy.deepcopy(self.certificate)
                certificate[field] = str(v.Q(certificate[field]) + v.Q(1, 10**10))
                with self.assertRaises(ValueError):
                    v.audit(self.profile, certificate)

    def test_positive_series_domains_and_zero_rank(self):
        self.assertEqual(v.rank_cost_lower(0), 0)
        self.assertEqual(v.rank_cost_lower(1, v.Q(0)), 0)
        self.assertEqual(v.log_lower(v.Q(1)), 0)
        self.assertEqual(v.exp_lower(v.Q(0)), 1)
        for callback, arg in ((v.log_lower, v.Q(1, 2)), (v.exp_lower, v.Q(-1)),
                              (v.rank_cost_lower, -1), (v.rank_cost_lower, 73)):
            with self.subTest(arg=arg), self.assertRaises(ValueError):
                callback(arg)

    def test_relocated_package_and_source_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "standalone"
            shutil.copytree(ROOT, root)
            self.assertEqual(v.audit(*v.load_inputs(root)), self.result)
            path = root / "inputs/profile.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source sha256"):
                v.load_inputs(root)

    def test_source_head_and_file_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "standalone"
            shutil.copytree(ROOT, root)
            path = root / "SOURCES.json"
            manifest = json.loads(path.read_bytes())
            manifest["commit"] = "0" * 40
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "source commit"):
                v.load_inputs(root)
            manifest["commit"] = v.SOURCE_COMMIT
            manifest["files"].pop()
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "source file set"):
                v.load_inputs(root)


if __name__ == "__main__":
    unittest.main()
