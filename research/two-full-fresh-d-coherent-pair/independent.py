#!/usr/bin/env python3
"""Independent sparse operator and Laurent checks. JoyboyBrian; Apache-2.0."""
from fractions import Fraction as F
from pathlib import Path
import gzip
import hashlib
import json

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
SOURCE='research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'


def require(x,s):
    if not x:raise ValueError(s)


def sparse_operator(source,orientation,t):
    """Propagate all 632 coordinate functionals, independently of verify.py."""
    frames=source['canonical']['frames']
    state={('L',i):{i:F(1)} for i in range(632)}
    state['C',0]={}
    for event in source['programs'][orientation]:
        if event[0]=='scalar':
            g=event[1];d=tuple(g[1])
            if g[0]=='clear':state[d]={}
            elif g[0]=='copy':state[d]=dict(state[tuple(g[2])])
            elif g[0]=='scale':state[d]={i:v*F(g[2],g[3]) for i,v in state[d].items()}
            elif g[0]=='add':
                factor=F(g[3],g[4])
                target=state[d]
                for i,v in state[tuple(g[2])].items():
                    target[i]=target.get(i,F(0))+factor*v
                    if target[i]==0:del target[i]
            else:raise ValueError('scalar instruction')
        elif event[0]=='climb' or event[0]=='center':
            old,new=event[-3:-1]
            if event[0]=='climb':d=('L',event[2])
            else:d=('C',event[1])
            factor=t**(int(len(frames[new])==9)-int(len(frames[old])==9))
            state[d]={i:v*factor for i,v in state[d].items()}
        else:require(event[0] in ('warp','adapter','phase'),'source operation')
    require(state['C',0]=={},'owned buffer operator zero')
    for i in range(632):
        expected={i:F(1)}
        if orientation=='forward' and 112<=i<224:expected[i-112]=F(1)
        if orientation=='backward' and i<112:expected[i+112]=F(-1)
        factor=t if len(frames[source['canonical']['final'][i]])==9 else F(1)
        expected={j:v*factor for j,v in expected.items()}
        require(state['L',i]==expected,f'complete operator row {orientation}:{i}')
    return sum(len(state['L',i]) for i in range(632))


# Exact Laurent polynomials in commuting symbols t, q, epsilon.
def term(a=0,b=0,c=0,k=1):return {(a,b,c):F(k)} if k else {}
def add(x,y):
    z=x.copy()
    for m,v in y.items():
        z[m]=z.get(m,F(0))+v
        if not z[m]:del z[m]
    return z

def mul(x,y):
    z={}
    for a,u in x.items():
        for b,v in y.items():
            m=tuple(i+j for i,j in zip(a,b));z[m]=z.get(m,F(0))+u*v
    return {m:v for m,v in z.items() if v}

def matmul(x,y):return [[add(mul(x[i][0],y[0][j]),mul(x[i][1],y[1][j])) for j in range(2)] for i in range(2)]

def laurent():
    z={};one=term();minus=term(k=-1);t=term(a=1);q=term(b=1);qi=term(b=-1);eps=term(c=1)
    R=[[t,z],[z,one]];U=[[one,q],[z,one]];L=[[one,z],[term(b=-1,k=-1),one]]
    B=[[one,minus],[one,z]];S=[[one,z],[z,eps]];Si=[[one,z],[z,term(c=-1)]]
    product=S
    for matrix in (R,U,R,L,B,Si):product=matmul(product,matrix)
    expected=[[add(add(term(a=2),term(a=1,k=-1)),term(a=1,b=1)),add(term(a=2,c=-1,k=-1),term(a=1,c=-1))],
              [add(eps,term(b=-1,c=1,k=-1)),qi]]
    require(product==expected,'arbitrary-Q Laurent identity')
    wrong=[[entry.copy() for entry in row] for row in expected];wrong[0][1]={}
    require(product!=wrong,'discarded coherent pole rejected')
    # Endpoint compatibility restores the unscaled source at t=1.
    sub=lambda p:{(b,c):sum(v for (aa,bb,cc),v in p.items() if (bb,cc)==(b,c)) for a,b,c in p}
    require(all(v==0 for v in sub(product[0][1]).values()),'ideal t=1 zero pole')
    return product


def main():
    raw=(ROOT/SOURCE).read_bytes()
    require(hashlib.sha256(raw).hexdigest()=='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05','independent source pin')
    src=json.loads(gzip.decompress(raw));rows=0
    for o in ('forward','backward'):
        for t in (F(1),F(9,8)):
            require(sparse_operator(src,o,t)==744,'sparse full endpoint support');rows+=632
    laurent()
    print(f'PASS_INDEPENDENT_COHERENT_BOUNDARY: {rows} exact operator rows, arbitrary-Q Laurent identity, pole control')

if __name__=='__main__':main()
