"""Deficient directions of a unit under the Gram realisation (exact, Fractions), pair ranks, bilinear-form space, reflections."""
from math import gcd
from fractions import Fraction as Fr
from roots import *

def span_basis(L, T):
    """T linearly independent lines of L (greedy) -- an ambient basis of the span"""
    B = []
    for r in L:
        if rank_q(B + [r]) > len(B): B.append(r)
        if len(B) == T: break
    assert len(B) == T
    return B

def primitive(x):
    x = [Fr(c) for c in x]
    d = 1
    for c in x: d = d * c.denominator // gcd(d, c.denominator)
    w = [int(c * d) for c in x]; g = 0
    for c in w: g = gcd(g, abs(c))
    w = [c // g for c in w]
    for c in w:
        if c != 0:
            if c < 0: w = [-y for y in w]
            break
    return tuple(w)

def classes(L):
    """(B rows, basis of col(B), h, list of nonzero class supports as bitmasks)"""
    Br = b0rows(L); basis = colspace_basis(Br)
    return Br, basis, len(basis), [w for _, w in span_vectors(basis)]

def deficient_directions(L, T):
    """dict: class-support bitmask w -> primitive integer direction x (ambient) with L[t].x = 0 for all t in the class, for the classes
    whose lines do not span; asserts the annihilator is 1-dimensional in each such class."""
    Bm = span_basis(L, T); Br, basis, h, cl = classes(L); out = {}
    for w in cl:
        O = bits(w); rows = [[dot(L[t], b) for b in Bm] for t in O]
        if rank_q(rows) < T:
            ns = nullspace_q(rows, T); assert len(ns) == 1, "annihilator of a deficient class is not 1-dimensional"
            n = ns[0]
            x = [sum(n[i] * Bm[i][k] for i in range(T)) for k in range(len(Bm[0]))]
            out[w] = primitive(x)
    return out

def support(L, x): return [t for t in range(len(L)) if dot(L[t], x) != 0]

def reflect(v, r):
    c = Fr(2 * dot(v, r), dot(r, r))
    return primitive([a - c * b for a, b in zip(v, r)])

def bilinear_space_dim(L, T):
    """dimension of {N in V (x) V : r_t^T N r_s = 0 for every orthogonal pair t, s} (V = span of the lines), exact"""
    Bm = span_basis(L, T); v = len(L); G = gram(L)
    a = [[dot(L[t], b) for b in Bm] for t in range(v)]
    rows = []
    for t in range(v):
        for s in range(v):
            if t != s and G[t][s] == 0:
                rows.append([a[t][i] * a[s][j] for i in range(T) for j in range(T)])
    return T * T - rank_q(rows)
