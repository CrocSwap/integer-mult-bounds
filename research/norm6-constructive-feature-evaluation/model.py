"""Explicit shell-independent feature elimination. JoyboyBrian; Apache-2.0."""
from fractions import Fraction as Q
from itertools import combinations


def need(ok, message):
    if not ok:
        raise ValueError(message)


def features(d):
    return ([('f',i) for i in range(d)]+[('l',i) for i in range(d)]+
            [('s',i,j) for i in range(d) for j in range(d) if i!=j]+
            [('t',*v) for v in combinations(range(d),3)])


def relations(g):
    d=len(g); result=[]
    for i in range(d):
        row={('f',i):Q(3*g[i][i],2),('l',i):Q(g[i][i]-6,2)}
        for j in range(d):
            if j!=i:
                row[('s',j,i)]=Q(g[j][j],2)
                row[('s',i,j)]=Q(g[i][j])
        for j,k in combinations([a for a in range(d) if a!=i],2):
            row[('t',*sorted((i,j,k)))]=Q(g[j][k])
        result.append({k:v for k,v in row.items() if v})
    return result


def compile_features(g):
    d=len(g)
    need(d==48 and all(len(row)==d for row in g),'actual dimension48')
    need(all(g[i][j]==g[j][i] and isinstance(g[i][j],int)
             for i in range(d) for j in range(d)),'symmetric integer Gram')
    need(set(g[i][i] for i in range(d))<={6,8,10},'admitted diagonal')
    anchor=next(i for i in range(d) if g[i][i]==8)
    old=features(d); rs=relations(g)
    pivots=[('s',anchor,i) if g[i][i]==6 else ('l',i) for i in range(d)]
    removed=set(pivots); keep=[k for k in old if k not in removed]; solved={}
    for i in [a for a in range(d) if a!=anchor]+[anchor]:
        row=dict(rs[i]); pivot=pivots[i]; value=row.pop(pivot)
        for k in list(row):
            if k in removed:
                coefficient=row.pop(k)
                need(k in solved,'one-layer pivot dependence')
                for term,v in solved[k].items():
                    row[term]=row.get(term,Q(0))+coefficient*v
        solved[pivot]={k:-v/value for k,v in row.items() if v}
        need(not(set(solved[pivot])&removed),'retained features only')
    need(len(keep)==19600 and len(solved)==48,'complete48-feature elimination')
    need(all(v.denominator in (1,2,4) for row in solved.values() for v in row.values()),'quarter-integral transform')
    return old,keep,solved,anchor


def source_value(key,x):
    kind,*a=key
    if kind=='f':
        v=x[a[0]]; return (v*v*v-v)//3
    if kind=='l': return x[a[0]]
    if kind=='s': return x[a[0]]**2*x[a[1]]
    return x[a[0]]*x[a[1]]*x[a[2]]


def target_value(key,v):
    kind,*a=key
    if kind=='f': return v[a[0]]**3
    if kind=='l':
        z=v[a[0]]; return (z*z*z-z)//3-z
    if kind=='s': return v[a[0]]**2*v[a[1]]
    return 2*v[a[0]]*v[a[1]]*v[a[2]]


def evaluate(g,compiled,y):
    """Return quarter-scaled target numerators; final pairing divides by256."""
    old,keep,solved,_=compiled
    v=[sum(a*b for a,b in zip(row,y)) for row in g]
    result={key:4*target_value(key,v) for key in keep}
    for pivot,row in solved.items():
        weight=target_value(pivot,v)
        for key,c in row.items():
            result[key]+=int(4*c)*weight
    return result


def bounds(g,compiled):
    old,keep,solved,anchor=compiled
    coefficients={k:4 for k in keep}
    for row in solved.values():
        for key,c in row.items(): coefficients[key]+=abs(int(4*c))
    mass=max(coefficients.values()); edges=sum(map(len,solved.values()))
    height=max(abs(int(4*c)) for row in solved.values() for c in row.values())
    return {'anchor':anchor,'diagonal_counts':{str(z):sum(row[i]==z for i,row in enumerate(g)) for z in (6,8,10)},
            'old_terms':len(old),'new_terms':len(keep),'transform_nonzeros':edges,
            'quarter_scaled_coefficient_max':height,'target_accumulator_mass':mass,
            'target_denominator':256,'target_magnitude_bound':'2*mass*V^3/256',
            'target_integer_accumulator_bound':'2*mass*V^3',
            'evaluation_integer_multiplications':48*48+2*19648+edges,
            'evaluation_integer_additions_upper':48*48+3*19648+edges,
            'evaluation_exact_divisions_by3':48,
            'source_integer_multiplications_upper':2*19600,
            'source_integer_additions_upper':19600,
            'source_exact_divisions_by3':48,
            'target_workspace_integer_slots_upper':19600+2*48+16,
            'source_stream_workspace_integer_slots_upper':48+16,
            'descriptor_integer_slots_upper':4*19648+3*edges+48*48,
            'descriptor_generation_rational_ops_upper':2000000}
