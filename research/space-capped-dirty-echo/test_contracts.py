"""Fast adversarial tests for the planner, checker and public array contract."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT/filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


p = load('echo_planner', 'planner.py')
v = load('echo_verify', 'verify.py')


class Contracts(unittest.TestCase):
    def test_certificate_normalization_and_corruption(self):
        result=dict(tree=((0,1),(2,3)), calls=16)
        disk=json.loads(json.dumps(result))
        v.compare_certificate(result,disk)
        disk['tree'][1][0]=1
        with self.assertRaisesRegex(ValueError,'exact certificate mismatch'):
            v.compare_certificate(result,disk)
        disk=json.loads(json.dumps(result));disk['calls']=15
        with self.assertRaisesRegex(ValueError,'exact certificate mismatch'):
            v.compare_certificate(result,disk)
        for altered in (False, 0.0):
            disk=json.loads(json.dumps(result));disk['tree'][0][0]=altered
            with self.assertRaisesRegex(ValueError,'exact certificate mismatch'):
                v.compare_certificate(result,disk)

    def test_hand_computed_primary(self):
        self.assertEqual(p.optimize([1]*15, 5)['calls'], 152)
        self.assertEqual(p.optimize([1]*15, 4)['calls'], 224)
        self.assertEqual(p.optimize([1]*15, 14)['calls'], 56)
        self.assertEqual(v.cuts_oracle((1,)*15, 5)[0], (152, 152))

    def test_weight_orientation_is_not_assumed_symmetric(self):
        for weights in ([1,59,2,3,7,11], [11,7,3,2,59,1]):
            row = p.optimize(weights, 4)
            self.assertEqual((row['price'],row['calls']), v.cuts_oracle(tuple(weights),4)[0])
            v.word_check(p, row, len(weights))

    def test_real_implementation_mutations(self):
        source = (ROOT/'planner.py').read_text(encoding='utf-8')
        changes = [
            ('underprice_interior', '2 if j in (0, arity-1) else 4', '2'),
            ('reuse_reserved_space', 'remaining = space-arity+1', 'remaining = space'),
            ('exclude_binary', 'range(2, min(space+1, hi-lo)+1)', 'range(3, min(space+1, hi-lo)+1)'),
            ('prune_capacity_equality', 'hi-lo > 2**space', 'hi-lo >= 2**space'),
            ('wrong_inverse_order', 'for t, s, d, q in reversed(commands)', 'for t, s, d, q in commands'),
        ]
        for name, old, new in changes:
            with self.subTest(name=name):
                self.assertEqual(source.count(old),1)
                mutant = types.ModuleType(name)
                exec(compile(source.replace(old,new), name, 'exec'),mutant.__dict__)
                with self.assertRaises(ValueError):
                    v.enumeration_check(mutant)
                    v.word_check(mutant, mutant.optimize([1]*15,5),15)

    def test_nonlinear_restoration_does_not_mean_dirt_independence(self):
        increments=[]
        for dirt in (0,1):
            arrays=[[1],[0],[dirt],[7]]
            def leaf(src,dst,f,sign):
                dst[0] += sign*(src[0]**2 if f==1 else src[0])
            p.compose((0,1,2),arrays[0],arrays[1],[0,1,2],arrays[2:],leaf)
            self.assertEqual(arrays[0],[1])
            self.assertEqual(arrays[2:],[[dirt],[7]])
            increments.append(arrays[1][0])
        self.assertEqual(increments,[1,3])

    def test_nonadditive_leaf_is_outside_contract(self):
        arrays=[[1],[2],[3]]
        initial=copy.deepcopy(arrays)
        def bad(src,dst,f,sign):
            dst[0] += sign*(src[0]+dst[0]**2)
        for sign in (1,-1):
            p.compose((0,1),arrays[0],arrays[1],[0,1],arrays[2:],bad,sign)
        self.assertNotEqual(arrays,initial)

    def test_source_and_context_corruption_rejected(self):
        # No full mathematical rerun is needed: source authentication runs first.
        saved=v.ROOT
        # Use the caller's writable working directory, including sandboxed Windows.
        with tempfile.TemporaryDirectory(prefix='.echo-source-controls-', dir=Path.cwd()) as tmp:
            self.assertTrue(Path(tmp).resolve().is_relative_to(Path.cwd().resolve()))
            root=Path(tmp)/'research'/'space-capped-dirty-echo'
            root.mkdir(parents=True)
            manifest=json.loads((ROOT/'SOURCES.json').read_text())
            (root/'SOURCES.json').write_text(json.dumps(manifest),encoding='utf-8')
            for row in manifest['sources']:
                dest=root/row['path']
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes((ROOT/row['path']).read_bytes())
            try:
                v.ROOT=root
                v.sources()
                for row in (manifest['sources'][0], manifest['sources'][-2]):
                    path=root/row['path']; original=path.read_bytes()
                    path.write_bytes(original+b'\n')
                    with self.assertRaisesRegex(ValueError,'source pin'):
                        v.sources()
                    path.write_bytes(original)
            finally:
                v.ROOT=saved

    def test_failed_admission_has_no_callback(self):
        controls=v.negative_controls(p)
        self.assertEqual(controls['rejected_count'],326)

    def test_precision_bound_is_complete(self):
        from fractions import Fraction as F
        bits,bound=v.precision(152,F(1,512),16,F(18),64)
        self.assertLessEqual(bound,F(1,2**65))
        a=F(13*17)*512**3; G=2+16*512
        self.assertGreater(152*a*19*G**151/2**128,F(1,2**65))
        self.assertGreater(bits,128)


if __name__=='__main__':
    unittest.main(verbosity=2)
