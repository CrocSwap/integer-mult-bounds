"""Separate literal Kronecker construction and column-space rank on the first resonant source."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent

def need(v,s):
    if not v:raise ValueError(s)
def column_rank(a):
    basis={}
    for col in zip(*a):
        v=[x%5 for x in col]
        for pivot,w in sorted(basis.items()):
            q=v[pivot];v=[(x-q*y)%5 for x,y in zip(v,w)]
        pivot=next((i for i,x in enumerate(v) if x),None)
        if pivot is not None:
            inv=pow(v[pivot],-1,5);basis[pivot]=[x*inv%5 for x in v]
    return len(basis)
T=[[1]];K=[[1,1],[1,0]]
for _ in range(4):T=[[a*b%5 for a in row for b in small] for row in T for small in K]
M=[[(int(i==j)-T[i][j])%5 for j in range(16)] for i in range(16)];B=[r[1:-1] for r in M[1:-1]]
need(column_rank(M)==10 and column_rank(B)==9,'independent tensor/deletion ranks')
# Complete kernel census of the 4x4 tensor J2⊗J2−I.
L=[[0,1,1,1],[0,0,0,1],[0,0,0,1],[0,0,0,0]]
count=0
for n in range(625):
    v=[n//5**j%5 for j in range(4)]
    count+=int(all(sum(x*y for x,y in zip(row,v))%5==0 for row in L))
need(count==25,'independent two-block kernel census')
# Independently form every power directly from the binomial block identity,
# without iterating the primary verifier's matrix multiplication.
expected=((1,0,0,0,0),(2,1,0,0,0),(4,2,1,0,0),(6,4,2,1,0),(8,6,4,2,0))
for j in range(1,6):
    for power in range(1,6):
        a=[[0]*(2*j) for _ in range(2*j)]
        for i in range(j):
            for k in range(j):
                a[i][k]=a[j+i][j+k]=int(k-i==power)
                a[i][j+k]=power*(int(k-i==power-1)+int(k-i==power))%5
        need(column_rank(a)==expected[j-1][power-1],'direct binomial power certificate')
# Exact basis vectors for K/3 conjugate to J2: v=(3,1), w=(3,0).
U=((2,2),(2,0));v=(3,1);w=(3,0)
act=lambda z:tuple(sum(a*b for a,b in zip(row,z))%5 for row in U)
need(act(v)==v and act(w)==tuple((a+b)%5 for a,b in zip(v,w)),'explicit similarity')
need((v[0]*w[1]-v[1]*w[0])%5!=0,'similarity invertibility')
s=json.loads((P/'SOURCES.json').read_text());rows=[r for r in s['files'] if r['usage']=='input'];need(len(rows)==2,'source list')
for r in rows:need(hashlib.sha256((P.parents[1]/r['path']).read_bytes()).hexdigest()==r['sha256'],'source bytes')
r=json.loads((P/'RESULT.json').read_text());need(type(r['no_physical_supplier'])is bool and r['no_physical_supplier'],'typed scope')
need(r['fixtures'][0]['rank']==9,'receipt fixture')
print('PASS_INDEPENDENT_QUINARY_TENSOR_AND_KERNEL')
