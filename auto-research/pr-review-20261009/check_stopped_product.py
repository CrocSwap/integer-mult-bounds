#!/usr/bin/env python3
"""Independent exact controls for PR104's written factorization and wrapper.

Maintainer review with OpenAI Codex assistance, Apache-2.0.
Requires SymPy. These finite controls are not a proof of the all-size tape cost.
No implementation or certificate code from the submitted PR is imported.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

from itertools import product
import json
import random
import sympy as s


def reversal(n):
    return s.eye(n)[:, ::-1]


def factor_controls():
    rng = random.Random(104)
    tested = 0
    omitted_shear_rejected = 0
    for m in range(2, 6):
        for r in range(1, m):
            while True:
                basis = s.Matrix(m, m, lambda i, j: rng.randint(-3, 3))
                if basis.det() == 0:
                    continue
                P = basis*s.diag(*([1]*r+[0]*(m-r)))*basis.inv()
                if all(P[:i, :i].det() != 0 for i in range(1, r+1)):
                    break
            assert P*P == P and P.rank() == r
            # Independent leading-pivot elimination: A lower, B upper.
            Z, A, B = P.copy(), s.eye(m), s.eye(m)
            for i in range(r):
                scale = s.eye(m)
                scale[i, i] = 1/Z[i, i]
                Z, A = scale*Z, scale*A
                lower = s.eye(m)
                for k in range(i+1, m):
                    lower[k, i] = -Z[k, i]
                Z, A = lower*Z, lower*A
                upper = s.eye(m)
                for j in range(i+1, m):
                    upper[i, j] = -Z[i, j]
                Z, B = Z*upper, B*upper
            assert Z == s.diag(*([1]*r+[0]*(m-r)))
            C, I = reversal(m), s.eye(m)
            L, R = A, C*B*C
            assert L.is_lower and R.is_lower
            E, F = I[:, :r], C[:, :r]
            assert L*P*C*R == E*F.T
            Q = s.diag(L, R.inv())
            D = (I-P).row_join(P*C).col_join((C*P).row_join(C*(I-P)*C))
            g = Q*D*Q.inv()
            delta = g-s.eye(2*m)
            AA = delta[:r, :m]
            BB = delta[m:, m:]*F
            assert delta == E.col_join(BB)*AA.row_join(F.T)
            assert AA*E+F.T*BB == -2*s.eye(r)
            K = -(BB+F)*E.T+F*AA*(I-E*E.T)
            assert K*E == -BB-F and F.T*K == AA+E.T
            for f in (1, 2, 3):
                k = s.kronecker_product
                n, cf, eye = m*f, reversal(f), s.eye(f)
                lifted = k(I-P, eye).row_join(k(P*C, cf)).col_join(
                    k(C*P, cf).row_join(k(C*(I-P)*C, eye)))
                q = s.diag(k(L, eye), k(R.inv(), eye))
                shear = s.eye(2*n)
                shear[n:, :n] = k(K, cf)
                normalized = shear*q*lifted*q.inv()*shear.inv()
                expected = s.eye(2*n)
                for j in range(r*f):
                    a, b = j, 2*n-1-j
                    expected[a, a] = expected[b, b] = 0
                    expected[a, b] = expected[b, a] = 1
                assert normalized == expected, (m, r, f)
                omitted_shear_rejected += int(q*lifted*q.inv() != expected)
                tested += 1
    assert omitted_shear_rejected > 0
    return dict(exact_rational_factorizations=tested,
                omitted_cross_shear_changes_map=omitted_shear_rejected)


def wrapper_controls():
    count = 0
    for modulus in (3, 9):
        for n in (1, 2):
            for values in product(range(modulus), repeat=2*n):
                H, D = list(values[:n]), list(values[n:])
                D = [(d-h) % modulus for h, d in zip(H, D)]
                H, D = D[::-1], H[::-1]
                D = [(d+h) % modulus for h, d in zip(H, D)]
                H, D = D[::-1], H[::-1]
                D = [(h-d) % modulus for h, d in zip(H, D)]
                assert H == list(values[n:]) and D == list(values[:n])
                count += 1
    return dict(complete_modular_wrapper_addresses=count)


if __name__ == '__main__':
    print(json.dumps(dict(**factor_controls(), **wrapper_controls(),
                         scope='Finite exact algebra controls only; written recurrence and tape arguments reviewed separately'), indent=2))
