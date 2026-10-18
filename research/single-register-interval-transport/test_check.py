"""Failure controls and portable execution for the single-register audit."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('transport',ROOT/'check.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class Checks(unittest.TestCase):
    def test_four_factor_manual_witness(self):
        # Hand derivation: z2-=x; z1-=z2; z2-=z1; y+=z2.
        word=audit.trace(4,1);f=[1,1,-1,1]
        self.assertEqual(word[2:6],[(0,3,0,-1),(3,2,1,-1),(2,3,2,1),(3,1,3,1)])
        self.assertEqual([audit.impulse(word,f,2,6,j,4)[1] for j in range(4)],[-2,1,-1,2])
        self.assertNotEqual(sum(abs(audit.impulse(word,f,2,6,j,4)[1]) for j in range(4)),4)

    def test_wrong_destination_changes_lower_witness(self):
        word=audit.trace(8,1);f=[1,1,1,1,1,-1,-1,1]
        self.assertEqual(word[8][1],3)
        self.assertEqual(audit.impulse(word,f,9,22,3,5)[1],-2)
        self.assertEqual(audit.impulse(word,f,9,22,4,5)[1],3)

    def test_missing_restoration_breaks_independent_model(self):
        word=audit.trace(4,1);f=[1,1,-1,1]
        broken=word[:2]+word[3:]
        correct=audit.prefix(f,len(word))
        columns=[audit.impulse(broken,f,0,len(broken),j,4) for j in range(4)]
        self.assertNotEqual(columns,[list(c) for c in zip(*correct)])

    def test_singleton_bound_is_insufficient(self):
        vector=audit.impulse(audit.trace(4,1),[2]*4,0,16,0,4)
        self.assertGreater(max(map(abs,vector)),4*2)

    def test_source_corruption_rejected(self):
        with tempfile.TemporaryDirectory(prefix='transport damaged ') as temp:
            clone=Path(temp)/'package';shutil.copytree(ROOT,clone)
            p=clone/'vendor/dirty.py';p.write_text(p.read_text()+'\n# corruption\n')
            result=subprocess.run([sys.executable,'-I','-O','-B',str(clone/'check.py')],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('source hash',result.stderr)

    def test_optimized_readonly_relocation(self):
        with tempfile.TemporaryDirectory(prefix='transport relocated ') as temp:
            clone=Path(temp)/'package';shutil.copytree(ROOT,clone)
            files=[p for p in clone.rglob('*') if p.is_file()]
            before={str(p.relative_to(clone)):p.read_bytes() for p in files}
            for p in files:p.chmod(0o444)
            result=subprocess.run([sys.executable,'-I','-O','-B',str(clone/'check.py')],cwd=temp,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            receipt=json.loads(result.stdout)
            self.assertEqual(receipt['status'],'PASS_SINGLE_REGISTER_TRANSPORT')
            self.assertEqual(receipt['destination_intervals'],816036)
            self.assertEqual(before,{str(p.relative_to(clone)):p.read_bytes() for p in clone.rglob('*') if p.is_file()})

if __name__=='__main__':unittest.main()
