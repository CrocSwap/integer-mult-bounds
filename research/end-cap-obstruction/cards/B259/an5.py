from an1 import *
import sys
def dot(a,b): return bin(a&b).count('1')&1
for path in sys.argv[1:]:
    w=load(path);P=w['ports'];cur,rd=frames(w)
    bad=[t for t in range(V) if G.basis(list(cur[V+t])+list(G.perp(P[t])))!=G.perp(P[t])]
    ops=collections.defaultdict(list)
    for part in 'AB':
        for e in w[part]:
            F=G.basis(e[-1])
            for r in [e[1]]+([e[2]] if e[0]=='add' else []): ops[r].append((part,F))
    out=[]
    for g in range(0,len(bad),4):
        grp=bad[g:g+4]
        I={x for x in range(512) if all(dot(x,P[t])==0 for t in grp)}
        srcs=set()
        for t in grp: srcs|=rd[V+t]
        srcs-={V+t for t in grp}
        ex=0;nb=0;shared=0
        for s in srcs:
            e_s=0
            for part,F in ops[s]:
                S=sp(F) if F else {0}
                i=len([x for x in S if x in I]).bit_length()-1
                if i<len(F): e_s+=len(F)-i;nb+=1
            ex+=e_s
        out.append((grp,len(srcs),ex,nb))
    print(path.split('/')[-3],out)
