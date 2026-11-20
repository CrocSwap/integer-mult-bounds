from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"certified-gaussian-recovery"))

from fractions import Fraction
from math import prod
from intervals import root_of_unity
from fine_ring import Trace,chirp_middle,root_word


def coords(index, t):
    x=[]
    for n in t:
        x.append(index%n)
        index//=n
    return x


def oracle(values,s,t,q,opposite=False):
    M=prod(t)
    r=t[0]
    D=len(t)
    out=[]
    X=[coords(i,t) for i in range(M)]
    roots=[root_of_unity(j,r,q+32) for j in range(r)]
    for a in X:
        re=im=0
        for b,(u,v) in zip(X,values):
            angle=sum(s[k]*a[k]*b[k]*(r//t[k]) for k in range(D))*(-1 if opposite else 1)
            c,d=roots[angle%r]
            re+=c*u-d*v
            im+=c*v+d*u
        out.append((re/M,im/M))
    return out


def check(s,t,q,opposite=False):
    Q=1<<q
    v=[(((5*i+7)%19-9)*Q//64, ((11*i+5)%23-11)*Q//64) for i in range(prod(t))]
    tr=Trace()
    y=chirp_middle(v,s,t,q,inverse=opposite,trace=tr)
    w=oracle(v,s,t,q,opposite)
    er=max(Fraction(sum((a-u).absolute_upper() for a,u in zip(z,y0)),(1<<(q+32))*Q) for z,y0 in zip(w,y))
    if not (er<Fraction(3,Q)):
        raise ArithmeticError((s,t,q,er))
    print(s,t,q,'inverse' if opposite else 'forward', 'max bound in grid units',float(er*Q),'rings',tr.rings,'H bits',tr.h_bits,'max word',tr.max_scalar_operand,'tape bit travel',tr.travel)
    return y


def main():
    v=[(400,0),(-256,64),(100,-50),(141,211),(-88,-241),(300,1),(-100,17),(11,-301)]
    y=chirp_middle(v,(3,1),(4,2),10,f=16)
    receipt=[[63, -37], [58, -12], [14, -31], [19, -39], [32, 93], [-20, 124], [139, -50], [92, -47]]
    if not (list(map(list,y))==receipt):
        raise ArithmeticError('independent check failed at verify_middle.py:51')
    print("Byte-for-byte published #6987 fixture")
    for t,s,q in [((4,4),(3,1),20),((8,8),(5,7),180),((8,4,8),(7,3,5),28),((16,8),(9,7),80)]:
        for conj in (False,True):
            check(s,t,q,conj)
    for q in (6,72,256):
        for n in (4,8,16,32,64):
            for j in range(n):
                v=root_word(j,n,q,Trace())
                ref=root_of_unity(j,n,q+32)
                for a,w in zip(v,ref):
                    if not (max(abs((a<<32)-w.lo),abs((a<<32)-w.hi))<=2<<32):
                        raise ArithmeticError('independent check failed at verify_middle.py:62')
    print("All phase checks passed")

if __name__=="__main__":
    main()
