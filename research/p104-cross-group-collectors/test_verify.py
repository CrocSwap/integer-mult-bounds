#!/usr/bin/env python3
"""Git-free boundary tests for the registered P104 construction."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
INPUTS = ['research/p104-native-channel/inputs/LOWRANK-WITNESS.json',
          'research/p104-native-channel/inputs/P104-FIXTURE.json']


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.package = self.root/'research'/HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        for name in INPUTS:
            dest = self.root/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, dest)

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, script='verify.py', *args, ok=True):
        result = subprocess.run([sys.executable,'-I','-O','-B',str(self.package/script),*args],
                                cwd=self.root, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode == 0, ok, result.stdout+result.stderr)
        return result.stdout+result.stderr

    def hashes(self):
        return {str(p.relative_to(self.root)):sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_git_free_read_only_export(self):
        before = self.hashes()
        self.assertIn('PASS_P104_CROSS_GROUP', self.run_check())
        self.assertIn('PASS_INDEPENDENT_P104_CROSS_GROUP', self.run_check('independent.py'))
        self.assertEqual(before, self.hashes())

    def test_changed_result_rejects(self):
        path = self.package/'RESULT.json'
        result = json.loads(path.read_text())
        result['replays']['combined90']['added_rank_mass'] -= 1
        path.write_text(json.dumps(result))
        self.assertIn('complete result receipt', self.run_check(ok=False))

    def test_source_drift_rejects_before_arithmetic(self):
        for relative, needle in [('inputs/PR2504-CIRCUIT.json','retained sha256'),
                                  ('../p104-native-channel/inputs/P104-FIXTURE.json','live source pin')]:
            with self.subTest(relative=relative):
                path = self.package/relative
                original = path.read_bytes()
                path.write_bytes(original+b'\n')
                self.assertIn(needle, self.run_check(ok=False))
                path.write_bytes(original)

    def test_missing_evidence_rejects(self):
        (self.package/'CROSS-CONTROL.json').unlink()
        self.assertIn('CROSS-CONTROL.json', self.run_check(ok=False))

    def test_late_component_metadata_is_bound(self):
        path = self.package/'CIRCUIT.json'
        circuit = json.loads(path.read_text())
        circuit['late_acquisition']['routes'][0]['captures'][1]['cut'] += 1
        path.write_text(json.dumps(circuit))
        self.assertIn('late route metadata', self.run_check(ok=False))

    def test_output_is_exclusive_and_complete(self):
        output = self.root/'receipt.json'
        self.run_check('verify.py','--out',str(output))
        self.assertEqual(json.loads(output.read_text()),json.loads((self.package/'RESULT.json').read_text()))
        before = output.read_bytes()
        self.assertIn('FileExistsError',self.run_check('verify.py','--out',str(output),ok=False))
        self.assertEqual(before,output.read_bytes())


if __name__ == '__main__':
    unittest.main()
