#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact-grid controls, dense tensor-native and full-word constant executions."""
import copy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import random
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("format_primary", HERE/"verify.py")
V = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = V
spec.loader.exec_module(V)


class Fixed:
    def __init__(self, width):
        self.width = width

    def fit(self, x):
        if not -(1 << (self.width-1)) <= x < (1 << (self.width-1)):
            raise ArithmeticError("intermediate overflow")
        return x

    def divide(self, x, d):
        self.fit(x)
        q, r = divmod(x, d)
        if r:
            raise ArithmeticError("off-grid division")
        return self.fit(q)

    def add(self, a, b):
        return self.fit(a+b)

    def gaussian(self, x, y, sign):
        a, b = x; c, d = y
        sr, si = self.add(a, c), self.add(b, d)
        dr, di = self.add(a, -c), self.add(b, -d)
        numerators = (self.add(sr, -sign*di), self.add(si, sign*dr),
                      self.add(sr, sign*di), self.add(si, -sign*dr))
        out = tuple(self.divide(n, 2) for n in numerators)
        return out[:2], out[2:]


def gaussian_oracle(x, y, sign):
    # Direct complex linear combination, separate from pair-first additions.
    a, b = map(Q, x); c, d = map(Q, y)
    return ((a-sign*b+c+sign*d)/2, (b+sign*a+d-sign*c)/2), \
           ((c-sign*d+a+sign*b)/2, (d+sign*c+b-sign*a)/2)


def tensor_fixed(real, imag, label, sign, depth, width):
    """Pair-first array execution on actual nine-axis factors and one owned buffer."""
    f = Fixed(width)
    real, imag = real[:], imag[:]
    for layer in range(depth):
        axis = label << (9*layer)
        rr, ii = [0]*len(real), [0]*len(real)
        for x in range(len(real)):
            y = x ^ axis
            if x < y:
                a, b = f.gaussian((real[x],imag[x]),(real[y],imag[y]),sign)
                rr[x], ii[x] = a
                rr[y], ii[y] = b
        real, imag = rr, ii
    return real, imag


