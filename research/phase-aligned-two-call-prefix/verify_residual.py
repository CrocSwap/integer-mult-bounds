#!/usr/bin/env python3
"""Exact residual and projector transport for the repaired two-call prefix.

This verifier uses only the Python standard library. Entries are pairs of
fractions representing Gaussian rationals; no floating point or source checker
is used. Matrix words act right-to-left on e_x, x=x0+2*x1+4*x2.

Provenance: C, U=CNOT(0->2), V=SWAP(0,1), and the original two-image prefix
are from CrocSwap/integer-mult-bounds PR #4688, exact head
264c4b3cb13c82d171de352ecf60486dfb8d2bd4, package
research/complex-two-image-hook-prefix. The repair P=S_all U S_all,
Q=S_all V S_all, and the residual identity below are this contribution.

For EACH base letter A let A_f=A tensor ... tensor A (f factors). Define
F_f=C0_f (P_f+2 Q_f) C0_f. In particular F_f is NOT F_1 tensor ... tensor F_1.
We verify the two distinct word equalities
    J W C0 P C0 = M C2,       J W C0 Q C0 = K a.
Tensor functoriality applies separately to these two products. Linearity then
gives, for every positive integer f, with the SAME coefficient 2,
    J_f W_f F_f = M_f C2_f + 2 K_f a_f.
This is an exact target-plus-one-call residual identity, not a 5-in-14 program.

All scalar phases are attached to base letters before tensorization. Thus
(-A)_f=(-1)^f A_f. The projector sign map below retains this parity explicitly.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F
import json
from pathlib import Path


def q(real=0, imag=0):
    return (F(real), F(imag))


ZERO, ONE, I = q(), q(1), q(0, 1)
I_POWERS = (ONE, I, q(-1), q(0, -1))


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def scale(c, a):
    return tuple(tuple(mul(c, v) for v in row) for row in a)


def plus(a, b):
    return tuple(tuple(add(x, y) for x, y in zip(ar, br)) for ar, br in zip(a, b))


def mm(a, b):
    n = len(a)
    out = [[ZERO for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for k in range(n):
            if a[r][k] == ZERO:
                continue
            for c in range(n):
                if b[k][c] != ZERO:
                    out[r][c] = add(out[r][c], mul(a[r][k], b[k][c]))
    return tuple(tuple(row) for row in out)


def word(*letters):
    out = ident(len(letters[0]))
    for letter in letters:
        out = mm(out, letter)
    return out


def ident(n=8):
    return tuple(tuple(ONE if r == c else ZERO for c in range(n)) for r in range(n))


def adjoint(a):
    return tuple(tuple((a[c][r][0], -a[c][r][1]) for c in range(len(a))) for r in range(len(a)))


def monomial(permutation, phases=None):
    if phases is None:
        phases = [0] * len(permutation)
    n = len(permutation)
    require(sorted(permutation) == list(range(n)), "invalid monomial permutation")
    return tuple(tuple(I_POWERS[phases[c] % 4] if r == permutation[c] else ZERO for c in range(n)) for r in range(n))


def pauli(x, z):
    """Hermitian convention i^popcount(x&z) X^x Z^z, not bare X^x Z^z."""
    return monomial([j ^ x for j in range(8)], [(x & z).bit_count() + 2 * (j & z).bit_count() for j in range(8)])


def c_letter(bit):
    return plus(scale(q(F(1, 2), F(1, 2)), ident()), scale(q(F(1, 2), F(-1, 2)), pauli(1 << bit, 0)))


def s_letter(mask):
    """Product of S gates on the selected bits, with phase sum mod4."""
    return monomial(list(range(8)), [(j & mask).bit_count() for j in range(8)])


def conj(a, b):
    return word(a, b, adjoint(a))


def describe_pauli(a):
    hits = []
    for x in range(8):
        for z in range(8):
            for exponent in range(4):
                if a == scale(I_POWERS[exponent], pauli(x, z)):
                    hits.append({"label_x_or_8z": x | (8 * z), "phase_i_exponent": exponent})
    require(len(hits) == 1, "ambiguous or missing Hermitian Pauli label: " + str(hits))
    return hits[0]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify():
    e = ident()
    c0, c1, c2 = (c_letter(j) for j in range(3))
    sall = s_letter(7)
    u = monomial([0, 5, 2, 7, 4, 1, 6, 3])
    v = monomial([0, 2, 1, 3, 4, 6, 5, 7])
    p, qword = word(sall, u, sall), word(sall, v, sall)
    zall = pauli(0, 7)
    require(qword == word(zall, v), "Q=Z_all V")
    # Normalize each paid and free base letter independently.
    for name, a in (("C0", c0), ("C1", c1), ("C2", c2), ("S_all", sall), ("U", u), ("V", v), ("P", p), ("Q", qword)):
        require(word(a, adjoint(a)) == e, name + " unitarity")
    for bit, c in enumerate((c0, c1, c2)):
        require(word(c, c) == pauli(1 << bit, 0), "C_bit^2=X_bit")

    k = word(c0, c1, c2)
    a, b = pauli(1, 3), pauli(4, 4)  # a=Y0 Z1, b=Y2.
    w = pauli(0, 5)                  # W=Z0 Z2.
    jword = word(pauli(0, 2), v, c2) # J=Z1 V C2: exactly one paid call.
    m_perm = [2, 0, 3, 1, 4, 6, 5, 7]
    m_phases = [0, 0, 2, 2, 1, 3, 3, 1]
    m = monomial(m_perm, m_phases)
    u20 = monomial([0, 1, 2, 3, 5, 4, 7, 6])
    cz02 = monomial(list(range(8)), [2 * (x & 1) * ((x >> 2) & 1) for x in range(8)])
    s_parity02 = monomial(list(range(8)), [((x & 5).bit_count() % 2) for x in range(8)])
    require(cz02 == word(s_letter(1), s_letter(4), adjoint(s_parity02)), "CZ uses allowed S of parity")
    require(m == word(pauli(2, 0), v, u20, pauli(0, 2), s_letter(4), cz02), "M free-letter factorization")

    branch_p, branch_q = word(c0, p, c0), word(c0, qword, c0)
    require(word(jword, w, branch_p) == word(m, c2), "P branch target residual")
    require(word(jword, w, branch_q) == word(k, a), "Q branch target term")
    prefix = plus(branch_p, scale(q(2), branch_q))
    require(word(jword, w, prefix) == plus(word(m, c2), scale(q(2), word(k, a))), "combined identity")

    middle_a, middle_b = pauli(0, 3), pauli(4, 4)
    r = word(adjoint(p), qword)
    require(word(r, r, r, r) == e, "R has order dividing4")
    require(word(r, r) != e, "R has exact order4")
    require(word(r, middle_a) == word(middle_a, r), "R commutes A")
    require(word(r, middle_b) == word(middle_b, r), "R commutes B")
    require(conj(adjoint(c0), middle_a) == a, "input a label")
    require(conj(adjoint(c0), middle_b) == b, "input b label")
    out_a, out_b = conj(word(c0, p), middle_a), conj(word(c0, p), middle_b)
    require(out_a == scale(q(-1), a) and out_b == scale(q(-1), b), "base output signs")
    require(word(prefix, a) == word(out_a, prefix), "prefix a transport")
    require(word(prefix, b) == word(out_b, prefix), "prefix b transport")
    require(conj(jword, a) == conj(k, a) and conj(jword, b) == conj(k, b), "one-call projector bridge")
    lword = word(adjoint(jword), k)
    gword = word(w, branch_p)
    require(lword == word(v, pauli(0, 2), c0, c1), "residual L factorization")
    require(word(lword, lword) == scale(q(-1), a), "L^2=-a at base width")
    require(word(gword, gword) == scale(q(-1), e), "G^2=-I at base width")
    require(word(w, branch_q) == word(a, lword), "Q branch with W")
    for generator in (a, b):
        require(word(lword, generator) == word(generator, lword), "L centralizes input sectors")
        require(word(w, prefix, generator) == word(generator, w, prefix), "WF centralizes input sectors")
    projectors = []
    for alpha in (1, -1):
        for beta in (1, -1):
            ep = scale(q(F(1, 4)), word(plus(e, scale(q(alpha), a)), plus(e, scale(q(beta), b))))
            ep_out = scale(q(F(1, 4)), word(plus(e, scale(q(-alpha), a)), plus(e, scale(q(-beta), b))))
            require(word(ep, ep) == ep, "projector idempotence")
            require(word(prefix, ep) == word(ep_out, prefix), "base sector sign flip")
            projectors.append(ep)
    require(plus(plus(projectors[0], projectors[1]), plus(projectors[2], projectors[3])) == e, "complete four-sector partition")
    for i in range(4):
        for j in range(i):
            require(word(projectors[i], projectors[j]) == scale(ZERO, e), "orthogonal sectors")

    # Meaningful negative controls: one wrong free phase and one wrong mixer.
    wrong_phases = m_phases.copy()
    wrong_phases[0] = 1
    require(word(jword, w, branch_p) != word(monomial(m_perm, wrong_phases), c2), "wrong M phase rejected")
    require(word(jword, w, prefix) != plus(word(m, c2), word(k, a)), "wrong mixing coefficient rejected")
    return {
        "status": "PASS",
        "arithmetic": "exact Gaussian rationals; Python stdlib Fraction pairs",
        "branch_identities": ["J W C0 P C0 = M C2", "J W C0 Q C0 = K a"],
        "all_width_identity": "J_f W_f F_f = M_f C2_f + 2 K_f a_f",
        "all_width_reason": "Tensorize each branch word separately, then add with coefficient2; never tensorize the sum F_1.",
        "M_permutation": m_perm,
        "M_phase_i_exponents": m_phases,
        "M_free_factorization": "X1 SWAP01 CNOT(2->0) Z1 S2 CZ02",
        "input_generators": [describe_pauli(a), describe_pauli(b)],
        "output_generators_at_base_width": [describe_pauli(out_a), describe_pauli(out_b)],
        "target_generators_at_base_width": [describe_pauli(conj(k, a)), describe_pauli(conj(k, b))],
        "all_width_projectors": "e(alpha,beta)=(I+alpha*a_f)(I+beta*b_f)/4; F_f e(alpha,beta)=e(epsilon*alpha,epsilon*beta)F_f, epsilon=(-1)^f",
        "negative_controls": ["wrong M phase rejected", "wrong coefficient2 rejected"],
        "limitation": "Exact residual and sector transport only; no independent-array 5-in-14 continuation or improved kappa is claimed.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Optional JSON receipt path; otherwise print only")
    args = parser.parse_args()
    result = verify()
    data = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.write_text(data)
    print(data, end="")


if __name__ == "__main__":
    main()
