"""Behavioral export and source-integrity checks for the boundary witness."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

P = Path(__file__).resolve().parent
R = P.parents[1]


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='p104-boundary-')
        self.root = Path(self.temp.name)
        self.package = self.root / 'research' / P.name
        shutil.copytree(P, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        source = json.loads((P/'SOURCES.json').read_text())
        for record in source['files']:
            if record['usage'] == 'input':
                dest = self.root/record['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(R/record['path'],dest)

    def tearDown(self):
        self.temp.cleanup()

    def run_check(self, ok, text):
        result = subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py')],cwd=self.root,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode == 0,ok,result.stdout+result.stderr)
        self.assertIn(text,result.stdout+result.stderr)

    def test_git_free_read_only(self):
        snapshot = lambda: {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
        before = snapshot()
        self.run_check(True,'PASS_P104_DUAL_BOUNDARY_CONTRACTS')
        self.assertEqual(before,snapshot())
        self.assertFalse((self.root/'.git').exists())

    def test_proof_changed(self):
        path = self.package/'source/PR2497-README.md'
        path.write_bytes(path.read_bytes()+b'\nchanged contract\n')
        self.run_check(False,'retained proof SHA256')

    def test_missing_proof(self):
        (self.package/'source/PR2522-README.md').unlink()
        self.run_check(False,'FileNotFoundError')

    def test_native_executable_before_import(self):
        path = self.root/'research/p104-native-channel/vendor/native_verify.py'
        path.write_bytes(b"raise RuntimeError('MUST_NOT_EXECUTE')\n"+path.read_bytes())
        self.run_check(False,'source SHA256')

    def test_false_equality_receipt(self):
        path = self.package/'RESULT.json'
        result = json.loads(path.read_text())
        result['canonical_and_intrinsic_columns_equal'] = True
        path.write_text(json.dumps(result))
        self.run_check(False,'complete retained RESULT equality')


if __name__ == '__main__':
    unittest.main()
