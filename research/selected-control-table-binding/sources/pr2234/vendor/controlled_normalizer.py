"""Full-prefix coefficients and a common ordered-ADD adapter schedule.

Normal-form algebra: retained source527 and commdata2338's PR2160.
Physical continuation: Jose Manuel, with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from collections import Counter
from dataclasses import dataclass,field,replace
from math import gcd


def need(condition,message):
    if not condition:raise ValueError(message)


def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]


@dataclass
class Arithmetic:
    modulus:int
    counts:Counter=field(default_factory=Counter)
    prefix_cells:int=0

    def mul(self,a,b):
        self.counts["ring_multiply"]+=1
        return a*b%self.modulus

    def add(self,a,b):
        self.counts["ring_add"]+=1
        return (a+b)%self.modulus

    def inv(self,a):
        need(gcd(a,self.modulus)==1,"unit inversion")
        self.counts["unit_inverse"]+=1
        return pow(a,-1,self.modulus)


def matmul(a,b,arithmetic):
    out=[[0]*len(b[0]) for _ in a]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    if y:out[i][j]=arithmetic.add(out[i][j],arithmetic.mul(x,y))
    return out


def inverse(a,arithmetic):
    n=len(a);rows=[list(row)+unit for row,unit in zip(a,eye(n))]
    modulus=arithmetic.modulus
    for j in range(n):
        pivot=next((i for i in range(j,n) if gcd(rows[i][j],modulus)==1),None)
        need(pivot is not None,"invertible current full header")
        rows[j],rows[pivot]=rows[pivot],rows[j]
        unit=arithmetic.inv(rows[j][j])
        rows[j]=[arithmetic.mul(unit,x) for x in rows[j]]
        for i in range(n):
            if i==j or not rows[i][j]:continue
            c=rows[i][j]
            rows[i]=[arithmetic.add(x,-arithmetic.mul(c,y)) for x,y in zip(rows[i],rows[j])]
    need([row[:n] for row in rows]==eye(n),"inverse endpoint")
    return [row[n:] for row in rows]


@dataclass(frozen=True)
class ParentPrefix:
    """Allowed descriptor fields. Fresh child stock is a separate argument."""
    q:int
    width:int
    low:tuple
    high:tuple
    ancestor_weights:tuple
    atom_columns:int

    def full_matrix(self,arithmetic,low_only=False):
        n=len(self.low);cap=self.q**(self.width-1)
        need(n==len(self.high) and all(len(r)==n for r in self.low+self.high),"header dimensions")
        result=[]
        for a,b in zip(self.low,self.high):
            row=[]
            for low,high in zip(a,b):
                need(0<=low<self.q and 0<=high<cap,"low/high digit ranges")
                arithmetic.prefix_cells+=2
                row.append(low+(0 if low_only else self.q*high))
            result.append(row)
        return result

    def weights(self,arithmetic):
        need(len(self.ancestor_weights)==len(self.low)*self.atom_columns,"ancestor weight extent")
        out=[]
        for unit in self.ancestor_weights:
            arithmetic.prefix_cells+=1
            need(0<=unit<arithmetic.modulus and gcd(unit,self.q)==1,"ancestor weight is a unit")
            out.append(unit)
        return out


@dataclass
class Prepared:
    n:int
    rank:int
    f:int
    modulus:int
    projector:list
    pivots:tuple
    rows:tuple
    columns:tuple
    cross:list
    weights:tuple
    arithmetic:Arithmetic


@dataclass(frozen=True)
class GoodWeightChain:
    """Older-to-newer good ancestors, each with its own coarse column width.

    An ancestor prefix's weight tuple is a charged unit scratch vector for
    extracting unweighted pivots. The generated weights come from root_unit
    and the full ancestor matrices, via the retained child index rule.
    """
    current:ParentPrefix
    ancestors:tuple
    root_unit:int


def prepare_good_chain(control,axes,low_only_current=False,low_only_ancestors=False):
    prefix=control.current;modulus=prefix.q**prefix.width
    need(gcd(control.root_unit,modulus)==1,"unit root weight")
    aggregate=Arithmetic(modulus);forms=[]
    for ancestor,ancestor_axes in control.ancestors:
        need((ancestor.q,ancestor.width)==(prefix.q,prefix.width),"one atom radix and width down the coarse chain")
        form=prepare(ancestor,ancestor_axes,low_only_ancestors)
        aggregate.counts.update(form.arithmetic.counts);aggregate.prefix_cells+=form.arithmetic.prefix_cells
        forms.append(form)
    for previous,later in zip(forms,forms[1:]):
        need(later.f==previous.rank*previous.f//later.n,"successive coarse child width")
    if forms:
        need(prefix.atom_columns==forms[-1].rank*forms[-1].f//len(prefix.low),"current coarse child width")
    weights=[]
    for index in range(len(prefix.low)*prefix.atom_columns):
        value=control.root_unit%modulus
        aggregate.counts["root_weight_evaluation"]+=1
        for form in forms:
            k,j=divmod(index,form.f)
            need(k<form.rank,"descendant index lies in each ancestor child")
            need(k*form.f+j==index,"ancestor flat-index rule")
            value=aggregate.mul(value,form.pivots[k])
        weights.append(value)
    prepared=prepare(replace(prefix,ancestor_weights=tuple(weights)),axes,low_only_current)
    prepared.arithmetic.counts.update(aggregate.counts)
    prepared.arithmetic.prefix_cells+=aggregate.prefix_cells
    return prepared


def prepare(prefix,axes,low_only=False):
    """Read the full allowed prefix and compute each ring coefficient.

    All ADD slots remain in rows/columns, including coefficients equal to zero.
    Runtime ring counts include elimination and inversion; they are not TM steps.
    """
    n=len(prefix.low);r=len(axes);modulus=prefix.q**prefix.width
    need(prefix.q>=3 and prefix.q%2 and prefix.width>=1 and prefix.atom_columns>=1
         and 1<=r<n<=64,"preparation domain")
    need(len(set(axes))==r and all(0<=k<n for k in axes),"coordinate projector label")
    arithmetic=Arithmetic(modulus)
    g=prefix.full_matrix(arithmetic,low_only);gi=inverse(g,arithmetic)
    weights=prefix.weights(arithmetic)
    projector=matmul([[row[k] for k in axes] for row in g],[gi[k] for k in axes],arithmetic)
    a=[row[::-1] for row in projector];left,right=eye(n),eye(n)
    rows,columns,pivots=[],[],[]
    for k in range(r):
        column=n-1-k;pivot=a[k][column]
        need(gcd(pivot,prefix.q)==1,"nongeneric low class")
        pivots.append(pivot);pinv=arithmetic.inv(pivot)
        for i in range(k+1,n):
            c=-arithmetic.mul(a[i][column],pinv)%modulus;rows.append((i,k,c))
            if c:
                a[i]=[arithmetic.add(x,arithmetic.mul(c,y)) for x,y in zip(a[i],a[k])]
                left[i]=[arithmetic.add(x,arithmetic.mul(c,y)) for x,y in zip(left[i],left[k])]
        for j in range(column):
            c=-arithmetic.mul(a[k][j],pinv)%modulus;columns.append((column,j,c))
            if c:
                for i in range(n):
                    a[i][j]=arithmetic.add(a[i][j],arithmetic.mul(c,a[i][column]))
                    right[i][j]=arithmetic.add(right[i][j],arithmetic.mul(c,right[i][column]))
    target=[[0]*n for _ in range(n)]
    for k,pivot in enumerate(pivots):target[k][n-1-k]=pivot
    need(a==target,"rank and complete cross block")
    li,ri=inverse(left,arithmetic),inverse(right,arithmetic)
    lp=matmul(left,projector,arithmetic)
    a0=[[-x%modulus for x in row] for row in matmul(lp,li,arithmetic)[:r]]
    # B=-R^-1 C L^-1 E, obtained from the exact normalized YY block.
    b=[[-x%modulus for x in row] for row in matmul(ri,[row[:r] for row in li[::-1]],arithmetic)]
    cross=[[0]*n for _ in range(n)]
    for k,pivot in enumerate(pivots):
        pinv=arithmetic.inv(pivot)
        for i in range(n):cross[i][k]=(-b[i][k]-int(i==n-1-k)*pinv)%modulus
        for j in range(r,n):cross[n-1-k][j]=arithmetic.mul(pinv,a0[k][j])
    return Prepared(n,r,prefix.atom_columns,modulus,projector,tuple(pivots),
                    tuple(rows),tuple(columns),cross,tuple(weights),arithmetic)


def schedule(n,rank,f):
    """Only dimension, rank and f determine slots; no coefficient is inspected."""
    need(1<=rank<n and f>=1,"schedule dimensions")
    forward=[]
    for j in range(f):
        row_slot=column_slot=0
        for k in range(rank):
            for i in range(k+1,n):
                forward.append(("head",i*f+j,k*f+j,row_slot,j,1));row_slot+=1
        for k in range(rank):
            column=n-1-k
            for source in range(column):
                forward.append(("tail",n*f+column*f+f-1-j,n*f+source*f+f-1-j,column_slot,j,-1));column_slot+=1
        for i in range(n):
            for k in range(n):
                forward.append(("cross",n*f+i*f+f-1-j,k*f+j,i*n+k,j,1))
    need(all(target>source for _,target,source,_,_,_ in forward),"later-target schedule")
    backward=[(*slot[:5],-slot[5]) for slot in reversed(forward)]
    return forward,backward


def coefficient(prepared,slot):
    kind,_,_,index,j,sign=slot
    m,n,f=prepared.modulus,prepared.n,prepared.f
    if kind=="head":
        i,k,c=prepared.rows[index]
        value=prepared.arithmetic.mul(prepared.arithmetic.mul(c,prepared.weights[i*f+j]),
                                      prepared.arithmetic.inv(prepared.weights[k*f+j]))
    elif kind=="tail":value=prepared.columns[index][2]
    elif kind=="cross":
        i,k=divmod(index,n)
        value=prepared.arithmetic.mul(prepared.cross[i][k],prepared.arithmetic.inv(prepared.weights[k*f+j]))
    else:raise ValueError("unknown adapter kind")
    return sign*value%m


def child_weights(prepared):
    return tuple(prepared.weights[k*prepared.f+j]*pivot%prepared.modulus
                 for k,pivot in enumerate(prepared.pivots) for j in range(prepared.f))


def execute_addresses(prepared,head,tail):
    """Reference address execution, not the physical stream regression."""
    values=list(head)+list(tail);forward,backward=schedule(prepared.n,prepared.rank,prepared.f)
    for slot in forward:
        _,target,source,_,_,_=slot
        values[target]=(values[target]+coefficient(prepared,slot)*values[source])%prepared.modulus
    for i,weight in enumerate(child_weights(prepared)):
        j=len(values)-1-i
        values[i],values[j]=weight*values[j]%prepared.modulus,pow(weight,-1,prepared.modulus)*values[i]%prepared.modulus
    for slot in backward:
        _,target,source,_,_,_=slot
        values[target]=(values[target]+coefficient(prepared,slot)*values[source])%prepared.modulus
    return values[:len(head)],values[len(head):]
