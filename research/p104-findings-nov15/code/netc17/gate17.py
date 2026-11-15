"""NETC17 gate: distinct delivered pi-contents of a word + ratio-keyed greedy pair CSE (indexed). usage: gate17.py word.json.gz tag"""
import sys, collections, itertools, pickle, time, statistics as S
W5='inputs/'
sys.path.insert(0, W5+'REBUILDKIT')
from load import Word
from fractions import Fraction as Fr
P=2**61-1
path,tag=sys.argv[1],sys.argv[2]; CAP=int(sys.argv[3]) if len(sys.argv)>3 else 40
w=Word(path); W=w.W; n=w.n; N=w.N; dim=w.dim
Hs=set(r for r in range(n) if w.cls[r]=='h'); top=max(dim)
# a "helper" = class-h register that ever gives to a non-helper (carrier) or is read; census as NETC16
rows=[({r:1} if r<n else {}) for r in range(N)]
def md(q):
    q=Fr(q); return q.numerator%P*pow(q.denominator%P,P-2,P)%P
def add(R,a,S_):
    for k,v in S_.items():
        nv=(R.get(k,0)+a*v)%P
        if nv: R[k]=nv
        else: R.pop(k,None)
pi=lambda R: frozenset((k,v) for k,v in R.items() if k not in Hs)
touched=set(); givers=set(); gives=[]; hhreads=0
for t,e in enumerate(W['program']):
    op=e[0]; r=e[1]
    if op=='MOVE': continue
    if op in('INIT','CLEAR'): rows[r]={}; continue
    if op=='SCALE':
        q=md(e[2]); rows[r]={k:v*q%P for k,v in rows[r].items()}; continue
    s=e[2]; q=md(e[3])
    if r in Hs: touched.add(r)
    if s in Hs:
        touched.add(s)
        if r in Hs: hhreads+=1
        else:
            c=pi(rows[s])
            if c: gives.append((s,c)); givers.add(s)
    add(rows[r],q,rows[s])
nh=len(touched)
C=set(c for _,c in gives)
print(tag,'helpers touched',nh,'giving',len(givers),'hh reads',hhreads,'pi gives',len(gives),'distinct contents',len(C),'mean supp %.1f med %s'%(S.mean(len(c) for c in C),S.median(len(c) for c in C)),flush=True)
# projective normalisation
def norm(c):
    d=dict(c); k0=min(d); inv=pow(d[k0],P-2,P); return {k:v*inv%P for k,v in d.items()}
R=set(frozenset(norm(c).items()) for c in C); print('distinct projective contents',len(R))
rows=[dict(r) for r in R]; sub=[i for i,r in enumerate(rows) if len(r)<=CAP]
print('rows<=%d'%CAP,len(sub),'of',len(rows),'terms',sum(len(rows[i]) for i in sub),'naive adds',sum(len(rows[i])-1 for i in sub),flush=True)
big_adds=sum(len(r)-1 for r in rows if len(r)>CAP)
inv=lambda x: pow(x,P-2,P)
def pairs(r):
    ks=sorted(r)
    for i,a in enumerate(ks):
        ia=inv(r[a])
        for b in ks[i+1:]: yield (a,b,r[b]*ia%P)
idx=collections.defaultdict(set)
for i in sub:
    for p in pairs(rows[i]): idx[p].add(i)
import heapq
heap=[(-len(v),p) for p,v in idx.items() if len(v)>=2]; heapq.heapify(heap)
nxt=10**9; steps=0; t0=time.time()
while heap:
    negc,p=heapq.heappop(heap)
    cur=idx.get(p,())
    if len(cur)<2: continue
    if -negc!=len(cur): heapq.heappush(heap,(-len(cur),p)); continue
    a,b,ratio=p; new=nxt; nxt+=1; steps+=1
    for i in list(cur):
        r=rows[i]
        for p2 in pairs(r):
            s_=idx.get(p2)
            if s_ is not None: s_.discard(i)
        ca=r.pop(a); r.pop(b); r[new]=ca
        for p2 in pairs(r):
            idx[p2].add(i)
            if len(idx[p2])>=2: heapq.heappush(heap,(-len(idx[p2]),p2))
    if steps%2000==0: print(' step',steps,'%.0fs'%(time.time()-t0),flush=True)
rem=sum(max(len(rows[i])-1,0) for i in sub)
naive=sum(len(rows[i])-1 for i in sub)
print(tag,'CSE steps',steps,'remaining adds',rem,'total ops',steps+rem,'(+ big-row naive %d)'%big_adds,'ratio naive/ops %.2f'%(naive/(steps+rem)),'helpers',nh)
pickle.dump(dict(nh=nh,contents=len(C),proj=len(R),naive=naive,ops=steps+rem,big=big_adds,hh=hhreads,gives=len(gives),givers=len(givers)),open('gate_%s.pkl'%tag,'wb'))
