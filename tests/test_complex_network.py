"""Compressed complex side circuit: exact map, binary frames and witness."""
from dataclasses import replace
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from complex_circuit import (ComplexSideCircuit, Checks, Label, compile_roles, dot, odd,
                             simulate_invocation, tmask, verify_role_frames)
import complex_network as cn
from certify import network
from prepare_layers import serializable

ROOT = Path(__file__).resolve().parents[1]


def span(vectors):
    out = {0}
    for v in vectors: out |= {x ^ v for x in out}
    return out


class BinaryLabels(unittest.TestCase):
    def test_label_algebra_matches_enumeration(self):
        random.seed(11); h = 7; everything = span([1 << i for i in range(h)])
        for _ in range(250):
            gens = [random.randrange(1, 1 << h) for _ in range(random.randint(1, 4))]
            basis = []
            for g in gens:
                if g not in span(basis): basis.append(g)
            U = Label(basis); su = span(basis)
            gram = all(any(dot(x, y) for y in su) for x in su if x)
            self.assertEqual(U.nondegenerate(), gram)
            big = basis+[g for g in [random.randrange(1, 1 << h)] if g not in su]
            V = Label(big); sv = span(big)
            self.assertTrue(V.contains(U))
            res = span(U.complement_in(V))
            self.assertEqual(res, {x for x in sv if all(not dot(x, u) for u in su)})
            self.assertEqual(odd(U.complement_in(V)), any(x.bit_count() & 1 for x in res))
            perp = span(U.complement_in(Label([1 << i for i in range(h)])))
            self.assertEqual(perp, {x for x in everything if all(not dot(x, u) for u in su)})

    def test_full_disjoint_piece_has_alternating_residual(self):
        h = 8; S = (0, 1, 2)
        outside = Label([1 << p for p in range(h) if p not in S])
        target = Label([x for x in (1 << p for p in range(h)) if not dot(x, tmask(S))]
                       + [tmask((0, 1)), tmask((1, 2))])
        self.assertTrue(target.nondegenerate() and target.contains(outside))
        residual = outside.complement_in(target)
        self.assertEqual(len(residual), 2)
        self.assertFalse(odd(residual))
        # Leaving one outside point uncovered supplies the needed odd vector.
        smaller = Label([1 << p for p in range(h) if p not in S+(7,)])
        self.assertTrue(odd(smaller.complement_in(target)))

    def test_three_missed_points_cannot_cover_the_disjoint_triples(self):
        outside = range(3, 10)
        for missed in combinations(outside, 3):
            self.assertIn(tuple(sorted(missed)), list(combinations(outside, 3)))
        for missed in combinations(outside, 4):
            for T in combinations(outside, 3):
                self.assertTrue(set(missed)-set(T))


class SmallCircuits(unittest.TestCase):
    def test_map_labels_roles_and_dirty_invocations(self):
        random.seed(5)
        for h in (8, 9, 10, 11, 12):
            c = ComplexSideCircuit(h); k = Checks(c); code = compile_roles(c)
            self.assertTrue(k.verify_map()['side_map_exact'])
            self.assertTrue(k.verify_labels()['all_residuals_have_odd_vectors'])
            self.assertTrue(verify_role_frames(c, k, code)['reverse_complement_frames_nested'])
            self.assertEqual(code['roles'], c.additions+len(c.pieces))
            for S, node, _ in c.pieces:
                self.assertNotEqual(c.cover(node) | tmask(S), (1 << h)-1)
            r = lambda: Q(random.randint(-9, 9), 2**random.randint(0, 3))
            x = {t: r() for t in c.triples}; y = {t: r() for t in c.triples}
            side = [r() for _ in range(code['roles'])]
            center = {i: r() for i in list(range(h))+['*']}
            x1, y1, s1, c1 = simulate_invocation(c, code, x, y, side, center)
            self.assertEqual((x1, s1, c1), (x, side, center))
            self.assertTrue(all(y1[t] == y[t]+x[t] for t in c.triples))
            x2, y2, s2, c2 = simulate_invocation(c, code, x, y, side, center, inverse=True)
            self.assertEqual((y2, s2, c2), (y, side, center))
            self.assertTrue(all(x2[t] == x[t]-y[t] for t in c.triples))

    def test_basis_vectors_through_a_full_invocation(self):
        h = 8; c = ComplexSideCircuit(h); code = compile_roles(c)
        zero_side = [Q(0)]*code['roles']; zero_center = {i: Q(0) for i in list(range(h))+['*']}
        zeros = {t: Q(0) for t in c.triples}
        for T in c.triples:
            x = dict(zeros); x[T] = Q(1)
            _, y, side, center = simulate_invocation(c, code, x, zeros, zero_side, zero_center)
            self.assertEqual(y, x)
            self.assertEqual((side, center), (zero_side, zero_center))

    def test_side_coefficients_and_disjoint_additions(self):
        c = ComplexSideCircuit(10)
        self.assertEqual({coef for _, _, coef in c.pieces}, {Q(1, 2), Q(-1, 2)})
        for node in c.active:
            if c.args[node]:
                a, b = c.args[node]
                self.assertFalse(c.support[a] & c.support[b])


class Witness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = ComplexSideCircuit(cn.H); cls.n = cn.counts(cls.c)

    def test_counts_and_saving(self):
        n = self.n
        self.assertEqual(n['side_roles_per_invocation'], 108195)
        self.assertEqual(n['original_side_wires_per_invocation'], 3693800)
        self.assertEqual(n['s'], n['W']*n['m']-2*n['N']+2*n['L'])
        self.assertGreater(n['eta'], cn.COMPLEX_SAVING*cn.LOG_BOUND)
        old = network(cn.H)
        self.assertGreater(n['eta']/old['eta_c'], 33)
        self.assertLess(n['W'], old['Wc'])

    def test_parameters_and_failures(self):
        p = cn.parameters(); w = cn.witness(p, self.n)
        self.assertEqual(w['limiting_margins'], ['g3'])
        self.assertGreater(w['minimum_margin'], p.kappa)
        self.assertTrue(Q(1, 2**31) < p.kappa < Q(1, 2**30))
        with self.assertRaises(ValueError):  # retained c=1/5 makes g2 binding
            cn.witness(replace(p, c=Q(1, 5)), self.n)
        with self.assertRaises(ValueError):  # Gaussian margin forces epsilon<1/5
            cn.witness(replace(p, epsilon=Q(1, 5)), self.n)
        with self.assertRaises(ValueError):  # old complex saving fails the leaf bound
            cn.witness(replace(p, sigma=1-Q(418, 10**12)), self.n)
        self.assertLess(p.kappa, cn.BIT_SAVING/5)

    def test_guard_and_gate_bound(self):
        g = cn.guard(self.n, Q(1, 1000), Q(1, 10000))
        self.assertEqual(g['C1'], Q(49961, 10000))
        gates = cn.gate_count(self.c, self.n)
        self.assertLessEqual(gates['total_gates'], gates['twelve_W'])

    def test_certificate_regenerates(self):
        stored = json.loads((ROOT/'certificates/complex-network.json').read_text())
        self.assertEqual(stored, json.loads(json.dumps(serializable(cn.certificate()))))


if __name__ == '__main__':
    unittest.main()
