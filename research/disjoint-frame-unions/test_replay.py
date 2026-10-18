#!/usr/bin/env python3
"""Failure-detection controls for the source-bound optional replay."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / 'scripts')]
import verify
import audit_disjoint_tensor as audit
from experiments.disjoint_tensor import DisjointTensor


class ReplayControls(unittest.TestCase):
    def test_source_and_missing_file_are_rejected(self):
        pins = verify.admit_sources()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in pins['files']:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / name, dest)
            self.assertEqual(verify.admit_sources(root), pins)
            target = root / 'scripts/experiments/disjoint_tensor.py'
            original = target.read_bytes()
            target.write_bytes(original + b'\n# changed source\n')
            with self.assertRaisesRegex(ValueError, 'Source pin mismatch'):
                verify.admit_sources(root)
            target.write_bytes(original)
            (root / verify.FIXTURE).unlink()
            with self.assertRaisesRegex(ValueError, 'Source pin mismatch'):
                verify.admit_sources(root)

    def test_adapter_source_is_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            here = Path(tmp)
            shutil.copyfile(HERE / 'SOURCES.json', here / 'SOURCES.json')
            pins = json.loads((here / 'SOURCES.json').read_text())
            for name in pins['adapter_files']:
                shutil.copyfile(HERE / name, here / name)
            (here / 'accelerator.py').write_text('# not the admitted adapter\n')
            with patch.object(verify, 'HERE', here):
                with self.assertRaisesRegex(ValueError, 'Adapter pin mismatch'):
                    verify.admit_sources()

    @unittest.skipIf(sys.flags.optimize, 'Full inherited replay deliberately rejects -O')
    def test_complete_receipt_comparison_and_patch_restoration(self):
        receipt = json.loads((verify.ROOT / verify.FIXTURE).read_text())
        changed = copy.deepcopy(receipt)
        changed['expanded_disjoint_circuit']['roles'] += 1
        missing = copy.deepcopy(receipt)
        del missing['phase_frames']
        previous = DisjointTensor.frame_data
        for mutated in (changed, missing):
            with self.subTest(kind='changed' if mutated is changed else 'missing'):
                with patch.object(audit, 'certificate', return_value=mutated):
                    with self.assertRaisesRegex(ValueError, 'Complete historical certificate mismatch'):
                        verify.replay()
                self.assertIs(DisjointTensor.frame_data, previous)
        with patch.object(audit, 'certificate', side_effect=ValueError('deliberate audit failure')):
            with self.assertRaisesRegex(ValueError, 'deliberate audit failure'):
                verify.replay()
        self.assertIs(DisjointTensor.frame_data, previous)

    def test_optimized_full_replay_is_rejected(self):
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires assertions; omit -O', result.stderr)
        self.assertNotIn('PASS_DISJOINT_FRAME_UNIONS', result.stdout)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'keep.json'
            output.write_bytes(b'unchanged')
            result = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py'),
                                     '--output', str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Output already exists', result.stderr)
            self.assertEqual(output.read_bytes(), b'unchanged')


if __name__ == '__main__':
    unittest.main(verbosity=2)
