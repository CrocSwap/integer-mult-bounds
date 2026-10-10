# D of LP-module registers (plane regs from their plane frame onward, plus fresh module regs) in a word.
import sys, pickle, json, numpy as np, math, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
d=sys.argv[1]; lines=pickle.load(open(sys.argv[2],'rb'))
W=Word(d); rec=W.rec; dim=W.dim; init=W.init
mv=rec[rec[:,0]==0]
chains=collections.defaultdict(list)
for o,a,b,c,f,z in mv.tolist(): chains[a].append((b,c,f))
tot_plane=0; tot_fresh=0; tot_copy=0; nf=0
for key,L in lines.items():
    for X,p in L['planes'].items():
        r=p['r']
        # cost after reaching plane frame (dim 3)
        for b,c,f in chains[r]:
            if dim[b]>=3 and f>0: tot_plane+=g(f)
    for r in L['others']:
        if dim[init[r]]==24: continue
        nf+=1
        for b,c,f in chains[r]:
            if f>0: tot_fresh+=g(f)
    for r in L['copies']:
        for b,c,f in chains[r]:
            if f>0: tot_copy+=g(f)
print(d,'plane post-3 %.1f fresh %.1f (n=%d) module total %.1f per line %.1f | sigma20 copies %.1f'%(tot_plane,tot_fresh,nf,tot_plane+tot_fresh,(tot_plane+tot_fresh)/132,tot_copy))
