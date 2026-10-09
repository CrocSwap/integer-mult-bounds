"""Exact integer bases of the frames that the recycled word joins in a new order, and exact nesting over Q.

Stdlib only.  Node frames, late-copy intersections and root frames are rebuilt from the pinned PR97 witness with
Swapnil Jain's check_lifted.py machinery, exactly as check_frames.py derives them; sigma and V-leaf frames are the
primitive integer bases of the pinned data file."""
import sys
from fractions import Fraction
from math import gcd


def prim(r):
    r = [Fraction(x) for x in r]; den = 1
    for x in r: den = den * x.denominator // gcd(den, x.denominator)
    z = [int(x * den) for x in r]; g = 0
    for x in z: g = gcd(g, x)
    return [x // g for x in z] if g else z


class Exact:
    def __init__(self, S, W, folder):
        sys.path.insert(0, str(folder))
        import check_lifted as cl
        from linalg import null_exact, rank_mod, Q31
        self.S = S; self.h = h = S.h; self.cl = cl; self.null_exact = null_exact; self.rank_mod = rank_mod; self.Q31 = Q31
        pr = cl.Prog(W); bas, dn = cl.spans(pr); self.users = cl.users_of(pr, dn)
        fr = self.fr = cl.Frames(pr, dn, bas, self.users); fr.cobases(); d, _ = fr.dims(); self.ld, _ = cl.late_frames(fr, pr, self.users)
        assert all(S.node_dims[n] == d[n] for n in pr.act) and len(S.node_dims) == len(pr.act), 'recorded node dimensions'
        self.full = [[int(i == j) for j in range(h)] for i in range(h)]
        self._basis = {}; self._null = {}

    def ukey(self, n, k):
        u = self.users[n][k]
        return ('n', u[1]) if u[0] == 'gate' else self.cl.root_key(u)

    def basis(self, key):
        if key not in self._basis:
            S, fr = self.S, self.fr; kind = key[0]
            if kind == 'sigma': B = S.sigma[key[1]]
            elif kind == 'v': B = S.vstart[key[1]]
            elif kind == '0': B = []
            elif kind == 'F': B = self.full
            elif kind == 'out': B = [prim(r) for r in fr.exact_basis(('out', key[2][0], tuple(key[2])))]
            elif kind == 'c':
                n, lt = key[1], key[2]
                B = self.basis(self.ukey(n, lt[-1]))
                for kk in reversed(lt[:-1]): B = fr.intersect_exact(self.basis(self.ukey(n, kk)), B)
                B = [prim(r) for r in B]
            else: B = [prim(r) for r in fr.exact_basis(key)]
            assert len(B) == S.dim(key), ('exact dimension', key)
            self._basis[key] = B
        return self._basis[key]

    def null(self, key):
        if key not in self._null:
            B = self.basis(key)
            self._null[key] = [prim(z) for z in self.null_exact(B, self.h)] if B else self.full
        return self._null[key]

    def inside(self, a, b):
        """span(a) <= span(b), exactly over Q (integer dot products with an exact integer basis of b's annihilator)."""
        A = self.basis(a)
        if not A or len(self.basis(b)) == self.h: return True
        if len(A) > len(self.basis(b)): return False
        return all(sum(x * z for x, z in zip(ra, rz)) == 0 for ra in A for rz in self.null(b))

    def nondegenerate(self, key):
        """G = I - J/9 nondegenerate on the frame: det(9 B G B^T) nonzero mod 2^31-1, hence over Z."""
        B = self.basis(key)
        if not B or len(B) == self.h: return True
        sm = [sum(b) for b in B]
        gram = [[9 * sum(x * y for x, y in zip(a, b)) - sa * sb for b, sb in zip(B, sm)] for a, sa in zip(B, sm)]
        return self.rank_mod(gram, self.Q31) == len(B)
