#!/usr/bin/env python3
"""Admission and mathematical mutation controls, standard-library only."""
import copy
import gzip
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V = runpy.run_path(str(HERE/'verify.py'))
I = runpy.run_path(str(HERE/'independent.py'))


class MathematicalTests(unittest.TestCase):
    def test_complete_small_binary_matrices(self):
        # All 4096 binary 3x4 response matrices and all 16 possible support masks.
        for entries in range(1 << 12):
            columns = [(entries >> (3*j)) & 7 for j in range(4)]
            rank, basis = V['kernel'](columns, list(range(4)), offset=0)
            masks = [sum(1 << x for x in b) for b in basis]
            generated = {0}
            for mask in masks:
                generated |= {x^mask for x in tuple(generated)}
            brute = set()
            for mask in range(16):
                response = 0
                for j,c in enumerate(columns):
                    if mask >> j & 1:
                        response ^= c
                if response == 0:
                    brute.add(mask)
            self.assertEqual(generated, brute)
            self.assertEqual(1 << (4-rank), len(brute))
            rows = [[c >> bit & 1 for c in columns] for bit in range(3)]
            second_rank, second_basis = I['nullrows'](rows,4)
            self.assertEqual(second_rank, rank)
            self.assertEqual(len(second_basis),len(basis))

    def test_scoped_geometry_controls(self):
        self.assertEqual(len(V['controls']()),6)

    def test_equal_weight_responses_remain_distinct(self):
        # A zero-response direction must vanish, not merely have equal popcount.
        columns = [0b001,0b010,0b100]
        self.assertEqual(V['kernel'](columns,[0,1,2],offset=0),(3,[]))


    def test_actual_raw_boundary_mutations(self):
        word = json.loads(gzip.decompress((ROOT/V['WORD']).read_bytes()))
        V['extract'](word)
        bad = copy.deepcopy(word)
        bad['D'][0][2].pop()
        with self.assertRaisesRegex(ValueError, 'raw response/compensation equality'):
            V['extract'](bad)
        bad = copy.deepcopy(word)
        bad['C'].pop()
        with self.assertRaisesRegex(ValueError, 'raw response/compensation equality'):
            V['extract'](bad)
        bad = copy.deepcopy(word)
        bad['scatter'][0].append(0)
        with self.assertRaisesRegex(ValueError, 'raw response/compensation equality'):
            V['extract'](bad)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='r439 closure test ')
        self.root = Path(self.tmp.name)
        self.package = self.root/'research'/HERE.name
        shutil.copytree(HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
        source = V['WORD']
        destination = self.root/source
        destination.parent.mkdir(parents=True)
        shutil.copyfile(ROOT/source,destination)

    def tearDown(self):
        self.tmp.cleanup()

    def execute(self, script):
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.package/script)],
                              cwd=self.root, text=True, capture_output=True, timeout=120)

    def test_relocated_optimized_replay(self):
        for script in ['verify.py','independent.py']:
            result = self.execute(script)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('PASS_R439_KERNEL_ENTRANCE',result.stdout)

    def test_source_mutation_rejected_by_both(self):
        p = self.root/V['WORD']
        p.write_bytes(p.read_bytes()+b'changed')
        for script in ['verify.py','independent.py']:
            result = self.execute(script)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source',result.stderr)

    def test_missing_intersection_rejected(self):
        p = self.package/'CERTIFICATE.json'
        data = json.loads(p.read_text())
        data['classification']['classes'].pop()
        p.write_text(json.dumps(data))
        result = self.execute('independent.py')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('exact closure equals certificate',result.stderr)

    def test_wrong_kernel_rejected(self):
        p = self.package/'CERTIFICATE.json'
        data = json.loads(p.read_text())
        row = next(r for r in data['classification']['classes'] if r['nullity'])
        row['kernel_basis'] = [[444,469]]
        p.write_text(json.dumps(data))
        result = self.execute('independent.py')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('independent kernel basis',result.stderr)

    def test_wrong_eligible_helper_rejected(self):
        p = self.package/'CERTIFICATE.json'
        data = json.loads(p.read_text())
        data['classification']['classes'][0]['eligible_helpers'].append(222)
        p.write_text(json.dumps(data))
        result = self.execute('independent.py')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('independent eligibility',result.stderr)

    def test_receipt_overwrite_refused(self):
        result = subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py'),
                                 '--write',str(self.package/'CERTIFICATE.json')],
                                cwd=self.root,text=True,capture_output=True,timeout=120)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('FileExistsError',result.stderr)


if __name__ == '__main__':
    unittest.main()
