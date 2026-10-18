"""Exact cubic budgets combining the retained partial-inverse and stride bounds."""
from fractions import Fraction as F
from math import gcd
from common import need
from uniform import ceil_log2


def plan(r,phi,p,m):
    need(all(type(v) is int for v in (r,phi,p,m)) and r>=3 and 1<=phi<=r and p>=0 and m>=0,
         'integer cubic budget inputs')
    ell,c=ceil_log2(r),ceil_log2(r-1)
    d=1+2*ell+r*(r-1)*phi
    a0=2*d+r+2
    g=d+ell+2*r+2
    h=a0+2*r
    e=max(d+1,a0+1,p+2*a0+m+3)
    factor_bits=max((r-1)*ell,e+r+3)
    J=c+2*h+3*g+ell+m+5
    W=p+J+2
    guard=m+ell+h+g+8
    depth=2*g+(W-1).bit_length()+4
    need(W>=2*g+8 and ceil_log2(4*(depth+1))<=W-g,'uniform stride admission')
    # n<=2^c, 7<=2^3 and r*2^(h+m)+1<=2^(ell+h+m+1).
    # These exact exponent bounds avoid constructing enormous fractions.
    t_exponent=c+h+3+3*g-W
    need(r-1<=1<<c and r<=1<<ell and t_exponent<=-1,'common-error contraction')
    error_exponent=1+t_exponent+ell+h+m+1
    need(error_exponent==J-W==-p-2,'common-subproduct execution bound')
    error=F(1,1<<(p+2))
    need(W<=p+m+9*r**3 and guard<=m+6*r**3 and factor_bits<=p+m+6*r**3,
         'cubic precision, preparation and guard')
    return dict(r=r,phi=phi,p=p,m=m,ell=ell,c=c,d=d,a0=a0,g=g,h=h,J=J,W=W,
                guard=guard,e=e,factor_bits=factor_bits,effective_depth=depth,t_exponent=t_exponent,execution_bound=error,
                complete_word_bound=p+2*m+16*r**3)


def main():
    rows=[]
    for r in [3,4,5,7,8,9,11,13,16,17,25,27,32,49,64,81,125,128]:
        phi=sum(gcd(r,j)==1 for j in range(1,r))
        for p in [0,1,32,128]:
            for m in [0,1,16]:
                record=plan(r,phi,p,m)
                # Keep compact integer budgets; every admission and exponent inequality
                # is checked exactly. The proof explains their universal
                # implication for the rational perturbation bound.
                rows.append({k:v for k,v in record.items() if k!='execution_bound'})
    # Coefficients in ascending powers of t=r-3, obtained by exact shifts
    # of the polynomial differences, rather than finite radix sampling.
    def shifted(coefficients):
        from math import comb
        return [sum(coefficients[j]*comb(j,i)*3**(j-i) for j in range(i,len(coefficients)))
                for i in range(len(coefficients))]
    width=shifted([-24,-31,7,2])
    guard=shifted([-15,-14,3,3])
    factor=shifted([-14,-11,4,2])
    need(width==[0,65,25,2] and guard==[51,85,30,3] and factor==[43,67,22,2],
         'cubic polynomial identities')
    need(all(v>=0 for v in width+guard+factor),'all-size nonnegative remainders')
    print('PASS cubic budget rows',len(rows),'identities 3',flush=True)
    return dict(rows=rows,working_width_remainder=width,integer_guard_remainder=guard,
                factor_preparation_remainder=factor)
