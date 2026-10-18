"""Propose the coupled certificate with exact rational simplex; not trusted by replay.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
Default output is JSON on stdout. --out writes exclusively to a fresh file.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json
import sys
import argparse
import hashlib
from collections import Counter

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
source = ROOT / 'research/complex-local-word-ceiling/ceiling.py'
if hashlib.sha256(source.read_bytes()).hexdigest() != '86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc':
    raise ValueError('pinned interval source')
spec = importlib.util.spec_from_file_location('cost', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost)

def shapes():
    rows = []
    for mask in range(256):
        stops = [0] + [i for i in range(1,9) if mask >> (i-1) & 1] + [9]
        jumps = [b-a for a,b in zip(stops,stops[1:])]
        caps = []
        for k in range(1,8):
            a,b = next((a,b) for a,b in zip(stops,stops[1:]) if a <= k < b)
            caps.append(0 if a==0 or b==9 else 2**(7-b+a))
        rows.append((stops,jumps,caps+[int(1 in stops),int(8 in stops)]))
    return rows

def simplex(c,A,b):
    n,m = len(c),len(b)
    T = [[Q(x) for x in row]+[Q(-int(i==j)) for j in range(m)]+[Q(int(i==j)) for j in range(m)]+[Q(b[i])] for i,row in enumerate(A)]
    basis = [n+m+i for i in range(m)]
    def optimize(coeff,allowed):
        rc = [Q(v) for v in coeff]+[Q(0)]
        for i in range(m):
            cb=coeff[basis[i]]
            if cb:
                rc=[x-cb*y for x,y in zip(rc,T[i])]
        rc[-1]=-rc[-1]
        pivots=0
        while True:
            choices=[j for j in allowed if rc[j]>0]
            if not choices:
                return rc
            j=min(choices)
            eligible=[i for i in range(m) if T[i][j]>0]
            if not eligible:
                raise ValueError('unbounded')
            i=min(eligible,key=lambda i:(T[i][-1]/T[i][j],basis[i]))
            pivot=T[i][j]
            T[i]=[v/pivot for v in T[i]]
            for r in range(m):
                if r!=i and T[r][j]:
                    q=T[r][j]
                    T[r]=[v-q*w for v,w in zip(T[r],T[i])]
            q=rc[j]
            rhs=rc[-1]+q*T[i][-1]
            rc=[v-q*w for v,w in zip(rc,T[i])]
            rc[-1]=rhs
            basis[i]=j
            pivots+=1
            if pivots>10000:
                raise ValueError('pivot budget')
    phase1=optimize([Q(0)]*(n+m)+[Q(-1)]*m,range(n+m))
    if phase1[-1]!=0 or any(j>=n+m for j in basis):
        raise ValueError(('phase1',phase1[-1],basis))
    rc=optimize([-Q(v) for v in c]+[Q(0)]*(2*m),range(n+m))
    x=[Q(0)]*n
    for i,j in enumerate(basis):
        if j<n:
            x[j]=T[i][-1]
    mu=[-rc[n+i] for i in range(m)]
    if not all(sum(A[i][j]*x[j] for j in range(n))>=b[i] for i in range(m)):
        raise ValueError('proposed primal infeasible')
    if not all(sum(A[i][j]*mu[i] for i in range(m))<=c[j] for j in range(n)):
        raise ValueError('proposed dual infeasible')
    if sum(c[j]*x[j] for j in range(n))!=sum(b[i]*mu[i] for i in range(m)):
        raise ValueError('proposed primal/dual gap')
    return x,mu

def optimize(a,scale):
    s=shapes()
    cc={r:cost.child_cost(r,73,a) for r in range(1,10)}
    idle=cost.child_cost(51,73,a)
    c=[(sum(cc[r][0] for r in jumps)-Q(9,51)*idle[1])*scale for _,jumps,_ in s]
    c=[Q(v.numerator//v.denominator) for v in c]
    b=[4656,4656,4672,4680,4672,4656,4656,208,208]
    A=[[s[j][2][i] for j in range(256)] for i in range(9)]
    x,mu=simplex(c,A,b)
    return x,[v/scale for v in mu]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    x,_=optimize(Q(1,500),10**12)
    base={1:1074,2:58,3:86,4:104,5:48,6:24,7:8,8:8}
    profile=Counter({r:Q(n) for r,n in base.items()})
    h=shapes()
    for j,v in enumerate(x):
        for r in h[j][1]:
            profile[r]+=v
    lo,hi=cost.ceiling(profile,73,832,9,56,grid=Q(1,10**10))
    _,mu=optimize(hi,10**14)
    result={'a_lo':str(lo),'a_hi':str(hi),
            'primal':{str(j):str(v) for j,v in enumerate(x) if v},
            'dual':[str(v) for v in mu],'cost_rounding_scale':10**14}
    payload=json.dumps(result,indent=2)+'\n'
    if args.out:
        with args.out.open('x',encoding='utf-8') as stream:
            stream.write(payload)
    else:
        sys.stdout.write(payload)


if __name__=='__main__':
    main()
