"""Mathematical fault controls and portable package tests; Apache-2.0."""
import copy
from fractions import Fraction as Q
import importlib.util
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import circuits as C
import verify as V
import independent as I


def toy(coefficients):
    return [["scalar", ["add", ["L", 0], ["L", i+1], q.numerator, q.denominator], 7]
            for i, q in enumerate(map(Q, coefficients))]


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.programs, cls.checks = V.inputs()
        cls.events = cls.programs["backward"]

    def test_baseline_is_retained_pr696_on_every_macro(self):
        spec = importlib.util.spec_from_file_location("p696_checked", ROOT / "research/complex-dyadic-lowering/lower.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        count = 0
        for program in self.programs.values():
            for event in program:
                if event[0] == "scalar":
                    self.assertEqual(C.lower(event[1]), module.lower(event[1])); count += 1
        self.assertEqual(count, 38394)

    def test_signed_denominator_alignment_and_dirty_work(self):
        for qs in itertools.product((Q(-5,4), Q(-1), Q(-1,2), Q(1,2), Q(1), Q(5,4)), repeat=3):
            V.local_check(toy(qs))
        for qs in ((-3, Q(1,4), Q(-7,8), 2), (Q(-1,2),)*4, (Q(3,8),Q(-5,4),7,Q(-1,16))):
            V.local_check(toy(qs))
        w = toy((Q(-3,4), Q(5,8), Q(-1,2), 2)); good = C.joint(w)
        for i in range(len(good)):
            with self.assertRaises(ValueError): V.local_check(w, good[:i]+good[i+1:])
        changed = list(good); changed[-2] = ("subtract" if good[-2][0] == "add" else "add", *good[-2][1:])
        with self.assertRaises(ValueError): V.local_check(w, changed)

    def test_source_and_frame_boundaries(self):
        w = toy((Q(1,2), Q(-3,4), Q(5,8)))
        variants=[]
        z=copy.deepcopy(w); z[1][2]=8; variants.append(z)
        z=copy.deepcopy(w); z[1][1][1]=["L",8]; variants.append(z)
        z=copy.deepcopy(w); z[1][1][2]=["L",0]; variants.append(z)
        z=copy.deepcopy(w); z[1][1][2]=["L",1]; variants.append(z)
        z=copy.deepcopy(w); z[1][1][2]=["W",0]; variants.append(z)
        z=copy.deepcopy(w); z[1]=["phase","boundary"]; variants.append(z)
        z=copy.deepcopy(w)
        for e in z:e[2]=0
        variants.append(z)
        for z in variants:
            self.assertFalse(C.compatible(z))
            with self.assertRaises(ValueError): C.joint(z)
        for n,d in ((True,2),(1,True),(1,3),(0,1),(1,0)):
            z=copy.deepcopy(w); z[1][1][3:]=[n,d]
            with self.assertRaises(ValueError): C.joint(z)

    def test_quartet_beats_every_pair_partition_after_clear_discount(self):
        w=self.events[9519:9523]
        self.assertEqual([str(C.coefficient(e[1])) for e in w], ["-1/2","1/2","-1/2","1/2"])
        self.assertEqual(len(C.joint(w)),7)
        def prices(i):
            if i==len(w):return [(0,0)]
            answers=[]
            for n in (1,2):
                if i+n<=len(w):
                    cost=len(C.lower(w[i][1])) if n==1 else len(C.joint(w[i:i+n]))
                    answers.extend((cost+c,1+b) for c,b in prices(i+n))
            return answers
        self.assertEqual(min(cost-(blocks-1) for cost,blocks in prices(0)),9)

    def test_greedy_endpoint_success_is_not_optimality(self):
        w=self.events[18626:18631]; rows=C.census(w); recipe,score=C.choose(w,rows)
        self.assertEqual(score,9); self.assertEqual(recipe,[[0,3],[3,2]])
        greedy=[[0,4]]
        V.local_check(w[:4])  # A valid endpoint still loses two primitives.
        with self.assertRaisesRegex(ValueError,"not optimal"): I.check_recipe(w,greedy)
        self.assertEqual(I.check_recipe(w,recipe),9)
        for recipe in ([[0,3],[2,3]],[[True,4]],[[0,5]],[]):
            with self.assertRaises(ValueError): I.check_recipe(w,recipe)

    def test_interval_dp_against_exhaustive_partitions(self):
        coeff=(Q(-3,4),Q(1,2),Q(5,4),Q(-1),Q(2),Q(-5,8))
        for length in range(2,7):
            w=toy(coeff[:length]); rows=C.census(w); opts={}
            for row in rows:
                if row['saving']>row['length']-1:opts.setdefault(row['start'],[]).append(row)
            def brute(i):
                if i>=length:return 0
                return max([brute(i+1)]+[r['saving']+brute(i+r['length']) for r in opts.get(i,[])])
            self.assertEqual(C.choose(w,rows)[1],brute(0))
            self.assertEqual(I.select_forward(w,I.census(w))[0],brute(0))

    def test_minimal_offline_optimized_replay_and_corruption(self):
        with tempfile.TemporaryDirectory(prefix="four source package ") as d:
            root=Path(d)/"repository with spaces"; package=root/"research/x4-four-source-horner"
            shutil.copytree(HERE,package,ignore=shutil.ignore_patterns("__pycache__"))
            for name in V.REQUIRED:
                dest=root/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/name,dest)
            before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            env=dict(os.environ);env.pop("PYTHONPATH",None); env["PYTHONDONTWRITEBYTECODE"]="1"
            def run(script="verify.py"):
                return subprocess.run([sys.executable,"-I","-O","-B",str(package/script)],cwd=root,env=env,text=True,capture_output=True,timeout=180)
            result=run(); self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            result=run("independent.py");self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(before,{str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()})
            source=root/(V.INPUT+"LOCAL-CHECKS.json"); original=source.read_bytes(); source.write_bytes(original+b" ")
            result=run();self.assertNotEqual(result.returncode,0);self.assertIn("source digest",result.stderr);source.write_bytes(original)
            source=package/"SOURCES.json";original=source.read_bytes(); data=json.loads(original);data['files'].pop(next(iter(data['files'])));source.write_text(json.dumps(data))
            result=run();self.assertNotEqual(result.returncode,0);self.assertIn("source pin",result.stderr);source.write_bytes(original)
            # Change only receipt type; the canonical comparison must not accept int == float.
            source=package/"EXPECTED.json";data=json.loads(source.read_bytes());data['saved_real']=22048.0;source.write_text(json.dumps(data))
            result=run();self.assertNotEqual(result.returncode,0);self.assertIn("receipt mismatch",result.stderr)


if __name__ == '__main__': unittest.main(verbosity=2)
