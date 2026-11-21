import sys; sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
from collections import Counter, defaultdict
W=pk.load('<word-rung-package>/data/t7669.json.gz')
n=W['public']; P=W['program']; dim=[len(f) for f in W['frames']]
live=set(W['live']); H=W['hosted']
cls={}
for r in live: cls[r]='X'; cls[r+112]='Y'
for r in H['X2']: cls[r]='X2'
for r in H['Y2']: cls[r]='Y2'
mv=defaultdict(list)
for i,e in enumerate(P):
    if e[0]=='MOVE': mv[e[1]].append((dim[e[2]],dim[e[3]],e[2],e[3],i))
# public non-main
tot=Counter(); ranks=defaultdict(Counter)
for r,L in mv.items():
    c = 'own' if r>=n else cls.get(r,'helper')
    for a,b,*_ in L:
        d=b-a
        ranks[c][d]+=1
        if r<n: assert d>0,(r,L)
for c in ranks: print(c, sorted(ranks[c].items()), 'moves',sum(ranks[c].values()))
# per main: climb, #moves, moves list
for c in ['X','Y','X2','Y2']:
    cl=Counter(); nm=Counter()
    for r,k in cls.items():
        if k!=c: continue
        L=mv.get(r,[])
        climb=dim[W['final'][r]]-dim[W['initial'][r]]
        cl[(dim[W['initial'][r]],dim[W['final'][r]],tuple(b-a for a,b,*_ in L))]+=1
    print(c, len(cl)); 
    for k,v in sorted(cl.items(), key=lambda x:-x[1])[:12]: print('  ',k,v)
# helpers
hc=Counter()
for r in range(n):
    if r in cls: continue
    L=mv.get(r,[])
    hc[(dim[W['final'][r]]-dim[W['initial'][r]], tuple(b-a for a,b,*_ in L))]+=1
print('helpers',len(hc), sum(hc.values()))
for k,v in sorted(hc.items(), key=lambda x:-x[1])[:25]: print('  ',k,v)
nsplit=sum(v for k,v in hc.items() if len(k[1])>1); print('helpers split moves',nsplit)
# owned moves
for r,L in sorted(mv.items()):
    if r>=n: print('own',r,[(a,b,i) for a,b,_,_,i in L])
