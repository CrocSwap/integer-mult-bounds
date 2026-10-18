# SPDX-License-Identifier: Apache-2.0
"""Public CLI controls in an export without Git or predecessor executables."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent


class PublicTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='simultaneous-rounding-')
        self.addCleanup(self.temp.cleanup)
        self.package=Path(self.temp.name)/'package';shutil.copytree(HERE,self.package)
        self.env=os.environ.copy();self.env['PATH']='';self.env['PYTHONUTF8']='1'

    def cli(self,*args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py'),*args],
                              capture_output=True,text=True,encoding='utf-8',env=self.env,
                              cwd=self.package,timeout=60)

    def hashes(self):
        return {str(p.relative_to(self.package)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.package.rglob('*') if p.is_file()}

    def test_readonly_and_existing_output(self):
        before=self.hashes();r=self.cli();self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(before,self.hashes())
        r=self.cli('--out',str(self.package/'RESULT.json'))
        self.assertNotEqual(r.returncode,0);self.assertIn('already exists',r.stderr)
        self.assertEqual(before,self.hashes())

    def test_sources(self):
        for row in json.loads((self.package/'REFERENCES.json').read_bytes())['files']:
            p=self.package/row['local'];raw=p.read_bytes();p.write_bytes(raw+b' ')
            r=self.cli();p.write_bytes(raw)
            self.assertNotEqual(r.returncode,0);self.assertIn('reference source pin',r.stderr)

    def test_receipt(self):
        p=self.package/'RESULT.json';raw=p.read_bytes()
        for mutation in ('boolean','float','count'):
            obj=json.loads(raw)
            if mutation=='boolean':obj['cases'][0]['target_bits']=False
            elif mutation=='float':obj['circuits']=27.0
            else:obj['circuits']=28
            p.write_text(json.dumps(obj),encoding='utf-8')
            r=self.cli();self.assertNotEqual(r.returncode,0);self.assertIn('result receipt',r.stderr)

    def test_actual_interaction_and_guard_mutations(self):
        p=self.package/'verify.py';raw=p.read_text(encoding='utf-8')
        for old,new,diagnostic in (
            ('inv(f[i+1])','inv(f[i])','ordered interaction identity'),
            ('target+ceil_log2(8*len(gates)*b**3)','target','interaction budget'),
        ):
            self.assertIn(old,raw);p.write_text(raw.replace(old,new),encoding='utf-8')
            r=self.cli();self.assertNotEqual(r.returncode,0);self.assertIn(diagnostic,r.stderr)
        p.write_text(raw,encoding='utf-8')


if __name__=='__main__':unittest.main()
