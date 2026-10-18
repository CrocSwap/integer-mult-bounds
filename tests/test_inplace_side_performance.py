"""Focused controls for the faster inplace-side prefix checker."""
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from experiments import inplace_side as optimized


ORIGINAL_SHA256 = "4e7cb3df2e263f6c7f5907c55e3ee04c08926e6dbc984bbda1722a27b0a48ff6"


def load_baseline():
    path = ROOT / "research/inplace-side-performance/baseline.py"
    spec = importlib.util.spec_from_file_location("inplace_side_baseline", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InplaceSidePerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()
        cls.witnesses = json.loads(
            (ROOT / "scripts/experiments/inplace_side_witnesses.json").read_text(encoding="utf-8")
        )

    def test_baseline_bytes_match_original_pin(self):
        data = (ROOT / "research/inplace-side-performance/baseline.py").read_bytes()
        self.assertEqual(sha256(data).hexdigest(), ORIGINAL_SHA256)
        self.assertNotEqual(
            sha256((ROOT / "scripts/experiments/inplace_side.py").read_bytes()).hexdigest(),
            ORIGINAL_SHA256,
        )

    def test_witness_receipts_match_baseline_fieldwise(self):
        self.assertEqual([w["h"] for w in self.witnesses], [42, 46, 50])
        for witness in self.witnesses:
            args = (witness["h"], witness["pivots"], witness["swaps"])
            self.assertEqual(
                optimized.verify_prefix(*args),
                self.baseline.verify_prefix(*args),
            )

    def test_greatest_unused_mutant_rejects_target_witnesses(self):
        path = ROOT / "research/inplace-side-performance/verify.py"
        spec = importlib.util.spec_from_file_location("inplace_side_performance_verify", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        mutant = module.greatest_unused_mutant_verify_prefix
        for witness in self.witnesses:
            with self.assertRaises(ValueError):
                mutant(witness["h"], witness["pivots"], witness["swaps"])

    def test_certificate_only_source_pin_changes(self):
        import subprocess
        from audit_inplace_side import certificate
        from prepare_layers import serializable

        base = json.loads(
            subprocess.check_output(
                ["git", "show", "0b1cccf86e2f5132ed286a26ef0a681a495740ea:certificates/inplace-side.json"],
                cwd=ROOT,
            )
        )
        regenerated = json.loads(json.dumps(serializable(certificate())))
        committed = json.loads((ROOT / "certificates/inplace-side.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, regenerated)
        old_pin = base["source_sha256"].pop("scripts/experiments/inplace_side.py")
        new_pin = regenerated["source_sha256"].pop("scripts/experiments/inplace_side.py")
        self.assertEqual(old_pin, ORIGINAL_SHA256)
        self.assertEqual(
            new_pin,
            sha256((ROOT / "scripts/experiments/inplace_side.py").read_bytes()).hexdigest(),
        )
        self.assertEqual(base, regenerated)


if __name__ == "__main__":
    unittest.main()
