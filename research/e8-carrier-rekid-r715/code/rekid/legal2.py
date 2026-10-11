import os,sys,pickle,itertools,time
os.environ['E8COORD']='ham'
import frames as Fm, e8lib as E, ham1, compile2 as C2
from collections import Counter,defaultdict
h=pickle.load(open('h865.pkl','rb'))
V=120; N=len(h.content)
needed=C2.needed_symbols(h)
pc=lambda m: bin(m).count('1')
flats=sorted(set(h.frame[u] for u in range(N)) | set(Fm.HYP))
flats=[F for F in flats if Fm.dim(F)>=2]
print('flats dim>=2:',len(flats))
# candidate "C" building blocks: existing symbols + single lines, and XOR of up to 3 of them (mitm 1+2)
allsyms=list(range(0,N))   # includes sources
bycount=Counter()
found=defaultdict(list)
t0=time.time()
for S in needed:
    if S<V: continue
    fS=h.frame[S]; cS=h.content[S]
    cand=[u for u in allsyms if Fm.inside(h.frame[u],fS) and u!=S and h.content[u]!=cS]
    cc=[h.content[u] for u in cand]
    one={}
    for i,a in enumerate(cc): one.setdefault(a,(cand[i],))
    two={}
    for i in range(len(cand)):
        for j in range(i+1,len(cand)):
            two.setdefault(cc[i]^cc[j],(cand[i],cand[j]))
    for F in flats:
        if not Fm.inside(F,fS): continue
        if pc(F)<=pc(cS): continue
        C=F^cS
        if pc(C)>=pc(cS): continue    # complement must be smaller than S
        hit=one.get(C) or two.get(C)
        if hit: found[S].append((F,hit))
print('time',time.time()-t0)
print('S with a smaller-complement identity (|F|>|S|, |C|<|S|, C = <=2 existing symbols/lines):',len(found))
c=Counter()
for S,l in found.items():
    c[(pc(h.content[S]),h.dim[S],len(l))]+=1
print(sorted(c.items()))
for S,l in list(found.items())[:6]:
    for F,hit in l[:3]:
        print('S',pc(h.content[S]),'dim',h.dim[S],'F dim',Fm.dim(F),'|F|',pc(F),'C=',[ (pc(h.content[u]),h.dim[u]) for u in hit])
