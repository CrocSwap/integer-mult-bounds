# Upper-network register analysis on a given word dir: for each helper, content at each frame; classify death points.
import json, collections, sys, math
import numpy as np
sys.path.insert(0,'/home/claude/work/eval')
from cost import load_snapshot
d=sys.argv[1]
s,fr,dim,rec=load_snapshot(d)
v=s['v'];n=s['n'];R=n+1
g=lambda r: r*math.log(120/r) if r>0 else 0
init={r:dim[s['initial'][str(r)]] for r in range(n)}
Wd=(v+63)//64
val=np.zeros((R,Wd),np.uint64)
for i in range(v): val[i,i//64]|=np.uint64(1)<<np.uint64(i%64)
def pc(x):
    return int(np.unpackbits(x.view(np.uint8)).sum())
cur={r:dim[s['initial'][str(r)]] for r in range(n)}
maxc=np.zeros(R,int)
lastnonfull={}   # role -> (dim before final jump, content size at that time)
chain=collections.defaultdict(list)
for k in range(len(rec)):
    o,a,b,c,f,z=map(int,rec[k])
    if o==0:
        if a>=2*v and a<n:
            if dim[c]==24 and a not in lastnonfull: lastnonfull[a]=(cur[a],pc(val[a]))
            chain[a].append(dim[c]-cur[a])
        cur[a]=dim[c]
    elif o==1:
        if c&1: val[a]^=val[b]
        if a>=2*v and a<n: maxc[a]=max(maxc[a],pc(val[a]))
    elif o==2: val[n]=val[a]
    elif o==3: val[n]=0
cat=collections.defaultdict(lambda:[0,0.0])
for h in range(2*v,n):
    if init[h]==24: continue
    dd,cs=lastnonfull.get(h,(None,None))
    key=(dd, 'c%d'%cs if cs is not None and cs<=8 else ('c9-40' if cs is not None and cs<=40 else ('c41-180' if cs is not None and cs<=180 else 'c>180')))
    cat[key][0]+=1; cat[key][1]+=sum(g(x) for x in chain[h] if x>0)
tot=sum(x[1] for x in cat.values())
for k,(c,dd) in sorted(cat.items(), key=lambda x:-x[1][1])[:40]:
    print('%-25s n=%5d D=%8.0f (%4.1f%%) per=%.1f'%(str(k),c,dd,100*dd/tot,dd/c))
print('total helper D',round(tot))
