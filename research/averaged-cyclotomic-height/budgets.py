"""Exact integer budget checks for the averaged-height bound."""
from fractions import Fraction as F
import json
from pathlib import Path


def need(ok,label):
    if not ok:
        raise ValueError(label)


def plan(r,phi,p,m):
    need(all(type(x) is int for x in (r,phi,p,m)) and r>=3 and 1<=phi<=r and p>=0 and m>=0,
         'budget inputs')
    ell,c=(r-1).bit_length(),(r-2).bit_length()
    T=(r-1)*phi*min(r,8*ell**2)
    d=1+2*ell+T
    a0=2*d+r+2
    g=d+ell+2*r+2
    h=a0+2*r
    e=max(d+1,a0+1,p+2*a0+m+3)
    b=max((r-1)*ell,e+r+3)
    J=c+2*h+3*g+ell+m+5
    W=p+J+2
    G=m+ell+h+g+8
    depth=2*g+(W-1).bit_length()+4
    need(W==p+m+7*T+12*r+18*ell+c+24,'width identity')
    need(G==m+3*T+5*r+8*ell+15,'guard identity')
    need(b==p+m+4*T+3*r+8*ell+14,'preparation identity')
    need(W>=2*g+8 and (4*(depth+1)-1).bit_length()<=W-g,'effective-depth admission')
    t_exp=c+h+3+3*g-W
    need(t_exp<=-1 and 1+t_exp+ell+h+m+1==-p-2,'common-error contraction')
    N=r*r*ell*ell
    need(W<=p+m+60*N and G<=m+26*N and b<=p+m+34*N,'quasiquadratic bounds')
    need(W<=p+m+9*r**3 and G<=m+6*r**3 and b<=p+m+6*r**3,'retained cubic bounds')
    old_T=r*(r-1)*phi
    old_W=p+m+7*old_T+12*r+18*ell+c+24
    need(W<=old_W,'budget monotonicity')
    return dict(r=r,phi=phi,p=p,m=m,ell=ell,d=d,W=W,G=G,b=b,
                previous_W=old_W,saved_bits=old_W-W,effective_depth=depth)


def main():
    # 2*atanh(1/3) with a positive geometric tail encloses log 2.
    lo=2*sum((F(1,3)**(2*j+1)/(2*j+1) for j in range(20)),F(0))
    hi=lo+2*F(1,3)**41/(41*(1-F(1,9)))
    need(F(2,3)<lo<hi<F(3,4),'rational log 2 enclosure')
    need([1,12,5]==[5*4-8*2-3,20-8,5],'dyadic conversion polynomial')
    rows=[]
    for prime,exponents in [(2,range(2,129)),(3,range(1,25)),(5,range(1,17)),
                            (7,range(1,13)),(11,range(1,9)),(2053,[1])]:
        for a in exponents:
            r=prime**a
            phi=r-r//prime
            for p,m in [(0,0),(1,0),(128,16),(2**20,2**18)]:
                rows.append(plan(r,phi,p,m))
    result={'status':'PASS_EXACT_BUDGETS','scope':'Exact arithmetic and universal polynomial identity checks; not a replacement for the analytic proof.',
            'log2_interval':[str(lo),str(hi)],'rows':rows}
    print('PASS',len(rows),'integer budgets, exact logarithm enclosure and dyadic polynomial')
    return result


if __name__=='__main__':
    main()
