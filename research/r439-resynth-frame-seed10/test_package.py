#!/usr/bin/env python3
"""Proof-coverage and admission controls for the independent frame checker."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('frame_check_under_test', HERE / 'check.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class CoverageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nomination = json.loads((HERE / 'NOMINATION.json').read_text())
        cls.receipt = json.loads((HERE / 'CERTIFICATE.json').read_text())
        word = json.loads(gzip.decompress((check.ROOT / check.WORD).read_bytes()))
        cls.problem = check.Problem(word)

    def rejected_nomination(self, mutation, message):
        data = copy.deepcopy(self.nomination)
        mutation(data)
        with tempfile.TemporaryDirectory(prefix='frame coverage ') as tmp:
            (Path(tmp) / 'NOMINATION.json').write_text(json.dumps(data))
            previous = check.HERE
            check.HERE = Path(tmp)
            try:
                with self.assertRaisesRegex(ValueError, message):
                    check.compare_nomination(self.problem, self.receipt['summary'], self.receipt['base_commit'])
            finally:
                check.HERE = previous

    def test_omitted_legal_frame(self):
        self.rejected_nomination(lambda d: d['free_nodes'][10]['choices'].pop(), 'free-frame domain')

    def test_omitted_component(self):
        self.rejected_nomination(lambda d: d['components'].pop(10), 'nomination components')

    def test_changed_copy_boundary(self):
        def change(data):
            key = sorted(data['original_copy_frames'])[10 % 9]
            data['original_copy_frames'][key] = '0'
        self.rejected_nomination(change, 'COPY frames')

    def test_invented_improvement(self):
        self.rejected_nomination(lambda d: d['summary'].__setitem__('improving_components', 1),
                                 'improving_components')

    def test_corrupted_source(self):
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
        first = next(iter(manifest['files']))
        with tempfile.TemporaryDirectory(prefix='frame source ') as tmp:
            path = Path(tmp) / first
            path.parent.mkdir(parents=True)
            path.write_bytes((check.ROOT / first).read_bytes() + b'\ncorrupt source\n')
            previous = check.ROOT
            check.ROOT = Path(tmp)
            try:
                with self.assertRaisesRegex(ValueError, 'source hash mismatch'):
                    check.check_sources()
            finally:
                check.ROOT = previous

    def test_optimized_python_complete_verification(self):
        completed = subprocess.run([sys.executable, '-I', '-B', '-O', str(HERE / 'check.py')],
                                   capture_output=True, text=True, timeout=120)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn('PASS_R439_RESYNTH', completed.stdout)


if __name__ == '__main__':
    unittest.main()
