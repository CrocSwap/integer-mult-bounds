"""Auxiliary source frames: rank bookkeeping, pivot profile, boundaries, patch."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import random
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from source_frame_network import (assembly, bit_certificate, bit_counts, certificate,
                                  complex_certificate, parameters)
from controlled_bit_rank_moment import counts as batched_counts
from make_source_frame_patch import patched_files

P = 1000003  # prime modulus for the small exact model


def inv(a):
    return pow(a % P, P-2, P)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def kron(A, B):
    return [[a*b % P for a in ra for b in rb] for ra in A for rb in B]


def add(*Ms, signs=None):
    signs = signs or [1]*len(Ms)
    n = len(Ms[0])
    return [[sum(s*M[i][j] for s, M in zip(signs, Ms)) % P for j in range(n)] for i in range(n)]


def mul(A, B):
    cols = list(zip(*B))
    return [[sum(a*b for a, b in zip(row, col)) % P for col in cols] for row in A]


def mat_inv(A):
    n = len(A)
    M = [list(row)+[int(i == j) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        r = next(r for r in range(c, n) if M[r][c] % P)
        M[c], M[r] = M[r], M[c]
        f = inv(M[c][c]); M[c] = [x*f % P for x in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                g = M[r][c]; M[r] = [(x-g*y) % P for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]


def line_projector(t, omega):
    """Orthogonal projector onto <t> for the form omega, modulo P."""
    tw = [sum(t[k]*omega[k][j] for k in range(len(t))) % P for j in range(len(t))]
    f = inv(sum(a*b for a, b in zip(t, tw)))
    return [[t[i]*tw[j]*f % P for j in range(len(t))] for i in range(len(t))]


def lower_lower_pivots(A):
    """Pivots of the retained elimination: topmost row, rightmost active column."""
    A = [list(r) for r in A]
    n = len(A)
    active = [True]*n
    pivots = []
    for r in range(n):
        c = next((c for c in range(n-1, -1, -1) if active[c] and A[r][c] % P), None)
        if c is None:
            continue
        pivots.append((r, c))
        f = inv(A[r][c])
        for i in range(r+1, n):
            if A[i][c]:
                g = A[i][c]*f % P
                A[i] = [(x-g*y) % P for x, y in zip(A[i], A[r])]
        active[c] = False
    return pivots


class SmallStageTwoModel(unittest.TestCase):
    """h=5 five-subset labels in PR #10's coordinate order and basis family."""

    def setUp(self):
        random.seed(5)
        h = self.h = 5
        H = h*h
        self.m = h*H
        c = 2*inv(25)  # label form I-(2/25)J
        omega = [[(int(i == j)-c) % P for j in range(h)] for i in range(h)]
        t = [1]*h
        Pi = line_projector(t, omega)
        # coordinates (alpha, i): alpha = third factor (slow), i = (first, second) factors
        self.PD0 = kron(Pi, kron(add(eye(h), Pi, signs=[1, -1]), eye(h)))
        self.PD1 = kron(Pi, eye(H))
        self.I = eye(self.m)

    def rank(self, A):
        return len(lower_lower_pivots(A))

    def test_exit_is_idempotent_of_rank_m_minus_h(self):
        E = add(self.I, self.PD0, self.PD1, signs=[1, 1, -1])
        self.assertEqual(mul(E, E), E)
        self.assertEqual(mul(self.PD1, self.PD0), self.PD0)
        self.assertEqual(self.rank(E), self.m-self.h)
        climb = self.rank(add(self.PD1, self.PD0, signs=[1, -1]))
        old = self.rank(self.PD0)+climb+self.rank(add(self.I, self.PD1, signs=[1, -1]))
        self.assertEqual(old, self.m)
        self.assertEqual(climb+self.rank(E), self.m)

    def test_pivot_profile_after_controlled_basis(self):
        h, m, H = self.h, self.m, self.h*self.h
        rnd = lambda n: [[random.randrange(P) for _ in range(n)] for _ in range(n)]
        K = rnd(H)
        T = [[0]*m for _ in range(m)]
        Tinv = [[0]*m for _ in range(m)]
        for i in range(H):
            G = rnd(h); Gi = mat_inv(G)
            for a in range(h):
                for b in range(h):
                    T[a*H+i][b*H+i] = G[a][b]
                    Tinv[a*H+i][b*H+i] = Gi[a][b]
        S = mul(T, kron(eye(h), K))
        Sinv = mul(kron(eye(h), mat_inv(K)), Tinv)
        E = add(self.I, self.PD0, self.PD1, signs=[1, 1, -1])
        piv = lower_lower_pivots(mul(mul(S, E), Sinv))
        corner = [(r, c) for r, c in piv if r < h]
        middle = [(r, c) for r, c in piv if r >= h]
        self.assertEqual(len(piv), m-h)
        self.assertEqual(sorted(c for _, c in corner), list(range(m-h, m)))
        self.assertEqual(middle, [(i, i) for i in range(h, m-h)])


class Certificates(unittest.TestCase):
    def test_counts_preserve_rank_sum_and_deficit(self):
        n, old = bit_counts(), batched_counts()
        self.assertEqual(n['eta'], old['eta'])
        self.assertEqual(n['exit_rank'], n['m']-n['h'])
        self.assertEqual(n['removed_entrance_rank'], n['h']**2-n['h'])
        total = n['singleton_calls']+sum(r['copies']*r['chunk_digits'] for r in n['recursive_blocks'])
        self.assertEqual(total, old['original_rank_sum'])

    def test_exponent_boundaries(self):
        self.assertLess(bit_certificate()['moment_upper'], 1)
        self.assertLess(complex_certificate()['moment_upper'], 1)
        with self.assertRaises(ValueError):
            bit_certificate(a=Q(155, 10**8))
        with self.assertRaises(ValueError):
            complex_certificate(a=Q(2, 10**6))
        w = assembly()
        self.assertGreater(w['parameters']['kappa'], Q(1, 2**21))
        self.assertGreater(w['absorption_gap'], 0)
        with self.assertRaises(ValueError):
            assembly(replace(parameters(), kappa=w['minimum_margin']))

    def test_certificate_improves_pr10(self):
        result = certificate()
        self.assertGreater(result['improvement_over_PR10'], 6)
        self.assertEqual(result['assembly']['parameters']['kappa'], Q(7699, 10**10))


class Patch(unittest.TestCase):
    def test_labels_references_and_values(self):
        root = Path(__file__).resolve().parents[1]
        sources = {str(p.relative_to(root/'upstream')): p.read_text()
                   for p in (root/'upstream').rglob('*.tex')}
        sources.update({name: new for name, old, new in patched_files()})
        text = '\n'.join(sources.values())
        labels = re.findall(r'\\label\{([^}]+)\}', text)
        self.assertEqual(len(labels), len(set(labels)))
        self.assertFalse(set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', text))-set(labels))
        swap = sources['build/sections/04-swap.tex']
        self.assertIn(r'\label{lem:scratch-source-frames}', swap)
        self.assertIn(r'Put $\tau=1-154/10^8$.', swap)
        layers = sources['build/sections/05-layers.tex']
        self.assertIn(r'Fix $\tau=1-154/10^8$ and $\sigma=1-18/10^7$.', layers)
        self.assertIn(r'\label{sec:source-frame-complex}', layers)
        self.assertIn(r'\kappa=7699/10^{10}>2^{-21}', sources['build/sections/00-introduction.tex'])
        self.assertNotIn('6149999', sources['build/sections/08-assembly.tex'])


if __name__ == '__main__':
    unittest.main()
