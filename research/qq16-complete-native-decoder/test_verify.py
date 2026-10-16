"""Temporal ownership, source authentication and read-only export controls."""
from copy import deepcopy
import importlib.util
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
spec=importlib.util.spec_from_file_location('complete_decoder',HERE/'verify.py')
V=importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class TestBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.R,cls.records,_=V.N.load_sources()
        cls.expected,_=V.logical_reference()
        cls.word=V.program(cls.R)
        cls.temp=tempfile.TemporaryDirectory(prefix='qq16-complete-')
        cls.export=Path(cls.temp.name).resolve()
        if not cls.export.is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise RuntimeError('unexpected temporary root')
        cls.package=cls.export/'research'/HERE.name
        shutil.copytree(HERE,cls.package,ignore=shutil.ignore_patterns('__pycache__'))
        for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if item['usage']=='input':
                dst=cls.export/item['path'];dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/item['path'],dst)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_export(self,*args):
        env=dict(os.environ);env['PATH']=''
        return subprocess.run([sys.executable,'-I','-B','-O',str(self.package/'verify.py'),*args],
                              cwd=self.export,env=env,capture_output=True,text=True,timeout=90)

    def test_git_free_read_only_export(self):
        before={str(p.relative_to(self.export)):p.read_bytes() for p in self.export.rglob('*') if p.is_file()}
        result=self.run_export()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        after={str(p.relative_to(self.export)):p.read_bytes() for p in self.export.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_early_record_cannot_retire_before_output_copy(self):
        word=deepcopy(self.word)
        last=word.pop()
        index=next(i for i,e in enumerate(word) if e['op']=='history_boundary')
        word.insert(index+1,last)
        with self.assertRaisesRegex(ValueError,'L2 full x1 checkpoint'):
            V.replay(word,self.R,self.records,self.expected)

    def test_cover_sweep_cannot_enter_private_owner_body(self):
        word=deepcopy(self.word)
        i=next(i for i,e in enumerate(word) if e['op']=='current_map')
        event=word.pop(i)
        j=next(i for i,e in enumerate(word) if e['op']=='private_begin')
        word.insert(j+1,event)
        with self.assertRaisesRegex(ValueError,'whole cover outside private body'):
            V.replay(word,self.R,self.records,self.expected)

    def test_committed_word_and_receipt_required(self):
        for filename,mutate in [
            ('RESULT.json',lambda v:v['invoice'].__setitem__('native_rank_mass',351)),
            ('WORD.json',lambda v:v[-1].__setitem__('frame','current'))]:
            path=self.package/filename;raw=path.read_bytes()
            try:
                value=json.loads(raw);mutate(value);path.write_text(json.dumps(value))
                result=self.run_export()
                self.assertNotEqual(result.returncode,0)
                self.assertIn('committed '+filename+' differs',result.stderr)
            finally: path.write_bytes(raw)
        path=self.package/'RESULT.json';raw=path.read_bytes()
        path.unlink()
        try: self.assertNotEqual(self.run_export().returncode,0)
        finally: path.write_bytes(raw)

    def test_authenticated_predecessor_before_execution(self):
        path=self.package/'vendor/pr2511/audit.py';raw=path.read_bytes()
        try:
            path.write_bytes(b'raise RuntimeError("SHOULD_NOT_EXECUTE")\n'+raw)
            result=self.run_export()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('pending source hash:',result.stderr)
            self.assertNotIn('RuntimeError: SHOULD_NOT_EXECUTE',result.stderr)
        finally: path.write_bytes(raw)
        path=self.export/'research/joint-query/verify_scalar.py';raw=path.read_bytes()
        try:
            path.write_bytes(raw+b'\n# source drift\n')
            result=self.run_export()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source hash:',result.stderr)
        finally: path.write_bytes(raw)

    def test_write_refuses_overwrite(self):
        before=(self.package/'RESULT.json').read_bytes()
        result=self.run_export('--write')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(before,(self.package/'RESULT.json').read_bytes())


if __name__=='__main__':
    unittest.main()
