#!/usr/bin/env python3
"""Independent source/vertex checks and actual package faults; Apache-2.0."""
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import oracle


class IntervalTests(unittest.TestCase):
    def run_copy(self, root, *args):
        script = root/'research'/HERE.name/'verify.py'
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(script), *args],
                              cwd=root, text=True, capture_output=True, timeout=120)

    def copy_inputs(self, root):
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage'] == 'input':
                dest = root/row['path']; dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT/row['path'], dest)
        return package

    def test_independent_scalar_vertices(self):
        # Directly instrument the immutable dispatcher, without the new emitter
        # or polynomial/sign-alignment engines. Enumerate every +/-1 assignment.
        maxima, intervals, assignments = [], 0, 0
        source = ROOT/'research/dirty-cubic-precision/vendor/628/dirty.py'
        for n in range(1, 9):
            d = (n-1).bit_length()+2; best = 1
            positive = oracle.source_events(source, n, 1)
            negative = oracle.source_events(source, n, -1)
            for factors in itertools.product((-1, 1), repeat=n):
                assignments += 1
                for word in (positive, negative):
                    for a in range(len(word)):
                        matrix = oracle.eye(d)
                        for x, y, factor, sign in word[a:]:
                            for col in range(d):
                                matrix[y][col] += sign*factors[factor]*matrix[x][col]
                            best = max(best, sum(abs(v) for v in matrix[y]))
                            intervals += 1
            maxima.append(best)
        self.assertEqual(maxima, [2, 3, 4, 6, 7, 8, 8, 9])
        self.assertEqual(assignments, 510)
        self.assertEqual(intervals, 1553988)

    def test_recursive_prefixes_against_literal_source(self):
        source = ROOT/'research/dirty-cubic-precision/vendor/628/dirty.py'
        for n in range(1, 9):
            d = (n-1).bit_length()+2
            word = oracle.source_events(source, n, 1)
            for factors in ((1,)*n, (-1,)*n, tuple((-1)**j for j in range(n))):
                matrix = oracle.eye(d)
                self.assertEqual(oracle.prefix(n, 0, factors), matrix)
                for boundary, (x, y, j, sign) in enumerate(word, 1):
                    matrix[y] = [v+sign*factors[j]*u for v, u in zip(matrix[y], matrix[x])]
                    self.assertEqual(oracle.prefix(n, boundary, factors), matrix)

    def test_identity_cut_inverse_recurrence(self):
        # Check the entire Q matrix underlying the written proof, not only the
        # final target row. Prefix oracle constructs no expanded word or Q formula.
        for h in range(1, 15):
            n = 1 << (h-1); cut = 3*(4**(h-1))//5
            actual = oracle.inverse(oracle.prefix(n, cut, (1,)*n))
            expected = oracle.eye(h+1)
            for i in range(1, h+1):
                expected[i] = [0]*(h+1)
                expected[i][0] = -int(i % 2 == 0)
                for j in range(i, h+1):
                    expected[i][j] = (-1)**(j-i)
            self.assertEqual(actual, expected)

    def test_source_and_predecessor_corruptions(self):
        mutations = [('research/dirty-cubic-precision/vendor/628/dirty.py', 'source drift'),
                     ('research/'+HERE.name+'/vendor/PR1278-PROOF.md', 'predecessor drift')]
        for relative, reason in mutations:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp); self.copy_inputs(root)
                with (root/relative).open('a') as stream:
                    stream.write('\nCORRUPTED SOURCE\n')
                result = self.run_copy(root, '--bindings-only')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(reason, result.stderr)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); package = self.copy_inputs(root)
            p = package/'SOURCES.json'; manifest = json.loads(p.read_text())
            manifest['files'] = [r for r in manifest['files'] if r.get('usage') != 'input']
            p.write_text(json.dumps(manifest))
            result = self.run_copy(root, '--bindings-only')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source inventory mismatch', result.stderr)

    def test_understated_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); package = self.copy_inputs(root)
            p = package/'CERTIFICATE.json'; receipt = json.loads(p.read_text())
            receipt['family'][1]['norm'] = 4
            p.write_text(json.dumps(receipt))
            result = self.run_copy(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('certificate mismatch', result.stderr)

    def test_full_read_only_relocation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.copy_inputs(root)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            for name in before:
                (root/name).chmod(0o444)
            result = self.run_copy(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS_DIRTY_INTERVAL_COEFFICIENT_BOUNDARY', result.stdout)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
