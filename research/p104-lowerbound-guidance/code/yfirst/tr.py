import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter
paths={r:[dim[W['initial'][r]]] for r in range(n)}
for e in P:
    if e[0]=='MOVE' and e[1]<n: paths[e[1]].append(dim[e[3]])
pat=tuple(int(x) for x in sys.argv[1].split(','))
mind=int(sys.argv[2]) if len(sys.argv)>2 else 0
hs=[r for r in range(n) if kind(r)=='H' and tuple(paths[r])==pat]
h=hs[int(sys.argv[3]) if len(sys.argv)>3 else 0]
print('helper',h,'path',paths[h])
cur=list(W['initial'])+[None]*W['owned_fields']
cnt=Counter()
for i,e in enumerate(P):
    if e[0]=='MOVE':
        cur[e[1]]=e[3]
        if e[1]==h: print(i,'MOVE ->',dim[e[3]],F[e[3]])
        continue
    if e[0]=='INIT': cur[e[1]]=e[2]; continue
    if e[0] in('ADD','COPY') and h in (e[1],e[2]):
        if dim[e[4]]<mind: continue
        o=e[2] if e[1]==h else e[1]; d='in ' if e[1]==h else 'out'
        print(i,d,kind(o)+str(o),e[3],'@d',dim[e[4]], 'partner path',paths.get(o) if o<n else 'owned')
    elif e[0]=='SCALE' and e[1]==h and dim[e[3]]>=mind: print(i,e)
