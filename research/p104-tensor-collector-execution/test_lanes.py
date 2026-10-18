"""Scalar differential, signed-lane isolation and retained rejection controls."""
import ast
from dataclasses import FrozenInstanceError
import itertools
from pathlib import Path
import random
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter
import lanes


class Checks(unittest.TestCase):
    def test_signed_arithmetic_and_isolation(self):
        c = lanes.Context(2, 16)
        r = random.Random(28)
        limit = c.radix // 2
        cases = [-limit, -limit+1, -257, -17, -1, 0, 1, 17, 257, limit-2, limit-1]
        for a, b in itertools.product(cases, repeat=2):
            xs = [(a, b), (b, a), (-1, 0), (0, -1)]
            ys = [(b, a), (a, b), (1, 1), (-1, -1)]
            x, y = c.pack(xs), c.pack(ys)
            self.assertEqual(list(x), xs)
            self.assertEqual(list(x ^ y), [(u ^ s, v ^ t) for (u,v),(s,t) in zip(xs,ys)])
            for k in [0, 1, 3, c.bits-1]:
                self.assertEqual(list(x.quotient(k)), [(u >> k, v >> k) for u,v in xs])
                self.assertEqual(list(x.residue(k)), [(u % (1<<k), v % (1<<k)) for u,v in xs])
            for op in ['add', 'sub']:
                expected = [(u+s,v+t) if op == 'add' else (u-s,v-t) for (u,v),(s,t) in zip(xs,ys)]
                if all(-limit <= z < limit for pair in expected for z in pair):
                    actual = x+y if op == 'add' else x-y
                    self.assertEqual(list(actual), expected)
                else:
                    with self.assertRaisesRegex(ValueError, 'overflow'):
                        x+y if op == 'add' else x-y
        for _ in range(80):
            xs = [(r.randrange(-10000,10000),r.randrange(-10000,10000)) for _ in range(4)]
            x = c.pack(xs)
            for k in [0,1,3,9]:
                self.assertEqual(list(x.shift(k)), [(a<<k,b<<k) for a,b in xs])
                self.assertEqual(x.shift(k).shift(-k), x)
            for width in [2,8,16]:
                if all(-(1<<(width-1)) <= z < 1<<(width-1) for pair in xs for z in pair):
                    self.assertEqual(list(x.encode(width)), [(a%(1<<width),b%(1<<width)) for a,b in xs])
                    self.assertEqual(x.encode(width).decode(width), x)
                else:
                    with self.assertRaisesRegex(ValueError, 'headroom'):
                        x.encode(width)

    def test_implicit_sign_extension(self):
        c=lanes.Context(2,8)
        xs=[(-1,-2),(3,-4),(-7,8),(0,-1)]
        ys=[(5,-6),(-3,4),(7,-8),(-1,0)]
        for width in [5,8,160,4096]:
            a,b=c.pack(xs).encode(width),c.pack(ys).encode(width)
            got=lanes.xor_words(a,b)
            expected=[((u%(1<<width))^(v%(1<<width)), (s%(1<<width))^(t%(1<<width)))
                      for (u,s),(v,t) in zip(xs,ys)]
            self.assertEqual(list(got),expected)
            self.assertEqual(list(got.decode(width)),[(u^v,s^t) for (u,s),(v,t) in zip(xs,ys)])
        with self.assertRaisesRegex(ValueError,'decode words'):
            c.pack(xs).encode(160) + c.pack(ys).encode(160)
        self.assertNotEqual(c.pack(xs).encode(160),c.pack(xs).encode(159))
        with self.assertRaisesRegex(ValueError,'width tag'):
            lanes.xor_words(c.pack(xs).encode(160),c.pack(ys).encode(159))
        # A raw zero target is legal; an untagged negative encoding is not.
        self.assertEqual(list(lanes.xor_words(c.zero,c.pack(xs).encode(160))),list(c.pack(xs).encode(160)))
        with self.assertRaisesRegex(ValueError,'unsigned encoded'):
            lanes.xor_words(c.pack(xs),c.pack(ys).encode(160))

    def test_all_signed_pairs(self):
        old, c = adapter.load(1, 16, False)
        for z in itertools.product(range(-3,4), repeat=4):
            x = [(z[0],z[1]),(z[2],z[3])]
            for inv in [False,True]:
                for linear in [False,True]:
                    ref = (old.CORE.linear_numerators if linear else old.CORE.lifted)(x,(0,),inv)
                    self.assertEqual(list(lanes.transform(c.pack(x),(0,),inv,linear)),ref)

    def test_wide_sparse_axes(self):
        r=random.Random(28)
        for n in [2,3,5,9]:
            old,c=adapter.load(n,320,False)
            for width in [1,53,160,257]:
                x=[(r.randrange(-(1<<width),1<<width),r.randrange(-(1<<width),1<<width)) for _ in range(1<<n)]
                axes=tuple(r.sample(range(n),n))
                for block in [axes,axes[::2],()]:
                    for inv in [False,True]:
                        for linear in [False,True]:
                            expected=(old.CORE.linear_numerators if linear else old.CORE.lifted)(x,block,inv)
                            actual=lanes.transform(c.pack(x),block,inv,linear)
                            self.assertEqual(list(actual),expected)

    def test_retained_macro_branches(self):
        r=random.Random(28)
        for n in [3,5,7]:
            old,c0=adapter.load(n,320,False)
            new,c=adapter.load(n,320,True)
            x=[(r.randrange(-100,100),r.randrange(-100,100)) for _ in range(1<<n)]
            for params in [dict(),dict(d=3,spacing=1,suffix=0,outer=4)]:
                a,b=old.Executor(n,320,**params),new.Executor(n,320,**params)
                for inverse in [False,True]:
                    for method in ['fast_lift','original_lift']:
                        ref=getattr(a,method)(x,tuple(range(n)),inverse)
                        got=getattr(b,method)(c.pack(x),tuple(range(n)),inverse)
                        self.assertEqual(list(got),ref)
                    target=[(r.randrange(1<<20),r.randrange(1<<20)) for _ in range(1<<n)]
                    ref=a.dense_linear(x,target,tuple(range(n)),320,inverse)
                    got=b.dense_linear(c.pack(x),c.pack(target),tuple(range(n)),320,inverse)
                    self.assertEqual(list(got),ref)
                self.assertEqual(a.counts,b.counts)
            axes=tuple(range(n))
            for model,src,zero in [(old,x,[(0,0)]*len(x)),(new,c.pack(x),c.zero)]:
                with self.assertRaisesRegex(ValueError,'backend private output must return zero'):
                    model.CORE.evaluate(src,zero,axes,320,model.CORE.DirectOracle(),omit_cleanup=True)

    def test_wide_complete_core(self):
        old,_=adapter.load(5,320,False)
        new,c=adapter.load(5,320,True,value_width=259)
        r=random.Random(28)
        x=[(r.randrange(-(1<<257),1<<257),r.randrange(-(1<<257),1<<257)) for _ in range(32)]
        a,b=old.Executor(5,320,outer=3),new.Executor(5,320,outer=3)
        for inverse in [False,True]:
            ref=a.original_lift(x,tuple(range(5)),inverse)
            got=b.original_lift(c.pack(x),tuple(range(5)),inverse)
            self.assertEqual(list(got),ref)
        self.assertEqual(a.counts,b.counts)

    def test_masks_phase_and_gate_controls(self):
        old,_=adapter.load(9,160,False)
        new,c=adapter.load(9,160,True)
        x=[(i%19-9,i%23-11) for i in range(512)]
        for controls,targets in [((0,1),None),((0,2),(1,3))]:
            for negative in [False,True]:
                self.assertEqual(list(lanes.character(c.pack(x),controls,targets,negative)),old.character(x,controls,targets,negative))
        for recipe in old.SOURCE['recipes']:
            for side in ['left','right']:
                for inverse in [False,True]:
                    self.assertEqual(list(lanes.recipe_phase(c.pack(x),recipe[side],1,inverse)),old.recipe_phase(x,recipe[side],1,inverse))
        e=new.Executor(9,160)
        tiny,ct=adapter.load(2,64,True)
        witness=ct.pack([(0,0),(0,0),(0,0),(1,0)])
        unguarded=tiny.Executor(2,64).address_word(witness,(1,),(0,))
        expected=[(0,0),(1,0),(0,0),(0,0)]
        self.assertNotEqual(list(unguarded),expected)
        self.assertEqual(list(tiny.Executor(2,64).address_gate(witness,(1,),(0,))),expected)
        right=e.address_oracle(c.pack(x),c.zero,(0,),(1,))
        with self.assertRaisesRegex(ValueError,'literal dense address inverse'):
            e.address_oracle(c.pack(x),c.zero,(0,),(1,),omit_phase=True)

    def test_fail_closed(self):
        c=lanes.Context(2,16)
        with self.assertRaises(FrozenInstanceError):
            c.zero.real=7
        for payload in [[(0,0)],[(True,0)]*4]:
            with self.assertRaises(ValueError): c.pack(payload)
        with self.assertRaisesRegex(ValueError,'distinct'):
            lanes.transform(c.zero,(0,0))
        with self.assertRaisesRegex(ValueError,'overflow'):
            c.pack([(c.radix//2-1,0)]*4).shift(1)
        with self.assertRaisesRegex(ValueError,'exact guarded'):
            c.pack([(1,0)]*4).shift(-1)
        with self.assertRaisesRegex(ValueError,'unsigned encoded'):
            c.pack([(-1,0)]*4).decode(8)
        with self.assertRaisesRegex(ValueError,'unique source'):
            adapter.rewrite('changed', [('expected','new',1)])


if __name__=='__main__':
    unittest.main()
