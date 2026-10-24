# SPDX-License-Identifier: Apache-2.0
"""Actual relocated CLI and regenerated implementation mutation controls."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class Controls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='signed-scaling-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        original = Path(__file__).resolve().parent
        self.package = self.root/'research'/original.name
        shutil.copytree(original,self.package,ignore=shutil.ignore_patterns('__pycache__'))
        for name in json.loads((original/'VERIFY.json').read_text())['inputs']:
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(original.parent.parent/name,target)

    def run_script(self, mode='independent', optimize=True, write=False):
        command=[sys.executable,'-I']+(['-O'] if optimize else [])
        command += ['-W','error','-B',str(self.package/'verify.py'),'--mode',mode]
        if write:command.append('--write')
        env=dict(os.environ);env['PATH']='/no-git';env.pop('PYTHONPATH',None)
        return subprocess.run(command,cwd=self.root,env=env,capture_output=True,text=True,
                              timeout=40,check=False)

    def snapshot(self):
        return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def rejected(self,result,reason):
        self.assertNotEqual(result.returncode,0,result.stdout)
        self.assertIn(reason,result.stderr)

    def replace_kernel(self,old,new):
        path=self.package/'kernel.py';text=path.read_text()
        self.assertEqual(text.count(old),1)
        path.write_text(text.replace(old,new))

    def test_git_free_readonly_both_engines_and_modes(self):
        before=self.snapshot()
        for mode in ('primary','independent'):
            for optimize in (False,True):
                result=self.run_script(mode,optimize)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('PASS_SIGNED_DYADIC_SCALING',result.stdout)
        self.assertEqual(self.snapshot(),before)

    def test_source_corruption(self):
        path=self.root/'research/bit-row-route-generator/interpreter.py'
        path.write_bytes(path.read_bytes()+b'\ncorrupt source\n')
        self.rejected(self.run_script(),'source SHA256')

    def test_boolean_scientific_receipt(self):
        path=self.package/'RESULT.json';value=json.loads(path.read_text())
        value['physical']['cases']=True
        path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        self.rejected(self.run_script(),'complete typed receipt')

    def test_changed_table_rejects_before_execution(self):
        path=self.package/'TABLE.json.gz';value=json.loads(gzip.decompress(path.read_bytes()))
        value['2/1:True']['tapes']=True
        path.write_bytes(gzip.compress(json.dumps(value).encode(),mtime=0))
        self.rejected(self.run_script(),'exact complete tables')

    def test_regenerated_unused_counter_tail_mutant(self):
        self.replace_kernel("    b._seek_right(a, Q_COUNT, fail, 'Q_erasure_end')\n",'')
        self.rejected(self.run_script(write=True),'entire private tape/head return')

    def test_regenerated_missing_owner_rewind_mutant(self):
        self.replace_kernel("    if source == output:\n        rewind(output, 'original_owner_overwrite_start')\n",'')
        self.rejected(self.run_script(write=True),'scaled original owner/output and record order')

    def test_regenerated_missing_negative_seek_mutant(self):
        path=self.package/'kernel.py';text=path.read_text()
        start=text.index("        rewind(b.LEFT_LENGTH, 'negative_seek_count')")
        end=text.index("        rewind(b.LEFT_LENGTH, 'negative_reverse_count')",start)
        path.write_text(text[:start]+text[end:])
        self.rejected(self.run_script(write=True),'table rejected')


if __name__=='__main__':unittest.main(verbosity=2)
