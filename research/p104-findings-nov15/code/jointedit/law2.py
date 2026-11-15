# Lock test: for each contact at main stop G (main P->G->N, partner A->G->B), the charts X where both can meet with
# all four neighbours kept are  join(P,A) <= X <= meet(N,B).  Forced iff join == meet == G.
import jl, pricekit as pk, pickle
from collections import Counter
W=pk.load('inputs/ATTACK/STACK7616/best7616.json.gz'); M=jl.Word(W)
sp=M.sp; fr=W['frames']
def join(a,b):
    S={0}
    for v in fr[a]+fr[b]:
        if v not in S: S|={x^v for x in S}
    m=0
    for x in S: m|=1<<x
    return m
def nb(po,G):
    k=po.index(G); return (po[k-1] if k>0 else None, po[k+1] if k+1<len(po) else None)
c=Counter(); st=Counter(); rows=[]
for m in sorted(M.mains):
    o=M.path(m)
    for gi in range(1,len(o)-1):
        P,G,N=o[gi-1],o[gi],o[gi+1]; locks=[]
        for i in [i for i in M.ops[m] if M.tag[i]==G]:
            e=M.ev[i]
            if e[0]=='SCALE': continue
            p=e[2] if e[1]==m else e[1]
            if p>=M.n: locks.append('owned'); continue
            A,B=nb(M.path(p),G)
            lo = join(P,A) if A is not None else sp[P]
            hi = (sp[N]&sp[B]) if B is not None else sp[N]
            jf = lo==sp[G]; mf = hi==sp[G]
            if A is not None and (sp[A]&~sp[P])==0 or B is not None and (sp[N]&~sp[B])==0 or B is None or A is None: k='free'
            elif jf and mf: k='forced'
            elif jf: k='join'      # lower side forced, room above G
            elif mf: k='meet'
            else: k='room'
            c[k]+=1; locks.append(k)
        b=[k for k in locks if k!='free']
        st[(len(b),) if len(b)!=1 else (1,b[0])]+=1
print('contacts',c); print('stops',sorted(st.items(),key=str))
