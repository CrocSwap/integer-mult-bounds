import json, collections, sys, math, pickle
import numpy as np
sys.path.insert(0,'/home/claude/work/eval'); sys.path.insert(0,'/home/claude/work/agentA')
from cost import load_snapshot
from decomp import lab, idx
s,fr,dim,rec=load_snapshot('/home/claude/work/snap')
v=s['v'];n=s['n']
info=pickle.load(open('/home/claude/work/agentA/T/info.pkl','rb'))
role={}
for cube,C in info.items():
    for r in C['X']: role[r]=('X',cube)
    for pl,(r,last,e) in C['BH'].items(): role[r]=('BH',cube)
    for r in C['single']: role[r]=('S',cube)
    for r in C['carrier']: role[r]=('C',cube)
    for r in C['death']: role[r]=('D',cube)
    for r in C['upper']: role[r]=('U',cube)
    for r in C['other']: role[r]=('Y' if v<=r<2*v else 'M',cube)
F=fr['frames']
P=lambda p:p//2
cube_of=[tuple(sorted(P(p) for p in lab[i])) for i in range(v)]
chi=np.zeros((v,24),dtype=np.int64)
for i in range(v):
    for p in lab[i]: chi[i,p]=1
icache={}
def cubeframe(fid):
    if fid in icache: return icache[fid]
    if dim[fid]==0 or dim[fid]>3: icache[fid]=None; return None
    A=np.array(F[str(fid)]['A'],dtype=np.int64)
    I=frozenset(np.nonzero(np.all(chi@A.T==0,axis=1))[0].tolist())
    cs={cube_of[i] for i in I}
    icache[fid]=next(iter(cs)) if len(cs)==1 else None
    return icache[fid]
cat=collections.Counter(); catfull=collections.Counter()
for k in range(len(rec)):
    o,a,b,c,f,z=map(int,rec[k])
    if o!=1: continue
    if dim[f]==24:
        ra=role.get(a,('?',))[0]; rb=role.get(b,('?',))[0]
        if ra!='?' or rb!='?': catfull[(ra,rb)]+=1
        continue
    cq=cubeframe(f)
    if cq is None: continue
    ra=role.get(a,('?',None)); rb=role.get(b,('?',None))
    cat[(ra[0],rb[0],dim[f], ra[1]==cq if ra[1] else None, rb[1]==cq if rb[1] else None)]+=1
for k,c in sorted(cat.items(), key=lambda x:-x[1]): print(c,k)
print('FULL-frame ADDs by roles:')
for k,c in sorted(catfull.items(), key=lambda x:-x[1])[:30]: print(c,k)
