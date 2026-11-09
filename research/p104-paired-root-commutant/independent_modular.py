#!/usr/bin/env python3
"""Lead's independent finite-field stress check of the paired-root theorem.

Constructs the Gram matrix directly from dual vectors, obtains a minimal
factorization by modular elimination, and solves the full primal commutant
by vectorized matrix equations. No worker or predecessor scientific imports.
"""
import json, random


def need(ok,why):
    if not ok: raise ValueError(why)


def eye(n): return [[int(i==j) for j in range(n)] for i in range(n)]
def tr(a): return list(map(list,zip(*a)))
def mat(a,b,p): return [[sum(x*y for x,y in zip(row,col))%p for col in zip(*b)] for row in a]


def rref(a,p):
    a=[row[:] for row in a];r=0;piv=[]
    if not a:return a,piv
    for c in range(len(a[0])):
        j=next((j for j in range(r,len(a)) if a[j][c]%p),None)
        if j is None:continue
        a[r],a[j]=a[j],a[r];inv=pow(a[r][c],-1,p);a[r]=[(x*inv)%p for x in a[r]]
        for i in range(len(a)):
            if i!=r and a[i][c]:
                q=a[i][c];a[i]=[(x-q*y)%p for x,y in zip(a[i],a[r])]
        piv.append(c);r+=1
        if r==len(a):break
    return a,piv


def inverse(a,p):
    n=len(a);b,piv=rref([row+e for row,e in zip(a,eye(n))],p)
    need(piv[:n]==list(range(n)),'invertible basis')
    return [row[n:] for row in b]


def random_gl(rng,p):
    while True:
        a=[[rng.randrange(p) for _ in range(2)] for _ in range(2)]
        if (a[0][0]*a[1][1]-a[0][1]*a[1][0])%p:return a


def outer(x,y,p):return [[a*b%p for b in y] for a in x]


def commutant_dimension(operators,p):
    n=len(operators[0]);eq=[]
    for a in operators:
        for i in range(n):
            for j in range(n):
                row=[0]*(n*n)
                for k in range(n):
                    row[i*n+k]=(row[i*n+k]+a[k][j])%p
                    row[k*n+j]=(row[k*n+j]-a[i][k])%p
                if any(row):eq.append(row)
    return n*n-len(rref(eq,p)[1])


def test(p,L,t,seed):
    need(p!=2,'characteristic two excluded')
    rng=random.Random(seed);H=random_gl(rng,p);Hi=inverse(H,p)
    inv2=pow(2,-1,p)
    A=([1,0],[1,0]);B=([1,1],[inv2,inv2]);E=([0,1],[0,1])
    pattern=[] if t==0 else ([A,E] if t==2 and L%2==0 else [A,A] if t==2 else [A,B,A,B] if L%2==0 else [A,B,B,A])
    pieces=[]
    for _ in range(L):
        Q=random_gl(rng,p);P=inverse(Q,p)
        pieces.append(('full',[(tr(Q)[i],P[i]) for i in range(2)]))
    # Put thin units at independently chosen gaps, retaining their order.
    gaps=sorted(rng.randrange(L+1) for _ in pattern)
    for j,((q,row),gap) in reversed(list(enumerate(zip(pattern,gaps)))):
        q=[x[0] for x in mat(H,[[x] for x in q],p)];row=mat([row],Hi,p)[0]
        scale=rng.randrange(1,p);q=[x*scale%p for x in q];row=[x*pow(scale,-1,p)%p for x in row]
        pieces.insert(gap,('thin',[(q,row)]))
    units=[item for _,block in pieces for item in block];N=len(units);n=N-2
    Z=[[sum(a*b for a,b in zip(row,q))%p for q,_ in units] for _,row in units]
    need(all(Z[i][i]==1 for i in range(N)),'rank-one dual projection')
    G=[[((i>j)-(i<j))*Z[i][j]%p for j in range(N)] for i in range(N)]
    cols=rref(G,p)[1];need(len(cols)==n,'corank two')
    Y=[[row[j] for j in cols] for row in G];rows=rref(tr(Y),p)[1]
    X=mat(inverse([Y[i] for i in rows],p),[G[i] for i in rows],p)
    need(mat(Y,X,p)==G,'minimal full-span factorization')
    product=eye(n);operators=[];index=0
    for kind,block in pieces:
        op=[[0]*n for _ in range(n)]
        if kind=='full':need(G[index][index+1]==G[index+1][index]==0,'full orthogonality')
        for _ in block:
            x=[row[index] for row in X];y=Y[index];a=outer(x,y,p)
            need(any(x) and any(y) and sum(q*r for q,r in zip(x,y))%p==0,'nonzero isotropic unit')
            product=mat([[(int(i==j)-2*a[i][j])%p for j in range(n)] for i in range(n)],product,p)
            op=[[(u+v)%p for u,v in zip(row,b)] for row,b in zip(op,a)];index+=1
        operators.append(op)
    need(product==[[(p-int(i==j))%p for j in range(n)] for i in range(n)],'full chronological product')
    dimension=commutant_dimension(operators,p);wanted=4 if t==0 else 2 if t==2 else 1
    need(dimension==wanted,'primal commutant dimension')
    return {'prime':p,'full_pairs':L,'thin':t,'seed':seed,'dimension':n,'commutant_dimension':dimension}


if __name__=='__main__':
    cases=[test(p,L,t,seed) for p in (3,5,7) for L,t in ((3,0),(2,2),(3,2),(2,4),(3,4)) for seed in (78,79,80)]
    controls={}
    for label,args in (('wrong_total_reflection_product',(5,2,0,78)),
                       ('excluded_characteristic_two',(2,3,0,78))):
        try:test(*args)
        except ValueError:controls[label]=True
        else:controls[label]=False
    need(all(controls.values()),'every negative control must reject')
    print(json.dumps({'cases':cases,'count':len(cases),'controls':controls},sort_keys=True))
    print('PASS_FINITE_FIELD_COMMUTANT_STRESS')
