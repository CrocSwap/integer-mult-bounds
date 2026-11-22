"""Count corner schedules on every actual low quotient for ranks two and three."""
from collections import Counter
from fractions import Fraction
from itertools import product
from math import prod
from pathlib import Path
import sys


def inverse(matrix, n):
    a = [list(matrix[i*n:(i+1)*n]) + [int(i==j) for j in range(n)] for i in range(n)]
    for j in range(n):
        k = next(k for k in range(j,n) if a[k][j])
        a[j],a[k] = a[k],a[j]
        q = pow(a[j][j],-1,3)
        a[j] = [q*x%3 for x in a[j]]
        for k in range(n):
            if k==j: continue
            q=a[k][j]
            a[k]=[(x-q*y)%3 for x,y in zip(a[k],a[j])]
    return tuple(x for row in a for x in row[n:])


def apply(matrix, vec):
    n = len(vec)
    return tuple(sum(a*v for a,v in zip(matrix[k*n:(k+1)*n],vec))%3 for k in range(n))


def run(runtime):
    sys.path.insert(0,str(Path(runtime).resolve()))
    from upstream import install
    install()
    from quotient_route import canonical_lows
    from five_exchange import corner_exchanges
    for n in (2,3,4):
        vectors=tuple(product(range(3),repeat=n))
        pairs=[(u,v) for u in vectors for v in vectors if sum(x*y for x,y in zip(u,v))%3==1]
        if n==4: pairs=[pairs[k] for k in (0,1,53,len(pairs)-1)]
        lows=[]
        for matrix in canonical_lows(n):
            inv=inverse(matrix,n)
            inv_t=tuple(inv[j*n+i] for i in range(n) for j in range(n))
            lows.append((matrix,inv_t))
        assert len(lows)==prod(3**j-1 for j in range(1,n+1))
        worst=0
        best=5
        for u,v in pairs:
            stats=Counter()
            for g,gt in lows:
                x,y=apply(g,u),apply(gt,v)
                piv=next(i for i in range(n) if x[i] and y[i])
                swaps=corner_exchanges(x,y,piv)
                z=list(x)+[(-a)%3 for a in x]
                w=list(y)+[(-a)%3 for a in y]
                for i,j in swaps:
                    j+=n
                    z[i],z[j]=z[j],z[i]
                    w[i],w[j]=w[j],w[i]
                assert z[0] and w[-1]
                stats["child"] += 1 + 2*len(swaps)
                stats["A"]+=bool(x[0])
                stats["B"]+=bool(y[-1])
                stats["both"]+=bool(x[0] and y[-1])
                stats["last_basis"]+=sum(c!=0 for c in x)==1 and bool(x[-1])
                stats["first_dual_basis"]+=sum(c!=0 for c in y)==1 and bool(y[0])
            Q=len(lows)
            a=Fraction(2*3**(n-1),3**n-1)
            assert stats["A"]==stats["B"]==a*Q and stats["both"]==Fraction(2,3)*a*Q
            assert stats["last_basis"]==stats["first_dual_basis"]==Fraction(2*Q,3**n-1)
            mean=Fraction(stats["child"],Q)
            assert mean<=Fraction(7,3)+Fraction(16,3*(3**n-1))
            worst=max(worst,mean)
            best=min(best,mean)
        print("rank",n,"low rows",len(lows),"native (u,v) pairs",len(pairs),"mean range",best,worst,flush=True)


if __name__ == "__main__":
    from upstream import HERE
    run(HERE)
