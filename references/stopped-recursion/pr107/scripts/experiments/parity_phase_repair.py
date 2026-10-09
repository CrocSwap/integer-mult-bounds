"""A deterministic frame-safe coarsening of the signed parity side DAG.

This repair spends too many roles in the target instance. Its budget is a
construction count, not a lower bound on all possible repairs.
"""
from functools import cache

from binary_phase_frames import basis,classify,contains,dot
from certify import require


@cache
def characteristic(U):
    """Characteristic vector w of a nondegenerate binary dot-product space."""
    U=basis(U);d=len(U)
    require(classify(U)['nondegenerate'],'Characteristic vector needs a nondegenerate space')
    rows=[sum(dot(a,b)<<j for j,b in enumerate(U)) | (dot(a,a)<<d) for a in U]
    for i in range(d):
        j=next(j for j in range(i,d) if rows[j]>>i&1)
        rows[i],rows[j]=rows[j],rows[i]
        for j in range(d):
            if j!=i and rows[j]>>i&1:rows[j]^=rows[i]
    w=0
    for i,row in enumerate(rows):
        if row>>d&1:w^=U[i]
    require(all(dot(w,x)==dot(x,x) for x in U),'Wrong characteristic vector')
    return w


def coarsen(c):
    S={};keep=set();chars={};inputs={t:i for i,t in enumerate(c.inputs)}
    for x in sorted(c.active):
        if c.args[x]:
            a,b=c.args[x];S[x]=basis(S[abs(a)]+S[abs(b)])
        else:S[x]=(c.inputs[x-1],)
        if not classify(S[x])['nondegenerate']:continue
        w=characteristic(S[x]);chars[x]=w
        supp=c.support[x][0]|c.support[x][1]
        if len(S[x])==1 or w not in inputs or not supp>>inputs[w]&1:keep.add(x)
    require(all(abs(x) in keep for x in c.outputs.values()),'An output fails the repair criterion')
    newargs={}
    for x in sorted(keep):
        if not c.args[x]:newargs[x]=();continue
        todo=list(c.args[x]);front=[]
        while todo:
            a=todo.pop();y=abs(a)
            if y in keep and (len(S[y])==len(S[x]) or not contains(S[y],chars[x])):
                front.append(a)
            else:
                require(c.args[y] is not None,'Unsafe source line cannot be expanded')
                todo.extend(z if a>0 else -z for z in c.args[y])
        newargs[x]=tuple(front)
    active=set();todo=[abs(x) for x in c.outputs.values()]
    while todo:
        x=todo.pop()
        if x in active:continue
        active.add(x);todo.extend(abs(a) for a in newargs[x])
    # Check the actual signed rows and every source-span edge, not only counts.
    edges=0
    full=(1<<c.h)-1
    for x in sorted(active):
        require(classify(S[x])['nondegenerate'] and classify(S[x])['nonalternating'],
                'Unsafe retained source span')
        require(not contains(S[x],full),'Final complement would be alternating')
        if not newargs[x]:continue
        p=n=0
        for a in newargs[x]:
            y=abs(a);yp,yn=c.support[y]
            if a<0:yp,yn=yn,yp
            require(not (p|n)&(yp|yn),'Coarsening introduced overlapping source support')
            p|=yp;n|=yn
            require(all(contains(S[x],v) for v in S[y]),'Non-nested repaired edge')
            require(len(S[x])==len(S[y]) or not contains(S[y],chars[x]),
                    'Nonzero alternating residual on a repaired edge')
            edges+=1
        require((p,n)==c.support[x],'Coarsening changed a signed coefficient')
    # Every final output must be exactly the nondegenerate target complement.
    for t,x in c.outputs.items():
        U=S[abs(x)]
        require(len(U)==c.h-1 and all(dot(v,t)==0 for v in U),
                'Wrong output frame')
    count=sum(max(0,len(newargs[x])-1) for x in active)+len(c.outputs)
    return dict(h=c.h,old_roles=sum(bool(c.args[x]) for x in c.active)+len(c.outputs),
                repaired_roles=count,retained_nodes=len(active),
                maximum_fanin=max(len(newargs[x]) for x in active),
                exact_signed_coefficients_verified=True,nested_edges_checked=edges,
                nonzero_residuals_nonalternating=True,source_and_output_boundaries_checked=True)


def five_point_obstruction():
    """Two source and two target triples force a nonzero common span vector."""
    a,b,c,d,e=(1<<i for i in range(5))
    S=(a|c|e,b|d|e);T=(a|b|e,c|d|e)
    v=S[0]^S[1]
    require(v and v==T[0]^T[1],'Missing common span vector')
    require(all(dot(x,y)==0 for x in S for y in T),'Not an allowed side rectangle')
    return dict(source_triples=S,target_triples=T,common_nonzero_vector=v,
                scope='No nondegenerate U with span(S) subset U subset span(T)^perp')
