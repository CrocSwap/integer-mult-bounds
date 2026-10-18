"""Real CLI export/failure checks. ywz65/Codex; Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='p104-operands-')
        self.p=Path(self.tmp.name)/'export'
        shutil.copytree(HERE,self.p,ignore=shutil.ignore_patterns('__pycache__'))

    def tearDown(self):
        for p in self.p.rglob('*'):
            if p.is_file():p.chmod(stat.S_IREAD|stat.S_IWRITE)
        self.tmp.cleanup()

    def cli(self,*args):
        env=os.environ.copy();env['PATH']='';env['PYTHONDONTWRITEBYTECODE']='1'
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.p/'verify.py'),*args],
                              cwd=self.p,capture_output=True,text=True,env=env,timeout=90)

    def fail(self,result,reason):
        self.assertNotEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn(reason,result.stderr)
        self.assertNotIn('PASS_P104_OPERAND_WEIGHTED_FEEDBACK',result.stdout)

    def test_read_only_git_free(self):
        files=[p for p in self.p.rglob('*') if p.is_file()]
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        for p in files:p.chmod(stat.S_IREAD)
        result=self.cli();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'PASS_P104_OPERAND_WEIGHTED_FEEDBACK')
        self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files})

    def test_source_corruption(self):
        for name in ('WORD.json.gz','verify.py'):
            path=self.p/'source'/name;original=path.read_bytes()
            with self.subTest(name=name):
                path.write_bytes(original+b'\n');self.fail(self.cli(),'source SHA256')
            path.write_bytes(original)

    def test_typed_receipt(self):
        path=self.p/'RESULT.json';original=path.read_bytes()
        for key,value in (('original_receipt_reproduced',1),('uniform_guard_bits',27.0)):
            with self.subTest(key=key):
                result=json.loads(original);result[key]=value
                path.write_text(json.dumps(result),encoding='utf-8')
                self.fail(self.cli(),'typed complete receipt differs')

    def test_actual_missing_operand(self):
        path=self.p/'verify.py';code=path.read_text(encoding='utf-8')
        old='a=norm(rows[e.dst])+abs(e.coefficient)*norm(rows[e.src]);w=1+abs(e.coefficient)'
        self.assertEqual(code.count(old),1)
        path.write_text(code.replace(old,'a=abs(e.coefficient)*norm(rows[e.src]);w=1+abs(e.coefficient)'),encoding='utf-8')
        self.fail(self.cli(),'new all-cut peak')

    def test_no_clobber(self):
        path=self.p/'RESULT.json';before=path.read_bytes()
        self.fail(self.cli('--write',str(path)),'FileExistsError')
        self.assertEqual(path.read_bytes(),before)


if __name__=='__main__':unittest.main()
