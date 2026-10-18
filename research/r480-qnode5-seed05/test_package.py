"""Fail-closed package checks. Apache-2.0; substantial OpenAI Codex assistance."""
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('qnode5_verifier', HERE / 'verify.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class PackageChecks(unittest.TestCase):
    def test_dense_boolean_transfer_preserves_order(self):
        candidate = json.loads((HERE / 'CANDIDATE.json').read_text())['best']['gates']
        changed = copy.deepcopy(candidate)
        changed[0][1] = 24
        with self.assertRaises(verifier.Reject):
            verifier.need(all(verifier.block_map(candidate, 1 << i) ==
                              verifier.block_map(changed, 1 << i) for i in range(12)), 'wrong output')

    def test_self_source_rejected(self):
        with self.assertRaises(verifier.Reject):
            verifier.block_map([[487, 19, [19]]], 1)

    def test_out_of_scope_register_rejected(self):
        with self.assertRaises(verifier.Reject):
            verifier.block_map([[487, 19, [120]]], 1)

    def test_source_pins_and_candidate_fail_closed(self):
        root = verifier.ROOT
        with tempfile.TemporaryDirectory(prefix='qnode5-controls-') as temp:
            copy_root = Path(temp)
            package = copy_root / 'research/r480-qnode5-seed05'
            shutil.copytree(HERE, package)
            pins = json.loads((package / 'SOURCES.json').read_text())
            for relative in pins['files']:
                destination = copy_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / relative, destination)
            source = copy_root / verifier.SOURCE
            source.write_bytes(source.read_bytes() + b'corruption')
            failed = subprocess.run([sys.executable, '-I', '-O', '-B', package / 'verify.py'],
                                    capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('source pin:', failed.stderr)
            shutil.copyfile(root / verifier.SOURCE, source)
            candidate = package / 'CANDIDATE.json'
            candidate.write_bytes(candidate.read_bytes() + b' ')
            failed = subprocess.run([sys.executable, '-I', '-O', '-B', package / 'verify.py'],
                                    capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('candidate digest', failed.stderr)

    def test_relocated_optimized_full_replay(self):
        with tempfile.TemporaryDirectory(prefix='qnode5-relocated-') as temp:
            root = Path(temp)
            package = root / 'research/r480-qnode5-seed05'
            shutil.copytree(HERE, package)
            pins = json.loads((package / 'SOURCES.json').read_text())
            for relative in pins['files']:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verifier.ROOT / relative, destination)
            result = subprocess.run([sys.executable, '-I', '-O', '-B', package / 'verify.py',
                                     '--replay-search', '--output', root / 'out'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('controls=93', result.stdout)
            self.assertEqual(json.loads((root / 'out/REPORT.json').read_text()),
                             json.loads((HERE / 'CERTIFICATE.json').read_text()))


if __name__ == '__main__':
    unittest.main()
