#!/usr/bin/env python3
"""Externally exercised corruption controls; no mathematical coverage by analogy.

Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


class CorruptionControls(unittest.TestCase):
    def rejects(self,script,args,reason):
        result=subprocess.run([sys.executable,'-I','-O','-B',str(script),*map(str,args)],
                              capture_output=True,text=True,timeout=180)
        self.assertNotEqual(result.returncode,0,result.stdout)
        self.assertIn(reason,result.stderr)
        self.assertNotIn('PASS_',result.stdout)

    def with_certificate(self,change,script,reason):
        data=json.loads((HERE/'CERTIFICATE.json').read_text());change(data)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'corrupt.json';path.write_text(json.dumps(data))
            flag='--certificate' if script=='independent_check.py' else '--check'
            self.rejects(HERE/script,[flag,path],reason)

    def test_missing_support_stratum(self):
        self.with_certificate(lambda d:d['strata'].pop(),'independent_check.py','incomplete support-stratum')

    def test_missing_exception(self):
        self.with_certificate(lambda d:d['exceptions'].pop(),'independent_check.py','exception inventory mismatch')

    def test_forged_copy_claim(self):
        self.with_certificate(lambda d:d['claim'].update(sharp_whole_copy_sum=63),'verify.py','certificate mismatch')

    def test_invalid_transport(self):
        self.with_certificate(lambda d:d['triple_transports'][0].update(permutation=[0]*8),
                              'independent_check.py','invalid permutation')

    def source_export(self,folder):
        root=Path(folder);package=root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                dest=root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],dest)
        return root,package

    def test_missing_source_pin(self):
        with tempfile.TemporaryDirectory() as folder:
            root,p=self.source_export(folder)
            j=json.loads((p/'SOURCES.json').read_text())
            j['files']=[r for r in j['files'] if not r['path'].endswith('/geometry.py')]
            (p/'SOURCES.json').write_text(json.dumps(j))
            self.rejects(p/'verify.py',[],'incomplete live source inventory')

    def test_changed_geometry_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root,p=self.source_export(folder)
            g=root/'research/p112-single-lift/geometry.py'
            g.write_bytes(g.read_bytes()+b'\n# altered pinned input\n')
            self.rejects(p/'verify.py',[],'source SHA256')


if __name__=='__main__':unittest.main(verbosity=2)
