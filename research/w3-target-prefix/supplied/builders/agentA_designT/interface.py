# Extract each cube's cube-layer interface: participating registers, their entry/exit frames and exit contents.
import json, collections, sys, math, pickle
import numpy as np
sys.path.insert(0,'/home/claude/work/eval'); sys.path.insert(0,'/home/claude/work/agentA')
from cost import load_snapshot
from decomp import lab, idx
s,fr,dim,rec=load_snapshot('/home/claude/work/snap')
v=s['v'];n=s['n']; R=n+1
F=fr['frames']
P=lambda p:p//2
cube_of=[tuple(sorted(P(p) for p in lab[i])) for i in range(v)]
chi=np.zeros((v,24),dtype=np.int64)
for i in range(v):
    for p in lab[i]: chi[i,p]=1
icache={}
def items_in(fid):
    if fid in icache: return icache[fid]
    if dim[fid]==0 or dim[fid]>3: icache[fid]=None; return None
    A=np.array(F[str(fid)]['A'],dtype=np.int64)
    I=frozenset(np.nonzero(np.all(chi@A.T==0,axis=1))[0].tolist())
    icache[fid]=I if I else None
    return icache[fid]
def cubeframe(fid):
    I=items_in(fid)
    if not I: return None
    cs={cube_of[i] for i in I}
    return next(iter(cs)) if len(cs)==1 else None
init={r:s['initial'][str(r)] for r in range(n)}
fin={r:s['final'][str(r)] for r in range(n)}
# simulate contents; track per register its frame and content at each move
Wd=(v+63)//64
val=np.zeros((R,Wd),np.uint64)
for i in range(v): val[i,i//64]|=np.uint64(1)<<np.uint64(i%64)
def its(r):
    b=np.unpackbits(val[r].view(np.uint8),bitorder='little')[:v]; return tuple(np.nonzero(b)[0].tolist())
cur={r:init[r] for r in range(n)}
part={}   # r -> dict(cube, entry_frame, entry_from_zero, frames list, exit (frame,dim,k), exit_content)
for r in range(n):
    c=cubeframe(init[r])
    if c is not None: part[r]=dict(cube=c,entry=init[r],fromzero=False,frames=[init[r]],exit=None,firstk=0)
for k in range(len(rec)):
    o,a,b,c,f,z=map(int,rec[k])
    if o==0:
        r=a; newf=c
        cq=cubeframe(newf)
        if r in part and part[r]['exit'] is None:
            if cq==part[r]['cube']:
                part[r]['frames'].append(newf)
            else:
                part[r]['exit']=(newf,dim[newf],k); part[r]['exit_content']=its(r)
        elif r not in part and cq is not None and dim[cur[r]]==0:
            part[r]=dict(cube=cq,entry=newf,fromzero=True,frames=[newf],exit=None,firstk=k)
        cur[r]=newf
    elif o==1:
        if c&1: val[a]^=val[b]
    elif o==2: val[n]=val[a]
    elif o==3: val[n]=0
pickle.dump(part,open('/home/claude/work/agentA/interface.pkl','wb'))
stat=collections.Counter()
for r,d in part.items():
    kind='X' if r<v else 'H'
    ex=d['exit']
    exd=ex[1] if ex else None
    cont=d.get('exit_content',())
    ncont=len(cont)
    lastdim=dim[d['frames'][-1]]
    stat[(kind,dim[d['entry']],lastdim,exd if exd in (24,23,22) else ('up' if exd else None),ncont if ncont<=4 else '>4')]+=1
for k,c in sorted(stat.items(), key=lambda x:-x[1])[:40]: print(c,k)
