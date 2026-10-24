"""Finite binary frame geometry and rooted cache-tree certificates.

Metric/Clifford principles are classical. Retain Dugongue's chart grammar,
Matarener's owned-center intersection proof, and the local geometry lineage.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter


def need(ok, why):
    if not ok:
        raise ValueError(why)


def span(basis):
    s={0}
    for x in basis:
        s |= {v^x for v in tuple(s)}
    return frozenset(s)


def dim(s):
    need(len(s)>0 and len(s)&(len(s)-1)==0,'binary subspace cardinality')
    return len(s).bit_length()-1


def distance(a,b):
    return dim(a)+dim(b)-2*dim(a&b)


def basis(s):
    rows={}
    for v in sorted(s):
        for p in sorted(rows,reverse=True):
            if v>>p&1:
                v^=rows[p]
        if v:
            rows[v.bit_length()-1]=v
    return list(rows.values())


def subspaces(n):
    seen={frozenset({0})}; todo=list(seen)
    while todo:
        s=todo.pop()
        for v in set(range(1<<n))-s:
            t=frozenset(s|{x^v for x in s})
            if t not in seen:
                seen.add(t);todo.append(t)
    return sorted(seen,key=lambda s:(len(s),sorted(s)))


def gf2_rank(rows):
    basis_={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p not in basis_:
                basis_[p]=x;break
            x^=basis_[p]
    return len(basis_)


def canonical_chart(u,n):
    """Inverse-image Lagrangian L_U={(x,x+z):x in U,z in U-perp}."""
    perp=[z for z in range(1<<n) if all((x&z).bit_count()%2==0 for x in u)]
    return span([x|((x^z)<<n) for x in u for z in perp])


def lagrangians(n):
    """All isotropic n-spaces, used only in the bounded n<=2 control."""
    out=[]
    for s in subspaces(2*n):
        if dim(s)!=n:
            continue
        b=basis(s); mask=(1<<n)-1
        if all((((a&mask)&(v>>n)).bit_count()+((v&mask)&(a>>n)).bit_count())%2==0
               for a in b for v in b):
            out.append(s)
    return out


def tree_bound(charts,parents):
    """Exact intersection-loss certificate for any equal-dimensional charts."""
    need(len(charts)==len(parents)>0 and parents[0] is None,'rooted tree')
    n=dim(charts[0]); common=charts[0]; mass=0; steps=[]
    for i in range(1,len(charts)):
        p=parents[i]
        need(type(p) is int and 0<=p<i,'parent precedes child')
        need(dim(charts[i])==n,'equal-dimensional Lagrangian charts')
        edge=n-dim(charts[p]&charts[i]);drop=dim(common)-dim(common&charts[i])
        need(drop<=edge,'intersection loss fits actual edge grade')
        common &= charts[i]; mass+=edge
        steps.append({'node':i,'parent':p,'grade':edge,'intersection_loss':drop})
    need(mass>=n-dim(common),'tree rank-mass floor')
    return {'edge_rank_mass':mass,'intersection_floor':n-dim(common),'steps':steps}


def fanout_program(n=3):
    """Two owned fields; original target updates remain in their given order."""
    z=[];line=[1];ab=[1,2];ac=[1,4]
    return [
        ['CLEAR','Z'],['CLEAR','W'],
        ['COPY','Z','X'],['MOVE','Z',z,line],
        ['COPY','W','Z'],['MOVE','W',line,ab],['ADD','Y1','W',1],['CLEAR','W'],
        ['COPY','W','Z'],['MOVE','W',line,ac],['ADD','Y2','W',1],['CLEAR','W'],
        ['CLEAR','Z']]


def dual_program():
    """Inverse-transpose main endpoint; reversed gather, same three grades."""
    z=[];line=[1];ab=[1,2];ac=[1,4]
    return [
        ['CLEAR','Z'],['CLEAR','W'],
        ['COPY','W','Y1'],['DUAL_MOVE','W',ab,line],['ADD','Z','W',1],['CLEAR','W'],
        ['COPY','W','Y2'],['DUAL_MOVE','W',ac,line],['ADD','Z','W',1],['CLEAR','W'],
        ['DUAL_MOVE','Z',line,z],['ADD','X','Z',-1],['CLEAR','Z']]


def tariffs(program):
    paid=Counter();ordinary=Counter()
    for e in program:
        if e[0] in ('MOVE','DUAL_MOVE'):
            r=distance(span(e[2]),span(e[3]))
            if r:paid[r]+=1
        else:ordinary[e[0]]+=1
    return {'paid':dict(sorted(paid.items())),'ordinary_field_passes':dict(sorted(ordinary.items())),
            'owned_fields':2,'new_productive_owners':0}
