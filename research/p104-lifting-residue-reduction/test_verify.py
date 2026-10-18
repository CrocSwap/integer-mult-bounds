"""Failure controls, not a formal proof. Tekalign/Codex, Apache-2.0."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
v = types.ModuleType('checked_verifier')
v.__file__ = str(HERE/'verify.py')
exec(compile((HERE/'verify.py').read_bytes(),v.__file__,'exec'),v.__dict__)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lift,cls.split,cls.plans = v.inputs()

    def test_signed_residue(self):
        for g in range(1,7):
            for x in range(-500,501):
                q,s = x >> g,x & ((1<<g)-1)
                self.assertEqual(x,(q<<g)+s)
                self.assertTrue(0 <= s < 1<<g)
        value = [(-17,31),(-1,-32),(17,-19),(4,-4)]
        v.check_case(self.lift,self.split,value,2,v.identity(4),v.identity(4))

    def test_short_guard_and_missing_residue(self):
        self.assertEqual(len(v.sharpness(self.lift)),10)
        value = [(1,0)]+[(0,0)]*127
        plan = v.identity(128)
        expected = self.lift.kernel(list(value),7,plan,plan)
        # Dropping the low bits silently loses this unit input.
        self.assertNotEqual(expected,self.split.linear([(0,0)]*128,7,plan,plan))

    def test_nonexact_backend(self):
        value = [(17,-9),(5,7),(0,1),(-4,3)]
        plan = v.identity(4)
        def wrong(value,*args):
            self.split.linear(value,*args)
            a,b = value[0]
            value[0] = (a+1,b)
        actual = self.split.kernel(list(value),2,plan,plan,self.lift,backend=wrong)
        expected = self.lift.kernel(list(value),2,plan,plan)
        self.assertNotEqual(actual,expected)
        # Absolute <1/2 is necessary for unique nearest integer; a tie cannot
        # certify both possible integer targets. Relative quality alone fails.
        from fractions import Fraction
        tie = Fraction(1,2)
        self.assertEqual(abs(tie-0),abs(tie-1))
        self.assertTrue(Fraction(1,1<<200) < Fraction(1,1<<100))
        # Even this tiny relative error allows a one-unit integer error.
        self.assertNotEqual((1<<200)+1,1<<200)

    def test_wrapper_phase_and_reverse_order(self):
        left,right = self.plans[0]
        value = [(x-256,3*x-700) for x in range(512)]
        original = self.lift.kernel(list(value),7,left,right)
        changed = list(left)
        y,phase = changed[53]
        changed[53] = (y,(phase+1)%4)
        self.assertNotEqual(original,self.split.kernel(list(value),7,changed,right,self.lift))
        # A literal inverse must undo stages in reverse order; stages of the
        # nonlinear map cannot be freely commuted like their ideals.
        plan = v.identity(4)
        data = [(1,0),(0,0),(0,0),(0,0)]
        sent = self.lift.kernel(list(data),2,plan,plan)
        wrong = list(sent)
        for bit in range(2):
            for x in range(4):
                if not x >> bit & 1:
                    y = x ^ (1<<bit)
                    wrong[x],wrong[y] = self.lift.pair(wrong[x],wrong[y],True)
        self.assertNotEqual(wrong,data)
        self.assertEqual(self.split.kernel(sent,2,plan,plan,self.lift,True),data)

    def test_scratch_and_invoice(self):
        observed = []
        value = [(-3,9),(2,-8)]
        self.split.kernel(value,1,v.identity(2),v.identity(2),self.lift,
                          observer=lambda q,s: observed.extend(q+s))
        self.assertEqual(observed,[(0,0)]*4)
        invoice = self.split.invoice(512,7,sum(len(self.lift.cycles(p)) for p in self.plans[0]))
        self.assertEqual(invoice['backend_calls'],1)
        self.assertEqual(invoice['residue_pairs'],1792)
        self.assertEqual(invoice['clear_component_writes'],2048)

    def test_source_authentication(self):
        pin = v.loads((HERE/'PREDECESSOR.json').read_bytes())
        raw = (HERE/pin['local']).read_bytes()
        v.authenticate(raw,pin)
        with self.assertRaisesRegex(ValueError,'source SHA256'):
            v.authenticate(raw+b'\n',pin)
        bad = dict(pin,git_blob='0'*40)
        with self.assertRaisesRegex(ValueError,'source blob'):
            v.authenticate(raw,bad)
        # Binding checks a changed source event even if hashes were updated.
        word = v.loads((v.ROOT/'research/p104-rounded-collector/inputs/WORD.json').read_bytes())
        import gzip
        native = v.loads(gzip.decompress((v.ROOT/'research/p104-rounded-collector/inputs/NATIVE.json.gz').read_bytes()))
        word['program'][2031][-1] = 6
        with self.assertRaisesRegex(ValueError,'native binding'):
            v.bind(word,native)

    def test_typed_receipt(self):
        for value in (True,1.0,'1'):
            self.assertNotEqual(v.canonical({'n':1}),v.canonical({'n':value}))
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
            v.loads('{"n":1,"n":2}')

    def test_read_only_git_free_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dest = root/'research'/HERE.name
            shutil.copytree(HERE,dest,ignore=shutil.ignore_patterns('__pycache__'))
            sources = v.loads((HERE/'SOURCES.json').read_bytes())
            for pin in sources['files']:
                if pin['usage'] == 'input':
                    target = root/pin['path']
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes((v.ROOT/pin['path']).read_bytes())
            for path in root.rglob('*'):
                path.chmod(0o555 if path.is_dir() else 0o444)
            try:
                env = dict(os.environ,PATH='/nonexistent',PYTHONOPTIMIZE='2')
                result = subprocess.run([sys.executable,'-I','-O','-B',str(dest/'verify.py')],
                                        cwd=root,env=env,text=True,capture_output=True,timeout=90)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout.strip(),'PASS_P104_LIFTING_RESIDUE_REDUCTION')
            finally:
                for path in root.rglob('*'):
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == '__main__':
    unittest.main()
