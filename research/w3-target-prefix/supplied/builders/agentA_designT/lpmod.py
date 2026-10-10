# Show the registers of one LP module (anti-diagonal (a,b')/(a',b) on pairs Pa,Pb) in a word: chains and contents
import json, collections, sys, math
import numpy as np
sys.path.insert(0,'/home/claude/work/eval'); sys.path.insert(0,'/home/claude/work/agentA')
from cost import load_snapshot
from decomp import lab
d=sys.argv[1]; a0=int(sys.argv[2]); b0=int(sys.argv[3])   # points a and b' (anti-diagonal: items containing (a0,b0) or (a0^1,b0^1))
s,fr,dim,rec=load_snapshot(d)
v=s['v'];n=s['n'];R=n+1
g=lambda r: r*math.log(120/r) if r>0 else 0
P=lambda p:p//2
mod=set(i for i,l in enumerate(lab) if (a0 in l and b0 in l) or ((a0^1) in l and (b0^1) in l))
print('module items',len(mod))
Wd=(v+63)//64
val=np.zeros((R,Wd),np.uint64)
for i in range(v): val[i,i//64]|=np.uint64(1)<<np.uint64(i%64)
mm=np.zeros(Wd,np.uint64)
for i in mod: mm[i//64]|=np.uint64(1)<<np.uint64(i%64)
inside=np.ones(R,bool); has=np.zeros(R,bool)
init={r:dim[s['initial'][str(r)]] for r in range(n)}
ev=collections.defaultdict(list)
def pc(x): return int(np.unpackbits(x.view(np.uint8)).sum())
for k in range(len(rec)):
    o,a,b,c,f,z=map(int,rec[k])
    if o==0: ev[a].append(('M',dim[c]))
    elif o==1:
        if c&1:
            val[a]^=val[b]
            if a>=2*v and a<n:
                if (val[a]&~mm).any(): inside[a]=False
                if (val[a]&mm).any(): has[a]=True
        if a>=2*v and a<n and dim[f]<24: ev[a].append(('A',dim[f],pc(val[a]&mm)))
        if b>=2*v and b<n and dim[f]<24: ev[b].append(('D',dim[f]))
regs=[h for h in range(2*v,n) if has[h] and inside[h] and init[h]<24]
tot=0
rows=[]
for h in regs:
    ch=[]; d0=init[h]
    for e in ev[h]:
        if e[0]=='M': ch.append(e[1]-d0); d0=e[1]
    D=sum(g(x) for x in ch if x>0); tot+=D
    rows.append((h,init[h],ch,D,[e for e in ev[h] if e[0]!='M' and e[1]>3][:8]))
for r in sorted(rows,key=lambda x:x[2]): 
    if r[3]>0: print(r[0],'sig',r[1],r[2],'%.1f'%r[3],r[4])
print('registers',len(regs),'D %.0f'%tot)
