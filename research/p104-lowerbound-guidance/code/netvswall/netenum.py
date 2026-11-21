import itertools, sys
from nv import *
def node_list(h,dmax):
    subs=subspaces(h); out=[]
    for a in subs:
        for b in subs:
            if b<=a and dimof(a)-dimof(b)<=dmax: out.append((a,b))
    return out
def count(h,labs,m,dmax):
    N=node_list(h,dmax); n=len(labs)
    A=lambda nd: frozenset(i for i,q in enumerate(labs) if q in nd[0])
    B=lambda nd: frozenset(i for i,q in enumerate(labs) if all(dot(q,y)==0 for y in nd[1]))
    tot=0
    for nodes in itertools.combinations_with_replacement(range(len(N)),m):
        d=[dimof(N[i][0])-dimof(N[i][1]) for i in nodes]
        if sum(d)>n-1: continue
        tot+=1
    return len(N),tot
h=int(sys.argv[1]); labs=[int(x) for x in sys.argv[2].split(',')]
for m in (2,3): print(m,count(h,labs,m,len(labs)-1))
