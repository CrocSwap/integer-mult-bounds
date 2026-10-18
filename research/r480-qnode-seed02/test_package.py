"""Portable source, recipe, output and finite-obligation fault tests."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import verify as V


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=V.inputs()
        cls.recipe=json.loads((HERE/'RECIPE.json').read_text())
        cls.candidate=V.build(cls.original,cls.recipe)

    def test_fixed_labels_and_frame_aliases(self):
        for field,value in ((0,0),(0,True),(1,240)):
            r=copy.deepcopy(self.recipe);r['replacement_A_events'][0][field]=value
            with self.assertRaises(ValueError):V.build(self.original,r)
        r=copy.deepcopy(self.recipe);r['replacement_A_events'][0][2]=[r['replacement_A_events'][0][1]]
        with self.assertRaises(ValueError):V.build(self.original,r)
        r=copy.deepcopy(self.recipe);r['object']['slice_start_inclusive']=2251
        with self.assertRaises(ValueError):V.build(self.original,r)
        r=copy.deepcopy(self.recipe);r['fixed_output_f2_rows'][0],r['fixed_output_f2_rows'][1]=r['fixed_output_f2_rows'][1],r['fixed_output_f2_rows'][0]
        with self.assertRaises(ValueError):V.build(self.original,r)

    def test_stale_cleanup_is_valid_but_differently_priced(self):
        bad=copy.deepcopy(self.candidate);bad['C']=copy.deepcopy(self.original['C'])
        self.assertEqual(V.replay(bad)['adds'],33949)
        with self.assertRaisesRegex(ValueError,'literal cleanup'):V.word_contract(self.original,bad)

    def test_endpoint_valid_growth_and_every_gate_deletion(self):
        r=V.controls(self.original,self.candidate,self.recipe)
        self.assertEqual(r['deleted_candidate_gates_rejected'],43)
        self.assertTrue(r['identity_growth_rejected'])

    def test_minimal_optimized_offline_copy_and_fail_closed_inputs(self):
        with tempfile.TemporaryDirectory(prefix='r480 qnode portable ') as name:
            temp=Path(name);root=temp/'repository with spaces';package=root/'research/r480-qnode-seed02'
            shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
            pins=json.loads((HERE/'SOURCES.json').read_text())
            for relative in pins['required_files']:
                target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/relative,target)
            before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            def run(script='verify.py',*args):
                return subprocess.run([sys.executable,'-I','-O','-B',str(package/script),*map(str,args)],
                    cwd=root,text=True,capture_output=True,timeout=180)
            emitted=temp/'new emitted words'
            result=run('verify.py','--replay-search','--emit',emitted)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            result=run('independent.py')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(before,{str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()})
            for label,word in (('original',self.original),('replacement',self.candidate)):
                self.assertEqual(V.canonical(json.loads(gzip.decompress((emitted/(label+'.json.gz')).read_bytes()))),V.canonical(word))
            output_before={p.name:p.read_bytes() for p in emitted.iterdir()}
            result=run('verify.py','--emit',emitted)
            self.assertNotEqual(result.returncode,0);self.assertIn('output already exists',result.stderr)
            self.assertEqual(output_before,{p.name:p.read_bytes() for p in emitted.iterdir()})
            source=root/V.WORD;raw=source.read_bytes();source.write_bytes(raw+b' ')
            result=run();self.assertNotEqual(result.returncode,0);self.assertIn('source hash',result.stderr);source.write_bytes(raw)
            source=package/'SOURCES.json';raw=source.read_bytes();bad=json.loads(raw)
            key=next(iter(bad['files']));del bad['files'][key];bad['required_files'].remove(key)
            source.write_text(json.dumps(bad));result=run()
            self.assertNotEqual(result.returncode,0);self.assertIn('source inventory',result.stderr);source.write_bytes(raw)
            source=package/'EXPECTED.json';bad=json.loads(source.read_bytes());bad['saved_adds']=18.0
            source.write_text(json.dumps(bad));result=run()
            self.assertNotEqual(result.returncode,0);self.assertIn('receipt mismatch',result.stderr)


if __name__=='__main__':unittest.main(verbosity=2)
