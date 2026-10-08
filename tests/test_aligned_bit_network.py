"""Aligned bit circuit with cheaper centers: map, schedule, frames, witness."""
from dataclasses import replace
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from bit_circuit import AlignedPairedCircuit
import aligned_bit_network as ab
from complex_circuit import ComplexSideCircuit
from complex_network import counts as complex_counts
from fast_gaussian import witness

ROOT = Path(__file__).resolve().parents[1]


def run(c, code, x, y, roles, inverse=False):
    """Exact F2 invocation of L',J',L'^-1,V,L',J',L'^-1,V with J'=J R_0.

    Forward: source x, target y. Inverse (stage 2): source y, target x.
    """
    x, y, roles = dict(x), dict(y), list(roles)
    src, tgt = (y, x) if inverse else (x, y)
    def L():
        for _, ins, outs in code['gates']:
            for s in ins[1:]: roles[ins[0]] ^= roles[s]
            for s in outs[1:]: roles[s] ^= roles[ins[0]]
    def Linv():
        for _, ins, outs in reversed(code['gates']):
            for s in outs[1:]: roles[s] ^= roles[ins[0]]
            for s in ins[1:]: roles[ins[0]] ^= roles[s]
    def V():
        for t, slot in code['sources'].items(): roles[slot] ^= src[t]
    def Jp():
        for (i, t), slot in code['outputs'].items():
            if t: tgt[t] ^= roles[slot]
            else:
                for T in tgt:
                    if i in T: tgt[T] ^= roles[slot]
    for op in (L, Jp, Linv, V, L, Jp, Linv, V): op()
    return x, y, roles


class SmallCircuits(unittest.TestCase):
    def test_map_frames_and_dirty_invocations(self):
        random.seed(2)
        for h in (8, 10, 12, 14):
            c = AlignedPairedCircuit(h); v = c.verify(); f = c.verify_frames()
            self.assertTrue(v['all_outputs_exact'] and v['totals_exact'])
            self.assertTrue(f['forward_frames_nested'] and f['reverse_complement_frames_nested'])
            self.assertEqual(v['centers'], h)
            code = c.compile()
            self.assertEqual(code['roles'], v['roles'])
            for _ in range(3):
                x = {t: random.randint(0, 1) for t in c.inputs}
                y = {t: random.randint(0, 1) for t in c.inputs}
                roles = [random.randint(0, 1) for _ in range(code['roles'])]
                x1, y1, r1 = run(c, code, x, y, roles)
                self.assertEqual((x1, r1), (x, roles))
                self.assertTrue(all(y1[t] == y[t] ^ x[t] for t in c.inputs))
                x2, y2, r2 = run(c, code, x, y, roles, inverse=True)
                self.assertEqual((y2, r2), (y, roles))
                self.assertTrue(all(x2[t] == x[t] ^ y[t] for t in c.inputs))

    def test_totals_span_the_star(self):
        c = AlignedPairedCircuit(10)
        for i in range(10):
            node = c.outputs[i, ()]
            want = sum(1 << c.pid[a, b] for a, b in combinations([p for p in range(10) if p != i], 2))
            self.assertEqual(c.support_in(node, i), want)

    def test_center_loss_is_star_dimension(self):
        """dim span{t_T: T contains i} = h-1 over Q, as used for the h-1 loss."""
        h = 9+3
        for i in (0, 5):
            rows = [[Q(int(p in T)) for p in range(h)] for T in combinations(range(h), 3) if i in T]
            # Gaussian elimination rank
            rank = 0; cols = h
            for col in range(cols):
                piv = next((r for r in range(rank, len(rows)) if rows[r][col]), None)
                if piv is None: continue
                rows[rank], rows[piv] = rows[piv], rows[rank]
                for r in range(len(rows)):
                    if r != rank and rows[r][col]:
                        f = rows[r][col]/rows[rank][col]
                        rows[r] = [a-f*b for a, b in zip(rows[r], rows[rank])]
                rank += 1
            self.assertEqual(rank, h-1)


class Witness(unittest.TestCase):
    def test_counts_and_saving(self):
        n = ab.counts_from(ab.ROLES)
        self.assertEqual(n['eta'], Q(49, 1284490000))
        self.assertEqual(n['deficit'], 1882384000000)
        self.assertGreater(n['eta'], ab.BIT_SAVING*ab.LOG_BOUND)
        self.assertLess(ab.ROLES, n['published_roles'])
        # With the old center loss h^2 the same circuit would not certify 325/10^11.
        v, N, m, h = n['v'], n['N'], n['m'], 50
        old_eta = Q(N-6*v*v*h*h, n['W']*m)
        self.assertLess(old_eta, ab.BIT_SAVING*ab.LOG_BOUND)

    def test_parameters_and_windows(self):
        p = ab.parameters(); cc = complex_counts(ComplexSideCircuit(25))
        w = witness(p, cc)
        self.assertEqual(w['limiting_margins'], ['g3'])
        self.assertGreater(w['minimum_margin'], p.kappa)
        self.assertTrue(Q(1, 2**30) < p.kappa < Q(1, 2**29))
        self.assertLess(p.kappa, ab.BIT_SAVING/2)
        with self.assertRaises(ValueError):  # leaf: (1-beta) a_c must exceed 1-lambda'
            b = Q(77, 100); witness(replace(p, beta=b, C1=5-4*b+Q(1, 10000)), cc)
        with self.assertRaises(ValueError):  # guard: beta must exceed 3/4
            b = Q(74, 100); witness(replace(p, beta=b, C1=5-4*b+Q(1, 10000)), cc)

    def test_certificate_fields(self):
        cert = json.loads((ROOT/'certificates/aligned-bit-network.json').read_text())
        self.assertEqual(int(cert['bit_counts']['side_and_center_roles']), ab.ROLES)
        self.assertEqual(cert['circuit']['additions'], 435346)
        self.assertTrue(cert['frames']['reverse_complement_frames_nested'])
        self.assertEqual(Q(cert['witness']['minimum_margin']), Q(162446751, 10**17))


class Patch(unittest.TestCase):
    def test_patch_text(self):
        from make_aligned_bit_patch import patched_files
        files = {name: new for name, _, new in patched_files()}
        motifs = files['build/sections/03-motifs.tex']
        self.assertIn(r'\label{prop:aligned-bit-interface}', motifs)
        self.assertIn(r'\tau=1-325/10^{11},\qquad\sigma=1-14/10^9.', motifs)
        self.assertIn(r'\ref{prop:aligned-bit-interface}', files['build/sections/04-swap.tex'])
        self.assertNotIn('296/10^{11}', files['build/sections/05-layers.tex']+files['build/sections/08-assembly.tex'])
        self.assertIn(r'\kappa=\frac{1624}{10^{12}}>2^{-30}', files['build/sections/08-assembly.tex'])


if __name__ == '__main__':
    unittest.main()
