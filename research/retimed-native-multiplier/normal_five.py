"""Use both public covered-line paths and independently decode every arbitrary record."""

from fractions import Fraction
from io import BytesIO
from itertools import product
from math import prod
from pathlib import Path
import sys


def main(package):
    sys.path.insert(0,str(package))
    from upstream import install
    install()
    from binary_receiver import Receiver
    from direct_body import same_order_line as direct_impl
    from factored_frames import Frame
    from five_exchange import same_order_line as five, direct_line as direct_five
    from direct_body import direct_line as direct_bound
    from quotient_route import canonical_lows
    from receiver import same_order_line as covered_impl
    from check_module_atoms import payload,expected_packet
    from ternary_frames import identity
    assert direct_impl is covered_impl
    assert direct_impl is five
    assert direct_bound is direct_five
    class Counted(Receiver):
        def weighted(self,*args,**kw):
            self.paid+=1
            return super().weighted(*args,**kw)
    n=2;f=1;unused=1;older=2;gap=2;suffix=4
    frame=Frame(n,(("add",0,1,Fraction(1)),("scale",1,Fraction(-1))), (1,))
    def weight(old,j):
        return (1,2)[(old+j)%2]
    for direct in (True,False):
        core=Counted(n,(1,1,0,0),direct=direct)
        core.paid=0
        lows=(tuple(x for row in identity(n) for x in row),) if direct else tuple(canonical_lows(n))
        maps=[]
        for flat in lows:
            low=tuple(flat[i:i+n] for i in range(0,n*n,n))
            u,v=frame.covered_line(low,1)
            maps.append((u,v))
        dims=(len(lows),older,3,3,gap,3,3)
        raw=payload(prod(dims)); source=BytesIO(raw); target=BytesIO()
        with core.storage():
            core.serve_line(source,target,frame,f,unused,older,gap,suffix,weight)
        def oracle(index,old,h0,h1,g,t0,t1):
            u,v=maps[index];a,b=weight(old,0),weight(old,1)
            d=(v[0]*(t0-a*h0)+v[1]*(t1-b*h1))%3
            return (index,old,(h0+a*u[0]*d)%3,(h1+b*u[1]*d)%3,g,
                    (t0-u[0]*d)%3,(t1-u[1]*d)%3)
        assert target.getvalue()==expected_packet(raw,dims,oracle)
        assert core.paid == (1 if direct else 32)
        print("direct" if direct else "quotient","lows",len(lows),"true children",core.paid,
              "records",prod(dims),"physical statistics",core.last_storage)


if __name__ == "__main__":
    from upstream import HERE
    main(HERE)
