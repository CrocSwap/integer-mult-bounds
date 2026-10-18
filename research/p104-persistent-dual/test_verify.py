#!/usr/bin/env python3
"""Export and authentication controls for the persistent P104 dual."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
REL=HERE.relative_to(ROOT)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='p104-persistent-')
        self.root=Path(self.temp.name)
        self.package=self.root/REL
        shutil.copytree(HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
        for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if r['usage']!='input': continue
            target=self.root/r['path']
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/r['path'],target)

    def tearDown(self):
        self.temp.cleanup()

    def run_verifier(self):
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py')],
                              cwd=self.root,capture_output=True,text=True,timeout=180)

    def hashes(self):
        return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_git_free_export_has_no_writes(self):
        before=self.hashes()
        result=self.run_verifier()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PASS_P104_PERSISTENT_DUAL',result.stdout)
        self.assertEqual(before,self.hashes())
        self.assertFalse((self.root/'.git').exists())

    def test_changed_executables_reject_before_import(self):
        paths=[self.package/'source/pr2479/verify.py',
               self.root/'research/p104-native-channel/check_native.py',
               self.root/'research/p104-native-channel/vendor/native_verify.py']
        for path in paths:
            with self.subTest(path=path.name):
                raw=path.read_bytes()
                path.write_bytes(b"raise RuntimeError('IMPORTED_MUTANT')\n")
                result=self.run_verifier()
                path.write_bytes(raw)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('source SHA256',result.stderr)
                self.assertNotIn('IMPORTED_MUTANT',result.stderr)
        (self.package/'source/pr2479/WORD.json').unlink()
        self.assertNotEqual(self.run_verifier().returncode,0)

    def test_full_receipt_drift_not_only_counts(self):
        path=self.package/'RESULT.json'
        receipt=json.loads(path.read_text())
        receipt['endpoint_rows']['X0']['Y0']='0'
        path.write_text(json.dumps(receipt),encoding='utf8')
        result=self.run_verifier()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('complete receipt mismatch',result.stderr)


if __name__=='__main__':
    unittest.main()
