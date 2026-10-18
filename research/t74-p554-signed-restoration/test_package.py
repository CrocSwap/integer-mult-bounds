#!/usr/bin/env python3
"""Subprocess, independent-column and package-corruption tests. Apache-2.0."""
import copy,hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('p554',P/'verify.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
def run(p,*args):
    return subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py'),*map(str,args)],cwd=p.parent,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
def column(w,col):
    a=[Q(0)]*704;a[col]=Q(1)
    for g in v.sequence(w):
        if g[0]=='add':a[g[1]]+=Q(g[3],g[4])*a[g[2]]
        elif g[0]=='scale':a[g[1]]*=Q(g[2],g[3])
        else:raise ValueError('unknown')
    return a
class Tests(unittest.TestCase):
    def test_signed_column_control(self):
        rec=v.read(P/'RECIPE.json')
        for pid in ('gauge44','extra'):
            base=v.read(P/'inputs'/(pid+'-1625.json.gz'));w,tags=v.build(base,rec,pid)
            self.assertEqual(column(w,554),column(base,554))
            m=copy.deepcopy(rec);m['edit']['tail'][0][1][3]=1;wrong,_=v.build(base,m,pid)
            self.assertNotEqual(column(wrong,554),column(base,554))
            # The defect really is dirty-only: the zero-pivot DATA column passes.
            self.assertEqual(column(wrong,74),column(base,74))
    def test_optimized_readonly_relocation(self):
        with tempfile.TemporaryDirectory(prefix='p554 space ') as d:
            dest=Path(d)/'read only package';shutil.copytree(P,dest)
            before={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
            for p in dest.rglob('*'):
                if p.is_file():p.chmod(0o444)
            r=run(dest);self.assertEqual(r.returncode,0,r.stdout[-3000:]);self.assertIn('controls=22',r.stdout)
            for rel,h in before.items():self.assertEqual(hashlib.sha256((dest/rel).read_bytes()).hexdigest(),h)
    def test_source_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'pkg';shutil.copytree(P,dest);p=dest/'inputs/gauge44-1625.json.gz';p.write_bytes(p.read_bytes()+b'changed')
            r=run(dest);self.assertNotEqual(r.returncode,0);self.assertIn('original source pin',r.stdout)
    def test_recipe_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'pkg';shutil.copytree(P,dest);p=dest/'RECIPE.json';j=v.read(p);j['edit']['tail'][0][1][3]=1;p.write_text(json.dumps(j))
            r=run(dest);self.assertNotEqual(r.returncode,0);self.assertIn('target content pin',r.stdout)
    def test_output_preservation(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'existing';dest.mkdir();p=dest/'sentinel';p.write_text('unchanged')
            r=run(P,'--out',dest);self.assertNotEqual(r.returncode,0);self.assertIn('output directory already exists',r.stdout);self.assertEqual(p.read_text(),'unchanged')
if __name__=='__main__':unittest.main(verbosity=2)
