"""Behavioral controls for exact code semantics and source integrity."""
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("restricted_primary",ROOT/"verify.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Tests(unittest.TestCase):
    def test_minimum_partition_and_inverse(self):
        # Unequal signature fibers demonstrate that this code is not a quotient group.
        base=[0,0,0,1]
        permutation=[1,2,3,0]
        row,code=v.restricted(base,permutation,4,2)
        self.assertEqual(row["states"],3)
        self.assertEqual(row["fiber_histogram"],{"1":2,"2":1})
        best=4
        for encoding in itertools.product(range(4),repeat=4):
            decoder={}
            update={}
            valid=True
            for x in range(4):
                a=encoding[x]
                b=encoding[(x+2)%4]
                if (a in decoder and decoder[a]!=base[x]) or (a in update and update[a]!=b):
                    valid=False
                    break
                decoder[a]=base[x]
                update[a]=b
            if valid:
                best=min(best,len(set(encoding)))
        self.assertEqual(best,3)
        # Erasing the future observation falsely claims two states.
        self.assertLess(len(set(base)),best)
        self.assertNotEqual(base[2],base[3])

    def test_wrong_update_period_and_nonpermutation(self):
        with self.assertRaisesRegex(ValueError,"cyclic period"):
            v.restricted([0,1,2,3],[1,2,3,0],2,1)
        with self.assertRaises(ValueError):
            v.restricted([0,1,2,3],[0,1,1,3],4,1)

    def test_signed_word_translation_and_rotation(self):
        m=v.authenticate()
        for rank in (1,2,3):
            q=1<<(rank//2+1)
            for j in range(m.shape(rank)):
                x=[((-1)**i)*(13*i*i+7) for i in range(m.shape(rank))]
                for step in (1,2,4):
                    signature=[]
                    for k in range(q//__import__("math").gcd(q,step)):
                        z=x[:]
                        z[j]+=k*step
                        signature.append(m.defect(z,rank))
                    y=x[:]
                    y[j]+=step
                    new=[]
                    for k in range(len(signature)):
                        z=y[:]
                        z[j]+=k*step
                        new.append(m.defect(z,rank))
                    self.assertEqual(new,signature[1:]+signature[:1])

    def test_real_pointwise_code_cannot_update(self):
        m=v.authenticate()
        x=(0,0,0,0)
        y=(0,0,1,1)
        self.assertEqual(m.defect(x,1),m.defect(y,1))
        self.assertNotEqual(m.defect((1,0,0,0),1),m.defect((1,0,1,1),1))

    def test_source_authentication_and_typed_receipt(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name).resolve()
            shutil.copytree(ROOT/"source",root/"source")
            shutil.copyfile(ROOT/"PREDECESSOR.json",root/"PREDECESSOR.json")
            model=root/"source/model.py"
            model.write_text(model.read_text().replace("dr // 2","dr // 3",1))
            with patch.object(v,"ROOT",root):
                with self.assertRaisesRegex(ValueError,"predecessor bytes"):
                    v.authenticate()
        receipt=json.loads((ROOT/"RESULT.json").read_text())
        bad=json.loads(json.dumps(receipt))
        bad["censuses"][1]["coordinates"][0]["steps"][1]["states"]=32
        self.assertFalse(v.typed_equal(receipt,bad))
        self.assertFalse(v.typed_equal(1,True))
        self.assertFalse(v.typed_equal([1,2],[1]))

    def test_optimized_git_free_export(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)/"package"
            shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns("__pycache__"))
            before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob("*") if p.is_file()}
            proc=subprocess.run([sys.executable,"-I","-O","-Werror","-B",str(root/"verify.py")],
                                cwd=name,text=True,capture_output=True,timeout=120)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn("PASS_P104_RESTRICTED_UPDATE_CODES_NO_NEW_KAPPA",proc.stdout)
            after={str(p.relative_to(root)):p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before,after)
            proc=subprocess.run([sys.executable,"-I","-B",str(root/"verify.py"),"--write"],
                                cwd=name,text=True,capture_output=True,timeout=120)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn("FileExistsError",proc.stderr)


if __name__=="__main__":unittest.main()
