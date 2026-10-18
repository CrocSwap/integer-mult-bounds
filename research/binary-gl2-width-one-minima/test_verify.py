"""Export, mathematical-certificate and source-boundary failure controls."""
import copy
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

class Evidence(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='gl2-width-one-')
        self.root=Path(self.tmp.name)
        self.pkg=self.root/'research/binary-gl2-width-one-minima'
        shutil.copytree(HERE,self.pkg,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                path=self.root/row['path']
                path.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],path)

    def tearDown(self): self.tmp.cleanup()

    def invoke(self,script,*args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.pkg/script),*args],
            cwd=self.root,capture_output=True,text=True,encoding='utf-8',timeout=60)

    def hashes(self):
        return {p.relative_to(self.root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_git_free_readonly_both_engines(self):
        before=self.hashes()
        for script in ('verify.py','check.py'):
            result=self.invoke(script)
            self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(before,self.hashes())

    def test_semantic_distance_and_endpoint_controls(self):
        checker=runpy.run_path(str(self.pkg/'check.py'))
        rows=json.loads((self.pkg/'DISTANCES.json').read_text())
        receipt=json.loads((self.pkg/'RESULT.json').read_text())
        with self.assertRaisesRegex(ValueError,'complete independently enumerated domain'):
            checker['audit'](rows[1:],receipt)
        corrupt=copy.deepcopy(rows)
        next(row for row in corrupt if row[1]==1)[1]=3
        with self.assertRaisesRegex(ValueError,'distance edge inequality'):
            checker['audit'](corrupt,receipt)
        corrupt=copy.deepcopy(receipt)
        next(row for row in corrupt['targets'] if row['word'])['word'].pop()
        with self.assertRaisesRegex(ValueError,'all eight dirty witness columns'):
            checker['audit'](rows,corrupt)
        corrupt=copy.deepcopy(receipt)
        corrupt['targets'][-1]=copy.deepcopy(corrupt['targets'][0])
        with self.assertRaisesRegex(ValueError,'all ordered targets exactly once'):
            checker['audit'](rows,corrupt)

    def test_source_and_typed_evidence(self):
        source=self.pkg/'source/pr2599/PROOF.md'
        original=source.read_bytes()
        source.write_bytes(original+b'\nChanged premise\n')
        for script in ('verify.py','check.py'):
            result=self.invoke(script)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source SHA mismatch',result.stderr)
        source.write_bytes(original)
        path=self.pkg/'RESULT.json'
        receipt=json.loads(path.read_text())
        receipt['new_selected_exponent']=0
        path.write_text(json.dumps(receipt),encoding='utf-8')
        result=self.invoke('verify.py')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('typed result mismatch',result.stderr)
        path.write_text('{"schema_version":1,"schema_version":1}',encoding='utf-8')
        self.assertIn('duplicate JSON key',self.invoke('verify.py').stderr)

    def test_exclusive_full_regeneration(self):
        out=self.root/'new-evidence'
        result=self.invoke('verify.py','--write-new',str(out))
        self.assertEqual(result.returncode,0,result.stderr)
        for name in ('DISTANCES.json','RESULT.json'):
            self.assertEqual(json.loads((out/name).read_text()),json.loads((self.pkg/name).read_text()))
        before=self.hashes()
        self.assertNotEqual(self.invoke('verify.py','--write-new',str(out)).returncode,0)
        self.assertEqual(before,self.hashes())

if __name__=='__main__': unittest.main()
