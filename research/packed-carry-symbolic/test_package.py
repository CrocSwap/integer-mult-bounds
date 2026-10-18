#!/usr/bin/env python3
"""Meaningful certificate and packaging controls; Apache-2.0, AI assistance disclosed."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('symbolic',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class PackageTests(unittest.TestCase):
    def test_full_evidence(self):
        self.assertEqual(v.run(),json.loads((HERE/'EXPECTED.json').read_text()))

    def test_infinite_tail_is_not_a_sample(self):
        # 10^100-N passes every tiny replay, but fails universally.
        self.assertFalse(v.nonnegative((-1,10**100),2))
        self.assertFalse(v.nonnegative((1,-3),2))
        self.assertTrue(v.nonnegative((1,-2),2))
        self.assertTrue(v.nonnegative((0,0),2))

    def relocated(self,root):
        package=root/'research'/'packed-carry-symbolic'
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        for name in v.INPUTS:
            dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
        return package

    def invoke(self,package):
        return subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py')],cwd=package.parent.parent.parent,capture_output=True,text=True,timeout=30)

    def test_optimized_readonly_relocation(self):
        with tempfile.TemporaryDirectory(prefix='symbolic carry ') as tmp:
            root=Path(tmp)/'copy';package=self.relocated(root)
            for path in root.rglob('*'):
                if path.is_file():path.chmod(0o444)
            r=self.invoke(package);self.assertEqual(r.returncode,0,r.stderr)

    def test_live_source_mutation_and_missing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'copy';package=self.relocated(root)
            source=root/'upstream/build/sections/05-layers.tex';original=source.read_bytes()
            source.write_bytes(original+b'\n')
            self.assertNotEqual(self.invoke(package).returncode,0)
            source.write_bytes(original);source.unlink()
            self.assertNotEqual(self.invoke(package).returncode,0)

    def test_receipt_and_manifest_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'copy';package=self.relocated(root)
            path=package/'EXPECTED.json';original=path.read_bytes();data=json.loads(original)
            data['proof']['affine_inequalities']-=1;path.write_text(json.dumps(data))
            self.assertNotEqual(self.invoke(package).returncode,0);path.write_bytes(original)
            path=package/'SOURCES.json';data=json.loads(path.read_text());data['files']=[r for r in data['files'] if r['path']!='upstream/LICENSE'];path.write_text(json.dumps(data))
            self.assertNotEqual(self.invoke(package).returncode,0)

    def test_output_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'receipt.json';path.write_bytes(b'keep')
            r=subprocess.run([sys.executable,'-I','-O','-B',str(HERE/'verify.py'),'--write',str(path)],capture_output=True,timeout=30)
            self.assertNotEqual(r.returncode,0);self.assertEqual(path.read_bytes(),b'keep')

if __name__=='__main__':unittest.main()
