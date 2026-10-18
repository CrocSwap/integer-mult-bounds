"""Semantic, invoice and publication failure controls. Tekalign/Codex, Apache-2.0."""
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
v = types.ModuleType('test_source_bound_verifier')
v.__file__ = str(HERE/'verify.py')
exec(compile((HERE/'verify.py').read_bytes(),v.__file__,'exec'),v.__dict__)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old,cls.check,cls.gaussian = v.inputs()

    def test_noninjective_overwrites_and_dirty_target(self):
        program = [('set',0,0,0)]*40+[('and',1,0,1)]
        # Two different inputs deliberately share an output; source retention
        # is necessary. Running an alleged function inverse cannot clean them.
        outputs = []
        for source in ([0,1],[1,1]):
            before = list(source)
            target = [1,0]
            invoice = self.check.evaluate(program,source,target)
            self.assertEqual(source,before)
            self.assertEqual(invoice,self.check.expected_invoice(41,2))
            outputs.append(target)
        self.assertEqual(outputs,[[1,0],[1,0]])

    def test_omitted_cleanup_and_corrupted_trace(self):
        program = [('not',0,0,0)]*65
        with self.assertRaisesRegex(ValueError,'checkpoint cleanup'):
            self.check.evaluate(program,[1,1],[0,0],omit_reverse=True)
        with self.assertRaisesRegex(ValueError,'inverse transition consistency'):
            self.check.evaluate(program,[1,1],[0,0],corrupt_history=True)

    def test_no_hidden_quadratic_bank_resets(self):
        size = 8
        for k in (4,8,16):
            program = [('not',0,0,0)]*(k*k*size)
            x,y = [1]*size,[0]*size
            good = self.check.evaluate(program,x,y)
            bad = self.check.evaluate(program,x,[0]*size,reset_bank_each_call=True)
            self.assertEqual(good['checkpoint_moves'],6*(k-2)*size)
            self.assertGreater(bad['checkpoint_moves'],good['checkpoint_moves'])
            self.assertGreaterEqual(bad['checkpoint_moves'],(k-1)*(k-2)*size)

    def test_tail_projection_alias_and_bad_types(self):
        code = [('not',0,0,0)]*53
        source = [0]*7
        target = [1,0,1]
        before = target.copy()
        self.check.evaluate(code,source,target,[0,2,6])
        self.assertEqual(target,[before[0]^1,before[1],before[2]])
        p = self.check.plan(53,7)
        self.assertLess(p['bounds'][-1][1]-p['bounds'][-1][0],p['max_segment'])
        with self.assertRaisesRegex(ValueError,'streaming projection order'):
            self.check.evaluate(code,source,[0,0],[6,0])
        with self.assertRaisesRegex(ValueError,'alias'):
            self.check.evaluate(code,source,source)
        with self.assertRaisesRegex(ValueError,'Boolean payload'):
            self.check.evaluate(code,[False]*7,[0]*7)
        for t,s in ((-1,7),(3,0),(True,8),(3,2.0)):
            with self.assertRaisesRegex(ValueError,'plan domain'):
                self.check.plan(t,s)

    def test_missing_output_gate_is_observable(self):
        code,size,projection = self.gaussian.compile_linear(2,(0,1),12)
        values = [(3,-5),(7,2),(-2,3),(4,-8)]
        source = self.gaussian.encode_input(values,12,size)
        expected = self.old.scaled(values,(0,1))
        # Remove every output write, keeping all scratch/carry operations.
        output_set = set(projection)
        changed = [gate for gate in code if gate[1] not in output_set]
        target = [0]*len(projection)
        self.check.evaluate(changed,source,target,projection)
        self.assertNotEqual(self.gaussian.decode_output(target,12),expected)
        with self.assertRaisesRegex(ValueError,'signed input headroom'):
            self.gaussian.encode_input([(2048,0)]*4,12,size)

    def test_scaled_orientations_not_integer_inverses(self):
        source = [(1,2),(3,-4),(-5,6),(7,8)]
        forward = self.old.scaled(source,(0,1))
        backward = self.old.scaled(forward,(0,1),True)
        self.assertEqual(backward,[(16*a,16*b) for a,b in source])
        self.assertNotEqual(backward,source)
        exp = v.exponents()
        self.assertEqual(exp['new_clean_space'],'1797203/1200000')
        self.assertNotEqual(exp['new_clean_space'],exp['old_clean_space'])

    def test_json_types_and_source_drift(self):
        for altered in (True,1.0,'1'):
            self.assertNotEqual(v.canonical({'n':1}),v.canonical({'n':altered}))
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
            v.loads('{"n":1,"n":2}')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for pin in v.loads((HERE/'SOURCES.json').read_bytes())['files']:
                if pin['usage'] == 'input':
                    target = root/pin['path']
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes((v.ROOT/pin['path']).read_bytes())
            path = root/'research/batched-spaced-lifting/model.py'
            path.write_bytes(path.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'source SHA256'):
                v.inputs(root)

    def test_readonly_export_and_receipt_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dest = root/'research'/HERE.name
            shutil.copytree(HERE,dest,ignore=shutil.ignore_patterns('__pycache__'))
            for pin in v.loads((HERE/'SOURCES.json').read_bytes())['files']:
                if pin['usage'] == 'input':
                    target = root/pin['path']
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes((v.ROOT/pin['path']).read_bytes())
            for path in root.rglob('*'):
                path.chmod(0o555 if path.is_dir() else 0o444)
            env = dict(os.environ,PATH='/nonexistent',PYTHONOPTIMIZE='2')
            command = [sys.executable,'-I','-O','-B',str(dest/'verify.py')]
            try:
                result = subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=90)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout.strip(),'PASS_LIFTING_CHECKPOINT_SPACE')
                receipt = dest/'RESULT.json'
                receipt.chmod(0o644)
                data = json.loads(receipt.read_text())
                data['bounds']['integer_plan_cases'] = True
                receipt.write_text(json.dumps(data))
                result = subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=90)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('typed receipt mismatch',result.stderr)
            finally:
                for path in root.rglob('*'):
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == '__main__':
    unittest.main()
