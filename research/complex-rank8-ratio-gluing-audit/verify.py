#!/usr/bin/env python3
"""Independent exact audit of PR1212, pinned 57099cb5684f38877f31d149d598801671a633db.

Standard library only. No network, predecessor imports, SAT solver, random samples,
numerical tolerance, or repository checkout. See audit.md for the universal proofs.
This program checks their integer/Laurent certificates and the finite E8 inputs.
Zero exclusion is an ASSUMED premise; neither it nor the multiplication theorem is
certified here. No P111/P104/P110 extension is attempted.

Credit: Brett Halligan/burntout76 and Ninefold (PR1212); DreamingOfClouds (PR717
model); themilkman216 (PR968). Substantial GPT-6 Pro assistance through ChatGPT.
This is an AI-assisted independent derivation/reimplementation, not human review.

Example:
  python3 -I -B verify.py --out run-report.json --certificate-out certificate.json
  python3 -I -B -O verify.py --check-certificate certificate.json

All essential data are literals or deterministically constructed below. Checks use
exceptions, not Python assert statements, and therefore also run with python -O.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import combinations, permutations, product
from math import prod
import json
from pathlib import Path
import platform
import sys

HEAD = "57099cb5684f38877f31d149d598801671a633db"
MAIN_BASE = "410026dc5513b87db92ae98571d1d5984c69a983"
PROOF_URL = ("https://raw.githubusercontent.com/burntout76/integer-mult-bounds/"
             + HEAD + "/research/complex-rank8-decoder-rigidity/PROOF.md")
CHECKS: list[dict] = []


class VerificationError(Exception):
    """An exact mathematical or certificate check failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def passed(name: str, **data) -> None:
    CHECKS.append({"name": name, "status": "PASS", **data})
    detail = " " + json.dumps(data, sort_keys=True) if data else ""
    print("PASS " + name + detail, flush=True)


def rejected(name: str, operation) -> None:
    try:
        operation()
    except VerificationError as exc:
        passed(name, expected_rejection=str(exc))
    else:
        raise VerificationError(name + ": an invalid control was accepted")


# ----------------------- small exact matrix arithmetic -----------------------
def transpose(A):
    return [list(c) for c in zip(*A)]


def mm(A, B):
    require(bool(A) and bool(B) and len(A[0]) == len(B), "matrix dimensions")
    return [[sum(x * y for x, y in zip(a, b)) for b in zip(*B)] for a in A]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def determinant(A):
    n = len(A)
    require(all(len(row) == n for row in A), "determinant requires square matrix")
    B = [[Q(x) for x in row] for row in A]
    ans = Q(1)
    for k in range(n):
        p = next((i for i in range(k, n) if B[i][k]), None)
        if p is None:
            return Q(0)
        if p != k:
            B[k], B[p] = B[p], B[k]
            ans = -ans
        pivot = B[k][k]
        ans *= pivot
        for i in range(k + 1, n):
            c = B[i][k] / pivot
            B[i] = [x - c * y for x, y in zip(B[i], B[k])]
    return ans


def inverse(A):
    n = len(A)
    B = [[Q(x) for x in row] + [Q(i == j) for j in range(n)]
         for i, row in enumerate(A)]
    for k in range(n):
        p = next((i for i in range(k, n) if B[i][k]), None)
        require(p is not None, "inverse of singular matrix")
        B[k], B[p] = B[p], B[k]
        pivot = B[k][k]
        B[k] = [x / pivot for x in B[k]]
        for i in range(n):
            if i != k:
                c = B[i][k]
                B[i] = [x - c * y for x, y in zip(B[i], B[k])]
    return [row[n:] for row in B]


# Laurent polynomials: exponent tuples -> integer coefficients. No substitutions
# at field elements are used for any positive symbolic certificate.
def monomial(n, i=None, power=1, coefficient=1):
    e = [0] * n
    if i is not None:
        e[i] = power
    return {tuple(e): coefficient} if coefficient else {}


def padd(*polys):
    out = {}
    for poly in polys:
        for e, c in poly.items():
            out[e] = out.get(e, 0) + c
            if not out[e]:
                del out[e]
    return out


def pscale(poly, c):
    return {e: a * c for e, a in poly.items() if a * c}


def pmul(A, B):
    out = {}
    for a, ca in A.items():
        for b, cb in B.items():
            e = tuple(x + y for x, y in zip(a, b))
            out[e] = out.get(e, 0) + ca * cb
            if not out[e]:
                del out[e]
    return out


def pdet(A):
    n = len(A)
    nvars = len(next(iter(A[0][0])))
    out = {}
    for perm in permutations(range(n)):
        sign = (-1) ** sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        term = monomial(nvars, coefficient=sign)
        for i, j in enumerate(perm):
            term = pmul(term, A[i][j])
        out = padd(out, term)
    return out


