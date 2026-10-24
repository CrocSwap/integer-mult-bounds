"""Exact P112 support, symmetry and coefficient classification checks.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from itertools import combinations, product


def need(ok,message):
    if not ok:raise ValueError(message)


def canon(v):
    v=tuple(v)
    return v if next(x for x in v if x)>0 else tuple(-x for x in v)


def dot(a,b):return sum(x*y for x,y in zip(a,b))


def rank(a):
    a=[[F(x) for x in r] for r in a]; k=0
    for j in range(len(a[0]) if a else 0):
        pivot=next((i for i in range(k,len(a)) if a[i][j]),None)
        if pivot is None:continue
        a[k],a[pivot]=a[pivot],a[k];t=a[k][j]
        a[k]=[x/t for x in a[k]]
        for i in range(k+1,len(a)):
            if a[i][j]:
                t=a[i][j];a[i]=[x-t*y for x,y in zip(a[i],a[k])]
        k+=1
    return k


def roots():
    rows=set()
    for i,j in combinations(range(8),2):
        for s in (-1,1):
            v=[0]*8;v[i]=2;v[j]=2*s;rows.add(tuple(v))
    for v in product((-1,1),repeat=8):
        if sum(x<0 for x in v)%2==0:rows.add(canon(v))
    removed=[]
    for j in range(4):
        for sign in (1,-1):
            v=[0]*8;v[2*j]=2;v[2*j+1]=2*sign;removed.append(tuple(v))
    return sorted(rows),removed,sorted(rows-set(removed))


def plus(a,b):return (a[0]+b[0],a[1]+b[1])
def times(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def inv(a):
    d=a[0]**2+a[1]**2;need(d!=0,'nonzero coefficient');return (a[0]/d,-a[1]/d)
def neg(a):return (-a[0],-a[1])
def cplx(x):return (F(x),F(0))


def crank(a):
    a=[r[:] for r in a];k=0;zero=cplx(0)
    for j in range(len(a[0])):
        pivot=next((i for i in range(k,len(a)) if a[i][j]!=zero),None)
        if pivot is None:continue
        a[k],a[pivot]=a[pivot],a[k];t=inv(a[k][j]);a[k]=[times(x,t) for x in a[k]]
        for i in range(k+1,len(a)):
            if a[i][j]!=zero:
                t=a[i][j];a[i]=[plus(x,neg(times(t,y))) for x,y in zip(a[i],a[k])]
        k+=1
    return k


def main():
    allrows,removed,x=roots();need((len(allrows),len(removed),len(x))==(120,8,112),'root inventory')
    need(all(dot(a,a)==8 for a in allrows),'doubled norm')
    supports={};normal_counts={}
    for alpha in allrows:
        c=[dot(v,alpha) for v in x];s=tuple(i for i,a in enumerate(c) if a)
        normal_counts[len(s)]=normal_counts.get(len(s),0)+1
        if len(s)==53:
            need(alpha in x and rank([x[i] for i in range(112) if i not in s])==7,'all equality supports')
            need(s not in supports,'distinct supports')
            need(sorted(c[i]**2 for i in s)==[16]*52+[64],'coefficient weights')
            supports[s]=alpha
    need(normal_counts=={53:112,56:8},'all root normals')
    y={canon(tuple(dot(v,a)//4 for a in removed)) for v in x}
    need(all(all(dot(v,a)%4==0 for a in removed) for v in x),'frame coordinates integral')
    planes={frozenset(i for i,z in enumerate(v) if z) for v in y}
    expected={frozenset(s) for s in combinations(range(8),4) if s[0]^s[1]^s[2]^s[3]==0}
    need(planes==expected and len(planes)==14,'affine plane supports')
    aff=[]
    for a,b,c in product(range(1,8),repeat=3):
        vals=[(a if j&1 else 0)^(b if j&2 else 0)^(c if j&4 else 0) for j in range(8)]
        if len(set(vals))==8:
            for shift in range(8):aff.append(tuple(v^shift for v in vals))
    need(len(set(aff))==1344,'full affine group')
    first=next(iter(planes));orbit={frozenset(p[i] for i in first) for p in aff}
    need(orbit==planes,'support transitivity')
    actions=0
    for p in aff:
        for plane in planes:
            need(frozenset(p[i] for i in plane) in planes,'plane action');actions+=1
    # Every independent frame sign flip preserves the literal root lines.
    for i in range(8):
        need({canon(tuple(-z if j==i else z for j,z in enumerate(v))) for v in y}==y,'sign symmetry')
    # Independent literal full-matrix check of the predecessor witness.
    alpha=(1,)*8;c=[dot(v,alpha) for v in x];s=[i for i,a in enumerate(c) if a]
    g=[[dot(a,b) for b in x] for a in x]
    witness=[[g[i][j]-(112 if i==j and i in s else 0) for j in range(112)] for i in range(112)]
    need(rank(witness)==59,'literal 112-row rank')
    need(rank([[g[i][j]-(112 if i==j and i in s[:51] else 0) for j in range(112)] for i in range(112)])==59,'additive rank59 is separate')
    cv=[c[i] for i in s];weights=[F(z*z,8) for z in cv]
    cases=0
    for eps in (cplx(0),(F(1,7),F(0)),(F(0),F(1,7))):
        terms=[cplx(-a/112) for a in weights]
        terms[0]=plus(terms[0],eps);terms[1]=plus(terms[1],neg(eps))
        delta=[times(cplx(a),inv(t)) for a,t in zip(weights,terms)]
        mat=[[plus(cplx(F(a*b,8)),delta[i] if i==j else cplx(0)) for j,b in enumerate(cv)] for i,a in enumerate(cv)]
        need(crank(mat)==52,'arbitrary coefficient equality rank')
        mat[0][0]=plus(mat[0][0],cplx(1))
        need(crank(mat)==53,'wrong coefficient restores full Schur rank')
        cases+=1
    need(len(s)==53 and len(s[:51])==51,'support distinction')
    print('PASS_P112_RANK59_CLASSIFICATION',dict(root_normals=120,equality_supports=112,affine_maps=1344,plane_actions=actions,literal_full_ranks=2,coefficient_pairs=cases,sign_generators=8,controls=5))

if __name__=='__main__':main()
