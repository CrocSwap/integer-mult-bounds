import sys, json, numpy as np
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from phi import classify; from jet2 import *
for i in range(3):
    P,Q=json.load(open(PKG+'/data/jf%d.json'%i)); v=len(P); R,A,free=setup(P,Q); w,H=classify(P,Q)
    an=analyse(P,Q,free,H); d=len(an['basis'])
    E=an['E']
    depM=[quad_matrix(an,[E[k] for k in range(len(E)) if z>>k&1]) for z in an['deps']]
    immM={t:quad_matrix(an,[(t,t)]+[E[k] for k in range(len(E)) if c>>k&1]) for t,c in an['imm'].items()}
    print('jf%d v %d |E| %d dimV %d #deps %d immovable %s'%(i,v,len(E),d,len(an['deps']),list(an['imm'])), flush=True)
    if d>26: print('  too big for F2 enumeration'); continue
    found=None; cnt=0
    for us,vals in eval_quads(depM+list(immM.values()),d):
        nd=len(depM); ok=np.ones(len(us),dtype=bool)
        for k in range(nd): ok&=(vals[k]==0)
        for k in range(nd,len(vals)): ok&=(vals[k]==1)
        cnt+=int(ok.sum())
        if found is None and ok.any(): found=int(us[np.argmax(ok)])
    print('  F2 points with all solvability quadrics 0 and all immovable Q_t = 1:',cnt,'example u',found, flush=True)
