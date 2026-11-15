# Which constraint locks the B2 slack?  B3w = windows only (blocks merged), B3o = block order only (full partner chart sets).
import sys, pickle, math
import b3
from collections import defaultdict
mode=sys.argv[1]
orig=b3.build
def build2(m):
    S,F,path,blocks=orig(m)
    if mode=='w':
        return S,F,path,[sorted(set().union(*[set(b) for b in blocks]),key=len)] if blocks else []
    # mode o: replace each contact's window set by the partner's full in-interval chart set: need partner ids -> rebuild
    st=b3.stays[m]; ev=[]
    for t,e in enumerate(b3.prog):
        if e[0] in('ADD','COPY') and (e[1]==m)!=(e[2]==m):
            ev.append(('recv' if e[1]==m else 'give', e[2] if e[1]==m else e[1]))
        elif e[0]=='SCALE' and e[1]==m: ev.append(('scale',None))
    bl=[]; kind=None
    for k,p in ev:
        if k=='scale': bl.append([]); kind='scale'; continue
        if k!=kind: bl.append([]); kind=k
        bl[-1].append(frozenset(G for G,s,e in b3.stays[p] if G is not None and b3.sp[S]<=b3.sp[G]<=b3.sp[F]))
    return S,F,path,[sorted(set(b),key=len) for b in bl if b]
b3.build=build2
agg=defaultdict(lambda:[0,0]); res={}
for m in sorted(b3.cls):
    best,path,nb=b3.solve(m); c=b3.cls[m]
    agg[c][0]+=b3.val(path); agg[c][1]+=best[1]; res[m]=(b3.val(path),best[1],best[0],path)
pickle.dump(res,open('var_%s.pkl'%mode,'wb'))
for k,a in sorted(agg.items()): print(mode,k,'actual %.1f bound %.1f'%tuple(a))
print('nodes',b3.nodes[0])
