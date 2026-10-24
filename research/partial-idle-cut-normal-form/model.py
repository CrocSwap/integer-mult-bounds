"""Literal path-controller model and exact partial-idle projectors.

Prepared for Cinna Davis with substantial OpenAI Codex assistance; Apache-2.0.
Source controller: zxv; query thinning and joint frames: Cinna Davis.
"""
from collections import Counter
import math


def template(p):
    out=[];slots=[]
    def local(stage,j,back):
        out.append(('local',stage,j,back))
        if stage%2 and stage<=2*p-3:
            slots.append((j+1,tuple(range(stage+1))))
            out.append(('idle',len(slots)-1))
        elif stage%2==0 and 2<=stage<=2*p-2:
            slots.append((stage//2,(stage,)))
            out.append(('idle',len(slots)-1))
        elif stage==2*p:
            for k in range(p-1):
                slots.append((k,tuple(range(2*k+3,2*p+1))))
                out.append(('idle',len(slots)-1))
    def bridge(a,b,c):
        out.extend([('add',2*a,2*b,c),('add',2*b+1,2*a+1,-c)])
    local(0,0,False)
    for j in range(p):
        local(2*j+1,j,True)
        if j<p-1:bridge(j,j+1,1)
        local(2*j+2,j,False)
        if j<p-1:bridge(j,j+1,-1)
    for j in reversed(range(p-1)):bridge(j+1,j,1)
    out.extend(('swap',2*j,2*j+1) for j in range(p))
    return out,slots


def evaluate(p,events,assignment,values,q=None):
    n=2*p
    a=[[int(i==j) for j in range(n)] for i in range(n)]
    for e in events:
        if e[0]=='local':
            _,s,j,back=e;x,y=2*j,2*j+1
            if back:x,y=y,x
            coefficient=(-1 if back else 1) if q is None else (-q if back else 1/q)
            a[y]=[u+coefficient*v for u,v in zip(a[y],a[x])]
            d=values.get(s,1)
            a[x]=[d*v for v in a[x]];a[y]=[d*v for v in a[y]]
        elif e[0]=='idle':
            j,stages=assignment[e[1]]
            d=math.prod(values.get(s,1) for s in stages)
            for r in (2*j,2*j+1):a[r]=[d*v for v in a[r]]
        elif e[0]=='add':
            _,d,s,c=e;a[d]=[u+c*v for u,v in zip(a[d],a[s])]
        else:
            _,x,y=e;a[x],a[y]=a[y],[-v for v in a[x]]
    return a


def multiply(a,b):
    bt=list(zip(*b))
    return [[sum(x*y for x,y in zip(row,col)) for col in bt] for row in a]


def commute(a,b):
    return multiply(a,b)==multiply(b,a)



def vertex(p,stage):
    return 0 if stage == 0 else min((stage-1)//2,p-1)


def thick(p):
    return [0,*range(1,2*p,2),2*p]


def core(p,j,mask):
    if not mask >> j & 1: raise ValueError('Native vertex absent')
    lo=hi=j
    while lo and mask >> (lo-1) & 1: lo-=1
    while hi+1<p and mask >> (hi+1) & 1: hi+=1
    return lo,hi


def projector(p,j,mask):
    v=[mask>>i&1 for i in range(p)]
    return [[v[i] if i==k else ((-1)**(k-i)*(v[k]-v[k-1])
             if i<k<=j else 0) for k in range(p)] for i in range(p)]


def family_invoice(p,masks,block=8,ports=112,helpers=None,paid_local=None):
    stages=thick(p)
    if len(masks)!=len(stages):raise ValueError('Wrong number of stage sets')
    main=Counter();paid=Counter();counts=[[0,0,0] for _ in range(p)]
    for stage,mask in zip(stages,masks):
        j=vertex(p,stage)
        if not mask>>j&1:raise ValueError('Missing native stage')
        for i in range(p):
            if mask>>i&1:
                counts[i][0 if i==j else 1 if i>j else 2]+=1
    for n,a,b in counts:
        main[1+block*(n+a+b)]+=2*ports
        if a:paid[block*a]+=2*ports
        if b:paid[block*b]+=2*ports
    targets=main.copy()
    if helpers is not None:targets.update({r:len(stages)*m for r,m in helpers.items()})
    if paid_local is not None:paid.update({r:len(stages)*m for r,m in paid_local.items()})
    if paid_local is not None:paid[1]+=ports*(p-1)
    return targets,paid


def canonical_masks(p,cut):
    return [sum(1<<i for i in range(min(vertex(p,s),cut),max(vertex(p,s),cut)+1))
            for s in thick(p)]
