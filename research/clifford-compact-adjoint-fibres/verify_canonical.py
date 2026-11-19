"""Verify the spherical inverse and literal stabilizer transition amplitudes."""
from fractions import Fraction as F
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from adjoint import IDENTITY,Q,conjugate,power
from canonical import COUNTS,ORDER,apply,coefficient,distance,point_set,profile,radial_matrix,transition
from verify_adjoint import add,literal,target


def reference(S,p,r,c,L,R):
    left,l=literal(L)
    mid,m=literal(S)
    right,b=literal(R)
    total=(0,0)
    x,z=divmod(p,16)
    for row,values in enumerate(left):
        for col,vector in enumerate(right):
            sign=2*(((row^x) & z).bit_count()%2)
            val=Q.multiply_i(mid[row^x][col],sign)
            total=add(total,Q.multiply(conjugate(values[r]),Q.multiply(val,vector[c])))
    return tuple(F(v,1 << (l+m+b-6)) for v in total)


def main():
    h=profile()
    rhs=[F(1,4**13)*F(-1,64)**j for j in range(5)]
    K=radial_matrix()
    Q.need(all(sum(a*b for a,b in zip(row,h,strict=True))==v for row,v in zip(K,rhs,strict=True)),
           "Five exact normal equations")
    Q.need(all(COUNTS[i]*K[i][j]==COUNTS[j]*K[j][i] for i in range(5) for j in range(5)),
           "Weighted adjointness")
    projected=16*(ORDER//sum(COUNTS))*sum(n*x*y for n,x,y in zip(COUNTS,rhs,h,strict=True))
    Q.need(projected==F(478566778595,5856573836677349376) and 0<projected<1,"Projection norm")
    Q.need(all(h) and (ORDER//sum(COUNTS))*sum(n*(16<<j) for j,n in enumerate(COUNTS))
           ==8338459852800,"Exact support of the full canonical inverse")
    maps=[IDENTITY,target([1,33,16]),target([7,29,63,91]),target([17,34,68,136]),target([3,128,12])]
    seen=set()
    probes=0
    for i,S in enumerate(maps):
        for L,R in ((IDENTITY,IDENTITY),(maps[3],maps[2]),(maps[1],maps[4])):
            j=distance(point_set(L[:4]),point_set([apply(S,b) for b in R[:4]]))
            for p in (0,4,15,7,16,32,35,182,255):
                r,c=(p+3*i)%16,(7*i+2*p)%16
                value=reference(S,p,r,c,L,R)
                Q.need(value==transition(S,p,r,c,L,R),"Independent lift multiplication")
                v=conjugate(value)
                Q.need(coefficient(S,p,r,c,L,R)==(h[j]*v[0],h[j]*v[1]),"Canonical amplitude")
                actual=power((v[0]/4,v[1]/4),13)
                Q.need(actual==(rhs[j]*v[0],rhs[j]*v[1]),"Literal adjoint phase and displacement rank")
                if value!=(0,0):
                    seen.add(j)
                probes+=1
    Q.need(seen.issuperset({0,1,2,3,4}),"All five nonempty distance classes")
    print("PASS exact five spherical normal equations, adjointness, off-span projection norm,",
          probes,"absolute-phase probes and 8,338,459,852,800 nonzero canonical coefficients.")


if __name__=='__main__':
    main()
