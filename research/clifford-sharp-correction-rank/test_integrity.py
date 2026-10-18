"""Public replay, relocation, source-before-execution, and corruption controls."""
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
ROOT=HERE.parents[1]

class Integrity(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='sharp-correction-')
        self.root=Path(self.tmp.name)
        self.pkg=self.root/'research'/HERE.name
        shutil.copytree(HERE,self.pkg,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row.get('usage')=='input':
                dest=self.root/row['path']
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],dest)

    def tearDown(self): self.tmp.cleanup()

    def call(self,script='verify.py',args=(),good=True,opt=True):
        env=os.environ.copy()
        env.pop('PYTHONOPTIMIZE',None)
        result=subprocess.run([sys.executable,'-I',*(['-O'] if opt else []),'-B',str(self.pkg/script),*map(str,args)],
                              cwd=self.root,env=env,text=True,capture_output=True,timeout=60)
        self.assertEqual(result.returncode==0,good,result.stdout+result.stderr)
        return result

    def files(self):
        return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_git_free_read_only_both_engines(self):
        before=self.files()
        self.assertFalse((self.root/'.git').exists())
        self.call(opt=False)
        self.call('independent.py')
        self.assertEqual(before,self.files())

    def test_source_authenticated_before_execution(self):
        path=next(self.root/row['path'] for row in json.loads((HERE/'SOURCES.json').read_text())['files']
                  if row['path'].endswith('clifford_exact.py'))
        path.write_bytes(path.read_bytes()+b'\nraise RuntimeError("TAMPER_WAS_EXECUTED")\n')
        result=self.call(good=False)
        self.assertIn('source SHA256',result.stderr)
        self.assertNotIn('TAMPER_WAS_EXECUTED',result.stderr)
        self.call('independent.py',good=False)

    def test_receipt_type_and_scientific_witness(self):
        receipt=self.pkg/'RESULT.json'
        value=json.loads(receipt.read_text())
        value['sixteen_lane']['minimum_correction_rank']=True
        receipt.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        self.assertIn('committed exact receipt',self.call(good=False).stderr)
        shutil.copyfile(HERE/'RESULT.json',receipt)
        witness=self.pkg/'WITNESS.json'
        value=json.loads(witness.read_text())
        value['correction_columns'][0][0][0]+=1
        witness.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        self.assertIn('committed full witness',self.call(good=False).stderr)
        self.assertIn('complete native-coordinate',self.call('independent.py',good=False).stderr)

    def test_missing_evidence_and_exclusive_output(self):
        witness=self.pkg/'WITNESS.json'
        witness.unlink()
        self.call(good=False)
        fresh=self.root/'new.json'
        self.call(args=('--write',fresh))
        self.assertEqual(fresh.read_bytes(),(HERE/'RESULT.json').read_bytes())
        before=fresh.read_bytes()
        self.call(args=('--write',fresh),good=False)
        self.assertEqual(before,fresh.read_bytes())

if __name__=='__main__': unittest.main()
