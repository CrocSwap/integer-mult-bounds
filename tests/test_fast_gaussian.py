"""Fast Gaussian resampling: chirp identity, powers of E, block sums, witness."""
from dataclasses import replace
from decimal import Decimal as D, getcontext
from fractions import Fraction as Q
from math import floor
from pathlib import Path
import json
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import fast_gaussian as fg
from prepare_layers import serializable

ROOT = Path(__file__).resolve().parents[1]
getcontext().prec = 160


def pi():
    """Machin's formula at the current decimal precision."""
    def arctan_inv(x):
        x = D(x); total = term = 1/x; k = 1; sign = -1
        while True:
            term /= x*x; nxt = term/(2*k+1)
            if nxt < D(10)**(-getcontext().prec-5): return total
            total += sign*nxt; sign = -sign; k += 1
    return 4*(4*arctan_inv(5)-arctan_inv(239))


PI = pi()


def q_beta(s, t, j):
    x = Q(t*j, s); q = floor(x+Q(1, 2)); return q, x-q


def E_matrix(s, t, alpha, H=6):
    """Dense E of HvdH Section 4.2 with |h|<=H (neglected tail below 1e-60 here)."""
    sig = Q(t, s); E = [[D(0)]*s for _ in range(s)]
    for l in range(s):
        _, bl = q_beta(s, t, l)
        for h in range(-H, H+1):
            if not h: continue
            _, bh = q_beta(s, t, l+h)
            X = (sig*h+bl)**2-bh**2
            E[l][(l+h) % s] += (-PI*alpha*alpha*D(X.numerator)/D(X.denominator)).exp()
    return E


