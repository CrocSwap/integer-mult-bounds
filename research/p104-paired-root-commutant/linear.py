"""Exact standard-library linear algebra for paired-root certificates."""
from fractions import Fraction as Q

def require(ok, message):
    if not ok: raise ValueError(message)

def identity(n): return [[Q(i == j) for j in range(n)] for i in range(n)]
def transpose(a): return [list(row) for row in zip(*a)]
def dot(x, y): return sum((a*b for a, b in zip(x, y)), Q(0))
def multiply(a, b):
    bt = transpose(b)
    return [[dot(row,col) for col in bt] for row in a]
def add(a, b, sign=1): return [[x+sign*y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(a, s): return [[s*x for x in row] for row in a]
def outer(x, y): return [[a*b for b in y] for a in x]
def flatten(a): return [x for row in a for x in row]

def rref(a):
    a = [[Q(x) for x in row] for row in a]; pivots=[]; i=0
    for j in range(len(a[0])):
        k=next((k for k in range(i,len(a)) if a[k][j]),None)
        if k is None: continue
        a[i],a[k]=a[k],a[i]; pivot=a[i][j]; a[i]=[x/pivot for x in a[i]]
        for k in range(len(a)):
            if k!=i and a[k][j]:
                c=a[k][j]; a[k]=[x-c*y for x,y in zip(a[k],a[i])]
        pivots.append(j); i+=1
        if i==len(a): break
    return a[:i],pivots

def rank(a): return len(rref(a)[1])
def nullspace(a):
    reduced,pivots=rref(a); out=[]
    for j in range(len(a[0])):
        if j in pivots: continue
        v=[Q(k==j) for k in range(len(a[0]))]
        for i,k in enumerate(pivots): v[k]=-reduced[i][j]
        out.append(v)
    return out

def inverse(a):
    n=len(a); require(all(len(r)==n for r in a),'inverse expects square matrix')
    reduced,pivots=rref([list(r)+e for r,e in zip(a,identity(n))])
    require(pivots==list(range(n)),'singular matrix')
    return [r[n:] for r in reduced]

def left_transvection(a,x,y,c=Q(-2)):
    ym=[dot(y,col) for col in transpose(a)]
    return [[v+c*u*w for v,w in zip(row,ym)] for u,row in zip(x,a)]

def rank_factor(a):
    x,pivots=rref(a); y=[[row[j] for j in pivots] for row in a]
    require(multiply(y,x)==a,'rank factorization')
    return x,y

def sparse_rank(rows):
    """Independent forward elimination for commutator constraints."""
    basis={}
    for source in rows:
        row={j:Q(c) for j,c in source.items() if c}
        while row:
            p=min(row); c=row[p]
            if p not in basis:
                basis[p]={j:v/c for j,v in row.items()}; break
            for j,v in basis[p].items():
                value=row.get(j,Q(0))-c*v
                if value: row[j]=value
                else: row.pop(j,None)
    return len(basis)

def direct_commutant_dimension(operators):
    """All entries of SM-MS=0; no dual data or normal-form inputs."""
    n=len(operators[0])
    def equations():
        for m in operators:
            for i in range(n):
                for j in range(n):
                    row={}
                    for k in range(n):
                        if m[k][j]:
                            key=i*n+k; row[key]=row.get(key,Q(0))+m[k][j]
                        if m[i][k]:
                            key=k*n+j; row[key]=row.get(key,Q(0))-m[i][k]
                    yield row
    return n*n-sparse_rank(equations())

def restricted_commutant_dimension(operators,basis):
    columns=[]
    for b in basis:
        col=[]
        for m in operators: col.extend(flatten(add(multiply(b,m),multiply(m,b),-1)))
        columns.append(col)
    return len(basis)-rank(transpose(columns))
