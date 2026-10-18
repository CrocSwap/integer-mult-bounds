#!/usr/bin/env python3
"""Exact checker for the restoration-coalescing research note.

Independently builds a recursion batch that borrows a dirty workspace stream,
then compares the inherited eager per-child restoration against a deferred
single-pass restoration.  All arithmetic is exact Gaussian rationals
(Fraction real and imaginary parts); no floating point, no random tolerance,
no imported supplier verifier.  Pure standard library.

Run:
    python3 -I -O -B research/restoration-coalescing/verify.py

Expected first line:
    PASS_RESTORATION_COALESCING phase=... perm=... hetero_dense=... reader_diverges=... reader_cancels_5to1=... hetero_mults=...

`--write PATH` emits the deterministic certificate JSON to PATH.
`--json` prints the full certificate to stdout.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "ce7ad1b6ab09452c3478723a2e96ed5ff212dc08"


def need(condition, message):
    if not condition:
        raise ValueError(message)


# --------------------------------------------------------------------------
# Exact Gaussian rationals:  a + b i,  a,b in Fraction.
# --------------------------------------------------------------------------
class G:
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = Fraction(re)
        self.im = Fraction(im)

    def __add__(self, other):
        other = _g(other)
        return G(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return G(-self.re, -self.im)

    def __sub__(self, other):
        return self + (-_g(other))

    def __mul__(self, other):
        other = _g(other)
        return G(self.re * other.re - self.im * other.im,
                 self.re * other.im + self.im * other.re)

    __rmul__ = __mul__

    def conj(self):
        return G(self.re, -self.im)

    def scale(self, s):
        return G(self.re * Fraction(s), self.im * Fraction(s))

    def __eq__(self, other):
        other = _g(other)
        return self.re == other.re and self.im == other.im

    def is_zero(self):
        return self.re == 0 and self.im == 0

    def key(self):
        return (str(self.re), str(self.im))

    def __repr__(self):
        return f"({self.re}+{self.im}i)"


def _g(x):
    return x if isinstance(x, G) else G(x)


def gi_pow(j):
    """i^j for integer j, exact."""
    j %= 4
    return (G(1), G(0, 1), G(-1), G(0, -1))[j]


def popcount(x):
    return bin(x).count("1")


# --------------------------------------------------------------------------
# Structured appliers.  Each returns (result_vector, opcount_dict).
# --------------------------------------------------------------------------
def apply_diag(v, phases):
    """Diagonal unit-phase restoration.  Cost: one coefficient pass = N mults."""
    need(len(v) == len(phases), "diag dimension")
    out = [p * x for p, x in zip(phases, v)]
    return out, {"passes": 1, "mults": len(v), "adds": 0}


def apply_perm(v, perm):
    """Permutation restoration.  Cost: one routing pass = N moves, 0 mults."""
    need(sorted(perm) == list(range(len(v))), "perm not a permutation")
    out = [v[perm[x]] for x in range(len(v))]
    return out, {"passes": 1, "mults": 0, "adds": 0, "moves": len(v)}


def _walsh_dense(e):
    n = 1 << e
    H = [[G((-1) ** (popcount(x & y))) for y in range(n)] for x in range(n)]
    return H


def apply_walsh_fast(v):
    """Fast Walsh-Hadamard on e bits, then scale by 1/N = H^{-1}.
    Cost: N*log2(N) adds and N mults (the 1/N scaling).  Exact."""
    n = len(v)
    need(n & (n - 1) == 0, "walsh length")
    e = n.bit_length() - 1
    a = list(v)
    adds = 0
    step = 1
    while step < n:
        for i in range(0, n, 2 * step):
            for j in range(i, i + step):
                u, w = a[j], a[j + step]
                a[j] = u + w
                a[j + step] = u - w
                adds += 2
        step *= 2
    scale = Fraction(1, n)
    out = [x.scale(scale) for x in a]
    return out, {"passes": 1, "mults": n, "adds": adds}


def apply_dense(M, v):
    """Dense matrix-vector product.  Cost: N^2 mults + N(N-1) adds."""
    n = len(v)
    out = []
    mults = 0
    adds = 0
    for x in range(n):
        acc = G(0)
        for y in range(n):
            acc = acc + M[x][y] * v[y]
            mults += 1
            adds += 1
        out.append(acc)
        adds -= 1  # N-1 additions per row
    return out, {"passes": 1, "mults": mults, "adds": max(adds, 0), "dense": True}


# --------------------------------------------------------------------------
# Linear algebra on exact matrices (used to build and verify compositions).
# --------------------------------------------------------------------------
def mat_identity(n):
    return [[G(1) if x == y else G(0) for y in range(n)] for x in range(n)]


def mat_diag(phases):
    n = len(phases)
    return [[phases[x] if x == y else G(0) for y in range(n)] for x in range(n)]


def mat_perm(perm):
    n = len(perm)
    return [[G(1) if perm[x] == y else G(0) for y in range(n)] for x in range(n)]


def mat_mul(A, B):
    n = len(A)
    out = [[G(0)] * n for _ in range(n)]
    for x in range(n):
        for k in range(n):
            if A[x][k].is_zero():
                continue
            a = A[x][k]
            for y in range(n):
                if B[k][y].is_zero():
                    continue
                out[x][y] = out[x][y] + a * B[k][y]
    return out


def mat_vec(M, v):
    n = len(v)
    return [sum((M[x][y] * v[y] for y in range(n)), G(0)) for x in range(n)]


def mat_eq(A, B):
    return all(A[x][y] == B[x][y] for x in range(len(A)) for y in range(len(A)))


def mat_nnz(M):
    return sum(1 for row in M for c in row if not c.is_zero())


# --------------------------------------------------------------------------
# The recursion batch.
#
# State:  D (data stream) and W (borrowed dirty workspace), both length N.
# A fixed source vector s (read-only) supplies each child's data increment.
#
#   scratch-only child i :  D' = D + B_i s ,  W' = G_i W
#   reader child i       :  D' = D + B_i W ,  W' = G_i W      (reads W)
#
# The inherited invariant restores W to its node-entry value w0 after EVERY
# child (eager).  The deferred scheme lets W drift and restores it ONCE at the
# node exit via (G_r ... G_1)^{-1}.  Observables are the final D and final W.
# --------------------------------------------------------------------------
class Batch:
    def __init__(self, n, e):
        self.n = n
        self.e = e
        self.Walsh = _walsh_dense(e)

    def run_eager(self, w0, children):
        """Restore W to w0 after each child.  Returns (D, W, cost)."""
        n = self.n
        D = [G(0)] * n
        W = list(w0)
        cost = {"passes": 0, "mults": 0, "adds": 0, "moves": 0, "restoration_passes": 0}
        for child in children:
            kind = child["kind"]
            Bvec = child["B"]
            s = child["s"]
            Gmat = child["G"]
            inverse = child["Ginv"]          # restoration operator G_i^{-1}
            apply = child["apply_inverse"]   # callable(v) -> (vec, cost)
            if kind == "reader":
                incr = _scalevec(Bvec, W)
            else:
                incr = _scalevec(Bvec, s)
            D = _vecadd(D, incr)
            W = mat_vec(Gmat, W)             # child dirties the workspace
            # eager restoration to w0 (equivalently apply G_i^{-1} to the
            # just-dirtied W; both return exactly w0 when the invariant held).
            W, rcost = apply(W)
            _acc(cost, rcost)
            cost["restoration_passes"] += 1
        return D, W, cost

    def run_deferred(self, w0, children, deferred_apply):
        """No intermediate restoration; one composed restoration at exit.

        deferred_apply applies (G_r ... G_1)^{-1} to the drifted workspace using
        whatever structure the composed operator RETAINS: a diagonal phase, a
        permutation, or a dense matrix.  This is where the cost result lives."""
        n = self.n
        D = [G(0)] * n
        W = list(w0)
        cost = {"passes": 0, "mults": 0, "adds": 0, "moves": 0, "restoration_passes": 0}
        for child in children:
            kind = child["kind"]
            Bvec = child["B"]
            s = child["s"]
            Gmat = child["G"]
            if kind == "reader":
                incr = _scalevec(Bvec, W)
            else:
                incr = _scalevec(Bvec, s)
            D = _vecadd(D, incr)
            W = mat_vec(Gmat, W)             # no restoration here
        # one composed restoration: (G_r ... G_1)^{-1} applied to drifted W
        W, rcost = deferred_apply(W)
        _acc(cost, rcost)
        cost["restoration_passes"] += 1
        return D, W, cost


def _vecadd(a, b):
    return [x + y for x, y in zip(a, b)]


def _scalevec(Bvec, v):
    return [b * x for b, x in zip(Bvec, v)]


def _acc(total, delta):
    for k in ("mults", "adds", "moves", "passes"):
        total[k] = total.get(k, 0) + delta.get(k, 0)


# --------------------------------------------------------------------------
# Operator construction helpers returning full child records.
# --------------------------------------------------------------------------
def make_child(B, s, Gmat, Ginv_mat, apply_inverse, kind, inv_struct):
    return {
        "B": B, "s": s, "G": Gmat,
        "Ginv": Ginv_mat,
        "apply_inverse": apply_inverse,
        "kind": kind,
        "inv_struct": inv_struct,          # ("diag",phases)|("perm",perm)|("walsh",e)
        "composed_inverse_dense": None,
    }


def build_phase_children(n, e, a_list):
    """Scratch-only children whose restorations are diagonal unit phases."""
    children = []
    for a in a_list:
        phases = [gi_pow(a * popcount(x)) for x in range(n)]
        inv_phases = [p.conj() for p in phases]  # unit phase inverse
        Gmat = mat_diag(phases)
        Ginv = mat_diag(inv_phases)
        B = [G(1) for _ in range(n)]
        s = [G(popcount(x) + 1) for x in range(n)]
        apply_inv = lambda v, ph=inv_phases: apply_diag(v, ph)
        children.append(make_child(B, s, Gmat, Ginv, apply_inv, "scratch",
                                   ("diag", inv_phases)))
    return children


def build_perm_children(n, e, shifts):
    """Scratch-only children whose restorations are permutations (rotations)."""
    children = []
    for sh in shifts:
        perm = [((x + sh) % n) for x in range(n)]
        inv_perm = [((x - sh) % n) for x in range(n)]
        Gmat = mat_perm(perm)
        Ginv = mat_perm(inv_perm)
        B = [G(1) for _ in range(n)]
        s = [G(x + 1) for x in range(n)]
        apply_inv = lambda v, ip=inv_perm: apply_perm(v, ip)
        children.append(make_child(B, s, Gmat, Ginv, apply_inv, "scratch",
                                   ("perm", inv_perm)))
    return children


def build_hetero_children(n, e):
    """Scratch-only children with MIXED restoration families: a diagonal
    phase, then a Walsh transform, then a permutation.  Their composition is
    dense and destroys the cheap structure."""
    phase = [gi_pow(popcount(x)) for x in range(n)]
    inv_phase = [p.conj() for p in phase]
    c0 = make_child([G(1)] * n, [G(popcount(x) + 1) for x in range(n)],
                    mat_diag(phase), mat_diag(inv_phase),
                    (lambda v, ph=inv_phase: apply_diag(v, ph)), "scratch",
                    ("diag", inv_phase))
    H = _walsh_dense(e)
    # H^{-1} = (1/N) H
    Hinv = [[c.scale(Fraction(1, n)) for c in row] for row in H]
    c1 = make_child([G(1)] * n, [G(x + 1) for x in range(n)],
                    H, Hinv,
                    (lambda v: apply_walsh_fast(v)), "scratch",
                    ("walsh", e))
    sh = 1
    perm = [((x + sh) % n) for x in range(n)]
    inv_perm = [((x - sh) % n) for x in range(n)]
    c2 = make_child([G(1)] * n, [G(2) for _ in range(n)],
                    mat_perm(perm), mat_perm(inv_perm),
                    (lambda v, ip=inv_perm: apply_perm(v, ip)), "scratch",
                    ("perm", inv_perm))
    return [c0, c1, c2]


def build_reader_children(n, e):
    """One scratch-only child then one READER child (reads W into D).

    This is a counterexample to *unrestricted* deferral: one reader child CAN
    break the rewrite.  It is not a proof that read-free is necessary; see
    build_reader_cancellation_children for an exact nonzero-reader batch on
    which deferral is valid (as in PR1199/PR1203/PR1205)."""
    a_list = [1, 1]
    children = build_phase_children(n, e, a_list)
    children[1]["kind"] = "reader"
    return children


def build_reader_cancellation_children(n, e):
    """Five READER children that each read and negate the workspace.

    Exact nonzero-reader counterexample in the shape of PR1199: reader
    coefficients [1,1,1,-1,1], scratch G_i = -I for every child.  Read-free
    fails outright (every child reads W, four of them after nonidentity drift),
    yet the summed defect vanishes and deferral is exact: both schemes add
    3*w0 to the data and restore W, while the restoration bill falls from
    five negations to one."""
    coeffs = [G(1), G(1), G(1), G(-1), G(1)]
    children = []
    for c in coeffs:
        neg = [G(-1) for _ in range(n)]
        Gmat = mat_diag(neg)                     # negation is its own inverse
        B = [c for _ in range(n)]
        apply_inv = lambda v, ph=neg: apply_diag(v, ph)
        children.append(make_child(B, [G(0)] * n, Gmat, Gmat, apply_inv,
                                   "reader", ("diag", neg)))
    return children


# --------------------------------------------------------------------------
# Compose the individual structured inverses; return a deferred_apply that uses
# the RETAINED structure, plus a description of what structure survived.
# --------------------------------------------------------------------------
def _is_diag(M):
    n = len(M)
    for x in range(n):
        for y in range(n):
            if x != y and not M[x][y].is_zero():
                return False
    return True


def _is_perm(M):
    n = len(M)
    for x in range(n):
        row = [y for y in range(n) if not M[x][y].is_zero()]
        if len(row) != 1 or M[x][row[0]] != G(1):
            return False
    cols = set()
    for x in range(n):
        col = [y for y in range(n) if not M[y][x].is_zero()]
        if len(col) != 1:
            return False
        cols.add(col[0])
    return len(cols) == n


def compose_structured(children):
    """Return (deferred_apply, description).

    The mathematically exact composed restoration is
    (G_r ... G_1)^{-1} = G_1^{-1} ... G_r^{-1}, built as a dense product by
    direct_composed_inverse.  We then detect whether that exact product RETAINS
    cheap structure:

    * diagonal    -> a single unit-phase pass  (N mults)
    * permutation -> a single routing pass     (moves, 0 mults)
    * otherwise   -> dense                     (N^2 mults)

    The structured form is derived from the exact dense product and then checked
    to agree with it on the standard basis, so the cheap application is certified
    against the exact operator rather than assumed."""
    n = len(children[0]["B"])
    dense = direct_composed_inverse(children)   # exact G_1^{-1}...G_r^{-1}
    if _is_diag(dense):
        ph = [dense[x][x] for x in range(n)]
        # self-check: diagonal application equals dense application
        for x in range(n):
            basis = [G(1) if y == x else G(0) for y in range(n)]
            a, _ = apply_diag(basis, ph)
            b = mat_vec(dense, basis)
            need(_veceq(a, b), "diag structured != dense")
        return (lambda v, p=ph: apply_diag(v, p)), {"form": "diag", "nnz": mat_nnz(dense)}
    if _is_perm(dense):
        perm = [0] * n
        for x in range(n):
            for y in range(n):
                if not dense[x][y].is_zero():
                    perm[x] = y
        for x in range(n):
            basis = [G(1) if y == x else G(0) for y in range(n)]
            a, _ = apply_perm(basis, perm)
            b = mat_vec(dense, basis)
            need(_veceq(a, b), "perm structured != dense")
        return (lambda v, p=perm: apply_perm(v, p)), {"form": "perm", "nnz": mat_nnz(dense)}
    return (lambda v, M=dense: apply_dense(M, v)), {"form": "dense",
                                                    "nnz": mat_nnz(dense)}


def direct_composed_inverse(children):
    """Return (G_r ... G_1)^{-1}.

    The workspace drifts as W_r = (G_r ... G_1) w0.  Since
    (G_r ... G_1)^{-1} = G_1^{-1} G_2^{-1} ... G_r^{-1}, we build the product in
    forward child order:  acc = G_1^{-1} G_2^{-1} ... G_r^{-1}.
    Applying acc to W_r returns w0 exactly."""
    n = len(children[0]["B"])
    inv = mat_identity(n)
    for child in children:                 # forward order
        inv = mat_mul(inv, child["Ginv"])  # acc = acc * G_i^{-1}
    return inv


def summed_defect(children):
    """Exact terminal-observation criterion for this note's additive model.

    Under eager restoration every reader reads the node-entry workspace w0.
    Under deferral reader i reads the drifted P_{i-1} w0, with
    P_{i-1} = G_{i-1} ... G_1 and P_0 = I.  The final data therefore differ by

        M w0,   M = sum_{reader i} Diag(B_i) (P_{i-1} - I).

    The deferred scheme returns the same observables for every w0 exactly when
    M is the zero matrix (the final workspace is restored by the single
    composed restoration in both schemes).  This is the summed-defect criterion
    of PR1199/PR1203/PR1205.  Read-free batches make every term vanish
    separately and are therefore SUFFICIENT; nonzero-reader batches can cancel
    and are not excluded, so read-free is NOT necessary."""
    n = len(children[0]["B"])
    P = mat_identity(n)                       # P_0 = I (drift before child 1)
    M = [[G(0) for _ in range(n)] for _ in range(n)]
    for child in children:
        if child["kind"] == "reader":
            B = child["B"]
            for x in range(n):
                for y in range(n):
                    cell = P[x][y] - (G(1) if x == y else G(0))
                    M[x][y] = M[x][y] + B[x] * cell
        P = mat_mul(child["G"], P)             # P_i = G_i P_{i-1}
    return M


def apply_factorized(v, children):
    """Apply the exact composed restoration G_1^{-1} ... G_r^{-1} through its
    RETAINED factorization: the cheap structured inverses applied one after
    another (G_r^{-1} first, ..., G_1^{-1} last).  The cost is the sum of the
    factor costs, not N^2: a dense composed product retains its factors, and
    density of the matrix is not a statement about application cost."""
    total = {"passes": 0, "mults": 0, "adds": 0, "moves": 0}
    out = list(v)
    for child in reversed(children):
        out, c = child["apply_inverse"](out)
        _acc(total, c)
    return out, total


# --------------------------------------------------------------------------
# Main verification.
# --------------------------------------------------------------------------
def verify():
    cert = {"base": BASE, "cases": {}}
    n = 8
    e = 3
    batch = Batch(n, e)
    w0 = [G(popcount(x) + 1, x % 3) for x in range(n)]

    # ---- Case 1: homogeneous phase restorations, read-free batch. ----
    phase_children = build_phase_children(n, e, [1, 2, 3])
    r = len(phase_children)
    comp_inv = direct_composed_inverse(phase_children)
    phase_defer, phase_desc = compose_structured(phase_children)
    need(phase_desc["form"] == "diag", "phase composition should stay diagonal")

    D_e, W_e, cost_e = batch.run_eager(w0, phase_children)
    D_d, W_d, cost_d = batch.run_deferred(w0, phase_children, phase_defer)
    need(_veceq(D_e, D_d), "phase: data mismatch under deferral")
    need(_veceq(W_d, w0), "phase: workspace not restored by deferral")
    need(_veceq(W_e, w0), "phase: workspace not restored eagerly")
    need(cost_e["restoration_passes"] == r, "phase: eager restoration count")
    need(cost_d["restoration_passes"] == 1, "phase: deferred restoration count")
    need(cost_d["mults"] < cost_e["mults"], "phase: deferral should cut mults")
    cert["cases"]["phase"] = {
        "children": r,
        "composed_form": phase_desc["form"],
        "eager_restoration_passes": cost_e["restoration_passes"],
        "deferred_restoration_passes": cost_d["restoration_passes"],
        "eager_mults": cost_e["mults"],
        "deferred_mults": cost_d["mults"],
        "mult_ratio": str(Fraction(cost_e["mults"], max(cost_d["mults"], 1))),
        "observables_equal": True,
    }

    # ---- Case 2: homogeneous permutation restorations, read-free batch. ----
    perm_children = build_perm_children(n, e, [1, 2, 4])
    r2 = len(perm_children)
    perm_defer, perm_desc = compose_structured(perm_children)
    need(perm_desc["form"] == "perm", "perm composition should stay a permutation")
    D_e2, W_e2, cost_e2 = batch.run_eager(w0, perm_children)
    D_d2, W_d2, cost_d2 = batch.run_deferred(w0, perm_children, perm_defer)
    need(_veceq(D_e2, D_d2), "perm: data mismatch under deferral")
    need(_veceq(W_d2, w0), "perm: workspace not restored by deferral")
    need(cost_e2["restoration_passes"] == r2, "perm: eager restoration count")
    need(cost_d2["restoration_passes"] == 1, "perm: deferred restoration count")
    need(cost_d2["mults"] <= cost_e2["mults"], "perm: deferral should not raise mults")
    cert["cases"]["perm"] = {
        "children": r2,
        "composed_form": perm_desc["form"],
        "eager_restoration_passes": cost_e2["restoration_passes"],
        "deferred_restoration_passes": cost_d2["restoration_passes"],
        "eager_moves": cost_e2.get("moves", 0),
        "deferred_moves": cost_d2.get("moves", 0),
        "observables_equal": True,
    }

    # ---- Case 3 (correctness): one reader child CAN break deferral. ----
    # This is a counterexample to unrestricted deferral, hence a proof that
    # read-free is SUFFICIENT.  It is not evidence that read-free is necessary:
    # Case 5 gives an exact nonzero-reader batch on which deferral is valid
    # (the counterexamples of PR1199/PR1203/PR1205).
    reader_children = build_reader_children(n, e)
    reader_defer, _ = compose_structured(reader_children)
    D_e3, W_e3, _ = batch.run_eager(w0, reader_children)
    D_d3, W_d3, _ = batch.run_deferred(w0, reader_children, reader_defer)
    need(_veceq(W_d3, w0), "reader: final workspace should still be restored")
    need(not _veceq(D_e3, D_d3), "reader: this example should CHANGE the data output")
    diff = _vecsub(D_e3, D_d3)
    need(any(not c.is_zero() for c in diff), "reader: expected nonzero discrepancy")
    M3 = summed_defect(reader_children)
    need(mat_nnz(M3) > 0, "reader: summed defect should be nonzero in this example")
    cert["cases"]["reader_negative"] = {
        "observables_equal": False,
        "discrepancy_nonzero": True,
        "summed_defect_nonzero": True,
        "discrepancy": [c.key() for c in diff],
    }

    # ---- Case 5 (correctness): nonzero readers that cancel exactly. ----
    # PR1199's counterexample shape: five reader children, each reading and
    # negating the workspace, coefficients [1,1,1,-1,1].  Read-free fails
    # outright, yet the summed defect is exactly the zero matrix and deferral
    # is valid: both schemes add 3*w0 to the data and restore W.  The
    # restoration bill falls from five negations to one.  This falsifies the
    # "read-free is necessary" direction of the note's original iff.
    cancel_children = build_reader_cancellation_children(n, e)
    cancel_defer, cancel_desc = compose_structured(cancel_children)
    Mc = summed_defect(cancel_children)
    need(mat_nnz(Mc) == 0, "cancellation: summed defect should vanish exactly")
    D_e5, W_e5, cost_e5 = batch.run_eager(w0, cancel_children)
    D_d5, W_d5, cost_d5 = batch.run_deferred(w0, cancel_children, cancel_defer)
    need(_veceq(D_e5, D_d5), "cancellation: data mismatch under deferral")
    need(_veceq(W_d5, w0), "cancellation: workspace not restored by deferral")
    need(cost_e5["restoration_passes"] == 5, "cancellation: eager restoration count")
    need(cost_d5["restoration_passes"] == 1, "cancellation: deferred restoration count")
    cert["cases"]["reader_cancellation"] = {
        "children": 5,
        "reader_coefficients": ["1", "1", "1", "-1", "1"],
        "readers_nonzero": True,
        "summed_defect_zero": True,
        "observables_equal": True,
        "eager_restoration_passes": cost_e5["restoration_passes"],
        "deferred_restoration_passes": cost_d5["restoration_passes"],
    }

    # ---- Case 4 (cost): heterogeneous composition is dense, and density of
    # the composed matrix is NOT an application-cost statement. ----
    # The composed inverse of a phase/Walsh/permutation mix is dense (all N^2
    # entries nonzero).  Applying that dense product DIRECTLY costs N^2 = 64
    # multiplications against 16 for the three structured eager restorations,
    # so direct dense deferral loses 64 vs 16 at N = 8.  But the composed
    # operator retains its factorization into the three cheap structured
    # inverses; applied sequentially it costs exactly the eager sum (16) and
    # matches the dense product on every basis column.  Deferral therefore
    # costs more only when no cheap factorization is retained and the dense
    # product must be applied directly.
    hetero = build_hetero_children(n, e)
    comp_inv4 = direct_composed_inverse(hetero)
    hetero_defer, hetero_desc = compose_structured(hetero)
    need(hetero_desc["form"] == "dense",
         "hetero: composed inverse should be dense (structure destroyed)")
    # eager restoration cost = sum of structured inverse applications
    eager_struct_cost = {"mults": 0, "adds": 0, "moves": 0, "passes": 0}
    for c in hetero:
        _, rc = c["apply_inverse"](list(w0))
        _acc(eager_struct_cost, rc)
    # deferred restoration cost, DIRECT dense application of the composed product
    _, dcost = hetero_defer(list(w0))
    # deferred restoration cost, RETAINED factorization: sequential application
    # of G_3^{-1}, G_2^{-1}, G_1^{-1}, self-checked against the dense product
    # on the standard basis before its cost is trusted.
    fac_w, fac_cost = apply_factorized(w0, hetero)
    need(_veceq(fac_w, mat_vec(comp_inv4, w0)),
         "hetero: factorized application != dense product on w0")
    for x in range(n):
        basis = [G(1) if y == x else G(0) for y in range(n)]
        a, _ = apply_factorized(basis, hetero)
        b = mat_vec(comp_inv4, basis)
        need(_veceq(a, b), "hetero: factorized application != dense product on basis")
    need(fac_cost["mults"] == eager_struct_cost["mults"],
         "hetero: retained factorization should cost exactly the eager sum")
    need(dcost["mults"] > fac_cost["mults"],
         "hetero: direct dense application should exceed factorized application")
    nnz = mat_nnz(comp_inv4)
    is_dense = nnz == n * n
    D_e4, W_e4, cost_e4 = batch.run_eager(w0, hetero)
    D_d4, W_d4, cost_d4 = batch.run_deferred(w0, hetero, hetero_defer)
    need(_veceq(D_e4, D_d4), "hetero: data mismatch under deferral")
    need(_veceq(W_d4, w0), "hetero: workspace not restored by deferral")
    need(is_dense, "hetero: composed inverse should be dense")
    need(dcost["mults"] >= eager_struct_cost["mults"],
         "hetero: direct dense application eliminates no multiplications")
    cert["cases"]["hetero_negative"] = {
        "children": len(hetero),
        "composed_form": hetero_desc["form"],
        "composed_inverse_nnz": nnz,
        "composed_inverse_dense": is_dense,
        "eager_structured_mults": eager_struct_cost["mults"],
        "deferred_dense_mults": dcost["mults"],
        "deferred_factorized_mults": fac_cost["mults"],
        "deferred_factorized_passes": fac_cost["passes"],
        "factorized_matches_dense": True,
        "observables_equal": True,
        "mult_elimination": False,
    }

    cert["dimension_N"] = n
    cert["e"] = e
    cert["summary"] = (
        "phase=PASS perm=PASS hetero_dense=CONFIRMED "
        "reader_diverges=CONFIRMED reader_cancels=CONFIRMED "
        "factorized_matches_dense=CONFIRMED"
    )
    return cert


def _veceq(a, b):
    return len(a) == len(b) and all(x == y for x, y in zip(a, b))


def _vecsub(a, b):
    return [x - y for x, y in zip(a, b)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cert = verify()
    phase = cert["cases"]["phase"]
    perm = cert["cases"]["perm"]
    reader = cert["cases"]["reader_negative"]
    cancel = cert["cases"]["reader_cancellation"]
    hetero = cert["cases"]["hetero_negative"]

    line = (
        "PASS_RESTORATION_COALESCING "
        f"phase={phase['eager_restoration_passes']}->{phase['deferred_restoration_passes']}"
        f"(x{phase['mult_ratio']}) "
        f"perm={perm['eager_restoration_passes']}->{perm['deferred_restoration_passes']} "
        f"hetero_dense={hetero['composed_inverse_dense']} "
        f"reader_diverges={reader['observables_equal'] == False} "
        f"reader_cancels_5to1="
        f"{cancel['observables_equal'] and cancel['deferred_restoration_passes'] == 1} "
        f"hetero_mults=eager{hetero['eager_structured_mults']}"
        f"|factorized{hetero['deferred_factorized_mults']}"
        f"|dense{hetero['deferred_dense_mults']}"
    )
    committed = ROOT / "CERTIFICATE.json"
    if args.write is None and committed.exists():
        recorded = json.loads(committed.read_text())
        if json.dumps(recorded, sort_keys=True) != json.dumps(cert, sort_keys=True):
            raise ValueError("recomputed certificate differs from committed CERTIFICATE.json")
    print(line)
    if args.json:
        print(json.dumps(cert, indent=2, sort_keys=True))
    if args.write:
        args.write.write_text(json.dumps(cert, indent=2, sort_keys=True))
        print(f"WROTE {args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
