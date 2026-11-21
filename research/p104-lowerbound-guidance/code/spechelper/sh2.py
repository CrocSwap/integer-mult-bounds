# SPECHELPER sh2: t7669 vs the C1 hub-stop floor rows. Checks: rank (max chart dim), helper finals, strict ascent, stop-register climb>=2,
# every chart receiving an arrival hosts an intermediate stop (V exempt), the 104 P_t charts (Y/Y2 finals) host a stop each.
import sys, signal; signal.alarm(900)
sys.path.insert(0,'code/fewstops')
from load import *
from collections import defaultdict, Counter
N=n+W['owned_fields']
cur=list(W['initial'])
chain=defaultdict(list)
for r in range(n): chain[r].append(cur[r])
arr=defaultdict(int)
for e in P:
    if e[0]=='MOVE' and e[1]<n:
        chain[e[1]].append(e[3]); arr[SP[e[3]]]+=1
fr=lambda b: len(SP[b]).bit_length()-1   # dim of chart
print('public',n,'max chart dim',max(len(f) for f in F),'frames',len(F))
V=max(range(len(F)),key=lambda b:len(F[b]))
print('V dim',len(F[V]))
# strict ascent (as sets) and climb of stop registers
bad=0; stops=defaultdict(list); fin=Counter(); hfin=Counter()
for r in range(n):
    ch=chain[r]
    for a,b in zip(ch,ch[1:]):
        if not (SP[a]<SP[b]): bad+=1
    d0,d1=len(F[ch[0]]),len(F[ch[-1]])
    for c in ch[1:-1]: stops[SP[c]].append((r,d1-d0,len(ch)-2))
    if kind(r)=='H': hfin[len(F[ch[-1]])]+=1
    fin[(kind(r),len(F[ch[-1]]))]+=1
print('non-strict hops',bad)
print('helper final dims',dict(sorted(hfin.items())))
print('min climb of a stop register',min(c for L in stops.values() for (_,c,_) in L))
# per-chart rows
miss=[F_ for F_ in arr if not stops[F_]]
print('charts with arrivals',len(arr),'without stop',len(miss),[len(x).bit_length()-1 for x in miss])
# P_t charts: finals of Y2 and Y
Pt=set(); 
for r in range(n):
    if kind(r) in('Y','Y2'): Pt.add(SP[chain[r][-1]])
print('Y/Y2 final charts',len(Pt),'dim set',Counter(len(x).bit_length()-1 for x in Pt))
ys=Counter()
for r in range(n):
    if kind(r) in ('Y','Y2'): ys[kind(r),len(F[chain[r][-1]])]+=1
print(ys)
nst=[len(stops[c]) for c in Pt]
print('P_t charts hosting >=1 stop',sum(1 for k in nst if k>=1),'of',len(Pt),'min',min(nst))
print('total stops',sum(len(v) for v in stops.values()))