def pmm(A, B):
    return [[padd(*(pmul(a, b) for a, b in zip(row, col)))
             for col in zip(*B)] for row in A]


def pminor(A, i, j, c, d):
    return padd(pmul(A[i][c], A[j][d]), pscale(pmul(A[i][d], A[j][c]), -1))


H0 = [[1, 1, 1, 1], [1, 1, -1, -1],
      [1, -1, 1, -1], [1, -1, -1, 1]]
PAIRS4 = list(combinations(range(4), 2))


def groups(H, c, d):
    return tuple(sorted(tuple(i for i in range(4) if H[i][c] * H[i][d] == s)
                        for s in (-1, 1)))


def all_group_minors_zero(A, H=H0):
    return all(A[i][c] * A[j][d] == A[i][d] * A[j][c]
               for c, d in PAIRS4 for i, j in groups(H, c, d))


def local_algebra():
    # Variables (x,y,z,X,Y,Z); row exponents encode monomial equalities = 1.
    E = [[0, 1, -1, 0, -1, 1], [0, -1, -1, 0, 1, 1],
         [1, 0, -1, -1, 0, 1], [-1, 0, -1, 1, 0, 1],
         [1, -1, 0, -1, 1, 0], [-1, -1, 0, 1, 1, 0]]
    M = [[0, -1, 1], [0, 1, 1], [-1, 0, 1],
         [1, 0, 1], [-1, 1, 0], [1, 1, 0]]
    U = [[0, 0, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0],
         [1, 1, 0, 0, 0, 0], [-1, -1, 1, 1, 0, 0],
         [1, 0, -1, 0, 1, 0], [0, -1, 1, 0, 0, 1]]
    V = [[-1, 0, 1], [0, -1, 1], [0, 0, 1]]
    D = [[1, 0, 0], [0, 1, 0], [0, 0, 2],
         [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    require(determinant(U) == determinant(V) == 1, "local unimodularity")
    require(mm(mm(U, M), V) == D, "local Smith certificate")
    # x,y,z,X,Y,Z = x,y,z,x*p,y*q,z*r, an integral monomial automorphism.
    T = identity(6)
    for i in range(3):
        T[3 + i][i] = 1
    require(mm(E, T) == [[0, 0, 0] + row for row in M], "six-variable normalization")
    V6 = identity(6)
    for i in range(3):
        for j in range(3):
            V6[i + 3][j + 3] = V[i][j]
    W = mm(T, V6)
    W = [[row[j] for j in (3, 4, 5, 0, 1, 2)] for row in W]
    D6 = [[(1, 1, 2, 0, 0, 0)[i] if i == j else 0 for j in range(6)] for i in range(6)]
    require(determinant(W) == -1 and mm(mm(U, E), W) == D6, "full Smith certificate")
    passed("algebra.unimodular", diagonal=[1, 1, 2, 0, 0, 0], det_U=1, det_W=-1)

    # Directly recover exactly the six displayed equations from the twelve minors.
    one = monomial(6)
    x, y, z, X, Y, Z = [monomial(6, i) for i in range(6)]
    N = [[one, x, y, z], [one, x, Y, Z],
         [one, X, y, Z], [one, X, Y, z]]
    expected = [padd(pmul(y, Z), pscale(pmul(Y, z), -1)),
                padd(pmul(y, z), pscale(pmul(Y, Z), -1)),
                padd(pmul(x, Z), pscale(pmul(X, z), -1)),
                padd(pmul(x, z), pscale(pmul(X, Z), -1)),
                padd(pmul(x, Y), pscale(pmul(X, y), -1)),
                padd(pmul(x, y), pscale(pmul(X, Y), -1))]
    got = [pminor(N, i, j, c, d) for c, d in ((2, 3), (1, 3), (1, 2))
           for i, j in groups(H0, c, d)]
    require(got == expected, "six minor equations or their signs")
    require(all(not pminor(N, i, j, 0, d)
                for d in (1, 2, 3) for i, j in groups(H0, 0, d)), "first-column minors")
    passed("algebra.exact_minor_reduction", total_group_minors=12, remaining_equations=6)

    # Polynomial ideal equality, independent of the Smith computation.
    p, q, r = [monomial(3, i) for i in range(3)]
    one3 = monomial(3)
    F = [padd(r, pscale(q, -1)), padd(pmul(q, r), pscale(one3, -1)),
         padd(r, pscale(p, -1)), padd(pmul(p, r), pscale(one3, -1)),
         padd(q, pscale(p, -1)), padd(pmul(p, q), pscale(one3, -1))]
    G = [padd(p, pscale(r, -1)), padd(q, pscale(r, -1)),
         padd(pmul(r, r), pscale(one3, -1))]
    require(G == [pscale(F[2], -1), pscale(F[0], -1), padd(F[1], pmul(r, F[0]))],
            "ideal forward identities")
    require(F == [pscale(G[1], -1), padd(G[2], pmul(r, G[1])),
                  pscale(G[0], -1), padd(G[2], pmul(r, G[0])),
                  padd(G[1], pscale(G[0], -1)),
                  padd(G[2], pmul(q, G[0]), pmul(r, G[1]))], "ideal reverse identities")
    passed("algebra.polynomial_ideal_equality", forward_identities=3, reverse_identities=6)

    # Universal determinant in Z[t], then modulo t^2-1.
    t, one1 = monomial(1, 0), monomial(1)
    C = [[one1 if i == 0 or j == 0 or i == j else pscale(t, -1)
          for j in range(4)] for i in range(4)]
    dt = pdet(C)
    expected_dt = {(0,): -2, (1,): -6, (2,): -6, (3,): -2}
    require(dt == expected_dt, "det C(t) = -2(1+t)^3")
    reduced = {}
    for (e,), coef in dt.items():
        reduced[(e % 2,)] = reduced.get((e % 2,), 0) + coef
    require(reduced == {(0,): -8, (1,): -8}, "determinant modulo t^2-1")
    require(determinant(H0) == -16, "positive branch rank four")
    require(all_group_minors_zero([[1] * 4 for _ in range(4)]), "negative branch minors")
    passed("algebra.branch_determinant", determinant_coefficients=[-2, -6, -6, -2],
           reduced_coefficients=[-8, -8], positive_branch_determinant=-16, negative_branch_rank=1)

    # Exhaust the finite sign alphabet, not any nonzero field-valued parameters.
    sign_rows = list(product((-1, 1), repeat=4))
    dots = [[sum(x * y for x, y in zip(a, b)) for b in sign_rows] for a in sign_rows]
    target = [groups(H0, c, d) for c, d in PAIRS4]
    nh = nsame = 0
    for inds in product(range(16), repeat=4):
        H = [sign_rows[i] for i in inds]
        had = all(dots[inds[i]][inds[j]] == 0 for i, j in PAIRS4)
        nh += int(had)
        if all(groups(H, c, d) == target[k] for k, (c, d) in enumerate(PAIRS4)):
            nsame += 1
            normalized = [[H[i][j] * H[i][0] * H[0][j] * H[0][0]
                           for j in range(4)] for i in range(4)]
            require(had and normalized == H0, "sign-equivalence classification")
            outer = [[H0[i][j] * H[i][j] for j in range(4)] for i in range(4)]
            require(all(outer[i][j] == H[i][0] * H[0][j] * H[0][0]
                        for i in range(4) for j in range(4)), "negative branch outer product")
    require(nh == 768 and nsame == 128, "finite sign-matrix counts")
    passed("algebra.sign_equivalence", sign_matrices=65536, hadamard_matrices=nh,
           fixed_labeled_group_structures=nsame)

    # Deliberately nonsymmetric H, to detect inverse-transpose mistakes.
    H = [([-x for x in row] if i == 0 else list(row)) for i, row in enumerate(H0)]
    require(H != transpose(H), "nonsymmetric sign control")
    def scaled(sign_matrix, b=False, factor=4):
        out = []
        for i in range(4):
            row = []
            for j in range(4):
                e = [0] * 8
                e[i] = e[4 + j] = -1 if b else 1
                row.append({tuple(e): sign_matrix[i][j] * (factor if b else 1)})
            out.append(row)
        return out
    A = scaled(H)
    B = scaled(H, b=True)
    expect = [[monomial(8, coefficient=16 * int(i == j)) for j in range(4)] for i in range(4)]
    require(pmm(A, transpose(B)) == expect, "symbolic A B^T = 16I")
    passed("algebra.ordinary_inverse_transpose", formal_nonzero_variables=8)

    U_bad = deepcopy(U)
    U_bad[0][0] += 1
    rejected("control.corrupt_unimodular_certificate",
             lambda: require(mm(mm(U_bad, M), V) == D, "altered U rejected"))
    require(pmm(A, transpose(scaled(transpose(H), b=True))) != expect, "wrong H^T must fail")
    require(pmm(A, transpose(scaled(H, b=True, factor=1))) != expect, "missing factor four must fail")
    passed("control.wrong_transpose_and_factor_rejected")
    # Retain only the three ratio equalities: p=q=r=2 then violates the products.
    v = (Q(2), Q(2), Q(2))
    values = [prod((v[i] ** e for i, e in enumerate(row)), start=Q(1)) for row in M]
    require(values == [1, 4, 1, 4, 1, 4], "quadratic relation deletion control")
    passed("control.quadratic_relations_are_not_discardable", values=[str(x) for x in values])
    # Characteristic two: 16I=0 no longer forces invertibility.
    J = [[1] * 4 for _ in range(4)]
    require(determinant(J) == 0 and all(x % 2 == 0 for row in mm(J, transpose(J)) for x in row),
            "characteristic-two duality no longer forces full rank")
    passed("control.characteristic_two_is_excluded", matrix="A=B=J mod 2", determinant=0)
    # Boundary solution to the LOCAL minor system after nonzeroness is removed.
    perm = (0, 2, 3, 1)
    A0 = [[4 * int(perm[i] == j) for j in range(4)] for i in range(4)]
    require(all_group_minors_zero(A0), "boundary example must satisfy all group minors")
    require(mm(A0, transpose(A0)) == [[16 * z for z in row] for row in identity(4)], "boundary duality")
    passed("control.zero_boundary_local_counterexample", permutation=list(perm),
           note="Not a zero-free solution and not a counterexample to the E8 theorem")
    # Independent isolated-class counterexample, rather than the predecessor Pascal example.
    A1 = [[1 + int(i == j) for j in range(4)] for i in range(4)]
    B1 = [[16 * x for x in row] for row in transpose(inverse(A1))]
    minor = A1[0][0] * A1[1][1] - A1[0][1] * A1[1][0]
    require(all(x for row in A1 + B1 for x in row) and determinant(A1) == 5 and minor == 3,
            "isolated class counterexample")
    require(mm(A1, transpose(B1)) == [[16 * z for z in row] for row in identity(4)], "isolated duality")
    passed("control.within_class_equations_insufficient", determinant=5, forced_minor_violation=3)
    return {"original_exponent_matrix_E": E, "normalized_matrix_M": M,
            "row_unimodular_U": U, "column_unimodular_V": V,
            "full_column_unimodular_W": W, "smith_diagonal": [1, 1, 2, 0, 0, 0],
            "H0": H0, "det_C_t_coefficients": [-2, -6, -6, -2]}


# -------------------- independent finite E8 construction ---------------------
def canonical(v):
    v = tuple(v)
    return v if next(x for x in v if x) > 0 else tuple(-x for x in v)


def doubled_roots():
    roots = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = a, b
            roots.add(tuple(v))
    roots.update(v for v in product((-1, 1), repeat=8) if v.count(-1) % 2 == 0)
    return sorted(roots)


def frame_vectors(pairs):
    out = []
    for i, j in pairs:
        for sign in (1, -1):
            v = [0] * 8
            v[i], v[j] = 2, 2 * sign
            out.append(tuple(v))
    return out


def affine_planes():
    return sorted(tuple(k for k in range(8) if (k & a).bit_count() % 2 == b)
                  for a in range(1, 8) for b in (0, 1))


def check_steiner(blocks):
    require(len(blocks) == 14 and len(set(blocks)) == 14, "need 14 distinct blocks")
    require(all(len(S) == 4 and len(set(S)) == 4 for S in blocks), "block sizes")
    require(all(sum(set(T) <= set(S) for S in blocks) == 1
                for T in combinations(range(8), 3)), "each triple must occur once")
    require(all(sum(set(P) <= set(S) for S in blocks) == 3
                for P in combinations(range(8), 2)), "each pair must occur three times")
    require(all(len(set(S) & set(T)) in (0, 2) for S, T in combinations(blocks, 2)), "block intersections")
    require(all(tuple(k for k in range(8) if k not in S) in blocks for S in blocks), "complementary blocks")


def construct_unit(name, lines, Gram, F0, F1):
    F = F0 if name == "P120" else F1
    live = set(range(120)) if name == "P120" else set(range(120)) - set(F0)
    require(len(live) == int(name[1:]) and set(F) <= live, "live pivot")
    require(all(Gram[i][j] == 2 * int(i == j) for i in F for j in F), "pivot orthogonality")
    info = {}
    block_lines = defaultdict(list)
    for i in range(120):
        if i in F:
            continue
        eps = tuple(Gram[i][f] for f in F)
        S = tuple(k for k, s in enumerate(eps) if s)
        require(len(S) == 4 and all(eps[k] in (-1, 1) for k in S), "four signed pivot coordinates")
        require(all(2 * lines[i][j] == sum(eps[k] * lines[F[k]][j] for k in S)
                    for j in range(8)), "integer frame reconstruction")
        info[i] = (S, eps)
        block_lines[S].append(i)
    blocks = sorted(block_lines)
    check_steiner(blocks)
    require(blocks == affine_planes(), "explicit affine-plane identification")
    require(all(len(v) == 8 for v in block_lines.values()), "eight root lines per block")
    passed(name + ".geometry.support_design", blocks=14, triples=56, pairs=28)
    all_classes = []
    for S in blocks:
        sign_reps = set()
        for i in block_lines[S]:
            s = tuple(info[i][1][k] for k in S)
            sign_reps.add(tuple(x * s[0] for x in s))
        require(sign_reps == {(1,) + s for s in product((-1, 1), repeat=3)}, "all sign lines in a block")
        for parity in (0, 1):
            ids = [i for i in block_lines[S] if sum(info[i][1][k] == -1 for k in S) % 2 == parity]
            H = [[info[i][1][k] for k in S] for i in ids]
            require(len(ids) == 4 and mm(H, transpose(H)) == [[4*x for x in row] for row in identity(4)],
                    "Hadamard row identities")
            require(mm(transpose(H), H) == [[4*x for x in row] for row in identity(4)], "Hadamard columns")
            gs = [groups(H, c, d) for c, d in PAIRS4]
            require(all(all(len(g) == 2 for g in pair) for pair in gs) and len(set(gs)) == 3,
                    "three perfect matchings")
            for c, d in PAIRS4:
                rest = tuple(k for k in range(4) if k not in (c, d))
                require(groups(H, c, d) == groups(H, *rest), "complementary-column matchings")
            labeling = next((p for p in permutations(range(4))
                             if all(groups([H[i] for i in p], c, d) == groups(H0, c, d)
                                    for c, d in PAIRS4)), None)
            require(labeling is not None, "simultaneous row labeling")
            count_live = sum(i in live for i in ids)
            require(count_live in (0, 4), "every live line is in a complete live class")
            all_classes.append({"support": S, "parity": parity, "lines": ids, "H": H,
                                "labeling_to_H0_groups": list(labeling), "live_count": count_live})
    classes = [C for C in all_classes if C["live_count"] == 4]
    require(len(classes) == (28 if name == "P120" else 26), "complete live class count")
    require(all(any(C["support"] == S for C in classes) for S in blocks), "complete class on every block")
    absent = [C for C in all_classes if not C["live_count"]]
    if name == "P112":
        require(len(absent) == 2 and not set(absent[0]["support"]) & set(absent[1]["support"]),
                "punctures are whole classes on complementary blocks")
        require(set(absent[0]["lines"] + absent[1]["lines"]) == set(F0), "exact puncture")
    checked_pairs = 0
    for i, j in combinations(info, 2):
        S, si = info[i]
        T, sj = info[j]
        ov = set(S) & set(T)
        require(2 * Gram[i][j] == sum(si[k] * sj[k] for k in ov), "orthogonality identity")
        rule = (not ov or (len(ov) == 2 and sum(si[k] * sj[k] for k in ov) == 0)
                or (S == T and sum(si[k] == -1 for k in S) % 2 == sum(sj[k] == -1 for k in T) % 2))
        require((Gram[i][j] == 0) == rule, "complete orthogonality rule")
        checked_pairs += 1
    passed(name + ".geometry.classes_and_orthogonality", complete_live_classes=len(classes),
           nonpivot_line_pairs=checked_pairs, absent_classes=len(absent))

    witnesses = []
    counts = Counter()
    for c, C in enumerate(classes):
        S = C["support"]
        for k, ell in combinations(S, 2):
            for sign in (-1, 1):
                group = [i for i in C["lines"] if info[i][1][k] * info[i][1][ell] == sign]
                require(len(group) == 2, "two rows per witness group")
                js = [j for j in sorted(live - set(F)) if info[j][0] != S
                      and set(info[j][0]) & set(S) == {k, ell}
                      and all(Gram[i][j] == 0 for i in group)]
                require(bool(js) and all(info[j][1][k] * info[j][1][ell] == -sign for j in js),
                        "live witness with opposite product")
                counts[len(js)] += 1
                witnesses.append({"class": c, "pair": [k, ell], "rows": group, "witnesses": js})
    expected_hist = {8: 336} if name == "P120" else {6: 96, 8: 216}
    require(dict(counts) == expected_hist, "exact group-witness census")
    edges = []
    for c, d in combinations(range(len(classes)), 2):
        C, D = classes[c], classes[d]
        if C["support"] == D["support"]:
            continue
        ov = sorted(set(C["support"]) & set(D["support"]))
        if len(ov) != 2:
            continue
        pairs = [[i, j] for i in C["lines"] for j in D["lines"] if Gram[i][j] == 0]
        require(all(sum(i == ii for ii, jj in pairs) == 2 for i in C["lines"])
                and all(sum(j == jj for ii, jj in pairs) == 2 for j in D["lines"]), "gluing witnesses both orders")
        require(all(info[i][1][ov[0]] * info[j][1][ov[0]] ==
                    -info[i][1][ov[1]] * info[j][1][ov[1]] for i, j in pairs), "gluing cancellation signs")
        edges.append({"classes": [c, d], "pair": ov, "orthogonal_row_pairs": pairs})
    require(len(edges) == (336 if name == "P120" else 288), "class overlap count")
    passed(name + ".geometry.witnesses", group_obligations=len(witnesses),
           group_witness_count_histogram=dict(counts), unordered_class_overlaps=len(edges),
           ordered_two_term_equations=16 * len(edges))
    return {"unit": name, "pivot_line_ids": F, "pivot_doubled_roots": [lines[f] for f in F],
            "punctured_line_ids": sorted(set(range(120)) - live), "blocks": blocks,
            "all_classes": all_classes, "classes": classes,
            "group_witnesses": witnesses, "overlap_edges": edges}


# Sparse INTEGER matrices. Rows are maps column -> integer coefficient.
def vadd(*rows):
    out = {}
    for row in rows:
        for k, v in row.items():
            out[k] = out.get(k, 0) + v
            if not out[k]:
                del out[k]
    return out


def vscale(row, c):
    return {k: c * v for k, v in row.items() if c * v}


def smm(A, B):
    return [vadd(*(vscale(B[k], c) for k, c in row.items())) for row in A]


def sid(n):
    return [{i: 1} for i in range(n)]


def sparse_encode(A):
    return [[[k, v] for k, v in sorted(row.items())] for row in A]


def check_retraction(M, P, Qmat, W):
    N, d, m = len(P), len(Qmat), len(M)
    require(len(W) == N, "W row count")
    for A, cols in ((M, N), (P, d), (Qmat, N), (W, m)):
        require(all(all(isinstance(k, int) and 0 <= k < cols and type(v) is int and v != 0
                        for k, v in row.items()) for row in A), "integral sparse matrix dimensions")
    require(smm(M, P) == [{} for _ in M], "M P = 0")
    require(smm(Qmat, P) == sid(d), "Q P = I")
    residual = [vadd({i: 1}, vscale(row, -1)) for i, row in enumerate(smm(P, Qmat))]
    require(residual == smm(W, M), "I - P Q = W M")


def glue_certificate(unit):
    name = unit["unit"]
    classes, edges = unit["classes"], unit["overlap_edges"]
    n = len(classes)
    coordinates = [(c, k) for c, C in enumerate(classes) for k in C["support"]]
    index = {v: i for i, v in enumerate(coordinates)}
    N = len(coordinates)
    def ratio(c, k, ell):
        return vadd({index[c, k]: 1}, {index[c, ell]: -1}) if k != ell else {}
    by_pair = {P: [c for c, C in enumerate(classes) if set(P) <= set(C["support"])]
               for P in combinations(range(8), 2)}
    edge_index = {(e["classes"][0], e["classes"][1], *e["pair"]): t for t, e in enumerate(edges)}
    M = [vadd(ratio(c, *e["pair"]), vscale(ratio(d, *e["pair"]), -1))
         for e in edges for c, d in [e["classes"]]]
    def transfer(c, d, k, ell):
        """Integer edge combination for R_c(k,ell)-R_d(k,ell); at most two edges."""
        if c == d:
            return {}
        a, b = sorted((k, ell))
        if classes[c]["support"] == classes[d]["support"]:
            bridge = next((e for e in by_pair[a, b] if classes[e]["support"] != classes[c]["support"]), None)
            require(bridge is not None, "same-block bridge exists")
            return vadd(transfer(c, bridge, k, ell), transfer(bridge, d, k, ell))
        lo, hi = sorted((c, d))
        require((lo, hi, a, b) in edge_index, "direct overlap edge exists")
        sign = (1 if c < d else -1) * (1 if k < ell else -1)
        return {edge_index[lo, hi, a, b]: sign}
    # Check every ordered transfer, including both classes in a single block.
    transfer_count = 0
    for (k, ell), cs in by_pair.items():
        require(len(cs) >= 3, "pair has complete live classes in multiple blocks")
        for c, d in product(cs, repeat=2):
            comb = transfer(c, d, k, ell)
            require(smm([comb], M)[0] == vadd(ratio(c, k, ell), vscale(ratio(d, k, ell), -1)),
                    "integer pair-transfer identity")
            require(sum(abs(v) for v in comb.values()) <= 2, "two-edge transfer bound")
            transfer_count += 1
    reps = {k: by_pair[0, k][0] for k in range(1, 8)}
    grows = [{}] + [ratio(reps[k], k, 0) for k in range(1, 8)]
    anchors = [C["support"][0] for C in classes]
    # Parameter order: c_0,...,c_(n-1),g_1,...,g_7; g_0 is identically 1.
    P = [vadd({c: 1}, {n + k - 1: 1} if k else {}) for c, k in coordinates]
    Qmat = [vadd({index[c, a]: 1}, vscale(grows[a], -1)) for c, a in enumerate(anchors)] + grows[1:]
    W = []
    for c, k in coordinates:
        a = anchors[c]
        if k == a:
            row = {}
        elif a == 0:
            row = transfer(c, reps[k], k, 0)
        elif k == 0:
            row = vscale(transfer(c, reps[a], a, 0), -1)
        else:
            d = next((j for j, C in enumerate(classes) if {0, a, k} <= set(C["support"])), None)
            require(d is not None, "complete class covers contraction triangle")
            row = vadd(transfer(c, d, k, a), transfer(d, reps[k], k, 0),
                       vscale(transfer(d, reps[a], a, 0), -1))
        require(sum(abs(v) for v in row.values()) <= 6, "six-edge contraction bound")
        W.append(row)
    check_retraction(M, P, Qmat, W)
    rank = N - (n + 7)
    require(rank == (77 if name == "P120" else 71), "gluing lattice rank")
    passed(name + ".gluing.integral_retraction", coordinates=N, constraints=len(M),
           free_parameters=n + 7, saturated_lattice_rank=rank,
           checked_pair_transfers=transfer_count, max_W_row_l1=max(sum(abs(x) for x in row.values()) for row in W))
    Wbad = deepcopy(W)
    Wbad[0] = vadd(Wbad[0], {0: 1})
    rejected(name + ".control.corrupt_gluing_certificate", lambda: check_retraction(M, P, Qmat, Wbad))
    # One class-coordinate twist preserves local duality but breaks an actual E2 equation.
    edge = edges[0]
    c, d = edge["classes"]
    k, ell = edge["pair"]
    i, j = edge["orthogonal_row_pairs"][0]
    C, D = classes[c], classes[d]
    eps_i = dict(zip(C["support"], C["H"][C["lines"].index(i)]))
    eps_j = dict(zip(D["support"], D["H"][D["lines"].index(j)]))
    residual = 4 * (2 * eps_i[k] * eps_j[k] + eps_i[ell] * eps_j[ell])
    require(abs(residual) == 4, "unglued class scaling must violate a real overlap equation")
    passed(name + ".control.unglued_scaling", classes=[c, d], pair=[k, ell], rows=[i, j], E2_residual=residual)
    return {"coordinates": coordinates, "parameter_order": {"class_parameters": n, "g_points": list(range(1, 8))},
            "anchors": anchors, "base_pair_representatives": reps,
            "M": sparse_encode(M), "P": sparse_encode(P), "Q": sparse_encode(Qmat), "W": sparse_encode(W),
            "rank": rank, "free_parameters": n + 7}


def triangle_certificate():
    # All edges oriented low -> high. Star edges first, then nonstar edges.
    edges = [(0, j) for j in range(1, 8)] + list(combinations(range(1, 8), 2))
    idx = {e: i for i, e in enumerate(edges)}
    B = identity(28)
    for row, (i, j) in enumerate(edges[7:], start=7):
        B[row][idx[0, i]] += 1
        B[row][idx[0, j]] -= 1
    require(determinant(B) == 1, "unimodular triangle/star basis")
    incidence = [[int(v == i) - int(v == j) for v in range(8)] for i, j in edges]
    image = mm(B, incidence)
    require(image[:7] == incidence[:7] and image[7:] == [[0] * 8 for _ in range(21)],
            "21 fundamental triangle boundaries")
    passed("gluing.triangle_contraction", edges=28, star_edges=7, fundamental_triangles=21, determinant=1)
    # Abstract overlap-compatible atlas, NOT an E8 live-set counterexample.
    supports = [(0, 1, 2, 3), (2, 3, 4, 5), (0, 1, 4, 5)]
    gamma = [{k: Q(1) for k in supports[0]}, {k: Q(1) for k in supports[1]},
             {0: Q(2), 1: Q(2), 4: Q(1), 5: Q(1)}]
    require(all(any(set(pair) <= set(S) for S in supports) for pair in combinations(range(6), 2)),
            "toy pair coverage")
    for c, d in combinations(range(3), 2):
        ov = sorted(set(supports[c]) & set(supports[d]))
        require(len(ov) == 2 and gamma[c][ov[0]] / gamma[c][ov[1]] ==
                gamma[d][ov[0]] / gamma[d][ov[1]], "toy overlap compatibility")
    def rho(i, j):
        c = next(c for c, S in enumerate(supports) if {i, j} <= set(S))
        return gamma[c][i] / gamma[c][j]
    holonomy = rho(0, 2) * rho(2, 4) * rho(4, 0)
    require(holonomy == Q(1, 2) and not any({0, 2, 4} <= set(S) for S in supports), "toy nontrivial holonomy")
    passed("control.pair_coverage_without_triangles", loop=[0, 2, 4, 0], holonomy=str(holonomy),
           note="Abstract six-point atlas, not an E8 puncture or a claimed extension")
    rejected("control.corrupt_steiner_design", lambda: check_steiner(affine_planes()[1:]))
    return {"edge_order": edges, "unimodular_star_triangle_basis": B,
            "toy_atlas_supports": supports, "toy_loop": [0, 2, 4, 0], "toy_holonomy": "1/2"}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, help="write an execution report JSON")
    parser.add_argument("--certificate-out", type=Path, help="write deterministic complete integer certificates")
    parser.add_argument("--check-certificate", type=Path, help="also require a saved certificate to equal fresh reconstruction")
    args = parser.parse_args()
    CHECKS.clear()
    certificate = {"schema": "PR1212-lemmas5-6-independent-audit-v1", "head": HEAD,
                   "user_main_base": MAIN_BASE, "proof_url": PROOF_URL,
                   "assumed_not_reproved": ["predecessor zero-exclusion Lemma 4"],
                   "local_algebra": local_algebra()}
    roots = doubled_roots()
    lines = sorted({canonical(r) for r in roots})
    require(len(roots) == 240 and len(lines) == 120, "E8 root/line counts")
    dots = [[sum(x*y for x, y in zip(a, b)) for b in lines] for a in lines]
    require(all(x % 4 == 0 for row in dots for x in row), "integral Gram entries")
    Gram = [[x // 4 for x in row] for row in dots]
    require(all(Gram[i][i] == 2 and all(Gram[i][j] in (-1, 0, 1) for j in range(120) if i != j)
                for i in range(120)), "E8 Gram norms and off-diagonal entries")
    F0vectors = frame_vectors([(0, 1), (2, 3), (4, 5), (6, 7)])
    F1vectors = frame_vectors([(0, 2), (1, 3), (4, 6), (5, 7)])
    F0 = [lines.index(v) for v in F0vectors]
    F1 = [lines.index(v) for v in F1vectors]
    perm = [0, 2, 1, 3, 4, 6, 5, 7]
    require([tuple(v[i] for i in perm) for v in F0vectors] == F1vectors, "explicit pivot isometry")
    require({tuple(v[i] for i in perm) for v in roots} == set(roots), "pivot isometry preserves roots")
    require(not set(F0) & set(F1), "special P112 pivot is live")
    recipe = set()
    for i in range(120):
        if i in F0:
            continue
        eps = [Gram[i][f] for f in F0]
        support = tuple(k for k in range(8) if eps[k])
        if support in ((0, 1, 2, 3), (4, 5, 6, 7)) and sum(eps[k] == -1 for k in support) % 2 == 0:
            recipe.add(i)
    require(recipe == set(F1), "special pivot equals two complementary even classes")
    passed("geometry.independent_E8", roots=240, lines=120)
    certificate["doubled_root_line_representatives"] = lines
    certificate["units"] = {}
    for name in ("P112", "P120"):
        unit = construct_unit(name, lines, Gram, F0, F1)
        unit["gluing_lattice_certificate"] = glue_certificate(unit)
        certificate["units"][name] = unit
    certificate["triangle_certificate"] = triangle_certificate()
    serialized = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.check_certificate:
        loaded = json.loads(args.check_certificate.read_text(encoding="utf-8"))
        require(loaded == json.loads(serialized), "saved certificate differs from fresh exact reconstruction")
        passed("saved_certificate.exact_reconstruction_match", file=str(args.check_certificate))
    cert_sha = hashlib.sha256(serialized.encode()).hexdigest()
    if args.certificate_out:
        args.certificate_out.write_text(serialized, encoding="utf-8")
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report = {"verdict": "PASS: the checked certificates and finite inputs for Lemmas 5-6",
              "scope": "Universal proofs are in audit.md; zero exclusion remains an assumed premise.",
              "head": HEAD, "user_main_base": MAIN_BASE,
              "utc_execution_time": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "platform": platform.platform(), "optimized": sys.flags.optimize,
              "verify_py_sha256": source_sha, "certificate_sha256": cert_sha,
              "checks_passed": len(CHECKS), "checks": CHECKS,
              "not_run_or_not_claimed": ["predecessor verify.py or DRUP replay", "PR717/PR968 theorem audit",
                                         "main checkout or merge validation", "P111/P104/P110 extensions",
                                         "complete multiplication theorem", "independent human review"]}
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ALL PASS: " + str(len(CHECKS)) + " named checks; certificate SHA256 " + cert_sha, flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, ValueError, KeyError, IndexError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
