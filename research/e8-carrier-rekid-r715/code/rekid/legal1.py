# Task 1 census: for each needed composite symbol S, find tot-minus-complement identities S = Tot(F) ^ C
# with F a flat (closed mask) inside frame(S) and C a XOR of <=2 existing symbols (frames inside frame(S)), C != S.
import os,sys,pickle,itertools,time
os.environ['E8COORD']='ham'
import frames as Fm, e8lib as E, ham1, compile2 as C2
from collections import Counter,defaultdict
h=pickle.load(open('h865.pkl','rb'))
V=120; N=len(h.content)
needed=C2.needed_symbols(h)
pc=lambda m: bin(m).count('1')
# natural flats: frames of all symbols + all lines (sources) + frames of targets prefixes (HYP) + joins of pairs of symbol frames up to dim 6
flats=set(h.frame[u] for u in range(N))
flats.add(0)
print('natural flats (symbol frames)',len(flats))
# existing symbols (non-source) as candidates for C
syms=[u for u in range(V,N)]
bycont=defaultdict(list)
for u in range(N): bycont[h.content[u]].append(u)
cnt=Counter(); users=defaultdict(set); ex={}
t0=time.time()
for S in needed:
    if S<V: continue
    fS=h.frame[S]; cS=h.content[S]
    cand=[u for u in range(V,N) if Fm.inside(h.frame[u],fS) and u!=S]
    cand_c=[h.content[u] for u in cand]
    pairs={}
    for i,a in enumerate(cand_c):
        pairs.setdefault(a,(cand[i],))
    for i in range(len(cand)):
        for j in range(i+1,len(cand)):
            pairs.setdefault(cand_c[i]^cand_c[j],(cand[i],cand[j]))
    for F in flats:
        if F==0 or not Fm.inside(F,fS): continue
        T=F
        if T==cS: continue
        C=T^cS
        if C==0: continue
        # single source lines in C count as free singles: allow C = xor of <=2 symbols or C a single line
        if C in pairs or pc(C)==1:
            cnt[(pc(cS),h.dim[S])]+=1
            users[F].add(S)
            ex.setdefault(S,[]).append((F,C in pairs and pairs[C]))
print('time',time.time()-t0)
print('S with at least one tot-minus-complement identity:',len(ex),'of',len(needed)-V)
print('by (|S|,dim S):',sorted(cnt.items()))
big=sorted(users.items(),key=lambda kv:-len(kv[1]))[:10]
for F,us in big: print('flat dim',Fm.dim(F),'lines',pc(F),'used by',len(us))
