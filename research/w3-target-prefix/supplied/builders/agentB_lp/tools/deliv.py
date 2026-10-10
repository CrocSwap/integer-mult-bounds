import sys, json, pickle, collections
import numpy as np
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
W=Word(sys.argv[1]); rec=W.rec; dim=W.dim; init=W.init
lines=pickle.load(open(sys.argv[2],'rb'))
NR=len(rec)
byreg=collections.defaultdict(list)
for k in range(NR):
    o,a,b,c,f,z=rec[k]
    byreg[int(a)].append(k)
    if o==1 and b!=a: byreg[int(b)].append(k)
pat=collections.Counter(); examples={}
for key,v in lines.items():
    modset=set(v['others'])|{p['r'] for p in v['planes'].values()}
    copies=set(v['copies'])
    for Z,o in v['outs'].items():
        r=o['old']; kc=o['kcopy']
        # records of r at/after kcopy (excluding module inverses: FULL ADDs with module partner)
        sig=[]
        for k in byreg[r]:
            if k<kc: continue
            op,a,b,c,f,z=[int(x) for x in rec[k]]
            if op==0: sig.append('MV%d>%d'%(dim[b],dim[c]))
            elif op==1:
                other=b if a==r else a
                role='src' if b==r else 'dst'
                kind='copy' if other in copies else ('mod' if other in modset else ('Y' if W.s['v']<=other<2*W.s['v'] else ('X' if other<W.s['v'] else 'H')))
                sig.append('%s:%s@d%d c%d'%(role,kind,dim[f],c))
        t=tuple(sig)
        pat[t]+=1; examples.setdefault(t,(key,Z,r))
for t,c in pat.most_common(20): print(c,examples[t],t)
print(len(pat))
