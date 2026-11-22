"""Execute all 16 canonical low classes and their 27 genuine lifts at modulus nine."""

from collections import Counter
from fractions import Fraction
from io import BytesIO
from math import prod
from pathlib import Path
import sys

from direct_exact import exact_projector


def main(package):
    sys.path.insert(0,str(package))
    from upstream import install
    install()
    from binary_receiver import Receiver
    from check_module_atoms import expected_packet,payload
    from factored_frames import Frame
    from quotient_route import canonical_lows,representative
    from five_exchange import corner_exchanges
    class Measured(Receiver):
        def weighted(self,*args,**kwargs):
            self.calls+=1
            return super().weighted(*args,**kwargs)
    n=2;mod=9
    machine=Measured(n,(1,2,0,0),direct=False)
    machine.calls=0
    word=(("add",0,1,1),("add",1,0,Fraction(1,2)),("scale",0,-1))
    frame=Frame(2,word,(1,))
    uu,vv=exact_projector(n,word,1)
    def residue(x):
        return x.numerator*pow(x.denominator,-1,mod)%mod
    ru,rv=list(map(residue,uu)),list(map(residue,vv))
    heights=machine.high
    assert heights==27 and machine.low==16
    maps={};cases=Counter();nontrivial=set()
    for low_no,low in enumerate(canonical_lows(n)):
        indexes=set()
        for high in range(heights):
            # Chart lifts and an independent two-by-two inverse give true factors.
            (a,b),(c,d)=representative(low,high,n,2)
            invdet=pow((a*d-b*c)%mod,-1,mod)
            u=((a*ru[0]+b*ru[1])%mod,(c*ru[0]+d*ru[1])%mod)
            v=(invdet*(d*rv[0]-c*rv[1])%mod,invdet*(-b*rv[0]+a*rv[1])%mod)
            assert sum(i*j for i,j in zip(u,v))%mod==1
            pivot=next(i for i in range(n) if u[i]*v[i]%3)
            size=2*len(corner_exchanges(u,v,pivot))+1
            indexes.add(size);maps[low_no,high]=(u,v)
            nontrivial.add((u,v))
        assert len(indexes)==1
        cases[next(iter(indexes))]+=1
    dims=(16,27,9,9,9,9)
    def img(low,high,h0,h1,t0,t1):
        u,v=maps[low,high]
        a,b=2,5
        delta=v[0]*(t0-5*h0)+v[1]*(t1-2*h1)
        return low,high,(h0+a*u[0]*delta)%9,(h1+b*u[1]*delta)%9,(t0-u[0]*delta)%9,(t1-u[1]*delta)%9
    raw=payload(prod(dims));target=BytesIO()
    with machine.storage():
        machine.serve_line(BytesIO(raw),target,frame,1,1,1,1,4,lambda old,i:(2,5)[i])
    assert machine.calls==sum(k*v for k,v in cases.items())
    assert target.getvalue()==expected_packet(raw,dims,img)
    print("genuine lows",16,"high representatives",16*27,"distinct paired factors",len(nontrivial))
    print("records",prod(dims),"children",machine.calls,"class count",dict(cases),"arena",machine.last_storage)


if __name__ == "__main__":
    from upstream import HERE
    main(HERE)
