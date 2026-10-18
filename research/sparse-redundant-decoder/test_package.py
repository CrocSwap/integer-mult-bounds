#!/usr/bin/env python3
"""Mathematical receipt, provenance and standalone replay fault tests."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

class PackageTests(unittest.TestCase):
    def invoke(self, package, program='verify.py', extra=(), good=True):
        p=subprocess.run([sys.executable,'-I','-O','-B',str(package/program),*map(str,extra)],
                         cwd=package.parent,capture_output=True,text=True,timeout=180)
        self.assertEqual(p.returncode==0,good,p.stdout+p.stderr)
        return p

    def clone(self,root):
        p=root/'research'/HERE.name
        shutil.copytree(HERE,p)
        for x in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if x['usage']=='input':
                dest=root/x['path'];dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/x['path'],dest)
        return p

    def test_01_exact_generation_and_overwrite_guard(self):
        with tempfile.TemporaryDirectory(prefix='sparse receipt ') as tmp:
            out=Path(tmp)/'fresh.json'
            self.invoke(HERE,extra=['--write',out])
            self.assertEqual(out.read_bytes(),(HERE/'CERTIFICATE.json').read_bytes())
            self.invoke(HERE,extra=['--write',out],good=False)

    def test_02_both_optimized_checkers(self):
        self.assertIn('PASS_SPARSE_REDUNDANT_DECODER',self.invoke(HERE).stdout)
        self.assertIn('PASS_INDEPENDENT_SPARSE_DECODER',self.invoke(HERE,'independent.py').stdout)

    def test_03_receipt_theorem_mutation_both_engines(self):
        with tempfile.TemporaryDirectory(prefix='sparse mutation ') as tmp:
            package=self.clone(Path(tmp));path=package/'CERTIFICATE.json'
            data=json.loads(path.read_text());data['all_active_minimum']=64
            path.write_text(json.dumps(data))
            self.invoke(package,good=False)
            self.invoke(package,'independent.py',good=False)

    def test_04_missing_and_incomplete_receipt(self):
        with tempfile.TemporaryDirectory(prefix='sparse incomplete ') as tmp:
            package=self.clone(Path(tmp));path=package/'CERTIFICATE.json'
            data=json.loads(path.read_text());data['planes'][1]['counts']['0,0,1']=10794
            path.write_text(json.dumps(data));self.invoke(package,good=False)
            path.unlink();self.invoke(package,good=False)

    def test_05_changed_source_rejected(self):
        with tempfile.TemporaryDirectory(prefix='sparse source ') as tmp:
            package=self.clone(Path(tmp))
            source=Path(tmp)/'research/complex-frame-pair-decoders/PROOF.md'
            source.write_text(source.read_text()+'\nchanged\n')
            self.invoke(package,good=False)

    def test_06_read_only_relocation_preserves_bytes(self):
        with tempfile.TemporaryDirectory(prefix='sparse read only ') as tmp:
            root=Path(tmp);package=self.clone(root)
            files=[p for p in root.rglob('*') if p.is_file()]
            before={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            for p in files:p.chmod(0o444)
            self.invoke(package);self.invoke(package,'independent.py')
            after={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before,after)

if __name__=='__main__':unittest.main(verbosity=2)
