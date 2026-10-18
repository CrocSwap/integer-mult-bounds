import sys,collections,pickle
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B251')
from feas import *
Fx=set(range(224))|set(w['centers'])
# events: add ops in A,B,E sections (frames defined) whose TARGET is a fixed register: carrier = e[2]
def build_events():
    ops=[(i,tag,e) for i,(tag,e) in enumerate(prog) if e[0]=='add' and tag[0] in 'ABE']
    # target-chain: cap via backward pass over target ops only; L via forward pass
    Ls={};caps={}
    cur={}
    for i,tag,e in ops:
        x=e[1]
        if x in Fx:
            c=cur.get(x,start[x]);L=join(B(e[-1]),c);Ls[i]=L;cur[x]=L
    capq={}
    for i,tag,e in reversed(ops):
        x=e[1]
        if x in Fx:
            c=capq.get(x,end[x]);
            # cap = intersection(c, ...) ; ops frame subset of c. intersection of subspaces: store as member bitmask? use membership
            capq[x]=c;caps[i]=c
            # monotone: earlier ops must be inside this op's frame, so next cap for earlier = cap(o) itself bounded by F_o <= c ; we use c (upper) only
    return ops,Ls,caps
