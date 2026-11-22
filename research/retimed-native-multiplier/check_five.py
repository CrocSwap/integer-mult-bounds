"""Exercise all true tape records and compare them with dense weighted projectors."""

from contextlib import contextmanager
from collections import Counter
from io import BytesIO
from itertools import product
from math import prod
from pathlib import Path
from random import Random
import argparse
import sys


def main(package):
    sys.path.insert(0,str(package))
    from upstream import install
    install()
    from five_exchange import corner_exchanges, same_order_line
    from same_order_body import SameOrderBody
    from growing_binary import Weighted
    from module_atoms import component_widths
    from streaming_routes import cold_swap_tape
    from check_module_atoms import payload,expected_packet
    from ternary_leaf import select_pivot

    def weight(row,idx,mod=81):
        return (1,2,4,5,7,8)[(3*row+idx)%6]%mod

    # The signed rectangular test calls the source's true stopped weighted body.
    class LineCore(SameOrderBody,Weighted):
        def __init__(self,n,layout):
            super().__init__(n,layout,cold_swap_tape)
            self.stock=self.owners
            self.calls=0
        def weighted(self,*args,**kw):
            self.calls+=1
            # In these cases f<n. No fabricated data are supplied to a rank.
            assert kw["atoms"]<self.n
            return super().weighted(*args,**kw)

    cases=[
        # n, f, physical atom, high list, arbitrary prefix/gap
        (2,1,(1,1,0,0),[([1,0],[1,0])],2,2),
        (2,1,(1,1,0,0),[([0,1],[0,1])],2,2),
        (3,1,(1,1,0,0),[([0,1,1],[0,1,0])],2,2),
        (3,1,(1,1,0,0),[([1,1,2],[0,1,0])],2,2),
        (3,1,(1,1,0,0),[([1,1,2],[0,2,1])],2,2),
        (2,1,(1,2,0,0),[([1,0],[1,3]),([1,3],[1,3])],2,1),
        (2,1,(2,1,0,0),[([0,1],[2,1])],1,2),
        (3,2,(1,1,0,0),[([0,1,0],[0,1,1])],1,1),
        (2,1,(1,2,1,1),[([1,3],[1,3])],1,1),
    ]
    counts=Counter(); touched=0
    for n,f,layout,lines,older,gap in cases:
        core=LineCore(n,layout)
        q=core.modulus; A=core.atom; h=len(lines); repeat=2 if n==2 and older==2 and gap==2 else 1
        for u,v in lines: assert sum(a*b for a,b in zip(u,v))%q==1
        pivot=select_pivot(*lines[0])
        dims=(repeat,h*older)+(A,)*(n*f)+(gap,)+(A,)*(n*f)
        raw=payload(prod(dims)); src=BytesIO(raw); dst=BytesIO()
        same_order_line(core,src,dst,pivot=pivot,factors=lines.__getitem__,f=f,
                        unused=repeat,heights=h,older=older,gap=gap,suffix=4,weight=weight)
        sizes=[3**w for w in component_widths(layout)]
        split_cache={}
        def split(x):
            if x not in split_cache:
                y=x; pieces=[]
                for side in reversed(sizes):
                    y,r=divmod(y,side); pieces.append(r)
                split_cache[x]=pieces[::-1]
            return split_cache[x]
        def map_record(ext,combined,*args):
            high,old=divmod(combined,older);u,v=lines[high]
            front=list(args[:n*f]); end=list(args[n*f+1:]); mid=args[n*f]
            outfront=[0]*(n*f);outend=[0]*(n*f)
            for index,side in enumerate(sizes):
                for j in range(f):
                    slots=range(j,n*f,f)
                    a=[weight(old,slot,side) for slot in slots]
                    x=[split(front[slot])[index] for slot in slots]
                    y=[split(end[slot])[index] for slot in slots]
                    d=sum(v_i*(t-pow(k,-1,side)*z) for v_i,t,k,z in zip(v,y,a,x))%side
                    for i,slot in enumerate(slots):
                        outfront[slot]=outfront[slot]*side+(x[i]+a[i]*u[i]*d)%side
                        outend[slot]=outend[slot]*side+(y[i]-u[i]*d)%side
            return (ext,combined,*outfront,mid,*outend)
        assert dst.getvalue()==expected_packet(raw,dims,map_record)
        counts[core.calls]+=1; touched+=prod(dims)
        print("physical",n,f,layout,"highs",h,"children",core.calls,"records",prod(dims),flush=True)

    # Independent matrices use all selector cases at multiple moduli and arbitrary weights.
    rng=Random(2918); checked=0
    for n,mod in product((2,3,4,8,17),(3,9,27,81)):
        for repetition in range(100):
            while True:
                u=[rng.randrange(mod) for i in range(n)]
                v=[rng.randrange(mod) for i in range(n)]
                dot=sum(x*y for x,y in zip(u,v))
                if dot%3: break
            v=[x*pow(dot,-1,mod)%mod for x in v]
            a=[rng.choice([x for x in range(mod) if x%3]) for _ in u]
            piv=select_pivot(u,v)
            pairs=corner_exchanges(u,v,piv)
            z=[x*y%mod for x,y in zip(a,u)]+[-x%mod for x in u]
            w=[pow(x,-1,mod)*y%mod for x,y in zip(a,v)]+[-x%mod for x in v]
            target=[rng.randrange(mod) for _ in z]
            ans=[(x-y*sum(s*t for s,t in zip(w,target)))%mod for x,y in zip(target,z)]
            x=list(target); undo=[]
            def exchange(l,r):
                r+=n; unit=a[l]; reciprocal=pow(unit,-1,mod)
                for vec in (x,z):
                    vec[l],vec[r]=unit*vec[r]%mod,reciprocal*vec[l]%mod
                w[l],w[r]=reciprocal*w[r]%mod,unit*w[l]%mod
            for l,r in pairs:
                exchange(l,r)
            def add(don,dst,k):
                x[dst]=(x[dst]+k*x[don])%mod
                z[dst]=(z[dst]+k*z[don])%mod
                w[don]=(w[don]-k*w[dst])%mod
                undo.append((don,dst,-k))
            for i in range(1,2*n-1):
                add(0,i,-z[i]*pow(z[0],-1,mod))
            last=2*n-1
            for i in range(1,last):
                add(i,last,w[i]*pow(w[last],-1,mod))
            add(0,last,(pow(w[last],-1,mod)-z[last])*pow(z[0],-1,mod))
            assert z[0]*w[0]%mod==1 and z[-1]*w[-1]%mod==1 and not any(w[1:-1]+z[1:-1])
            k=-z[0]*w[last]%mod
            x[0],x[-1]=k*x[-1]%mod,pow(k,-1,mod)*x[0]%mod
            for c,d,y in reversed(undo): x[d]=(x[d]+y*x[c])%mod
            for l,r in reversed(pairs):
                exchange(l,r)
            assert x==ans and 2*len(pairs)+1<=5
            checked+=1
    print("physical cells",touched,"call counts",dict(counts),"independent modular vectors",checked)


if __name__ == "__main__":
    from upstream import HERE
    main(HERE)
