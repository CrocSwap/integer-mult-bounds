"""Test noncommuting placed bases against an independent exact matrix computation."""

from fractions import Fraction as Q
from io import BytesIO
from pathlib import Path
from math import prod
import sys


def exact_projector(n, word, axis):
    def eye():
        return [[Q(i == j) for j in range(n)] for i in range(n)]
    def times(a,b):
        return [[sum(a[i][k]*b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    basis=eye()
    for gate,i,*args in word:
        new=eye()
        if gate=="add":
            j,c=args
            new[j][i]=Q(c)
        elif gate=="scale":
            new[i][i]=Q(args[0])
        else:
            j=args[0]
            new[j],new[i]=new[i],new[j]
        basis=times(basis,new)
    aug=[row+unit for row,unit in zip(basis,eye())]
    for i in range(n):
        k=next(k for k in range(i,n) if aug[k][i])
        aug[i],aug[k]=aug[k],aug[i]
        q=aug[i][i]
        aug[i]=[v/q for v in aug[i]]
        for j in range(n):
            if j!=i:
                q=aug[j][i]
                aug[j]=[a-q*b for a,b in zip(aug[j],aug[i])]
    primal=[basis[i][axis] for i in range(n)]
    dual=aug[axis][n:]
    assert sum(i*j for i,j in zip(primal,dual))==1
    return primal,dual


def main(root):
    sys.path.insert(0,str(root))
    from upstream import install
    install()
    from binary_receiver import Receiver
    from factored_frames import Frame
    from check_module_atoms import payload, expected_packet

    class Counted(Receiver):
        def weighted(self,*args,**kwargs):
            self.calls+=1
            return super().weighted(*args,**kwargs)
    cases=[
       (2,1,(1,1,0,0),1,(("add",0,1,1),("add",1,0,1),("scale",0,-1))),
       (2,1,(1,2,0,0),0,(("scale",0,Q(5,2)),("add",0,1,Q(1,2)),("add",1,0,2))),
       (3,1,(1,1,0,0),2,(("add",2,0,1),("swap",1,2),("add",1,0,-1),("scale",1,-1))),
       (3,1,(1,1,0,0),0,(("scale",1,-1),("add",2,1,Q(1,2)),("add",0,2,-1),("swap",0,1))),
    ]
    total=0
    for n,f,layout,axis,word in cases:
        core=Counted(n,layout,direct=True)
        core.calls=0
        atom,mod=core.atom,core.modulus
        assert atom==mod
        earlier,middle,repeat=2,2,2
        dims=(repeat,earlier)+(atom,)*(n*f)+(middle,)+(atom,)*(n*f)
        u,v=exact_projector(n,word,axis)
        def residue(k):
            return k.numerator*pow(k.denominator,-1,mod)%mod
        u,v=list(map(residue,u)),list(map(residue,v))
        def weight(row,i):
            return (1,2,4,5,7,8)[(row+i)%6]%mod
        def image(unused,old,*coordinates):
            left=list(coordinates[:n*f]);right=list(coordinates[n*f+1:]);gap=coordinates[n*f]
            for j in range(f):
                col=range(j,n*f,f)
                delta=sum(z*(right[k]-pow(weight(old,k),-1,mod)*left[k]) for z,k in zip(v,col))
                for z,k in zip(u,col):
                    left[k]=(left[k]+weight(old,k)*z*delta)%mod
                    right[k]=(right[k]-z*delta)%mod
            return unused,old,*left,gap,*right
        raw=payload(prod(dims));target=BytesIO()
        with core.storage():
            core.serve_line(BytesIO(raw),target,Frame(n,word,(axis,)),f,repeat,earlier,middle,4,weight)
        assert core.calls==1
        assert target.getvalue()==expected_packet(raw,dims,image)
        total+=prod(dims)
        print("noncommuting",n,mod,axis,"calls",core.calls,"records",prod(dims),flush=True)
    print("complete noncommuting direct comparisons",total)


if __name__ == "__main__":
    from upstream import HERE
    main(HERE)
