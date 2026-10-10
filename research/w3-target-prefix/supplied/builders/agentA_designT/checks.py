import json, collections, sys, math, pickle
import numpy as np
sys.path.insert(0,'/home/claude/work/eval'); sys.path.insert(0,'/home/claude/work/agentA')
from cost import load_snapshot
from decomp import lab, idx
s,fr,dim,rec=load_snapshot('/home/claude/work/snap')
v=s['v'];n=s['n']
info=pickle.load(open('/home/claude/work/agentA/T/info.pkl','rb'))
part=pickle.load(open('/home/claude/work/agentA/interface.pkl','rb'))
role={}
for cube,C in info.items():
    for r in C['X']: role[r]=('X',cube)
    for pl,(r,last,e) in C['BH'].items(): role[r]=('BH',cube)
    for r in C['single']: role[r]=('S',cube)
    for r in C['carrier']: role[r]=('C',cube)
    for r in C['death']: role[r]=('D',cube)
    for r in C['upper']: role[r]=('U',cube)
    for r in C['other']: role[r]=('Y' if v<=r<2*v else 'M',cube)
bhlast={}
for cube,C in info.items():
    for pl,(r,last,e) in C['BH'].items(): bhlast[r]=last
bad=collections.Counter(); badcubes=set()
for k in range(len(rec)):
    o,a,b,c,f,z=map(int,rec[k])
    if o!=1 or dim[f]==24 or dim[f]>3 or dim[f]==0: continue
    ra=role.get(a,('?',None)); rb=role.get(b,('?',None))
    if ra[0]=='U' and rb[0]=='BH':
        if f!=bhlast[b]: bad['U-absorbs-at-other-plane-id']+=1; badcubes.add(rb[1])
    if (ra[0],rb[0]) in (('Y','BH'),('X','BH')): bad[(ra[0],rb[0])]+=1; badcubes.add(rb[1])
# X chain shapes
xs=collections.Counter()
for cube,C in info.items():
    for x,d in C['X'].items():
        fr_=[dim[f] for f in d['frames']]
        e=d['exit']
        xs[(tuple(fr_), e[1] if e else None)]+=1
print(bad, len(badcubes))
print(xs.most_common(20))
pickle.dump(badcubes,open('/home/claude/work/agentA/T/badcubes.pkl','wb'))
