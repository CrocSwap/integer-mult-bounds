#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Failure controls for arithmetic, extracted data, source pins and replay."""
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bounds as B
import verify as V


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.external = V.load_external()
        cls.snapshot = cls.external[V.SNAPSHOT]
        cls.census = cls.external[V.CENSUS]
        cls.upstream = V.load_upstream(cls.snapshot)

    def run_audit(self, snapshot=None, census=None, upstream=None):
        return V.audit(self.snapshot if snapshot is None else snapshot,
                       self.census if census is None else census,
                       self.upstream if upstream is None else upstream,
                       self.external[V.ASSEMBLY], self.external[V.SELECTED_AUDIT])

    def test_floor_square_root_is_not_an_upper_bound(self):
        # Integer-power comparison, independent of the root recurrence, must
        # detect an upper rounding replaced by floor at deliberately low precision.
        B.root_ladder.cache_clear()
        with patch.object(B, 'sqrt_up', B.isqrt):
            _, hi = B.rational_power(2, 1, Q(1, 2), 1, 8)
            self.assertLess(hi * hi, 2)
        B.root_ladder.cache_clear()
        lo, hi = B.rational_power(2, 1, Q(1, 2), 1, 8)
        self.assertLessEqual(lo * lo, 2)
        self.assertGreaterEqual(hi * hi, 2)

    def test_wrong_exponent_bit_order_breaks_exact_power(self):
        B.root_ladder.cache_clear()
        original = B.root_ladder
        with patch.object(B, 'root_ladder', lambda *a: tuple(reversed(original(*a)))):
            lo, hi = B.rational_power(3, 1, Q(1, 4), 2, 64)
            self.assertFalse(lo**4 <= 3 <= hi**4)

    def test_lost_exponent_ceiling_breaks_non_dyadic_power(self):
        # A floor dyadic exponent alone is insufficient for an upper bound.
        _, hi = B.rational_power(2, 1, Q(1, 4), 2, 64)
        self.assertLess(hi**3, 2)  # cannot enclose 2^(1/3)
        lo, hi = B.rational_power(2, 1, Q(1, 3), 2, 64)
        self.assertLessEqual(lo**3, 2)
        self.assertGreaterEqual(hi**3, 2)

    def test_unresolved_and_exact_equality_do_not_decide(self):
        for interval in ((Q(9, 10), Q(11, 10)), (Q(1), Q(1)), (Q(2), Q(1))):
            with self.assertRaises(ValueError):
                B.side(interval)

    def test_fractional_mixed_profile_is_not_rounded(self):
        census = deepcopy(self.census)
        row = next(w for w in census['words'] if w['id'] == 'W7')
        self.assertEqual(Q(row['local_profile_per_call']['3']), Q(137362, 333))
        self.assertEqual(Q(row['local_profile_per_call']['4']), Q(42458, 333))
        # Even the README's close display rounding, not just flooring to an
        # integer, is not the exact mixed-provider profile.
        row['local_profile_per_call']['3'] = '825/2'
        with self.assertRaisesRegex(ValueError, 'unknown or repeated'):
            self.run_audit(census=census)

    def test_omitted_profile_or_claim_fails(self):
        census = deepcopy(self.census); census['words'].pop()
        with self.assertRaisesRegex(ValueError, 'profile domain'):
            self.run_audit(census=census)
        snap = deepcopy(self.snapshot); snap['claims'].pop()
        with self.assertRaisesRegex(ValueError, 'claim domain'):
            self.run_audit(snapshot=snap)

    def test_wrong_membership_and_ceiling_fail(self):
        census = deepcopy(self.census)
        census['words'][0]['claims'][0] = 9999
        with self.assertRaisesRegex(ValueError, 'membership'):
            self.run_audit(census=census)
        census = deepcopy(self.census)
        census['words'][0]['a_ceiling'] = str(Q(census['words'][0]['a_ceiling']) - V.GRID)
        with self.assertRaisesRegex(ValueError, 'endpoint sign'):
            self.run_audit(census=census)

    def test_wrong_source_provider_count_fails(self):
        upstream = deepcopy(self.upstream)
        claim = next(c for c in self.snapshot['claims'] if c['pr'] == 1195)
        upstream[claim['head'], claim['profile_file']]['provider_counts']['gauge44'] += 9
        with self.assertRaisesRegex(ValueError, 'call count'):
            V.reconstruct(claim, upstream)

    def test_missing_absolute_count_is_not_inferred_from_ratio(self):
        # This is stronger than accepting W/N=896/9 without an original N.
        claim = next(c for c in self.snapshot['claims'] if c['pr'] == 1124)
        upstream = deepcopy(self.upstream)
        del upstream[claim['head'], claim['profile_file']]['complete_invocations']
        with self.assertRaisesRegex(ValueError, 'source call counts'):
            V.reconstruct(claim, upstream)

    def test_schema_rejects_boolean_negative_and_float(self):
        for value in (True, -1, 1.0):
            with self.assertRaises(ValueError):
                V.histogram({'1': value})
        for a in (-Q(1, 10), Q(11, 10), True, 0.01):
            with self.assertRaises(ValueError):
                B.rational_power(73, 1, a)

    def test_source_corruption_and_inventory_omission(self):
        with tempfile.TemporaryDirectory() as name:
            temp = Path(name)
            shutil.copytree(HERE, temp / 'package')
            package = temp / 'package'
            manifest = json.loads((package / 'UPSTREAM.json').read_text())
            row = manifest['records'][0]
            target = package / row['local']
            raw = gzip.decompress(target.read_bytes())
            # Same-length content corruption; recompression headers are irrelevant.
            raw = raw.replace(b'"kappa"', b'"KAPPA"', 1)
            target.write_bytes(gzip.compress(raw, mtime=0))
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                V.load_upstream(self.snapshot, package)
            # Even changing the secondary SHA256 cannot defeat the original Git blob.
            row['sha256'] = hashlib.sha256(raw).hexdigest()
            (package / 'UPSTREAM.json').write_text(V.canonical(manifest))
            with self.assertRaisesRegex(ValueError, 'Git blob'):
                V.load_upstream(self.snapshot, package)
            manifest['records'].pop()
            (package / 'UPSTREAM.json').write_text(V.canonical(manifest))
            with self.assertRaisesRegex(ValueError, 'inventory'):
                V.load_upstream(self.snapshot, package)

    def test_external_source_drift_and_inventory_omission(self):
        with tempfile.TemporaryDirectory() as name:
            temp = Path(name)
            for relative in V.REQUIRED:
                target = temp / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(V.ROOT / relative, target)
            package = temp / 'package'; package.mkdir()
            shutil.copyfile(HERE / 'SOURCES.json', package / 'SOURCES.json')
            target = temp / V.SNAPSHOT
            target.write_bytes(target.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'source drift'):
                V.load_external(temp, package)
            sources = json.loads((package / 'SOURCES.json').read_text())
            sources['files'] = [r for r in sources['files'] if r['path'] != V.SNAPSHOT]
            (package / 'SOURCES.json').write_text(V.canonical(sources))
            with self.assertRaisesRegex(ValueError, 'inventory'):
                V.load_external(temp, package)

    def test_optimized_read_only_relocation_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package)
            for relative in V.REQUIRED:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(V.ROOT / relative, target)
            files = sorted(p for p in root.rglob('*') if p.is_file())
            before = {p: p.read_bytes() for p in files}
            for p in files:
                p.chmod(0o444)
            cmd = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]
            passed = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertIn('PASS_INDEPENDENT_QUEUE_CEILINGS', passed.stdout)
            self.assertEqual(before, {p: p.read_bytes() for p in files})
            receipt = package / 'RESULT.json'; receipt.chmod(0o644)
            data = json.loads(receipt.read_text())
            data['endpoint_decisions'] = True
            receipt.write_text(V.canonical(data))
            failed = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('receipt differs', failed.stderr)


if __name__ == '__main__':
    unittest.main()
