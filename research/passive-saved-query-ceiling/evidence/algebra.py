"""Independent exact audit of ONE mixed-thin p2 policy; no search/emitter.

Own D-left semidirect-product interpreter (producer uses D-right normal form).
Only pinned Clifford primitives and interval library are reused. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256
import gzip, json, types, sys

HERE=Path(__file__).resolve().parent
def need(x,msg):
    if not x: raise ValueError(msg)

# D1^a D3^b followed by a word in Q,C1,C3.  C_s^2=I and
# D_s C_s D_s^-1=Q^-1 C_s Q; no own-D or Q/C commutation.
def reduce(w):
    out=[]
    for x in w:
        if out and (out[-1]==-x or (x in (2,3) and out[-1]==x)):
            out.pop()
        else: out.append(x)
    return tuple(out)
def act(w,b):
    out=()
    for x in w:
        if x in (2,3):
            n=b[x-2]
            pre=(1,)*n if n>=0 else (-1,)*(-n)
            post=(-1,)*n if n>=0 else (1,)*(-n)
            out=reduce(out+pre+(x,)+post)
        else: out=reduce(out+(x,))
    return out
def add(*ps):
    z=Counter()
    for p in ps:
        for k,v in p.items(): z[k]+=v
    return {k:v for k,v in z.items() if v}
def neg(p): return {k:-v for k,v in p.items()}
def mul(*ps):
    out={((0,0),()):F(1)}
    for p in ps:
        z=Counter()
        for (a,w),x in out.items():
            for (b,v),y in p.items():
                z[(tuple(i+j for i,j in zip(a,b)),reduce(act(w,b)+v))]+=x*y
        out={k:v for k,v in z.items() if v}
    return out
one={((0,0),()):F(1)}
q={((0,0),(1,)):F(1)}; qi={((0,0),(-1,)):F(1)}
c={((0,0),(2,)):F(1)}; e={((0,0),(3,)):F(1)}
d={((1,0),()):F(1)}; f={((0,1),()):F(1)}
def mm(A,B):
    return [[add(*(mul(A[i][k],B[k][j]) for k in range(len(B))))
             for j in range(len(B[0]))] for i in range(len(A))]
def lower(z): return [[one,{}],[z,one]]
def upper(z): return [[one,z],[{},one]]
def diag(x): return [[x,{}],[{},x]]
def replay(C,E):
    M=[[one.copy() if i==j else {} for j in range(4)] for i in range(4)]
    def plus(i,j,z): M[i]=[add(x,mul(z,y)) for x,y in zip(M[i],M[j])]
    def left(i,z): M[i]=[mul(z,x) for x in M[i]]
    def thick(pair,C,D):
        plus(2*pair,2*pair+1,neg(mul(q,C)))
        left(2*pair,D); left(2*pair+1,D)
    def bridge(i,j,sgn):
        plus(2*i,2*j,one if sgn==1 else neg(one))
        plus(2*j+1,2*i+1,neg(one) if sgn==1 else one)
    plus(0,2,neg(one)); plus(3,1,one)
    plus(1,0,mul(C,qi)); thick(0,C,d)
    left(2,d);left(3,d)  # both source paid IDLE jobs retained
    bridge(0,1,1);plus(1,0,mul(qi,C));bridge(0,1,-1)
    thick(1,E,f);plus(3,2,mul(qi,E));bridge(1,0,1)
    for i in (0,1): M[2*i],M[2*i+1]=M[2*i+1],[neg(x) for x in M[2*i]]
    plus(0,2,one);plus(3,1,neg(one))
    return M
