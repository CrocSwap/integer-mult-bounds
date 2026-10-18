#!/usr/bin/env python3
"""Boundary tests that supplement the mathematical controls. Apache-2.0."""
import json
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='qq16-accumulated-')
        cls.export = Path(cls.temp.name).resolve()
        cls.package = cls.export/'research'/HERE.name
        shutil.copytree(HERE,cls.package,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            if row['usage']=='input':
                target = cls.export/row['path']
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def replay(self):
        env = dict(os.environ)
        env['PATH'] = ''
        return subprocess.run([sys.executable,'-I','-O','-B',str(self.package/'verify.py')],
                              cwd=self.export,env=env,capture_output=True,text=True,timeout=60)

    def test_optimized_git_free_export_is_read_only(self):
        before = {p.relative_to(self.export):p.read_bytes() for p in self.export.rglob('*') if p.is_file()}
        result = self.replay()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PASS_QQ16_ACCUMULATED_FRAME_L2',result.stdout)
        after = {p.relative_to(self.export):p.read_bytes() for p in self.export.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_corrupted_receipts_and_literal_word_reject(self):
        for name,change in (
            ('RESULT.json',lambda v:v['invoice'].__setitem__('native_rank_mass',223)),
            ('WORD.json',lambda v:v[2].__setitem__('sign',-1)),
            ('MAPS.json',lambda v:v['1'].__setitem__('translation',0))):
            path = self.package/name
            original = path.read_bytes()
            try:
                value = json.loads(original)
                change(value)
                path.write_text(json.dumps(value),encoding='utf-8')
                result = self.replay()
                self.assertNotEqual(result.returncode,0,name)
                self.assertIn('committed '+name+' differs',result.stderr)
            finally:
                path.write_bytes(original)

    def test_source_drift_rejects_before_execution(self):
        path = self.export/'research/joint-query/verify_scalar.py'
        original = path.read_bytes()
        try:
            path.write_bytes(original+b'\nraise RuntimeError("must not execute")\n')
            result = self.replay()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source hash:',result.stderr)
            self.assertNotIn('must not execute',result.stderr)
        finally:
            path.write_bytes(original)

    def test_missing_receipt_rejects(self):
        path = self.package/'RESULT.json'
        original = path.read_bytes()
        self.assertTrue(path.resolve().is_relative_to(self.export))
        path.unlink()
        try:
            self.assertNotEqual(self.replay().returncode,0)
        finally:
            path.write_bytes(original)

    def test_equivalent_disjoint_preparation_order_is_accepted(self):
        spec = importlib.util.spec_from_file_location('local_verifier',HERE/'verify.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        R,U,T,records,_ = verifier.load_sources()
        word = verifier.program(R,U,T,records)
        swapped = word[4:8]+word[:4]+word[8:]
        self.assertEqual(verifier.replay(word,R,U,T,records),verifier.replay(swapped,R,U,T,records))


if __name__=='__main__':
    unittest.main()
