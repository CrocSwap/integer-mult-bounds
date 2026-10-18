#!/usr/bin/env python3
"""Semantic and packaging controls. Substantial Codex assistance; Apache-2.0."""
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('triangle_audit', HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class AuditTests(unittest.TestCase):
    def test_p4_nonunique_exact_fixture(self):
        left, right = (0, 1, 3), (5, 6, 7)
        retained = tuple(sorted(set(v.TARGET) | {tuple(sorted((a,b))) for a in left for b in right}))
        self.assertTrue(set(retained).issubset(v.edges(4)))
        self.assertEqual(len(retained), 12)
        self.assertTrue(v.fraction_oracle(4, retained, range(8)))
        for prime in (3, 5, 7):
            self.assertTrue(v.algebra_oracle(4, retained, prime=prime))
        self.assertFalse(v.fraction_oracle(4, retained, v.ROOTS))
        self.assertFalse(v.algebra_oracle(4, retained, prime=2))

    def test_matching_constraint_changes_attachment_count(self):
        envelopes = legal = 0
        for root in v.ROOTS:
            component = set(range(8)) - (set(v.ROOTS)-{root})
            for extra in combinations(sorted(component-{root}), 2):
                left = {root, *extra}
                right = component-left
                crossing = {tuple(sorted((a,b))) for a in left for b in right}
                envelopes += 1
                legal += crossing.issubset(v.edges(4))
        self.assertEqual((envelopes, legal), (30, 6))

    def test_irrelevant_raw_rows_cannot_replace_target_row(self):
        retained = tuple(e for e in v.edges(4) if e in v.TARGET or not set(e)&set(v.ROOTS))
        self.assertTrue(v.fraction_oracle(4, retained, v.ROOTS))
        self.assertFalse(v.fraction_oracle(4, retained, [x for x in range(8) if x != 4]))
        self.assertFalse(v.algebra_oracle(4, retained, [x for x in range(8) if x != 4], prime=5))

    def test_p5_endpoint_no_longer_ties(self):
        p = 5
        isolated, = v.classified_optima(p)
        self.assertEqual(len(isolated), 22)
        self.assertEqual((p-1)**2+3, 19)
        self.assertTrue(v.fraction_oracle(p, isolated, v.ROOTS))

    def test_exact_column_rank_known_fields(self):
        columns = [(1,1,0), (1,0,1), (0,1,1)]
        self.assertEqual(v.column_rank(columns, 3, 2), 2)
        for prime in (3,5,7):
            self.assertEqual(v.column_rank(columns, 3, prime), 3)
        self.assertEqual(v.column_rank([(1,2), (2,4)], 2, 5), 1)

    def test_subprocess_faults_and_readonly_relocation(self):
        with tempfile.TemporaryDirectory(prefix='triangle-audit-') as td:
            root = Path(td)
            package = root/'research'/'triangle-equality-audit'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            source_rel = 'research/prescribed-three-port-decoders/PROOF.md'
            source = root/source_rel
            source.parent.mkdir(parents=True)
            original = (v.ROOT/source_rel).read_bytes()
            source.write_bytes(original)

            def run(*args):
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *args],
                                      cwd=td, capture_output=True, text=True, timeout=180)

            source.write_bytes(original+b'\ncorrupt source\n')
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('source pin mismatch', bad.stderr)
            source.unlink()
            self.assertNotEqual(run().returncode, 0)
            source.write_bytes(original)
            receipt = json.loads((package/'CERTIFICATE.json').read_text())
            receipt['new_kappa'] = 0  # False == 0 in Python, but wrong JSON type.
            corrupted = root/'wrong.json'
            corrupted.write_text(json.dumps(receipt))
            bad = run('--certificate', str(corrupted))
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('certificate mismatch', bad.stderr)
            corrupted.unlink()
            for item in root.rglob('*'):
                item.chmod(0o555 if item.is_dir() else 0o444)
            good = run()
            self.assertEqual(good.returncode, 0, good.stdout+good.stderr)
            self.assertIn('PASS_TRIANGLE_EQUALITY_AUDIT', good.stdout)
            # Restore only our temporary tree's permissions for normal cleanup.
            for item in root.rglob('*'):
                item.chmod(0o755 if item.is_dir() else 0o644)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AuditTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    print('PASS_TRIANGLE_EQUALITY_TESTS groups=6 source_faults=2 receipt_faults=1 readonly_relocation=1')
