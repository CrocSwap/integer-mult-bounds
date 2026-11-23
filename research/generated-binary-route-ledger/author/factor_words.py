"""Source-grammar right words over Z[1/2]; all routes are fully charged.

A chronological word acting on x-as-column has matrix M^T and denotes x -> xM.
New model-assisted construction for CubeJerry. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Iterator

def need(ok,msg):
    if not ok:raise ValueError(msg)
def unit(x):
    x=F(x);return bool(x) and abs(x.numerator).bit_count()==1 and x.denominator.bit_count()==1
def atom_count(x):
    x=F(x);need(unit(x),'scale must be a dyadic unit')
    return max(abs(abs(x.numerator).bit_length()-x.denominator.bit_length()),int(x<0))
def invert_op(op):
    if op[0]=='swap':return tuple(op)
    if op[0]=='add':return ('add',op[1],op[2],str(-F(op[3])))
    need(op[0]=='scale','unknown operation');return ('scale',op[1],str(1/F(op[2])))
def relabel(op,f):
    if op[0] in ('swap','add'):return (op[0],f(op[1]),f(op[2]),*op[3:])
    return ('scale',f(op[1]),op[2])

@dataclass(frozen=True)
class Count:
    swaps:int=0
    adds:int=0
    upper:int=0
    scales:int=0
    atoms:int=0
    def __add__(self,other):return Count(*(x+y for x,y in zip(self.values(),other.values())))
    def __mul__(self,k):return Count(*(k*x for x in self.values()))
    def values(self):return self.swaps,self.adds,self.upper,self.scales,self.atoms
    def json(self):return dict(zip(('swaps','adds','upper','scales','atoms'),self.values()))
    def physical(self,n):return dict(ordinary_swaps=n*(self.swaps+2*self.upper),ordered_shifts_including_carry=n*self.adds+n*n,fixed_scalings=n*self.scales,signed_scale_atoms=n*self.atoms,carry_slots=n*n)

def recount(ops):
    t=a=u=d=h=0
    for op in ops:
        if op[0]=='swap':t+=1
        elif op[0]=='add':a+=1;u+=op[1]<op[2]
        elif op[0]=='scale':d+=1;h+=atom_count(op[2])
        else:raise ValueError('unknown word operation')
    return Count(t,a,u,d,h)

@dataclass(frozen=True)
class Recipe:
    kind:str
    n:int
    count:Count
    children:tuple=()
    data:object=None
    def json(self):return dict(kind=self.kind,n=self.n,count=self.count.json(),data=self.data,children=[c.json() for c in self.children])

def literal(n,ops,label):
    ops=tuple(tuple(op) for op in ops)
    return Recipe('literal',n,recount(ops),data=dict(label=label,ops=ops))
def identity(n):need(n>=1,'positive dimension');return Recipe('identity',n,Count())
def inverse(a):return Recipe('inverse',a.n,a.count,(a,))
def multiply(a,b):
    need(a.n==b.n,'product dimensions');return Recipe('multiply',a.n,a.count+b.count,(a,b))
def direct_sum(a,b):return Recipe('direct_sum',a.n+b.n,a.count+b.count,(a,b))
def tensor(a,b):return Recipe('tensor',a.n*b.n,a.count*b.n+b.count*a.n,(a,b))
def extend(a,n):
    need(n>=a.n,'identity extension cannot shrink');return Recipe('extend',n,a.count,(a,))
def permutation(order):
    order=tuple(order);n=len(order);need(sorted(order)==list(range(n)),'complete permutation required');cur=list(range(n));ops=[]
    for i,wanted in enumerate(order):
        j=cur.index(wanted)
        if i!=j:cur[i],cur[j]=cur[j],cur[i];ops.append(('swap',i,j))
    return Recipe('permutation',n,Count(swaps=len(ops)),data=dict(order=order,ops=ops))
def conjugate(t,a):
    need(t.n==a.n,'conjugation dimensions');return Recipe('conjugate',a.n,t.count*2+a.count,(t,a))
def guarded(s,sector_basis,rank):
    need(0<=rank<=sector_basis.n,'sector rank');return Recipe('guard',s.n*sector_basis.n,sector_basis.count*(2*s.n)+s.count*rank,(s,sector_basis),dict(rank=rank))

def emit(r,inverted=False)->Iterator[tuple]:
    k=r.kind
    if k=='identity':return
    if k in ('literal','permutation'):
        ops=r.data['ops']
        for op in (reversed(ops) if inverted else ops):yield invert_op(op) if inverted else tuple(op)
    elif k=='inverse':yield from emit(r.children[0],not inverted)
    elif k=='multiply':
        for child in (reversed(r.children) if inverted else r.children):yield from emit(child,inverted)
    elif k=='direct_sum':
        a,b=r.children;items=[(a,0),(b,a.n)]
        for child,off in (reversed(items) if inverted else items):
            for op in emit(child,inverted):yield relabel(op,lambda i:i+off)
    elif k=='tensor':
        a,b=r.children;groups=[(a,b.n,'columns'),(b,a.n,'rows')]
        for child,repeats,which in (reversed(groups) if inverted else groups):
            for j in (range(repeats-1,-1,-1) if inverted else range(repeats)):
                f=(lambda i:i*b.n+j) if which=='columns' else (lambda i:j*b.n+i)
                for op in emit(child,inverted):yield relabel(op,f)
    elif k=='extend':yield from emit(r.children[0],inverted)
    elif k=='conjugate':
        t,a=r.children;yield from emit(t);yield from emit(a,inverted);yield from emit(t,True)
    elif k=='guard':
        s,c=r.children;h=tensor(identity(s.n),c)
        yield from emit(h)
        indices=range(r.data['rank']-1,-1,-1) if inverted else range(r.data['rank'])
        for j in indices:
            for op in emit(s,inverted):yield relabel(op,lambda i:i*c.n+j)
        yield from emit(h,True)
    else:raise ValueError('unknown recipe '+k)

@dataclass(frozen=True)
class Tagged:
    basis:Recipe
    rank:int
    def __post_init__(self):need(0<=self.rank<=self.basis.n,'tagged rank')

def tagged_sum(p,q):
    n,m=p.basis.n,q.basis.n
    active=list(range(p.rank))+list(range(n,n+q.rank))
    order=active+[j for j in range(n+m) if j not in set(active)]
    return Tagged(multiply(direct_sum(p.basis,q.basis),permutation(order)),p.rank+q.rank)
def tagged_tensor(p,q):
    n,m=p.basis.n,q.basis.n
    active=[i*m+j for i in range(p.rank) for j in range(q.rank)];chosen=set(active)
    order=active+[j for j in range(n*m) if j not in chosen]
    return Tagged(multiply(tensor(p.basis,q.basis),permutation(order)),p.rank*q.rank)
def split(p,selected):
    selected=tuple(selected);need(len(set(selected))==len(selected) and all(0<=i<p.rank for i in selected),'split must select distinct carried image columns')
    used=set(selected);order=selected+tuple(j for j in range(p.basis.n) if j not in used)
    return Tagged(multiply(p.basis,permutation(order)),len(selected))
def tagged_conjugate(p,t):
    need(p.basis.n==t.n,'tag conjugation dimensions');return Tagged(multiply(t,p.basis),p.rank)
def placed(p,active,ambient):
    active=tuple(active);need(len(active)==p.basis.n and len(set(active))==len(active) and all(0<=i<ambient for i in active),'complete local placement')
    used=set(active);pi=permutation(active+tuple(i for i in range(ambient) if i not in used))
    return Tagged(multiply(pi,extend(p.basis,ambient)),p.rank)
def matcher(p,q):
    need(p.basis.n==q.basis.n and p.rank==q.rank,'whole-job matcher requires equal dimension and rank')
    return multiply(p.basis,inverse(q.basis))

def euclidean_seed(matrix,label):
    """Genuine Euclidean row reduction of M^T; used only for fixed finite seeds."""
    n=len(matrix);need(n and all(len(r)==n for r in matrix),'square seed')
    a=[[F(matrix[j][i]) for j in range(n)] for i in range(n)];ops=[];euclid_steps=0
    need(all(x.denominator.bit_count()==1 for row in a for x in row),'seed entries outside Z[1/2]')
    def swap(i,j):
        if i!=j:a[i],a[j]=a[j],a[i];ops.append(('swap',i,j))
    def add(i,j,c):
        if c:a[i]=[x+c*y for x,y in zip(a[i],a[j])];ops.append(('add',i,j,str(c)))
    for j in range(n):
        candidates=[i for i in range(j,n) if a[i][j]];need(candidates,'singular seed');swap(j,candidates[0])
        for i in range(j+1,n):
            while a[i][j]:
                quotient=a[j][j]//a[i][j];add(j,i,-quotient);swap(j,i);euclid_steps+=1
        pivot=a[j][j];need(unit(pivot),'seed determinant is not a dyadic unit')
        if pivot!=1:
            c=1/pivot;a[j]=[c*x for x in a[j]];ops.append(('scale',j,str(c)))
        for i in range(n):
            if i!=j:add(i,j,-a[i][j])
    need(a==[[F(i==j) for j in range(n)] for i in range(n)],'Euclidean reduction endpoint')
    out=literal(n,[invert_op(op) for op in reversed(ops)],label)
    return out,dict(euclidean_steps=euclid_steps,elimination_operations=len(ops))

def expanded_ordered_ops(r,inverted=False):
    for op in emit(r,inverted):
        if op[0]=='add' and op[1]<op[2]:
            i,j=op[1:3];yield ('swap',i,j);yield ('add',j,i,op[3]);yield ('swap',i,j)
        elif op[0]=='scale':
            x=F(op[2]);need(unit(x),'nonunit scale');negative=x<0;x=abs(x);factors=[]
            while x>1:factors.append(F(2));x/=2
            while x<1:factors.append(F(1,2));x*=2
            if negative:
                if factors:factors[0]=-factors[0]
                else:factors=[F(-1)]
            for c in factors:yield ('scale',op[1],str(c))
        else:yield op
