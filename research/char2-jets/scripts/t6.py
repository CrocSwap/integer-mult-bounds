# tied_min: all B with cost <= 13 (rank caps), classify CR2 (GF2/GF4)
import sys, json, collections, itertools
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from satlib import enumerate_B; from cr2 import *
P,Q=load_cfg('tied_min.json'); R,A,free=setup(P,Q); pi,sig=cfg_data(P,Q)
seen={}
for caps in set(itertools.permutations((4,4,5)))|set(itertools.permutations((3,5,5)))|set(itertools.permutations((3,4,6))):
    for ent in enumerate_B(P,Q,caps):
        seen[tuple(ent)]=1
print('B with cost<=13 (via caps):', len(seen))
stat=collections.Counter(); non=[]
for ent in seen:
    B=[[int(t==s) for s in range(12)] for t in range(12)]
    for t,s in ent: B[t][s]=1
    c=sum(blockranks(B,R,A))
    k=0
    for kk in (1,2,3):
        if isinstance(realise(pi,sig,set(ent),k=kk,limit=10**5),dict): k=kk; break
    stat[(c,k)]+=1
    if not k: non.append(ent)
print(sorted(stat.items())); json.dump(non, open('tm_c13_noncr2.json','w'))