def convolution_oracle(real, imag, label, sign, depth):
    """Expand tensor C directly as a sum of 2^depth translations, not butterflies."""
    terms = [(0,1,0)]
    for layer in range(depth):
        result = []
        for shift,a,b in terms:
            for delta,c,d in ((0,1,sign),(label << (9*layer),1,-sign)):
                result.append((shift ^ delta,a*c-b*d,a*d+b*c))
        terms = result
    rr, ii = [], []
    for x in range(len(real)):
        a = sum(c*real[x^shift]-d*imag[x^shift] for shift,c,d in terms)
        b = sum(d*real[x^shift]+c*imag[x^shift] for shift,c,d in terms)
        u, ur = divmod(a,1 << depth);v,vr=divmod(b,1 << depth)
        if ur or vr:
            raise ArithmeticError("oracle denominator")
        rr.append(u);ii.append(v)
    return rr, ii


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, data = V.load()
        cls.labels, cls.maps, _ = V.geometry(data)

    def test_all_small_gaussian_pairs(self):
        f = Fixed(16)
        count = 0
        for a in range(-2, 3):
            for b in range(-2, 3):
                for c in range(-2, 3):
                    for d in range(-2, 3):
                        for sign in (-1, 1):
                            actual = f.gaussian((2*a, 2*b), (2*c, 2*d), sign)
                            want = gaussian_oracle((a,b),(c,d),sign)
                            self.assertEqual(tuple(tuple(Q(z,2) for z in pair) for pair in actual), want)
                            count += 1
        self.assertEqual(count, 1250)

    def test_native_numerator_and_grid_failures(self):
        with self.assertRaises(ArithmeticError):
            Fixed(20).gaussian((1,0),(0,0),1)
        self.assertEqual(Fixed(20).gaussian((2,0),(0,0),1), ((1,1),(1,-1)))
        # All final outputs fit signed four-bit words, but a numerator is 12.
        self.assertEqual(gaussian_oracle((3,-3),(3,3),1), ((Q(6),Q(0)),(Q(0),Q(0))))
        with self.assertRaises(ArithmeticError):
            Fixed(4).gaussian((3,-3),(3,3),1)

    def test_actual_negative_line_on_dense_tensor_inputs(self):
        self.assertEqual(self.word[1707],["line","Z10",1,-1])
        self.assertEqual(self.labels[1],19)
        for depth in (1,2):
            size=1 << (9*depth);guard=9+3*(depth-1);width=3+28+6*(depth-1)
            rng=random.Random(4015+depth)
            real=[rng.randrange(-7,8)*(1 << guard) for _ in range(size)]
            imag=[rng.randrange(-7,8)*(1 << guard) for _ in range(size)]
            before=(real[:],imag[:])
            got=tensor_fixed(real,imag,19,-1,depth,width)
            self.assertEqual(got,convolution_oracle(real,imag,19,-1,depth))
            self.assertEqual((real,imag),before)
            self.assertEqual(tensor_fixed(*got,19,1,depth,width),before)

    def test_full_word_constant_payload_arithmetic(self):
        # These are actual owner/payload-constant inputs: cover permutations
        # and both signed C_q fix constants. Native interiors are still run.
        # No general huge-payload execution is inferred from this subspace.
        for depth, seed in ((1, 17), (2, 31), (8, 47)):
            rng = random.Random(seed)
            guard, width = 9+3*(depth-1), 3+28+6*(depth-1)
            unit = 1 << guard
            fixed = Fixed(width)
            exact = {s+str(j): (Q(rng.randrange(-7,8)),Q(rng.randrange(-7,8)))
                     for s in ("X","Y") for j in range(112)}
            bits = {n:tuple(int(x)*unit for x in z) for n,z in exact.items()}
            original = dict(bits)
            active = set()
            changed = 0
            for event in self.word:
                op = event[0]
                if op == "begin":
                    active = {s+str(j) for s in ("F","G")[:event[2]//8] for j in range(8)}
                elif op == "end":
                    self.assertTrue(all(bits[n] == (0,0) for n in active))
                    for n in active:
                        del bits[n], exact[n]
                    active = set()
                elif op == "checkpoint":
                    self.assertFalse(active)
                else:
                    n = event[1]
                    if op == "clear":
                        bits[n],exact[n] = (0,0),(Q(0),Q(0))
                    elif op == "add":
                        c = Q(event[3]);src=event[2]
                        term = tuple(fixed.divide(fixed.fit(c.numerator*x),c.denominator) for x in bits[src])
                        bits[n] = tuple(fixed.add(a,b) for a,b in zip(bits[n],term))
                        exact[n] = tuple(a+c*b for a,b in zip(exact[n],exact[src]))
                    elif op == "line":
                        for _ in range(depth):
                            out = fixed.gaussian(bits[n],bits[n],event[3])
                            want = gaussian_oracle(exact[n],exact[n],event[3])
                            self.assertEqual(out[0],out[1])
                            bits[n],exact[n] = out[0],want[0]
                    else:
                        self.assertEqual(op,"map")
                    self.assertEqual(tuple(Q(x,unit) for x in bits[n]),exact[n])
                    changed += 1
            self.assertEqual(changed,3808)
            self.assertTrue(all(bits[n] == z for n,z in original.items()))
            self.assertEqual(sum(n[0] in "ZW" for n in bits),224)

    def test_source_ownership_and_frame_mutants(self):
        w = copy.deepcopy(self.word)
        w.insert(0,["clear","X0","current"])
        with self.assertRaises(ValueError):V.analyze(w,self.labels,self.maps)
        w = copy.deepcopy(self.word)
        w.pop(next(i for i,e in enumerate(w) if e==["clear","Z2","query2"]))
        with self.assertRaises(ValueError):V.analyze(w,self.labels,self.maps)
        w = copy.deepcopy(self.word)
        w[1707][3] *= -1
        with self.assertRaises(ValueError):V.analyze(w,self.labels,self.maps)
        w = copy.deepcopy(self.word)
        w.insert(1707,["begin","overlap",8])
        with self.assertRaises(ValueError):V.analyze(w,self.labels,self.maps)

    def test_composed_storage_and_width(self):
        for depth in (1,2,3,8,100):
            t=depth-1
            # Producer exact encoded magnitude is <2^(P+214+38t) in q_prod.
            p=64; entry_p=p+214+38*t
            self.assertEqual(entry_p+28+6*t,p+242+44*t)
            self.assertEqual(71+19*t+9+3*t,80+22*t)
        self.assertEqual(2*(704+224+16+1),1890)
        self.assertEqual(2*(224+224+16+1),930)


if __name__ == "__main__":
    unittest.main(verbosity=2)
