# F4 facts (other 4-circuits) from left_nonXX.txt; orbit-mapped counts of directions served per X shape.
import numpy as np, pickle, sys, itertools, glob
from collections import Counter, defaultdict
import p112 as p
G=np.load('G.npy'); PL=p.PL; Pidx=np.array(p.P); inv={g:i for i,g in enumerate(p.P)}
reps=pickle.load(open('dirreps.pkl','rb'))
pcnt=lambda x:bin(x).count('1')
def lines(x): return [i for i in range(112) if x>>i&1]
rank=lambda ls:p.f2rank([PL[i] for i in ls])
def span(vs):
    S={0}
    for v in vs:
        if v not in S: S|={s^v for s in S}
    return S
def flats4_containing(vs):
    S=span(vs); k=len(S).bit_length()-1
    if k>4: return []
    if k==4: return [frozenset(S)]
    out=set()
    def ext(S):
        if len(S)==16: out.add(frozenset(S)); return
        for v in range(1,512):
            if v not in S: ext(S|{s^v for s in S})
    ext(S); return list(out)
lam=lambda F: sum(1<<i for i in range(112) if PL[i] in F)
summary=[]
A=defaultdict(set); B=defaultdict(set)   # X-shape -> set of (mask-id) served ; mask-id = orbit image bits
famflag=[]
for k,(sz,osz,o,tags) in enumerate(reps):
    fn='left_non%02d_%d.txt'%(k,sz)
    try: f=open(fn)
    except: summary.append((k,sz,'MISSING')); continue
    hdr=f.readline().strip(); L=[]
    for line in f:
        lo,hi=line.split(); L.append(int(lo,16)|(int(hi,16)<<64))
    L=sorted(set(L),key=pcnt); mins=[]
    for x in L:
        if not any((m&~x)==0 for m in mins): mins.append(x)
    hist=sorted(Counter(map(pcnt,mins)).items())
    mn=min(map(pcnt,mins)) if mins else '>9'
    six=[x for x in mins if pcnt(x)==6]
    bad6=[x for x in six if any(rank(c)<=3 for c in itertools.combinations(lines(x),4))]
    formF=[]
    for x in mins:
        ls=lines(x)
        if len(ls)>9: continue
        if rank(ls)<=4 or any(rank([i for i in ls if i!=l])<=4 for l in ls): formF.append(x)
    isfam=any(t[0]=='r6fam' for t in tags)
    summary.append((k,sz,osz,'fam' if isfam else 'r7',hdr.split()[-1],'min',mn,'hist',hist,'six',len(six),'bad6',len(bad6),'formF',len(formF),[ (pcnt(x),rank(lines(x))) for x in formF][:5]))
    if formF:
        if isfam: famflag.append((k,sz))
        # map over orbit: for each g, image of mask & leftovers
        seenm={}
        for g in G:
            gm=0
            for i in o: gm|=1<<inv[int(g[i])]
            if gm in seenm: continue
            seenm[gm]=1
            for x in formF:
                y=0
                for i in lines(x): y|=1<<inv[int(g[Pidx[i]])]
                ls=lines(y)
                if rank(ls)<=4:
                    for F in flats4_containing([PL[i] for i in ls]): A[F].add(gm)
                for l in ls:
                    rest=[i for i in ls if i!=l]
                    if rank(rest)<=4:
                        for F in flats4_containing([PL[i] for i in rest]):
                            if PL[l] not in F: B[(F,l)].add(gm)
for s in summary: print(s)
print('family masks with form-F leftovers (would give infinitely many directions):',famflag)
if A or B:
    print('X = 4-flat set: max #directions served',max((len(v) for v in A.values()),default=0),' #4-flats serving',len(A))
    best=0
    for (F,l),v in B.items(): best=max(best,len(A.get(F,set())|v))
    print('X = 4-flat set + 1 line: max #directions served',max(best,max((len(v) for v in A.values()),default=0)))
    pickle.dump({'A':dict(A),'B':dict(B)},open('formF.pkl','wb'))
