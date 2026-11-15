# Why contacts at a main stop G cannot be re-hosted at P (main's prev) or N (main's next): partner neighbours A->G->B.
import jl, pricekit as pk
from collections import Counter
W=pk.load('inputs/ATTACK/STACK7616/best7616.json.gz'); M=jl.Word(W)
sp=M.sp; c=Counter(); single=Counter()
def nb(po,G):
    k=po.index(G); return (po[k-1] if k>0 else None, po[k+1] if k+1<len(po) else None)
for m in sorted(M.mains):
    o=M.path(m)
    for gi in range(1,len(o)-1):
        P,G,N=o[gi-1],o[gi],o[gi+1]
        kinds=[]
        for i in [i for i in M.ops[m] if M.tag[i]==G]:
            e=M.ev[i]
            if e[0]=='SCALE': continue
            p=e[2] if e[1]==m else e[1]
            if p>=M.n: kinds.append('owned'); continue
            po=M.path(p); A,B=nb(po,G)
            Pok = A is None or (sp[A]&~sp[P])==0     # p's previous chart inside P
            Nok = B is None or (sp[N]&~sp[B])==0     # N inside p's next chart
            join = A is not None and (sp[A]|sp[P])==sp[G]   # bitmask union of spans is not a span; check G = smallest span containing both
            k=('P' if Pok else '')+('N' if Nok else '')
            c['geo:'+(k or 'none')]+=1
            kinds.append('free' if k else 'geo')
        bl=[k for k in kinds if k!='free']
        if len(bl)==1: single[bl[0]]+=1
print(c); print('stops with exactly one geometrically blocked contact:',single)
