#!/usr/bin/env python3
"""Independent finite controls for the PR130/144 weighted compiler.

Apache-2.0. Maintainer review with OpenAI Codex assistance. No submitted
implementation is imported. Finite algebra controls, not an all-size proof.
Requires SymPy. Exercises prime-power rings, including nonzero nonunits.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
import json
from math import gcd
import random
import sympy as s


def check():
    rng = random.Random(144130)
    count = bad_omission = nonunit_entries = 0
    for modulus in (9,25,27):
        def red(A):
            return A.applyfunc(lambda x: int(x)%modulus)
        def inv(A):
            return red(A.adjugate()*pow(int(A.det()),-1,modulus))
        for m in range(2,6):
            I,C = s.eye(m),s.eye(m)[:,::-1]
            for rank in range(1,m+1):
                for repeat in range(2):
                    for attempt in range(10000):
                        B = s.Matrix(m,m,lambda i,j:rng.randrange(modulus))
                        if gcd(int(B.det()),modulus)!=1:
                            continue
                        P = red(B*s.diag(*([1]*rank+[0]*(m-rank)))*inv(B))
                        if all(gcd(int(P[:i,:i].det()),modulus)==1 for i in range(1,rank+1)):
                            break
                    else:
                        raise AssertionError('No generic test fixture')
                    units = [a for a in range(1,modulus) if gcd(a,modulus)==1]
                    A = s.diag(*(rng.choice(units) for i in range(m)))
                    D = (I-P).row_join(P*C).col_join((C*P).row_join(C*(I-P)*C))
                    weighted = red(s.diag(A,I)*D*s.diag(inv(A),I))
                    assert red(weighted*weighted) == s.eye(2*m)
                    nonunit_entries += sum(int(x)!=0 and gcd(int(x),modulus)!=1 for x in weighted)
                    # Leading elimination, retaining each unit pivot in the middle.
                    Z,L,Bright = red(A*P),I.copy(),I.copy()
                    for i in range(rank):
                        pivot_inv = pow(int(Z[i,i]),-1,modulus)
                        lower,upper = I.copy(),I.copy()
                        for k in range(i+1,m):
                            lower[k,i] = -int(Z[k,i])*pivot_inv
                        Z,L = red(lower*Z),red(lower*L)
                        for j in range(i+1,m):
                            upper[i,j] = -int(Z[i,j])*pivot_inv
                        Z,Bright = red(Z*upper),red(Bright*upper)
                    R = C*Bright*C
                    assert L.is_lower and R.is_lower
                    E,F = I[:,:rank],C[:,:rank]
                    piv = s.diag(*(Z[i,i] for i in range(rank)))
                    assert Z == E*piv*E.T
                    Q = s.diag(L,inv(R))
                    g = red(Q*weighted*inv(Q))
                    delta = red(g-s.eye(2*m))
                    AA = delta[:rank,:m]
                    BB = red(delta[m:,m:]*F*inv(piv))
                    assert delta == red(E.col_join(BB)*AA.row_join(piv*F.T))
                    assert red(AA*E+piv*F.T*BB) == red(-2*s.eye(rank))
                    K = red(-(BB+F*inv(piv))*E.T+F*inv(piv)*AA*(I-E*E.T))
                    S = s.eye(2*m)
                    S[m:,:m] = K
                    expected = (I-E*E.T).row_join(E*piv*F.T).col_join(
                        (F*inv(piv)*E.T).row_join(I-F*F.T))
                    assert red(S*g*inv(S)) == red(expected)
                    bad_omission += int(g!=red(expected))
                    count += 1
    assert count==84 and bad_omission>0 and nonunit_entries>0
    return dict(status='PASS', weighted_factorizations=count,
                moduli=[9,25,27], nonzero_nonunit_entries=nonunit_entries,
                omitted_cross_shear_changes_map=bad_omission,
                scope='Finite exact algebra controls; recurrence and tape cost require written proof')


if __name__=='__main__':
    print(json.dumps(check(),indent=2))
