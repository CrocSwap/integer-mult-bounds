"""Exact rational recovery of the ten primary-prime data witnesses.

The ordered pivots are James Chang's PR34 reversed geometry. PR40/42 already
used a second prime to resolve these same finite-field failures. Here a
separate Fraction elimination certifies every ordered pivot and every
required zero, with no modular inference for the recovered pairs.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache


@lru_cache(None)
def recover(pairs):
    a,b,d=23,25,47
    pivots=[2*a]+[i+a+1 for i in range(1,a-1)]
    pivots += [2*a-i for i in range(a-1,a+5)]
    pivots += [i-a-3 for i in range(a+5,2*a-1)]+[1,0]
    assert len(set(pivots))==d
    records=[]
    for pair in pairs:
        aa,bb,cc,u,v,w,failed_row=pair
        S,T={aa,bb,cc},{u,v,w}
        x=[Q(3*(a+1),2*(3*(a+1)-10)) if i in S else -Q(a+1,5) for i in range(a)]
        y=[Q(3*(b+1),2*(3*(b+1)-10)) if i in T else -Q(b+1,5) for i in range(b)]
        # Exact PR34 controlled-permutation restrictions, including the
        # physical offset of the last-d column bank.
        row_a=list(range(a))+[a-1]+list(range(a))
        col_a=list(range(a))+[0]+list(range(a))
        matrix=[[Q(-1)+(x[row_a[i]] if row_a[i]==col_a[j] else 0)
                 +(y[i%b] if i%b==(a*b-d+j)%b else 0)
                 for j in range(d)] for i in range(d)]
        available=set(range(d)); values=[]; zero_checks=0
        for i,c in enumerate(pivots):
            assert c in available
            value=matrix[i][c]
            if not value:raise ValueError('Rational data pivot is zero')
            for j in available:
                if j>c:
                    if matrix[i][j]:raise ValueError('Ordered data zero failed')
                    zero_checks+=1
            values.append(str(value));available.remove(c)
            for r in range(i+1,d):
                ratio=matrix[r][c]/value
                if ratio:
                    for j in available:
                        if matrix[i][j]:matrix[r][j]-=ratio*matrix[i][j]
                    matrix[r][c]=Q(0)
        records.append(dict(pair=list(pair[:6]),primary_failed_row=failed_row,
                            pivots=values,ordered_zero_checks=zero_checks))
    return records
