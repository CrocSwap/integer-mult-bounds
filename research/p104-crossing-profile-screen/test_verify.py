"""Semantic and public-entry controls; standard library, no optimizer imports."""
import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import verify as v


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = v.histories()
        cls.demands = [r['forced'] for r in v.demands_from_sources()]
        cls.certs = v.read(v.P/'CERTIFICATES.json')
        cls.p = Q(98, 99)

    def test_rational_power_oracle(self):
        # Direct integer inequalities use neither logarithms nor exp.
        for r in range(1, 10):
            lo, hi = v.power(r, Q(98, 99))
            target = r**98 * v.SCALE**99
            self.assertLessEqual(lo**99, target)
            self.assertGreaterEqual(hi**99, target)
            lo, hi = v.power(r, Q(1, 2))
            self.assertLessEqual(lo*lo, r*v.SCALE*v.SCALE)
            self.assertGreaterEqual(hi*hi, r*v.SCALE*v.SCALE)

    def test_dummy_lifetimes_cannot_meet_arrivals(self):
        weak = v.read(v.P/'COUNT-ONLY.json')[str(self.p)]
        v.check_certificate(weak, self.rows, self.demands, self.p, False)
        with self.assertRaisesRegex(ValueError, 'primal constraint'):
            v.check_certificate(weak, self.rows, self.demands, self.p)
        cert = copy.deepcopy(self.certs[str(self.p)])
        cert['primal'] = {'0': '208', '255': '74'}
        # The cuts pass (74*64 > 4680); only 74 lifetimes actually enter H_t.
        with self.assertRaisesRegex(ValueError, 'primal constraint'):
            v.check_certificate(cert, self.rows, self.demands, self.p)

    def test_all_cheap_lifetimes_fail_cuts(self):
        cert = copy.deepcopy(self.certs[str(self.p)])
        cert['primal'] = {'129': '208'}
        with self.assertRaisesRegex(ValueError, 'primal constraint'):
            v.check_certificate(cert, self.rows, self.demands, self.p)

    def test_false_dual_and_alias(self):
        cert = copy.deepcopy(self.certs[str(self.p)])
        cert['dual'][7] = str(10*v.SCALE)
        with self.assertRaisesRegex(ValueError, 'dual inequality'):
            v.check_certificate(cert, self.rows, self.demands, self.p)
        cert = copy.deepcopy(self.certs[str(self.p)])
        first = next(iter(cert['primal']))
        cert['primal']['0'+first] = cert['primal'].pop(first)
        with self.assertRaisesRegex(ValueError, 'canonical primal encoding'):
            v.check_certificate(cert, self.rows, self.demands, self.p)

    def test_independent_history_recursion(self):
        def comps(n):
            if n == 0:
                yield ()
            for first in range(1, n+1):
                for tail in comps(n-first):
                    yield (first,)+tail
        observed = {tuple(r['jumps']): r for r in self.rows}
        self.assertEqual(set(comps(9)), set(observed))
        for jumps, row in observed.items():
            total, caps = 0, [0]*7
            for rank in jumps:
                after = total+rank
                if total > 0 and after < 9:
                    for cut in range(max(1, total), min(7, after-1)+1):
                        caps[cut-1] = 2**(7-rank)
                total = after
            self.assertEqual(caps, row['capacities'])
            # An arrival carrying source dependence needs a positive prior cut.
            self.assertEqual(row['endpoint_arrival'], int(jumps[-1] == 1 and len(jumps) >= 3))

    def test_export_and_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            package = root/'research/p104-crossing-profile-screen'
            shutil.copytree(v.P, package, ignore=shutil.ignore_patterns('__pycache__'))
            for row in v.read(v.P/'SOURCES.json')['files']:
                if row['usage'] == 'input':
                    dest = root/row['path']
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT/row['path'], dest)
            def run():
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                                      capture_output=True, text=True, timeout=60)
            before = {str(p.relative_to(root)): p.read_bytes()
                      for p in root.rglob('*') if p.is_file()}
            good = run()
            self.assertEqual(good.returncode, 0, good.stderr)
            after = {str(p.relative_to(root)): p.read_bytes()
                     for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            receipt = package/'RESULT.json'
            original = receipt.read_bytes()
            data = json.loads(original)
            data['endpoint_arrivals_required'] = True
            receipt.write_text(json.dumps(data), encoding='utf-8')
            self.assertIn('complete typed receipt', run().stderr)
            receipt.write_bytes(original)
            cert_path = package/'CERTIFICATES.json'
            raw = cert_path.read_bytes()
            data = json.loads(raw)
            data[str(self.p)]['primal'] = {'129': '208'}
            cert_path.write_text(json.dumps(data), encoding='utf-8')
            self.assertIn('primal constraint', run().stderr)
            cert_path.write_bytes(raw)
            source = root/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
            source_raw = source.read_bytes()
            source.write_bytes(source_raw+b' ')
            self.assertIn('live source SHA256', run().stderr)
            source.write_bytes(source_raw)
            predecessor = package/'inputs/PR2640-PROOF.md'
            predecessor.write_bytes(predecessor.read_bytes()+b' ')
            self.assertIn('retained predecessor SHA256', run().stderr)

    def test_predecessor_and_duplicate_keys(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            json.loads('{"a":1,"a":2}', object_pairs_hook=v.unique_pairs)
        self.assertEqual(self.demands, [4656, 4656, 4672, 4680, 4672, 4656, 4656])
        self.assertEqual(v.binary_rank([1, 2, 3]), 2)
        with self.assertRaisesRegex(ValueError, 'independent frame basis'):
            v.space([1, 2, 3])


if __name__ == '__main__':
    unittest.main()
