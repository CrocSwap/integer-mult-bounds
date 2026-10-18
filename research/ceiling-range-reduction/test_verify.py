# SPDX-License-Identifier: Apache-2.0
"""Public-CLI export, binding, and actual arithmetic mutation controls."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
RELATIVE=PACKAGE.relative_to(ROOT)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='ceiling-range-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.package=self.root/RELATIVE
        shutil.copytree(PACKAGE,self.package)
        sources=json.loads((PACKAGE/'SOURCES.json').read_bytes())
        self.inputs=[row['path'] for row in sources['files'] if row['usage']=='input']
        for name in self.inputs:
            dest=self.root/name;dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes((ROOT/name).read_bytes())
        self.env=os.environ.copy();self.env['PATH']='';self.env['PYTHONUTF8']='1'

    def run_cli(self,*args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py'),*args],
                              cwd=self.root,env=self.env,capture_output=True,text=True,
                              encoding='utf-8',timeout=180)

    def inventory(self):
        return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_git_free_default_is_read_only(self):
        before=self.inventory();result=self.run_cli()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(before,self.inventory())

    def test_live_source_corruption_rejects_before_execution(self):
        for name in ('research/complex-local-word-ceiling/ceiling.py',
                     'research/complex-local-word-ceiling/levers.py',
                     'certificates/selected-result.json'):
            with self.subTest(name=name):
                target=self.root/name;raw=target.read_bytes();target.write_bytes(raw+b' ')
                result=self.run_cli();target.write_bytes(raw)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('source pin:',result.stderr)

    def test_receipt_and_existing_output(self):
        target=self.package/'RESULT.json';raw=target.read_bytes()
        result=self.run_cli('--out',str(target))
        self.assertNotEqual(result.returncode,0);self.assertEqual(target.read_bytes(),raw)
        for mutation in ('count','boolean','float'):
            with self.subTest(mutation=mutation):
                obj=json.loads(raw)
                if mutation=='count':obj['independent_log_cases']+=1
                elif mutation=='boolean':obj['hypothetical_large_model']['stages']=True
                else:obj['independent_log_cases']=float(obj['independent_log_cases'])
                target.write_text(json.dumps(obj),encoding='utf-8')
                result=self.run_cli()
                self.assertNotEqual(result.returncode,0)
                self.assertIn('result receipt',result.stderr)

    def test_actual_log_and_exponential_mutants(self):
        target=self.package/'adapter.py';raw=target.read_text(encoding='utf-8')
        for old,new,diagnostic in (
            ('lo+=2*low;hi+=2*high','lo-=2*high;hi-=2*low','log enclosure'),
            ('range(squarings)','range(max(0,squarings-1))','exponential enclosure'),
        ):
            with self.subTest(mutation=old):
                self.assertIn(old,raw)
                target.write_text(raw.replace(old,new),encoding='utf-8')
                result=self.run_cli()
                self.assertNotEqual(result.returncode,0)
                self.assertIn(diagnostic,result.stderr)
        target.write_text(raw,encoding='utf-8')


if __name__=='__main__':unittest.main()