def matmul(A, B):
    n = len(A)
    return [[sum(A[i][k]*B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def norm(A): return max(sum(abs(x) for x in row) for row in A)


class ChirpAndPowers(unittest.TestCase):
    def test_chirp_identity_exact(self):
        random.seed(3)
        for _ in range(200):
            s = random.randint(5, 200); t = s+random.randint(1, s//4+1)
            sig = Q(t, s); th = sig-1
            y = Q(random.randint(-500, 500), random.randint(1, 50))
            a, b = random.randint(-40, 40), random.randint(-40, 40)
            ah = a+y/sig
            self.assertEqual((sig*a+y-b)**2, sig*th*ah**2+sig*(ah-b)**2-th*b*b)

    def test_step_inequality_closed_form(self):
        for s, t in ((5, 6), (13, 16), (31, 32), (61, 64), (97, 101), (127, 128)):
            self.assertEqual(fg.step_inequality(s, t, 7), 0)

    def test_powers_of_E_against_both_bounds(self):
        for s, t, alpha in ((29, 32, 2), (61, 64, 2), (31, 32, 3)):
            sig = Q(t, s); th = sig-1; a2 = alpha*alpha
            E = E_matrix(s, t, alpha); P = E
            pre = (PI*a2*(1/(4*D(th.numerator)/D(th.denominator))+D(1)/2)).exp()
            rate = D('2.01')*(-PI*a2*D(sig.numerator)/D(sig.denominator)).exp()
            for n in range(1, 13):
                if n > 1: P = matmul(P, E)
                self.assertLessEqual(norm(P), pre*rate**n)
            # The new bound is the useful one once n exceeds about 1/(4 theta).
            hvdh = (D('2.01')*(-PI*a2*D(th.numerator)/D(th.denominator)/2).exp())**12
            self.assertLess(pre*rate**12, hvdh)

    def test_block_correlation_matches_direct_sums(self):
        s, t, alpha = 61, 64, 3; sig = Q(t, s); th = sig-1
        random.seed(7); u = [D(random.randint(-1000, 1000))/1000 for _ in range(s)]
        fl = lambda r: D(r.numerator)/D(r.denominator)
        g = lambda lam, x: (-PI*fl(lam)*fl(x)*fl(x)).exp()
        # S map: outputs k in a block, lambda=1/(sigma alpha)^2.
        lam = 1/(sig*sig*alpha*alpha); k0 = 17; m = 6
        j0 = floor(k0/sig)-3*m; y = sig*j0-k0
        for b in range(m):
            direct = sum(g(lam, sig*(j0+a)+y-sig*j0-b) * u[(j0+a) % s] for a in range(8*m))
            ah = lambda a: a+y/sig
            chirp = (PI*fl(lam*th)*b*b).exp()*sum(g(lam*sig*th, ah(a))*u[(j0+a) % s]*g(lam*sig, ah(a)-b) for a in range(8*m))
            self.assertLess(abs(direct-chirp), D(10)**-120)
        # N map: f_j=exp(pi alpha^2 beta_j^2) u_j; the j=l term is exactly u_l.
        l = 23; q, bl = q_beta(s, t, l); f = lambda j: (PI*alpha*alpha*fl(q_beta(s, t, j)[1]**2)).exp()*u[j % s]
        terms = [g(Q(alpha*alpha), sig*j-q)*f(j) for j in range(l-8, l+9)]
        self.assertLess(abs(terms[8]-u[l]), D(10)**-120)


class Witness(unittest.TestCase):
    def test_parameters_and_scope(self):
        p = fg.parameters(); w = fg.witness_only()
        self.assertEqual(w['limiting_margins'], ['g3'])
        self.assertGreater(w['minimum_margin'], p.kappa)
        self.assertTrue(Q(1, 2**30) < p.kappa < Q(1, 2**29))
        self.assertGreater(p.kappa, 2*Q(59, 10**11))
        self.assertLess(p.kappa, fg.BIT_SAVING/2)

    def test_negative_cases(self):
        p = fg.parameters(); n = fg.counts(fg.ComplexSideCircuit(fg.H))
        with self.assertRaises(ValueError):  # Gaussian cost and prime growth need eps<1/2
            fg.witness(replace(p, epsilon=Q(1, 2)), n)
        with self.assertRaises(ValueError):  # guard needs eps*C1<1, so beta>3/4
            b = Q(74, 100); fg.witness(replace(p, beta=b, C1=5-4*b+fg.ZETA), n)
        with self.assertRaises(ValueError):  # leaf needs (1-beta)a_c > 1-lambda'
            b = Q(80, 100); fg.witness(replace(p, beta=b, C1=5-4*b+fg.ZETA), n)
        with self.assertRaises(ValueError):  # the retained complex saving cannot support beta=19/25
            fg.witness(replace(p, sigma=1-Q(418, 10**12)), n)
        # The retained Gaussian row would fail at this epsilon.
        old = fg.constraints(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
        self.assertLess(old['gaussian_cost'], 0)

    def test_neumann_counts(self):
        for d, b in ((3, 2**12), (8, 2**20), (64, 2**30), (1000, 2**40)):
            x = fg.application_counts(d, b)
            self.assertLessEqual(x['n_new'], 30*d)
            self.assertLess(x['n_new'], x['n_hvdh'])
            self.assertLessEqual(4*x['gamma'], b)
        with self.assertRaises(ValueError):  # alpha^2 theta < 1 is outside the lemma
            fg.neumann_count(600, 2, Q(1, 5))

    def test_certificate_regenerates(self):
        stored = json.loads((ROOT/'certificates/fast-gaussian.json').read_text())
        self.assertEqual(stored, json.loads(json.dumps(serializable(fg.certificate()))))


class Patch(unittest.TestCase):
    def test_resampling_and_assembly_text(self):
        from make_fast_gaussian_patch import patched_files
        files = {name: new for name, _, new in patched_files()}
        res = files['build/sections/07-resampling.tex']; asm = files['build/sections/08-assembly.tex']
        for label in ('lem:correction-powers', 'cor:neumann-count', 'lem:chirped-gaussian'):
            self.assertIn(r'\label{'+label+'}', res)
        self.assertNotIn(r'3/2+\delta', res+asm)
        self.assertIn(r'Gaussian line maps & $d^2p^\delta$ & $2\epsilon+\delta$', asm)
        self.assertIn(r'\kappa=\frac{1479}{10^{12}}>2^{-30}', asm)
        self.assertIn(r'\kappa=1479/10^{12}', files['build/main.tex'])


if __name__ == '__main__':
    unittest.main()
