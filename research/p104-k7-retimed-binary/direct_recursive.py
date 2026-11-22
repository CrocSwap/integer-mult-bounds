"""Exercise the production one-child direct dispatcher with nonconstant weights and real recursion."""
from fractions import Fraction as Q
from io import BytesIO
from math import gcd, prod
from pathlib import Path
from random import Random
import sys


def digits(q, radices):
    out=[]
    for r in reversed(radices):
        q,x=divmod(q,r)
        out.append(x)
    assert q==0
    return list(reversed(out))


def address(xs,radices):
    n=0
    for x,r in zip(xs,radices,strict=True):
        n=n*r+x
    return n


def factors(n,axis,word,modulus):
    # Follow the selected unit vector through the elementary factors on either side.
    u=[int(i==axis) for i in range(n)]
    v=u.copy()
    def residue(x):
        r=Q(x)
        return int(r.numerator*pow(r.denominator,-1,modulus)%modulus)
    for op,i,*args in reversed(word):
        if op=="add":
            j,k=args
            u[j]=(u[j]+residue(k)*u[i])%modulus
            v[i]=(v[i]-residue(k)*v[j])%modulus
        elif op=="scale":
            a=residue(args[0])
            u[i]=a*u[i]%modulus
            v[i]=pow(a,-1,modulus)*v[i]%modulus
        else:
            assert op=="swap"
            j=args[0]
            u[i],u[j]=u[j],u[i]
            v[i],v[j]=v[j],v[i]
    assert sum(a*b for a,b in zip(u,v))%modulus==1
    return u,v


def check(root):
    sys.path.insert(0,str(Path(root).resolve()))
    from upstream import install
    install()
    from binary_receiver import Receiver
    from direct_body import direct_line as bound
    from factored_frames import Frame
    from five_exchange import direct_line
    from module_atoms import component_widths
    assert bound is direct_line

    tests=[
        (2,2,(1,1,0,1),1,(("add",0,1,1),("swap",0,1),("scale",1,Q(5,2)),("add",1,0,2)),2,2,2),
        (2,1,(1,2,1,1),0,(("scale",0,Q(5,2)),("add",0,1,Q(1,2)),("add",1,0,2)),2,1,1),
        (3,1,(1,1,0,1),1,(("add",1,2,-1),("swap",0,2),("add",0,1,Q(1,2)),("scale",2,-1)),3,3,2),
    ]
    rng=Random(58119)
    for n,f,layout,axis,word,unused,older,gap in tests:
        core=Receiver(n,layout,direct=True)
        atom,mod=core.atom,core.modulus
        rings=[3**s for s in component_widths(layout)]
        u,v=factors(n,axis,word,mod)
        units=[a for a in range(mod) if gcd(a,mod)==1]
        weights=[[rng.choice(units) for _ in range(n*f)] for _ in range(older)]
        shape=[unused,older]+[atom]*(n*f)+[gap]+[atom]*(n*f)
        volume=prod(shape)
        inputs=bytearray(volume)
        expected=bytearray(volume)
        seen=set()
        samples=range(volume) if volume<15000 else rng.sample(range(volume),311)
        for src in samples:
            a=digits(src,shape)
            old=a[1]
            left = [digits(t,rings) for t in a[2:2+n*f]]
            right = [digits(t,rings) for t in a[3+n*f:]]
            for j in range(f):
                for k,m in enumerate(rings):
                    indices=range(j,n*f,f)
                    delta=sum(v[i] * (right[t][k]-pow(weights[old][t],-1,m)*left[t][k])
                              for i,t in enumerate(indices))
                    for i,t in enumerate(indices):
                        left[t][k]=(left[t][k]+weights[old][t]*u[i]*delta)%m
                        right[t][k]=(right[t][k]-u[i]*delta)%m
            a[2:2+n*f]=[address(t,rings) for t in left]
            a[3+n*f:]=[address(t,rings) for t in right]
            dest=address(a,shape)
            assert dest not in seen
            seen.add(dest)
            inputs[src]=rng.randrange(1,256)
            expected[dest]=inputs[src]
        calls=[]
        outer=core.weighted
        depth=0
        def counted(src,dst,**kw):
            nonlocal depth
            calls.append((depth,kw["atoms"]))
            depth+=1
            try:
                return outer(src,dst,**kw)
            finally:
                depth-=1
        core.weighted=counted
        src=BytesIO(b"prefix"+inputs+b"suffix")
        dst=BytesIO(b"prefix"+bytes(volume)+b"suffix")
        for tape in (src,dst):tape.seek(6)
        with core.storage():
            core.serve_line(src,dst,Frame(n,word,(axis,)),f,unused,older,gap,1,lambda row,j:weights[row][j])
        assert dst.getvalue()==b"prefix"+expected+b"suffix"
        assert src.getvalue()==b"prefix"+inputs+b"suffix"
        assert src.tell()==dst.tell()==6+volume
        assert [width for dep,width in calls if dep==0]==[f]
        print("direct",n,"f",f,"layout",layout,"volume",volume,"checked origins",len(seen),
              "root arrows",sum(dep==0 for dep,_ in calls),"nested",sum(dep>0 for dep,_ in calls),flush=True)

if __name__ == "__main__":
    from upstream import HERE
    check(HERE)
