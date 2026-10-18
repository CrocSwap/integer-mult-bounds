"""Bounded package replay, relocated read-only execution and actual corruptions."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent

def call(directory,*args):
    return subprocess.run([sys.executable,'-I','-O','-B',str(directory/'verify.py'),*map(str,args)],
                          cwd=directory.parent,text=True,capture_output=True,timeout=120)

class Package(unittest.TestCase):
    def test_full_replay(self):
        result=call(HERE)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('PASS_COMMUTING_DIRTY_PRECISION',result.stdout)
        print(result.stdout.strip())

    def test_readonly_relocation_and_receipt_fault(self):
        with tempfile.TemporaryDirectory(prefix='commuting precision ') as temp:
            package=Path(temp)/'package with spaces';shutil.copytree(HERE,package)
            for f in package.rglob('*'):
                if f.is_file():f.chmod(0o444)
            result=call(package)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            receipt=package/'CERTIFICATE.json';receipt.chmod(0o644)
            value=json.loads(receipt.read_text());value['budgets']['comparison'][5]['new_fractional']-=1
            receipt.write_text(json.dumps(value))
            result=call(package)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('certificate mismatch',result.stderr)

    def test_source_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'p';shutil.copytree(HERE,package)
            source=package/'vendor/pr1054/dirty_stride.py'
            source.write_text(source.read_text()+'\n# drift\n')
            result=call(package)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source SHA256',result.stderr)

    def test_missing_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'p';shutil.copytree(HERE,package)
            (package/'vendor/pr1278/PROOF.md').unlink()
            result=call(package)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('FileNotFoundError',result.stderr)

    def test_changed_interval_exponent(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'p';shutil.copytree(HERE,package)
            src=package/'precision.py';text=src.read_text()
            self.assertEqual(text.count('J, H = K+c, K+2*c'),1)
            src.write_text(text.replace('J, H = K+c, K+2*c','J, H = K+c, 2*c'))
            result=call(package)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('transport exponents',result.stderr)

    def test_changed_inverse_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'p';shutil.copytree(HERE,package)
            src=package/'precision.py';text=src.read_text()
            self.assertEqual(text.count('I = J+m+8*g+2*ell+16'),1)
            src.write_text(text.replace('I = J+m+8*g+2*ell+16','I = J+m+7*g+2*ell+16'))
            result=call(package)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('inverse preimage guard',result.stderr)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Package)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    print('PASS_COMMUTING_DIRTY_PRECISION_PACKAGE tests=6 relocation=1 corruptions=5')
