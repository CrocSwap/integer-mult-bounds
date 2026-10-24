"""Independent sparse factor checker, adapted from the root reviewer with attribution.
Uses ordered tensor construction and Fraction sector conversion, not primary formulas.
"""
from fractions import Fraction as F
import json,hashlib,time
from pathlib import Path

def matmul(a,b):
    bt=list(zip(*b))
    return [[sum(x*y for x,y in zip(row,col) if x and y) for col in bt] for row in a]
def rank(a):
    a=[list(map(F,r)) for r in a];k=0
    for j in range(len(a[0])):
        p=next((i for i in range(k,len(a)) if a[i][j]),None)
        if p is None:continue
        a[k],a[p]=a[p],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
        for i in range(k+1,len(a)):
            if a[i][j]:
                v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
        k+=1
    return k
def ordered_to_sector(a,d):
    pairs=[(i,j) for i in range(d) for j in range(i+1,d)]
    basis=[[(i*d+i,1)] for i in range(d)]+[[(i*d+j,1),(j*d+i,1)] for i,j in pairs]+[[(i*d+j,1),(j*d+i,-1)] for i,j in pairs]
    out=[]
    for v in basis:
        y=[sum(a[k][i]*c for i,c in v) for k in range(d*d)]
        out.append([y[i*d+i] for i in range(d)]+[F(y[i*d+j]+y[j*d+i],2) for i,j in pairs]+[F(y[i*d+j]-y[j*d+i],2) for i,j in pairs])
    return [list(r) for r in zip(*out)],pairs
def kron(a):return [[a[i][k]*a[j][l] for k in range(len(a)) for l in range(len(a))] for i in range(len(a)) for j in range(len(a))]
def need(value, message):
    if not value:raise ValueError(message)
rows=[]
for m in (2,3):
    d=2**m;n=d*d;s=d*(d-1)//2
    h=[[(-1)**((i&j).bit_count()) for j in range(d)] for i in range(d)]
    w=[[((-1)**(i*j)) if i//2==j//2 else 0 for j in range(d)] for i in range(d)]
    T,pairs=ordered_to_sector(kron(h),d);Q,_=ordered_to_sector(kron(w),d)
    targetrank=rank([r[:d] for r in T[d:d+s]]);slicerank=rank([r[:d] for r in Q[d:d+s]])
    need((targetrank,slicerank)==(d-1,d//2),'independent cross rank')
    pieces=[]
    for ws in (list(range(1,1+d//2)),list(range(1+d//2,d))):
        L=[[0]*n for _ in range(n)];R=[[0]*n for _ in range(n)]
        for p,address in enumerate(ws):
            e=pairs.index((2*p,2*p+1));v=[(-1)**((address&x).bit_count()) for x in range(d)]
            for z,x in enumerate(v):R[2*p][z]=x;L[z][2*p]=x
            for z,(i,j) in enumerate(pairs):
                if i^j==address:L[d+z][d+e]=1;R[d+e][d+z]=1
        pieces.append(matmul(matmul(L,Q),R))
    residual=[[T[i][j]-pieces[0][i][j]-pieces[1][i][j] for j in range(n)] for i in range(n)]
    sector=lambda i:0 if i<d else 1 if i<d+s else 2
    need(all(residual[i][j]==0 for i in range(n) for j in range(n) if sector(i)!=sector(j)),'two-call residual sectors')
    need(any(T[i][j]!=pieces[0][i][j] for i in range(d,d+s) for j in range(d)),'one-call negative')
    phasechecks=0
    # Each coordinate character factor is evaluated independently; no author helper imported.
    for p in range(d):
      for q in range(d):
       for i in range(d):
        for j in range(d):
         acc=1
         for k in range(d):
          e=(int(k==i)+int(k==j)-int(k==p)-int(k==q))%4
          z=[(1,0),(0,1),(-1,0),(0,-1)]
          real=sum(z[(t*e)%4][0] for t in range(4));imag=sum(z[(t*e)%4][1] for t in range(4))
          need(imag==0 and real in (0,4),'exact roots of unity');acc*=real//4
         need(acc==int(sorted((i,j))==sorted((p,q))),'free character projector')
         phasechecks+=1
    rows.append(dict(m=m,dimension=n,target_cross_rank=targetrank,slice_cross_rank=slicerank,all_endpoint_entries=n*n,phase_entries=phasechecks,one_call_negative_control=True))

P=Path(__file__).resolve().parent
sources=json.loads((P/'SOURCES.json').read_text());inputs=[r for r in sources['files'] if r['usage']=='input'];need(len(inputs)==2,'both source contracts')
for r in inputs:need(hashlib.sha256((P.parents[1]/r['path']).read_bytes()).hexdigest()==r['sha256'],'source bytes')
receipt=json.loads((P/'RESULT.json').read_text())
need(type(receipt['physical_tariff_claimed'])is bool and not receipt['physical_tariff_claimed'],'typed scope')
need([x['target_cross_rank'] for x in receipt['fixtures']]==[x['target_cross_rank'] for x in rows],'independent receipt ranks')
print('PASS_INDEPENDENT_SECTOR_FACTORS_AND_FREE_PROJECTORS')
