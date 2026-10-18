#!/usr/bin/env python3
"""Mathematical, lifecycle, accounting and source-export failure controls."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('two_copy_primary', HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = v.pinned_word()
        cls.n = 2*cls.word['v'] + cls.word['R']
        cls.part, cls.search = v.optimize(cls.word)

    def test_every_partition_dirty_scatter_boundary(self):
        baseline = tuple((i,) for i in range(9))
        want = v.replay(v.scatter_events(self.word, baseline), self.n)[0]
        counts = 0
        for p in v.partitions(list(range(9))):
            ins = v.scatter_events(self.word, p)
            self.assertLessEqual(v.scatter_contract(self.word, ins), 2)
            self.assertEqual(v.replay(ins, self.n)[0], want)
            counts += 1
        self.assertEqual(counts, 2620)

    def test_ring_block_on_signed_dirty_values(self):
        # Every scalar coefficient is tested independently; dense signed
        # examples make accidental zero-initialization assumptions visible.
        for a in (-7, 0, 11):
            for b in (-13, 0, 5):
                for y in (-3, 4):
                    p, q = a, b
                    left, right, both, neither = y+p, y+q, y, y
                    p += q
                    both += p
                    p -= q
                    self.assertEqual((left, right, both, neither, p, q),
                                     (y+a, y+b, y+a+b, y, a, b))

    def test_all_eight_temporary_gate_omissions(self):
        ins = v.events(self.word, self.part)
        indices = [i for i, e in enumerate(ins) if e[0] == 'add' and e[1] >= self.n]
        self.assertEqual(len(indices), 8)
        for i in indices:
            with self.subTest(i=i), self.assertRaisesRegex(ValueError, 'ERASE'):
                v.replay(ins[:i] + ins[i+1:], self.n)

    def test_same_add_total_does_not_prove_chronological_erase(self):
        ins = v.events(self.word, self.part)
        j = next(i for i, e in enumerate(ins) if e == ('add', self.n, self.n+1, -1))
        moved = ins[:j] + [ins[j+1], ins[j]] + ins[j+2:]
        self.assertEqual(sum(e[0] == 'add' for e in moved), 11380)
        with self.assertRaisesRegex(ValueError, 'ERASE'):
            v.replay(moved, self.n)

    def test_nonzero_or_persistent_source_is_not_a_zero_copy(self):
        ins = v.scatter_events(self.word, self.part)
        bad = [('add', self.word['v'], self.word['ret'][0], 1)] + ins
        with self.assertRaisesRegex(ValueError, 'ZERO'):
            v.scatter_contract(self.word, bad)
        with self.assertRaisesRegex(ValueError, 'unpriced'):
            v.scatter_contract(self.word, [('move', self.n, 0)] + ins)

    def test_wrong_center_and_underpriced_lifetime(self):
        ins = v.scatter_events(self.word, self.part)
        j = next(i for i, e in enumerate(ins) if e[0] == 'erase')
        bad = list(ins)
        bad[j] = ('erase', self.n, self.word['ret'][1])
        with self.assertRaises(ValueError):
            v.scatter_contract(self.word, bad)
        self.assertEqual(v.scatter_contract(self.word, ins), 2)
        self.assertNotEqual(v.scatter_contract(self.word, ins), 1)

    def test_no_unpaid_preparation_in_objective(self):
        # Removing the two charged shears per selected pair invents eight ADDs.
        gross = sum(self.search['intersection_matrix'][b[0]][b[1]]
                    for b in self.part if len(b) == 2)
        self.assertEqual(gross, 128)
        self.assertEqual(gross - 2*4, self.search['optimal_saving'])
        empty_overlap = {'ret':[0, 1], 'scatter':[[0], [1]]}
        p, result = v.optimize(empty_overlap)
        self.assertEqual(p, ((0,), (1,)))
        self.assertEqual(result['optimal_saving'], 0)

    def test_typed_and_strict_json(self):
        self.assertNotEqual(v.canonical({'count':1}), v.canonical({'count':True}))
        for value in ('{"x":1,"x":2}', '{"x":NaN}'):
            with tempfile.TemporaryDirectory() as td:
                f = Path(td)/'bad.json'
                f.write_text(value)
                with self.assertRaises(ValueError):
                    v.load(f)

    def test_source_export_and_cli_corruptions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = root/'research'/'bit-two-copy-scatter'
            pkg.mkdir(parents=True)
            for name in ('verify.py', 'SOURCES.json', 'CERTIFICATE.json'):
                shutil.copyfile(HERE/name, pkg/name)
            inputs = [i for i in v.load(HERE/'SOURCES.json')['files'] if i['usage'] == 'input']
            for item in inputs:
                dest = root/item['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT/item['path'], dest)
            cmd = [sys.executable, '-I', '-O', '-B', str(pkg/'verify.py')]
            def run():
                return subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=30)
            files = [p for p in root.rglob('*') if p.is_file()]
            initial = {str(p):p.read_bytes() for p in files}
            for p in files:
                p.chmod(0o444)
            try:
                result = run()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual({str(p):p.read_bytes() for p in files}, initial)
            finally:
                for p in files:
                    p.chmod(0o644)
            original = v.load(pkg/'CERTIFICATE.json')
            changes = (
                lambda x: x['candidate'].__setitem__('adds', 11379),
                lambda x: x['candidate'].__setitem__('peak_live_copies', 1),
                lambda x: x['local_recursive_invoice'].__setitem__('copy_rank_sum', 62),
                lambda x: x['search'].__setitem__('optimal_partitions', 104),
                lambda x: x['baseline'].__setitem__('peak_live_copies', True),
                lambda x: x['candidate_bounds'].__setitem__('B', 5911840),
            )
            for edit in changes:
                changed = copy.deepcopy(original)
                edit(changed)
                (pkg/'CERTIFICATE.json').write_text(json.dumps(changed))
                self.assertNotEqual(run().returncode, 0)
            (pkg/'CERTIFICATE.json').write_text(json.dumps(original))
            source = root/v.WORD
            source.write_bytes(source.read_bytes()+b'changed')
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source pin', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
