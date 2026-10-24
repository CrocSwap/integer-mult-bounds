"""Reject partial replays, mismatched claims and integrity-only substitutes."""
from copy import deepcopy
import json
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
driver = runpy.run_path(str(ROOT / 'scripts/verify_frontier5413.py'))
REVIEW = ROOT / 'docs/research/pr-intake-evidence/pr5413'


class ReceiptBoundaries(unittest.TestCase):
    def setUp(self):
        self.provider = json.loads((REVIEW / 'PROVIDER-COMPLETED.json').read_bytes())
        self.primary = json.loads((REVIEW / 'PRIMARY-PORTABLE-REPLAY.json').read_bytes())
        self.companion = json.loads((REVIEW / 'COMPANION-REPLAY.json').read_bytes())

    def check(self):
        driver['validate_receipts'](self.provider, self.primary, self.companion)

    def test_complete_review_receipts(self):
        self.check()

    def test_missing_precision_stage(self):
        self.primary['runs'] = [r for r in self.primary['runs'] if r['name'] != 'precision']
        with self.assertRaises(ValueError): self.check()

    def test_failed_provider_engine(self):
        self.provider['runs'][0]['returncode'] = 1
        with self.assertRaises(ValueError): self.check()

    def test_forged_complete_status(self):
        self.primary['status'] = 'PASS_PREFLIGHT_ONLY'
        with self.assertRaises(ValueError): self.check()

    def test_missing_output_comparison(self):
        del self.primary['fresh_scientific_summary']['global']
        with self.assertRaises(ValueError): self.check()

    def test_different_claim(self):
        self.primary['scope']['candidate_kappa'] = '.004'
        with self.assertRaises(ValueError): self.check()

    def test_companion_integrity_only(self):
        self.companion['fresh_necessary_screen'] = False
        with self.assertRaises(ValueError): self.check()

    def test_other_construction(self):
        self.companion['primary_head'] = '0' * 40
        with self.assertRaises(ValueError): self.check()

    def test_certificate_uses_fresh_funding(self):
        funding = json.loads((ROOT / driver['PRIMARY'] / 'reports/expected/funding.json').read_bytes())
        old = json.loads((ROOT / 'certificates/frontier4610/CLAIM.json').read_bytes())
        expected = json.loads((ROOT / 'certificates/frontier5413/CLAIM.json').read_bytes())
        self.assertEqual(driver['claim_from_sources'](funding, old), expected)
        changed = deepcopy(funding)
        changed['outer']['margins']['main_transform'] = '1/100'
        self.assertNotEqual(driver['claim_from_sources'](changed, old), expected)


if __name__ == '__main__':
    unittest.main()
