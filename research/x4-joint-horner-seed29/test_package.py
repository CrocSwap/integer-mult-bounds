"""Focused mathematical and packaging controls for the joint Horner package."""
import importlib.util
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("joint_verify_tests", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
I = V.module("joint_integer_tests", HERE / "independent.py")


def add(target, source, numerator, denominator=1, frame=3):
    return ["scalar", ["add", ["L", target], ["L", source], numerator, denominator], frame]


class Circuits(unittest.TestCase):
    def test_integer_and_fraction_identities(self):
        # Different denominator alignments and signs, including large odd digits.
        for p,q,d,e in itertools.product((-31,-3,1,7),(-15,-1,3,17),(1,2,8),(1,4,16)):
            a,b = add(0,1,p,d)[1],add(0,2,q,e)[1]
            word = V.J.lower_pair(a,b)
            V.check_pair(a,b,word)
            V.check_pair_cost(a,b,word)
            self.assertEqual(word,I.pair(a,b))
            I.matrix_check(a,b,word)

    def test_aliases_and_non_dyadics(self):
        a,b = add(0,1,3,4)[1],add(0,2,-1,2)[1]
        for source in (["L",0],["L",1],["W",0]):
            bad = [*b[:2],source,*b[3:]]
            with self.assertRaisesRegex(ValueError,"alias"):
                V.J.lower_pair(a,bad)
        for numerator,denominator in ((0,1),(1,3),(True,2),(1,0),(1,-2),(1,2.0)):
            bad = [*a[:3],numerator,denominator]
            with self.assertRaises(ValueError):
                V.J.lower_pair(bad,b)

    def test_physical_event_boundaries(self):
        a,b = add(0,1,1,2),add(0,2,1,2)
        self.assertTrue(V.J.compatible(a,b))
        for changed in (add(0,2,1,2,4),add(0,2,1,2,0),["phase",0,0]):
            self.assertFalse(V.J.compatible(a,changed))
        _,_,lower = V.inputs()
        census,chosen,_ = V.J.plan([a,["phase",0,0],b],lower)
        self.assertEqual((census,chosen),([],[]))

    def test_endpoint_and_cost_are_distinct(self):
        a,b = add(0,1,1,2)[1],add(0,2,1,2)[1]
        word = V.J.lower_pair(a,b)
        for mutated in (word[1:],word[:-1],word[:-2]+word[-1:]):
            with self.assertRaisesRegex(ValueError,"endpoint"):
                V.check_pair(a,b,mutated)
        expensive = word + [("clear",V.WORK)]
        V.check_pair(a,b,expensive)
        with self.assertRaisesRegex(ValueError,"cost"):
            V.check_pair_cost(a,b,expensive)

    def test_path_dp_by_exhaustive_small_matchings(self):
        _,_,lower = V.inputs()
        rng = random.Random(29)
        for _ in range(30):
            events = [add(0,1+i%2,rng.choice((-3,-1,1,5)),rng.choice((1,2,4))) for i in range(9)]
            census,chosen,scores = V.J.plan(events,lower)
            weights = {r["event"]:r["saving"] for r in census if r["saving"]>1}
            optimum = 0
            positions = list(weights)
            for mask in range(1<<len(positions)):
                selected = [p for j,p in enumerate(positions) if mask>>j&1]
                if all(b-a>1 for a,b in zip(selected,selected[1:])):
                    optimum = max(optimum,sum(weights[i] for i in selected))
            self.assertEqual(scores[0],optimum)
            self.assertEqual(sum(weights[i] for i in chosen),optimum)

    def test_independent_complete_certificate(self):
        self.assertEqual(I.run()["complete_real_primitives"],130602)


class Packaging(unittest.TestCase):
    def test_minimal_relocation_and_corruption(self):
        pins = json.loads((HERE/"SOURCES.json").read_text())
        with tempfile.TemporaryDirectory(prefix="joint Horner controls ") as directory:
            root = Path(directory)/"minimal tree with spaces"
            package = root/"research"/HERE.name
            package.mkdir(parents=True)
            for file in HERE.iterdir():
                if file.is_file():
                    shutil.copy2(file,package/file.name)
            for relative in pins["files"]:
                actual = relative
                if relative == "certificates/selected-result.json" and hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != pins["files"][relative]:
                    actual = "certificates/checkpoints/frontier799.json"
                dest = root/actual
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/actual,dest)
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            command = [sys.executable,"-I","-O","-B",str(package/"verify.py")]
            def run(command=command):
                return subprocess.run(command,cwd=directory,env=environment,capture_output=True,text=True,timeout=120)
            result = run()
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn("saved=13072",result.stdout)
            source = root/"research/complex-dyadic-lowering/lower.py"
            original = source.read_bytes()
            source.write_bytes(original+b"\n# corrupt pinned source\n")
            result = run()
            self.assertNotEqual(result.returncode,0)
            self.assertIn("source pin",result.stderr)
            source.write_bytes(original)
            receipt = package/"EXPECTED.json"
            original = receipt.read_bytes()
            data = json.loads(original)
            data["selected_events"][1] = data["selected_events"][0]+1
            receipt.write_text(json.dumps(data))
            result = run([sys.executable,"-I","-O","-B",str(package/"independent.py")])
            self.assertNotEqual(result.returncode,0)
            self.assertIn("overlapping pairs",result.stderr)
            data = json.loads(original)
            data["selected_events"] = data["selected_events"][1:]
            receipt.write_text(json.dumps(data))
            result = run([sys.executable,"-I","-O","-B",str(package/"independent.py")])
            self.assertNotEqual(result.returncode,0)
            self.assertIn("path optimality",result.stderr)
            receipt.write_bytes(original)
            # Checkpoint lookup must tolerate a new active selection, but must
            # still reject corruption of the exact historical checkpoint.
            contextual = root/"certificates/selected-result.json"
            checkpoint = root/"certificates/checkpoints/frontier799.json"
            if not checkpoint.exists():
                checkpoint.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(contextual,checkpoint)
            contextual.write_text('{"kappa":"unrelated new frontier"}\n')
            result = run([sys.executable,"-I","-O","-B",str(package/"independent.py")])
            self.assertEqual(result.returncode,0,result.stderr)
            checkpoint.write_text('{}\n')
            result = run()
            self.assertNotEqual(result.returncode,0)
            self.assertIn("source pin: certificates/selected-result.json",result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
