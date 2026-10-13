"""End-to-end equivalence and rejection controls for the pinned Gram checker."""
import copy
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import adapter


class PackageTests(unittest.TestCase):
    def run_frames(self, engine, frames, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / 'frames.json').write_text(json.dumps({'frames': frames}))
            return adapter.execute(engine, directory, **kwargs)

    def test_selected_all_determinants_and_receipt(self):
        frames = json.loads(adapter.source_check()[1])['frames']
        receipts = [self.run_frames(engine, frames, trace=True)
                    for engine in ('reference', 'prefix', 'compare')]
        self.assertIn('672 frames checked', receipts[0]['stdout'])
        for key in ('stdout', 'determinant_calls', 'determinant_trace_sha256'):
            self.assertEqual(len({r[key] for r in receipts}), 1, key)
        self.assertGreater(receipts[1]['kernel_stats']['hits'], 0)

    def test_fixture_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            process = subprocess.run([sys.executable, '-B', str(adapter.ROOT /
                'research/e8-bit-carrier-skeleton/code/bit/export_records.py'),
                str(adapter.ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'), tmp],
                capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual((Path(tmp) / 'frames.json').read_bytes(), adapter.source_check()[1])

    def test_frame_rejections(self):
        selected = json.loads(adapter.source_check()[1])['frames']
        bad_dimension = copy.deepcopy(selected)
        bad_dimension['1']['dim'] += 1
        dependent = {'bad': {'dim': 2, 'B': [[1, 0], [1, 0]], 'A': []}}
        annihilator = {'bad': {'dim': 1, 'B': [[1, 0]], 'A': [[1, 0]]}}
        large_residual = {'bad': {'dim': 1, 'B': [[2**127 - 1]], 'A': []}}
        singular_gram = {'bad': {'dim': 1, 'B': [[1] * 9], 'A': []}}
        cases = [(bad_dimension, {}), (dependent, {'h': 2}),
                 (annihilator, {'h': 2}), (large_residual, {'h': 1}),
                 (singular_gram, {'gram': 'triple9', 'h': 9})]
        for frames, kwargs in cases:
            errors = []
            for engine in ('reference', 'prefix', 'compare'):
                with self.subTest(engine=engine, kwargs=kwargs):
                    with self.assertRaises(AssertionError) as caught:
                        self.run_frames(engine, frames, **kwargs)
                    errors.append(caught.exception.args)
            self.assertTrue(all(error == errors[0] for error in errors))

    def test_zero_pivot_and_negative_gram_rejections(self):
        cases = [([[1] * 10], 10),
                 ([[1] * 9 + [0], [0] * 8 + [1, 1]], 10)]
        for basis, dimension in cases:
            frames = {'synthetic': {'dim': len(basis), 'B': basis, 'A': []}}
            outputs = []
            errors = []
            for engine in ('reference', 'prefix', 'compare'):
                kwargs = dict(gram='triple9', h=dimension)
                with self.assertRaises(AssertionError) as caught:
                    self.run_frames(engine, frames, **kwargs)
                errors.append(caught.exception.args)
                outputs.append(self.run_frames(engine, frames, positive=False, trace=True, **kwargs))
            self.assertTrue(all(error == errors[0] for error in errors))
            self.assertEqual(len({r['stdout'] for r in outputs}), 1)
            self.assertEqual(len({r['determinant_trace_sha256'] for r in outputs}), 1)

    def test_source_tampering(self):
        pins, _ = adapter.source_check()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in pins['source_sha256']:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((adapter.ROOT / name).read_bytes())
            adapter.source_check(root)
            for name in pins['source_sha256']:
                target = root / name
                original = target.read_bytes()
                target.write_bytes(original + b'\n')
                with self.assertRaisesRegex(ValueError, 'source pin mismatch'):
                    adapter.source_check(root)
                target.write_bytes(original)

    def test_new_frame_filter(self):
        frames = json.loads(adapter.source_check()[1])['frames']
        with tempfile.TemporaryDirectory() as tmp:
            old = Path(tmp)
            (old / 'frames.json').write_text(json.dumps({'frames': dict(list(frames.items())[::2])}))
            outputs = [self.run_frames(engine, frames, old=old, trace=True)
                       for engine in ('reference', 'prefix', 'compare')]
        self.assertIn('336 frames checked', outputs[0]['stdout'])
        self.assertEqual(len({r['stdout'] for r in outputs}), 1)
        self.assertEqual(len({r['determinant_trace_sha256'] for r in outputs}), 1)

    def test_cli_assertions_and_output_preservation(self):
        command = [sys.executable, '-B', str(adapter.HERE / 'adapter.py')]
        optimized = subprocess.run(command[:1] + ['-O'] + command[1:], capture_output=True, text=True)
        self.assertNotEqual(optimized.returncode, 0)
        self.assertIn('enabled assertions', optimized.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'receipt.json'
            path.write_text('preserve this result')
            existing = subprocess.run(command + ['--out', str(path)], capture_output=True, text=True)
            self.assertNotEqual(existing.returncode, 0)
            self.assertIn('output already exists', existing.stderr)
            self.assertEqual(path.read_text(), 'preserve this result')


if __name__ == '__main__':
    unittest.main(verbosity=2)
