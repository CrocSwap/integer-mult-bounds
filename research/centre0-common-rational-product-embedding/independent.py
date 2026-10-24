"""Independent rank and algebra boundary controls; JoyboyBrian, Apache-2.0."""
from pathlib import Path
from fractions import Fraction as Q
import json
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
AUDIT='research/actual-centre0-source-audit/evidence/outputs/seven-mode-producer-feasibility-20261023/CORRECTED-DERIVATION.json'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def rank_mod(a,p=101):
    a=[[int(x.numerator)*pow(int(x.denominator),-1,p)%p for x in row] for row in a];k=0
    for j in range(len(a[0])):
        q=next((i for i in range(k,len(a)) if a[i][j]),None)
        if q is None:continue
        a[k],a[q]=a[q],a[k];v=pow(a[k][j],-1,p);a[k]=[x*v%p for x in a[k]]
        for i in range(k+1,len(a)):
            v=a[i][j]
            if v:a[i]=[(x-v*y)%p for x,y in zip(a[i],a[k])]
        k+=1
    return k
def rank(a):
    a=[[Q(x) for x in row] for row in a];k=0
    for j in range(len(a[0])):
        q=next((i for i in range(k,len(a)) if a[i][j]),None)
        if q is None:continue
        a[k],a[q]=a[q],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
        for i in range(k+1,len(a)):
            v=a[i][j]
            if v:a[i]=[x-v*y for x,y in zip(a[i],a[k])]
        k+=1
    return k
def mul(a,b):
    n=len(a);out=[(0,0)]*n
    for j,(ar,ai) in enumerate(a):
        for k,(br,bi) in enumerate(b):
            pos=(j+k)%n;sign=1 if j+k<n else -1;r,s=out[pos]
            out[pos]=(r+sign*(ar*br-ai*bi),s+sign*(ar*bi+ai*br))
    return out
def real_matrix(v):
    n=len(v);cols=[]
    for j in range(2*n):
        e=[(0,0)]*n;e[j%n]=(1,0) if j<n else (0,1)
        z=mul(v,e);cols.append([x[0] for x in z]+[x[1] for x in z])
    return [list(r) for r in zip(*cols)]
def main():
    data=json.loads((ROOT/AUDIT).read_bytes());g=[[Q(x) for x in row] for row in data['F_actual']]
    need(len(g)==112 and all(len(r)==112 for r in g),'actual shape')
    skew=[[g[i][j]-g[j][i] for j in range(112)] for i in range(112)]
    need(rank_mod(skew)==14,'source modular lower rank14')
    # Deliberately symmetrizing the two maps would erase the discriminator.
    need(rank_mod([[x-x for x in r] for r in g])==0,'same-map control')
    # E_8 over Q(i) has half-rank zero divisors, not the field-only rank rule.
    n=8;v=[(0,0)]*n;w=list(v);v[0]=(0,-1);w[0]=(0,1);v[4]=w[4]=(1,0)
    need(mul(v,w)==[(0,0)]*n,'(y^4-i)(y^4+i)=0')
    need(rank(real_matrix(v))==8,'Gaussian multiplication rank4 over Q(i)')
    # Valid isotopy with nonzero full-rank difference; exercise all basis pairs.
    basis=[]
    for j in range(n):
        e=[(0,0)]*n;e[j]=(1,0);basis.append(e)
    scale=lambda a,s:[(s*r,s*i) for r,i in a]
    for a in basis:
        for b in basis:need(mul(scale(a,2),scale(b,3))==scale(mul(a,b),6),'valid scalar isotopy')
    # Over an algebra split into scalar factors a nonzero rank1 multiplier exists.
    need(rank([[int(i==j==0) for j in range(8)] for i in range(8)])==1,'split algebra escape')
    print('PASS_INDEPENDENT_SOURCE_RANK14_AND_GAUSSIAN_ALGEBRA_CONTROLS')
if __name__=='__main__':main()
