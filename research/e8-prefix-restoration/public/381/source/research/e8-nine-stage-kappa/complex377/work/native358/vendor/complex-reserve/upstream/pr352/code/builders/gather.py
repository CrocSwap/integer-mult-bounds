# Gather per-cube structural info for the cube-layer redesign.
import os
import json, collections, sys, math, pickle
import numpy as np
sys.path.insert(0,''+os.environ.get('W3WORK','work')+'/eval'); sys.path.insert(0,''+os.environ.get('W3WORK','work')+'/agentA')
from cost import load_snapshot
from decomp import lab, idx
s,fr,dim,rec=load_snapshot(''+os.environ.get('W3WORK','work')+'/snap')
v=s['v'];n=s['n']; R=n+1
F=fr['frames']
P=lambda p:p//2
cube_of=[tuple(sorted(P(p) for p in lab[i])) for i in range(v)]
bits=lambda i: tuple(p%2 for p in lab[i])
part=pickle.load(open(''+os.environ.get('W3WORK','work')+'/agentA/interface.pkl','rb'))
init={r:s['initial'][str(r)] for r in range(n)}
ZERO=s['ZERO']; FULL=s['FULL']
HH=20
chi=np.zeros((v,HH),dtype=np.int64)
for i in range(v):
    for p in lab[i]: chi[i,p]=1
icache={}
def items_in(fid):
    if fid in icache: return icache[fid]
    if dim[fid]==0 or dim[fid]>3: icache[fid]=None; return None
    A=np.array(F[str(fid)]['A'],dtype=np.int64)
    I=frozenset(np.nonzero(np.all(chi@A.T==0,axis=1))[0].tolist()); icache[fid]=I if I else None; return icache[fid]
cubes=collections.defaultdict(set)
for r,d in part.items(): cubes[d['cube']].add(r)
# classify participants
info={}
cnt=collections.Counter()
for cube,regs in cubes.items():
    items=sorted(i for i in range(v) if cube_of[i]==cube)
    byb={bits(i):i for i in items}
    C=dict(items=items,byb=byb,BH={},single={},carrier=[],death=[],upper=[],other=[],X={})
    for r in regs:
        d=part[r]; e=d['exit']
        if r<v: C['X'][r]=d; continue
        if v<=r<2*v: C['other'].append(r); continue
        if e is None: C['other'].append(r); cnt['noexit']+=1; continue
        c=d.get('exit_content',()); last=d['frames'][-1]
        if d['fromzero'] and dim[d['entry']]==3 and e[1] not in (HH-1,HH) and len(c)==4:
            C['upper'].append(r); continue
        if e[1]==HH:
            C['death'].append(r); continue
        if e[1]==HH-1 and len(c)==1:
            C['single'][r]=d; continue
        if len(c)==4 and dim[last]==3:
            pl=frozenset(c)
            if pl in C['BH']: cnt['dupBH']+=1
            C['BH'][pl]=(r,last,e); continue
        if d['fromzero'] and dim[d['entry']]==2 and dim[last]==2:
            C['other'].append(r); cnt['Mup']+=1; continue
        C['carrier'].append(r)
    info[cube]=C
    cnt['BHcount%d'%len(C['BH'])]+=1
print(cnt)
pickle.dump(info,open(''+os.environ.get('W3WORK','work')+'/agentA/T/info.pkl','wb'))
